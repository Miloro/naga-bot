import discord
from discord import app_commands
import asyncio

desafios = {}


# ==== Vista de botones para el retador ====
class EleccionRetador(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, desafios: dict, monto: str = "0"):
        super().__init__(timeout=60)  # 1 minuto para elegir
        self.interaction = interaction
        self.desafios = desafios
        self.monto = monto

    async def guardar_jugada(self, interaction: discord.Interaction, jugada: str):
        self.desafios[self.interaction.channel.id] = {
            "retador": self.interaction.user,
            "jugada": jugada,
            "activo": True
        }
        await interaction.response.send_message(f"✅ Jugada **{jugada}** guardada.", ephemeral=True)
        await self.interaction.followup.send(
            f"🪨📄✂️ {self.interaction.user.mention} aposto {self.monto}, averga quien tiene los coquitos grandes para ganarle.\n"
            f"¡Tienes 10 minutos para responder usando `/respuesta <jugada>`!"
        )
        self.stop()

    @discord.ui.button(label="🪨", style=discord.ButtonStyle.primary)
    async def piedra(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_jugada(interaction, "piedra")

    @discord.ui.button(label="📄", style=discord.ButtonStyle.success)
    async def papel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_jugada(interaction, "papel")

    @discord.ui.button(label="✂️", style=discord.ButtonStyle.danger)
    async def tijeras(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_jugada(interaction, "tijeras")


# ==== Comando desafío ====
async def desafio(interaction: discord.Interaction, monto: str):
    view = EleccionRetador(interaction, desafios, monto)
    await interaction.response.send_message("✋ Elige tu jugada:", view=view, ephemeral=True)

    # Espera 10 minutos antes de cerrar el desafío
    await asyncio.sleep(600)
    if desafios.get(interaction.channel.id, {}).get("activo", False):
        desafios[interaction.channel.id]["activo"] = False
        await interaction.channel.send("⏰ El desafío ha expirado, nadie respondió a tiempo.")


# ==== Comando respuesta ====
async def respuesta(interaction: discord.Interaction, eleccion: str):
    eleccion = eleccion.lower()
    if eleccion not in ["piedra", "papel", "tijeras"]:
        await interaction.response.send_message("⚠️ Solo puedes elegir: piedra, papel o tijeras.")
        return

    desafio = desafios.get(interaction.channel.id)
    if not desafio or not desafio["activo"]:
        await interaction.response.send_message("⚠️ No hay desafíos activos en este canal.")
        return

    #if interaction.user == desafio["retador"]:
    #    await interaction.response.send_message("⚠️ No puedes responder a tu propio desafío.")
    #    return

    # Cerramos el desafío
    desafio["activo"] = False
    jugada_retador = desafio["jugada"]
    jugada_oponente = eleccion

    resultado = determinar_ganador(jugada_retador, jugada_oponente)

    await interaction.response.send_message(
        f"🎮 **Desafío resuelto**\n"
        f"👤 Retador: {desafio['retador'].mention} jugó **{jugada_retador}**\n"
        f"👤 Oponente: {interaction.user.mention} jugó **{jugada_oponente}**\n\n"
        f"🏆 Resultado: {resultado}"
    )


# ==== Lógica del ganador ====
def determinar_ganador(j1, j2):
    if j1 == j2:
        return "🤝 ¡Empate!"
    if (j1 == "piedra" and j2 == "tijeras") or \
       (j1 == "papel" and j2 == "piedra") or \
       (j1 == "tijeras" and j2 == "papel"):
        return "🎉 ¡Gana el retador!"
    return "🎉 ¡Gana el oponente!"


# ==== Registro de comandos ====
def setup(bot):
    bot.tree.add_command(app_commands.Command(name="desafio", description="Inicia un desafío", callback=desafio))
    bot.tree.add_command(app_commands.Command(name="respuesta", description="Responde a un desafío", callback=respuesta))
