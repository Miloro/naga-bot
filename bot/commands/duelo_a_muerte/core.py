import discord
from discord import app_commands
import asyncio
import io
import aiohttp

from bot.commands.duelo_a_muerte.imagen_handler import *

desafios = {}

class DueloAMuerte:
    def __init__(self, interaccion_jugador_1: discord.Interaction, monto: int):
        self.interaccion_jugador_1 = interaccion_jugador_1
        self.interaccion_jugador_2 = None
        self.monto_apostado = monto
        self.bolsa_jugador_1 = 0
        self.bolsa_jugador_2 = 0
        self.jugada1 = None
        self.jugada2 = None
        self.channel = interaccion_jugador_1.channel
        self.avatar_jugador_1 = None
        self.avatar_jugador_2 = None
        self.imagen_jugada_intermedia = None


    async def iniciar_desafio(self):
        # Se manda un mensaje privado al que desafia
        await self.interaccion_jugador_1.response.send_message(
            "Arrancaste una pelea a muerte espera a ver quien tiene los coquitos para aceptar tu desafio...", ephemeral=True
        )
        # Se crea una imagen con la imagen de perfil de la persona que desafia
        # si la persona que desafia no tiene foto de perfil explota
        imagen_desafiar = Image.open("images/duelos/desafio.png").convert("RGBA")
        avatar_url = self.interaccion_jugador_1.user.avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    self.avatar_jugador_1 = Image.open(io.BytesIO(data)).convert("RGBA")
                else:
                    raise Exception(f"No se pudo descargar el avatar: {resp.status}")

        circulo_jugador_1 = make_circle_avatar(self.avatar_jugador_1, size=(500, 500))
        imagen_desafiar.paste(circulo_jugador_1, (650, 255), circulo_jugador_1 )
        await self.renderizar_imagen(imagen_desafiar)

        view = AceptarDuelo(self)

        await self.channel.send(
            f"{self.interaccion_jugador_1.user.mention} arranco un duelo a muerte con cuchillos apostando {self.monto_apostado} NA'GA puntos.\n"
            "¿Quién tiene los coquitos para aceptar?",
            view=view
        )

        # Tiempo límite de 5 minutos
        await asyncio.sleep(300)
        if self.channel.id in desafios and desafios[self.channel.id]["activo"]:
            desafios[self.channel.id]["activo"] = False
            await self.channel.send("El duelo a muerte ha expirado, nadie respondió a tiempo.")


    async def renderizar_imagen(self, imagen):
        with io.BytesIO() as image_binary:
            imagen.save(image_binary, "PNG")
            image_binary.seek(0)
            await self.interaccion_jugador_1.followup.send(
                file=discord.File(fp=image_binary, filename="meme_final.png")
            )

    async def iniciar_ronda(self):
        self.jugada1 = None
        self.jugada2 = None

        view1 = EleccionJugador(self, jugador=1)
        view2 = EleccionJugador(self, jugador=2)

        await self.interaccion_jugador_1.followup.send(
            "Elige tu jugada:",
            view=view1,
            ephemeral=True
        )
        await self.interaccion_jugador_2.followup.send(
            "Elige tu jugada:",
            view=view2,
            ephemeral=True
        )
        avatar_url2 = self.interaccion_jugador_2.user.avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url2)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    self.avatar_jugador_2 = Image.open(io.BytesIO(data)).convert("RGBA")
                else:
                    raise Exception(f"No se pudo descargar el avatar: {resp.status}")

        for _ in range(30):
            if self.jugada1 and self.jugada2:
                break
            await asyncio.sleep(1)

        if not self.jugada1 or not self.jugada2:
            await self.channel.send("No todos eligieron a tiempo. El duelo termina.")
            desafios[self.channel.id]["activo"] = False
            return

        resultado = self.determinar_ganador(self.jugada1, self.jugada2)
        if resultado == "empate":
            imagen_jugada = armar_jugada(armar_muerto(self.avatar_jugador_1), 670 ,armar_muerto(self.avatar_jugador_2), 670)
            await poner_texto_centro_imagen("EMPATE", "#964B00" ,imagen_jugada )
            await self.renderizar_imagen(imagen_jugada)
            desafios[self.channel.id]["activo"] = False
        elif resultado == "gana1":
            imagen_jugada = armar_jugada(armar_victoria(self.avatar_jugador_1), 500 ,armar_muerto(self.avatar_jugador_2), 670)
            await poner_texto_centro_imagen(f"{self.interaccion_jugador_1.user.display_name} GUINS","#FF0000", imagen_jugada)
            await self.renderizar_imagen(imagen_jugada)
            desafios[self.channel.id]["activo"] = False
        elif resultado == "gana2":
            imagen_jugada = armar_jugada(armar_muerto(self.avatar_jugador_1), 670 ,armar_victoria(self.avatar_jugador_2), 500)
            await poner_texto_centro_imagen(f"{self.interaccion_jugador_2.user.display_name} GUINS","#FF0000", imagen_jugada)
            await self.renderizar_imagen(imagen_jugada)
            desafios[self.channel.id]["activo"] = False
        else:
            try:
                fuente = ImageFont.truetype(RUTA_FUENTE, 100)
            except:
                fuente = ImageFont.load_default()

            b1 = f"{self.interaccion_jugador_1.user.display_name} X{self.bolsa_jugador_1}"
            b2 = f"{self.interaccion_jugador_2.user.display_name} X{self.bolsa_jugador_2}"

            draw = ImageDraw.Draw(self.imagen_jugada_intermedia)

            draw.text((15, 20), b1, font=fuente, fill="yellow", stroke_width=5, stroke_fill="black")


            bbox = draw.textbbox((0, 0), b2, font=fuente, stroke_width=3)
            texto_ancho = bbox[2] - bbox[0]


            img_ancho = self.imagen_jugada_intermedia.width


            x_pos = img_ancho - texto_ancho - 10
            y_pos = 10

            draw.text((x_pos, y_pos), b2, font=fuente, fill="yellow", stroke_width=5, stroke_fill="black")

            await self.renderizar_imagen(self.imagen_jugada_intermedia)
            if (resultado != ""):
                await self.channel.send(resultado)
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
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_jugador_1), 500, armar_ataque(self.avatar_jugador_2), 500)
                return "los dos tontos no tenian cuchillos"

        def atacar_vs_defender():
            if b1 > 0:
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_jugador_1), 500, armar_defensa(self.avatar_jugador_2), 500)
                self.bolsa_jugador_1 -= 1
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_jugador_1), 500, armar_defensa(self.avatar_jugador_2), 500)
            return ""

        def atacar_vs_agarrrar_un_cuchillo():
            if b1 > 0:
                self.bolsa_jugador_1 -= 1
                return "gana1"
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_jugador_1), 500, armar_juntar_cuchillo(self.avatar_jugador_2), 500)
                self.bolsa_jugador_2 += 1
                return f"el tonto de {self.interaccion_jugador_1.user.mention}  tiro cuchillo sin tener uno"

        def agarrrar_un_cuchillo_vs_atacar():
            if b2 > 0:
                return "gana2"
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_juntar_cuchillo(self.avatar_jugador_1), 500,armar_ataque(self.avatar_jugador_2), 500)
                self.bolsa_jugador_1 += 1
                return f"el tonto de {self.interaccion_jugador_2.user.mention}  tiro cuchillo sin tener uno"

        def agarrrar_un_cuchillo_vs_agarrrar_un_cuchillo():
            self.imagen_jugada_intermedia = armar_jugada(armar_juntar_cuchillo(self.avatar_jugador_1), 500,armar_juntar_cuchillo(self.avatar_jugador_2), 500)
            self.bolsa_jugador_1 += 1
            self.bolsa_jugador_2 += 1
            return ""

        def agarrrar_un_cuchillo_vs_defender():
            self.imagen_jugada_intermedia = armar_jugada(armar_juntar_cuchillo(self.avatar_jugador_1), 500,armar_defensa(self.avatar_jugador_2), 500)
            self.bolsa_jugador_1 += 1
            return ""

        def defender_vs_agarrrar_un_cuchillo():
            self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_jugador_1), 500,armar_juntar_cuchillo(self.avatar_jugador_2), 500)
            self.bolsa_jugador_2 += 1
            return ""

        def defender_vs_defender():
            self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_jugador_1),500, armar_defensa(self.avatar_jugador_2),500)
            return ""

        def defender_vs_atacar():
            if b2 > 0:
                self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_jugador_1),500, armar_ataque(self.avatar_jugador_2),500)
                self.bolsa_jugador_2 -= 1
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_jugador_1),500, armar_ataque(self.avatar_jugador_2),500)
            return ""

        reglas = {
            ("atacar", "atacar"): atacar_vs_atacar,
            ("atacar", "defender"): atacar_vs_defender,
            ("atacar", "agarrrar_un_cuchillo"): atacar_vs_agarrrar_un_cuchillo,
            ("defender", "atacar"): defender_vs_atacar,
            ("defender", "defender"): defender_vs_defender,
            ("defender", "agarrrar_un_cuchillo"): defender_vs_agarrrar_un_cuchillo,
            ("agarrrar_un_cuchillo", "atacar"): agarrrar_un_cuchillo_vs_atacar,
            ("agarrrar_un_cuchillo", "defender"): agarrrar_un_cuchillo_vs_defender,
            ("agarrrar_un_cuchillo", "agarrrar_un_cuchillo"): agarrrar_un_cuchillo_vs_agarrrar_un_cuchillo,
        }

        return reglas.get((jugada1, jugada2), lambda: "seguir")()

