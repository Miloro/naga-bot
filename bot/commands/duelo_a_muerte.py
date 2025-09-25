import discord
from discord import app_commands
import asyncio
from PIL import Image
import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageOps
import os
RUTA_FUENTE = os.path.join(os.path.dirname(__file__), "..", "fuentes", "DraculitoS_.ttf")


####################################################
#██████╗░██╗░█████╗░░██████╗        ██████╗░███████╗██████╗░██████╗░░█████╗░███╗░░██╗███████╗        ░█████╗░██╗░░░░░
#██╔══██╗██║██╔══██╗██╔════╝        ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗████╗░██║██╔════╝        ██╔══██╗██║░░░░░
#██║░░██║██║██║░░██║╚█████╗░        ██████╔╝█████╗░░██████╔╝██║░░██║██║░░██║██╔██╗██║█████╗░░        ███████║██║░░░░░
#██║░░██║██║██║░░██║░╚═══██╗        ██╔═══╝░██╔══╝░░██╔══██╗██║░░██║██║░░██║██║╚████║██╔══╝░░        ██╔══██║██║░░░░░
#██████╔╝██║╚█████╔╝██████╔╝        ██║░░░░░███████╗██║░░██║██████╔╝╚█████╔╝██║░╚███║███████╗        ██║░░██║███████╗
#╚═════╝░╚═╝░╚════╝░╚═════╝░        ╚═╝░░░░░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░╚═╝░░╚══╝╚══════╝        ╚═╝░░╚═╝╚══════╝
#
#░██████╗░██╗░░░██╗███████╗        ██╗░░░░░███████╗░█████╗░        ███████╗░██████╗████████╗███████╗
#██╔═══██╗██║░░░██║██╔════╝        ██║░░░░░██╔════╝██╔══██╗        ██╔════╝██╔════╝╚══██╔══╝██╔════╝
#██║██╗██║██║░░░██║█████╗░░        ██║░░░░░█████╗░░███████║        █████╗░░╚█████╗░░░░██║░░░█████╗░░
#╚██████╔╝██║░░░██║██╔══╝░░        ██║░░░░░██╔══╝░░██╔══██║        ██╔══╝░░░╚═══██╗░░░██║░░░██╔══╝░░
#░╚═██╔═╝░╚██████╔╝███████╗        ███████╗███████╗██║░░██║        ███████╗██████╔╝░░░██║░░░███████╗
#░░░╚═╝░░░░╚═════╝░╚══════╝        ╚══════╝╚══════╝╚═╝░░╚═╝        ╚══════╝╚═════╝░░░░╚═╝░░░╚══════╝

#░█████╗░░█████╗░██████╗░██╗░██████╗░░█████╗░
#██╔══██╗██╔══██╗██╔══██╗██║██╔════╝░██╔══██╗
#██║░░╚═╝██║░░██║██║░░██║██║██║░░██╗░██║░░██║
#██║░░██╗██║░░██║██║░░██║██║██║░░╚██╗██║░░██║
#╚█████╔╝╚█████╔╝██████╔╝██║╚██████╔╝╚█████╔╝
####################################################

async def poner_texto_centro_imagen(texto,imagen):
    draw = ImageDraw.Draw(imagen)
    tamano_fuente = 300
    try:
        fuente = ImageFont.truetype(RUTA_FUENTE, tamano_fuente)
    except:
        fuente = ImageFont.load_default()

    margen = 40
    while True:
        bbox = draw.textbbox((0, 0), texto, font=fuente, stroke_width=10)
        texto_ancho = bbox[2] - bbox[0]

        if texto_ancho + 2 * margen <= imagen.width or tamano_fuente <= 5:
            break

        tamano_fuente -= 5
        try:
            fuente = ImageFont.truetype(RUTA_FUENTE, tamano_fuente)
        except:
            fuente = ImageFont.load_default()


    x_pos = (imagen.width - texto_ancho) / 2
    texto_alto = bbox[3] - bbox[1]
    y_pos = ((imagen.height - texto_alto) / 2) - 90
    if texto == "EMPATE":
        color = "#964B00"
    else:
        color = "#FF0000"

    draw.text((x_pos, y_pos), texto, font=fuente, fill= color, stroke_width=10, stroke_fill="black")
    return draw

