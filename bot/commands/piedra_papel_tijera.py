import discord
from discord import app_commands
import asyncio

# Diccionario global para manejar desafíos por canal
desafios = {}

class DueloAMuerte:
    def __init__(self, interaccion_retador: discord.Interaction, monto: int):
        self.interaccion_retador = interaccion_retador
        self.interaccion_desafiado = None
        self.monto_apostado = monto
        self.bolsa_jugador_1 = 0
        self.bolsa_jugador_2 = 0
        self.jugada1 = None
        self.jugada2 = None
        self.channel = interaccion_retador.channel

    async def iniciar_desafio(self):
        # Mensaje inicial
        await self.interaccion_retador.response.send_message(
            "Espera a que alguien responda a tu desafío...", ephemeral=True
        )

        view = AceptarDuelo(self)
        await self.channel.send(
            f"{self.interaccion_retador.user.mention} inició un duelo a muerte ({self.monto_apostado}).\n"
            "¿Quién acepta el desafío?",
            view=view
        )

        # Tiempo límite de 5 minutos
        await asyncio.sleep(300)
        if self.channel.id in desafios and desafios[self.channel.id]["activo"]:
            desafios[self.channel.id]["activo"] = False
            await self.channel.send("El desafío ha expirado, nadie respondió a tiempo.")

    async def iniciar_ronda(self):
        self.jugada1 = None
        self.jugada2 = None

        # Enviar opciones privadas a cada jugador
        view1 = EleccionJugador(self, jugador=1)
        view2 = EleccionJugador(self, jugador=2)

        await self.interaccion_retador.followup.send(
            "Elige tu jugada:",
            view=view1,
            ephemeral=True
        )
        await self.interaccion_desafiado.followup.send(
            "Elige tu jugada:",
            view=view2,
            ephemeral=True
        )

        # Esperar hasta que ambos jueguen o expire tiempo
        for _ in range(30):
            if self.jugada1 and self.jugada2:
                break
            await asyncio.sleep(1)

        if not self.jugada1 or not self.jugada2:
            await self.channel.send("No todos eligieron a tiempo. El duelo termina.")
            desafios[self.channel.id]["activo"] = False
            return

        # Determinar ganador o continuar
        resultado = self.determinar_ganador(self.jugada1, self.jugada2)
        if resultado == "empate":
            await self.channel.send("Ambos dispararon y se mataron, ¡empate!")
            desafios[self.channel.id]["activo"] = False
        elif resultado == "gana1":
            await self.channel.send(f"🏆 {self.interaccion_retador.user.mention} gana el duelo!")
            desafios[self.channel.id]["activo"] = False
        elif resultado == "gana2":
            await self.channel.send(f"{self.interaccion_desafiado.user.mention} gana el duelo!")
            desafios[self.channel.id]["activo"] = False
        else:
            await self.channel.send("La batalla continúa...")
            await self.iniciar_ronda()

    def registrar_jugada(self, jugador: int, jugada: str):
        if jugador == 1:
            self.jugada1 = jugada
        else:
            self.jugada2 = jugada

    def determinar_ganador(self, jugada1: str, jugada2: str):
        b1 = self.bolsa_jugador_1
        b2 = self.bolsa_jugador_2

        def atacar_vs_atacar():
            if b1 > 0 and b2 > 0:
                self.bolsa_jugador_1 -= 1
                self.bolsa_jugador_2 -= 1
                return "empate"
            elif b1 == 0 and b2 > 0:
                return "gana2"
            elif b1 > 0 and b2 == 0:
                return "gana1"
            else:
                return "seguir"

        def atacar_vs_defender():
            if b1 > 0:
                self.bolsa_jugador_1 -= 1
            return "seguir"

        def atacar_vs_recargar():
            if b1 > 0:
                self.bolsa_jugador_1 -= 1
                return "gana1"
            else:
                self.bolsa_jugador_2 += 1
                return "seguir"

        def recargar_vs_atacar():
            if b2 > 0:
                return "gana2"
            else:
                self.bolsa_jugador_1 += 1
                return "seguir"

        def recargar_vs_recargar():
            self.bolsa_jugador_1 += 1
            self.bolsa_jugador_2 += 1
            return "seguir"

        def recargar_vs_defender():
            self.bolsa_jugador_1 += 1
            return "seguir"

        def defender_vs_recargar():
            self.bolsa_jugador_2 += 1
            return "seguir"

        reglas = {
            ("atacar", "atacar"): atacar_vs_atacar,
            ("atacar", "defender"): atacar_vs_defender,
            ("atacar", "recargar"): atacar_vs_recargar,
            ("defender", "atacar"): atacar_vs_defender,
            ("defender", "defender"): lambda: "seguir",
            ("defender", "recargar"): defender_vs_recargar,
            ("recargar", "atacar"): recargar_vs_atacar,
            ("recargar", "defender"): recargar_vs_defender,
            ("recargar", "recargar"): recargar_vs_recargar,
        }

        return reglas.get((jugada1, jugada2), lambda: "seguir")()


class AceptarDuelo(discord.ui.View):
    def __init__(self, duelo: DueloAMuerte):
        super().__init__(timeout=300)
        self.duelo = duelo

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.success)
    async def aceptar(self, interaction: discord.Interaction, button: discord.ui.Button):
        #if interaction.user == self.duelo.interaccion_retador.user:
        #    await interaction.response.send_message("No puedes aceptar tu propio duelo.", ephemeral=True)
        #    return

        self.duelo.interaccion_desafiado = interaction
        desafios[self.duelo.channel.id] = {"activo": True, "duelo": self.duelo}

        await interaction.response.send_message("Has aceptado el duelo!", ephemeral=True)
        await self.duelo.channel.send(
            f"🔥 {interaction.user.mention} ha aceptado el duelo contra {self.duelo.interaccion_retador.user.mention}!"
        )

        self.stop()
        await self.duelo.iniciar_ronda()


class EleccionJugador(discord.ui.View):
    def __init__(self, duelo: DueloAMuerte, jugador: int):
        super().__init__(timeout=30)
        self.duelo = duelo
        self.jugador = jugador

    async def registrar(self, interaction: discord.Interaction, jugada: str):
        self.duelo.registrar_jugada(self.jugador, jugada)
        await interaction.response.send_message(f"Elegiste **{jugada}**", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Recargar", style=discord.ButtonStyle.primary)
    async def recargar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar(interaction, "recargar")

    @discord.ui.button(label="Defender", style=discord.ButtonStyle.secondary)
    async def defender(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar(interaction, "defender")

    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.danger)
    async def atacar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar(interaction, "atacar")


async def desafio(interaction: discord.Interaction, monto: int):
    duelo = DueloAMuerte(interaction, monto)
    await duelo.iniciar_desafio()


def setup(bot):
    bot.tree.add_command(app_commands.Command(
        name="desafio",
        description="Inicia un desafío a muerte",
        callback=desafio
    ))
