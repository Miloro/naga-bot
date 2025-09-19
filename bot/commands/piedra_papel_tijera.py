import discord
from discord import app_commands
import asyncio

# Diccionario global donde guardamos los desafíos activos
# La clave será el channel.id y el valor un diccionario con:
# retador, jugada, monto, bolsas, estado
desafios = {}


# ==== Vista de botones para el retador ====
class EleccionRetador(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, desafios: dict, monto: str = "0", continuar: bool = False):
        super().__init__(timeout=60)  # 1 minuto de tiempo para elegir
        self.interaction = interaction
        self.desafios = desafios
        self.monto = monto
        self.continuar = continuar

    async def guardar_jugada(self, interaction: discord.Interaction, jugada: str):
        channel_id = self.interaction.channel.id

        if not self.continuar:
            # Crear desafío nuevo
            self.desafios[channel_id] = {
                "retador": self.interaction.user,
                "jugada": jugada,
                "monto": self.monto,
                "bolsa_jugador_1": 0,
                "bolsa_jugador_2": 0,
                "activo": True
            }

            # Confirmación oculta
            await interaction.response.send_message(f"✅ Jugada **{jugada}** guardada.", ephemeral=True)

            # Publicamos el desafío en el canal
            view = EleccionOponente(self.interaction, self.desafios)
            await self.interaction.followup.send(
                f"{self.interaction.user.mention} inició un duelo a muerte con cuchillos ({self.monto}).\n"
                f"¿Quién acepta el desafío? Elige tu jugada:",
                view=view
            )
        else:
            # Continuación: solo actualizamos jugada
            self.desafios[channel_id]["jugada"] = jugada
            await interaction.response.send_message(f"✅ Elegiste **{jugada}**", ephemeral=True)

        self.stop()

    @discord.ui.button(label="juntar faca", style=discord.ButtonStyle.primary)
    async def piedra(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_jugada(interaction, "mas_uno")

    @discord.ui.button(label="defender", style=discord.ButtonStyle.success)
    async def papel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_jugada(interaction, "defender")

    @discord.ui.button(label="atacar", style=discord.ButtonStyle.danger)
    async def tijera(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_jugada(interaction, "atacar")


# ==== Vista de botones para el oponente ====
class EleccionOponente(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, desafios: dict):
        super().__init__(timeout=600)
        self.interaction = interaction
        self.desafios = desafios

    async def resolver(self, interaction: discord.Interaction, jugada_oponente: str):
        channel_id = self.interaction.channel.id
        desafio = self.desafios.get(channel_id)

        if not desafio or not desafio["activo"]:
            await interaction.response.send_message("❌ El desafío ya no está activo.", ephemeral=True)
            return

        retador = desafio["retador"]
        jugada_retador = desafio["jugada"]

        # Resolver resultado y actualizar bolsas
        resultado = self.determinar_ganador(channel_id, jugada_retador, jugada_oponente)

        # Mostrar resultado en el canal
        if resultado in ["gana1", "gana2", "empate"]:
            desafio["activo"] = False
            await interaction.response.send_message(f"🏆 Resultado: {resultado}")
            self.stop()
        else:
            # Mostrar estado de bolsas
            b1 = desafio["bolsa_jugador_1"]
            b2 = desafio["bolsa_jugador_2"]
            await interaction.response.send_message(
                f"{resultado}\n"
                f"📦 Bolsas → Jugador 1: {b1} | Jugador 2: {b2}\n"
                f"{retador.mention}, elige tu próxima jugada:"
            )

            # Retador elige otra vez (ephemeral)
            view_retador = EleccionRetador(self.interaction, self.desafios, desafio["monto"], continuar=True)
            await interaction.followup.send("✋ Elige tu jugada:", view=view_retador, ephemeral=True)

            # Oponente recibe botones públicos de nuevo
            view_oponente = EleccionOponente(self.interaction, self.desafios)
            await interaction.followup.send(
                "👤 Turno del oponente, elige tu jugada:",
                view=view_oponente,
                ephemeral=True
            )

    def determinar_ganador(self, channel_id: int, jugada1: str, jugada2: str):
        desafio = self.desafios[channel_id]
        b1 = desafio["bolsa_jugador_1"]
        b2 = desafio["bolsa_jugador_2"]

        # Reglas con modificaciones de bolsas
        if jugada1 == "atacar" and jugada2 == "atacar":
            if b1 > 0 and b2 > 0:
                desafio["bolsa_jugador_1"] -= 1
                desafio["bolsa_jugador_2"] -= 1
                return "empate"
            elif b1 == 0 and b2 > 0:
                return "gana2"
            elif b1 > 0 and b2 == 0:
                return "gana1"
            else:
                return "nadie puede atacar"

        elif jugada1 == "atacar" and jugada2 == "defender":
            if b1 > 0:
                desafio["bolsa_jugador_1"] -= 1
                return "jugador 1 pierde un cuchillo"
            else:
                return "jugador 1 no hace nada"

        elif jugada1 == "atacar" and jugada2 == "mas_uno":
            if b1 > 0:
                return "gana1"
            else:
                desafio["bolsa_jugador_2"] += 1
                return "jugador 1 no hace nada y jugador 2 gana un cuchillo"

        elif jugada1 == "defender" and jugada2 == "atacar":
            if b2 > 0:
                desafio["bolsa_jugador_2"] -= 1
                return "jugador 2 pierde un cuchillo"
            else:
                return "jugador 2 no hace nada"

        elif jugada1 == "defender" and jugada2 == "defender":
            return "ambos se defienden"

        elif jugada1 == "defender" and jugada2 == "mas_uno":
            desafio["bolsa_jugador_2"] += 1
            return "jugador 2 gana un cuchillo"

        elif jugada1 == "mas_uno" and jugada2 == "atacar":
            if b2 > 0:
                return "gana2"
            else:
                desafio["bolsa_jugador_1"] += 1
                return "jugador 2 no hace nada y jugador 1 gana un cuchillo"

        elif jugada1 == "mas_uno" and jugada2 == "defender":
            desafio["bolsa_jugador_1"] += 1
            return "jugador 1 gana un cuchillo"

        elif jugada1 == "mas_uno" and jugada2 == "mas_uno":
            desafio["bolsa_jugador_1"] += 1
            desafio["bolsa_jugador_2"] += 1
            return "ambos ganan un cuchillo"

        return "jugada inválida"

    @discord.ui.button(label="juntar faca", style=discord.ButtonStyle.primary)
    async def piedra(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolver(interaction, "mas_uno")

    @discord.ui.button(label="defender", style=discord.ButtonStyle.success)
    async def papel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolver(interaction, "defender")

    @discord.ui.button(label="atacar", style=discord.ButtonStyle.danger)
    async def tijera(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolver(interaction, "atacar")


# ==== Comando desafío ====
async def desafio(interaction: discord.Interaction, monto: str):
    view = EleccionRetador(interaction, desafios, monto)
    await interaction.response.send_message("✋ Elige tu jugada:", view=view, ephemeral=True)

    await asyncio.sleep(600)
    if desafios.get(interaction.channel.id, {}).get("activo", False):
        desafios[interaction.channel.id]["activo"] = False
        await interaction.channel.send("⏰ El desafío ha expirado, nadie respondió a tiempo.")


# ==== Registro de comandos ====
def setup(bot):
    bot.tree.add_command(app_commands.Command(name="desafio", description="Inicia un desafío", callback=desafio))