async def procesar_imagen(imagen, controlador_juego):
    with io.BytesIO() as image_binary:
        imagen.save(image_binary, "PNG")
        image_binary.seek(0)
        await controlador_juego.interaccion_retador.followup.send(
            file=discord.File(fp=image_binary, filename="meme_final.png")
        )

def armar_jugada(player_1: Image.Image, y ,player_2: Image.Image, y2) -> Image.Image:
    fondo = Image.open("images/duelos/arena.png").convert("RGBA")
    player_2 = ImageOps.mirror(player_2)
    fondo.paste(player_1, (100, y), player_1 )
    fondo.paste(player_2, (1100, y2), player_2)
    return fondo

def armar_muerto(avatar: Image.Image) -> Image.Image:
    circulo_avatar = make_circle_avatar(avatar, size=(100, 100))
    fondo = Image.open("images/duelos/derrota.png").convert("RGBA")
    fondo.paste(circulo_avatar, (310, 145), circulo_avatar )
    return fondo

def armar_defensa(avatar: Image.Image) -> Image.Image:
    circulo_avatar = make_circle_avatar(avatar, size=(100, 100))
    fondo = Image.open("images/duelos/bloquear.png").convert("RGBA")
    fondo.paste(circulo_avatar, (50, 20), circulo_avatar )
    return fondo

def armar_ataque(avatar: Image.Image) -> Image.Image:
    circulo_avatar = make_circle_avatar(avatar, size=(100, 100))
    fondo = Image.open("images/duelos/lanzar.png").convert("RGBA")
    fondo.paste(circulo_avatar, (110, 10), circulo_avatar )
    return fondo

def armar_victoria(avatar: Image.Image) -> Image.Image:
    circulo_avatar = make_circle_avatar(avatar, size=(100, 100))
    fondo = Image.open("images/duelos/victoria.png").convert("RGBA")
    fondo.paste(circulo_avatar, (110, 10), circulo_avatar )
    return fondo

def armar_juntar_cuchillo(avatar: Image.Image) -> Image.Image:
    circulo_avatar = make_circle_avatar(avatar, size=(100, 100))
    fondo = Image.open("images/duelos/juntar.png").convert("RGBA")
    fondo.paste(circulo_avatar, (5, 300), circulo_avatar )
    return fondo