# arranco una vista de discord en resumen tiene un timer y una ui button  si se apreta aceptar
class AceptarDuelo(discord.ui.View):
    def __init__(self, duelo: DueloAMuerte):
        super().__init__(timeout=300)
        self.duelo = duelo


    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.success)
    async def aceptar(self, interaction: discord.Interaction, button: discord.ui.Button):
        #if interaction.user == self.duelo.interaccion_jugador_1.user:
        #    await interaction.response.send_message("No puedes aceptar tu propio duelo.", ephemeral=True)
        #    return

        self.duelo.interaccion_jugador_2 = interaction
        desafios[self.duelo.channel.id] = {"activo": True, "duelo": self.duelo}

        await interaction.response.send_message("aceptaste el duelo a muerte!", ephemeral=True)
        await self.duelo.channel.send(
            f"{interaction.user.mention} quiere cagarse a fakazos contra {self.duelo.interaccion_jugador_1.user.mention}!"
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
        jugada_str = ""
        match jugada:
            case "agarrrar_un_cuchillo":
                jugada_str = "Agarrrar una faka"
            case "defender":
                jugada_str = "Defender"
            case "atacar":
                jugada_str = "Atacar"
        await interaction.response.send_message(f"Elegiste **{jugada_str}**", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Agarrar Cuchillo", style=discord.ButtonStyle.primary)
    async def agarrrar_un_cuchillo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.registrar(interaction, "agarrrar_un_cuchillo")

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