def make_circle_avatar(avatar: Image.Image, size=(128, 128)) -> Image.Image:
    avatar = avatar.resize(size).convert("RGBA")

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    circular_avatar = Image.new("RGBA", size, (0, 0, 0, 0))
    circular_avatar.paste(avatar, (0, 0), mask)

    return circular_avatar

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
        self.avatar_retador = None
        self.avaatar_desafiado = None
        self.imagen_jugada_intermedia = None



    async def iniciar_desafio(self):
        await self.interaccion_retador.response.send_message(
            "Espera a que alguien responda a tu desafío...", ephemeral=True
        )

        imagen_desafiar = Image.open("images/duelos/desafio.png").convert("RGBA")
        avatar_url = self.interaccion_retador.user.avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    self.avatar_retador = Image.open(io.BytesIO(data)).convert("RGBA")
                else:
                    raise Exception(f"No se pudo descargar el avatar: {resp.status}")

        circulo_retador = make_circle_avatar(self.avatar_retador, size=(500, 500))


        imagen_desafiar.paste(circulo_retador, (650, 255), circulo_retador )
        await self.renderizar_imagen(imagen_desafiar)
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


    async def renderizar_imagen(self, imagen):
        with io.BytesIO() as image_binary:
            imagen.save(image_binary, "PNG")
            image_binary.seek(0)
            await self.interaccion_retador.followup.send(
                file=discord.File(fp=image_binary, filename="meme_final.png")
            )

    async def iniciar_ronda(self):
        self.jugada1 = None
        self.jugada2 = None


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
        avatar_url2 = self.interaccion_desafiado.user.avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url2)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    self.avaatar_desafiado = Image.open(io.BytesIO(data)).convert("RGBA")
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
            imagen_jugada = armar_jugada(armar_muerto(self.avatar_retador), 670 ,armar_muerto(self.avaatar_desafiado), 670)
            await poner_texto_centro_imagen("EMPATE", imagen_jugada)
            await self.renderizar_imagen(imagen_jugada)
            desafios[self.channel.id]["activo"] = False
        elif resultado == "gana1":
            imagen_jugada = armar_jugada(armar_victoria(self.avatar_retador), 500 ,armar_muerto(self.avaatar_desafiado), 670)
            await poner_texto_centro_imagen(f"{self.interaccion_retador.user.display_name} GUINS", imagen_jugada)
            await self.renderizar_imagen(imagen_jugada)
            desafios[self.channel.id]["activo"] = False
        elif resultado == "gana2":
            imagen_jugada = armar_jugada(armar_muerto(self.avatar_retador), 670 ,armar_victoria(self.avaatar_desafiado), 500)
            await poner_texto_centro_imagen(f"{self.interaccion_desafiado.user.display_name} GUINS", imagen_jugada)
            await self.renderizar_imagen(imagen_jugada)
            desafios[self.channel.id]["activo"] = False
        else:
            try:
                fuente = ImageFont.truetype(RUTA_FUENTE, 100)
            except:
                fuente = ImageFont.load_default()

            b1 = f"{self.interaccion_retador.user.display_name} X{self.bolsa_jugador_1}"
            b2 = f"{self.interaccion_desafiado.user.display_name} X{self.bolsa_jugador_2}"

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
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_retador), 500, armar_ataque(self.avaatar_desafiado), 500)
                return "los dos tontos no tenian cuchillos"

        def atacar_vs_defender():
            if b1 > 0:
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_retador), 500, armar_defensa(self.avaatar_desafiado), 500)
                self.bolsa_jugador_1 -= 1
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_retador), 500, armar_defensa(self.avaatar_desafiado), 500)
            return ""

        def atacar_vs_recargar():
            if b1 > 0:
                self.bolsa_jugador_1 -= 1
                return "gana1"
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_ataque(self.avatar_retador), 500, armar_juntar_cuchillo(self.avaatar_desafiado), 500)
                self.bolsa_jugador_2 += 1
                return "el tonto del desafiador tiro cuchillo sin tener uno"

        def recargar_vs_atacar():
            if b2 > 0:
                return "gana2"
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_juntar_cuchillo(self.avatar_retador), 500,armar_ataque(self.avaatar_desafiado), 500)
                self.bolsa_jugador_1 += 1
                return "el tonto del desafiado tiro cuchillo sin tener uno"

        def recargar_vs_recargar():
            self.imagen_jugada_intermedia = armar_jugada(armar_juntar_cuchillo(self.avatar_retador), 500,armar_juntar_cuchillo(self.avaatar_desafiado), 500)
            self.bolsa_jugador_1 += 1
            self.bolsa_jugador_2 += 1
            return ""

        def recargar_vs_defender():
            self.imagen_jugada_intermedia = armar_jugada(armar_juntar_cuchillo(self.avatar_retador), 500,armar_defensa(self.avaatar_desafiado), 500)
            self.bolsa_jugador_1 += 1
            return ""

        def defender_vs_recargar():
            self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_retador), 500,armar_juntar_cuchillo(self.avaatar_desafiado), 500)
            self.bolsa_jugador_2 += 1
            return ""

        def defender_vs_defender():
            self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_retador),500, armar_defensa(self.avaatar_desafiado),500)
            return ""

        def defender_vs_atacar():
            if b2 > 0:
                self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_retador),500, armar_ataque(self.avaatar_desafiado),500)
                self.bolsa_jugador_2 -= 1
            else:
                self.imagen_jugada_intermedia = armar_jugada(armar_defensa(self.avatar_retador),500, armar_ataque(self.avaatar_desafiado),500)
            return ""

        reglas = {
            ("atacar", "atacar"): atacar_vs_atacar,
            ("atacar", "defender"): atacar_vs_defender,
            ("atacar", "recargar"): atacar_vs_recargar,
            ("defender", "atacar"): defender_vs_atacar,
            ("defender", "defender"): defender_vs_defender,
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
        if interaction.user == self.duelo.interaccion_retador.user:
            await interaction.response.send_message("No puedes aceptar tu propio duelo.", ephemeral=True)
            return

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

    @discord.ui.button(label="Agarrar Cuchillo", style=discord.ButtonStyle.primary)
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
