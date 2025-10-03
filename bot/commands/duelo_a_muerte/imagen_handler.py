from PIL import Image, ImageDraw, ImageFont
from PIL import ImageOps
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUTA_FUENTE = os.path.join(BASE_DIR, "fuentes", "DraculitoS_.ttf")

async def poner_texto_centro_imagen(texto,color,imagen):
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

    draw.text((x_pos, y_pos), texto, font=fuente, fill= color, stroke_width=10, stroke_fill="black")
    return draw

def armar_jugada(imagen_jugador_1: Image.Image, y ,imagen_jugador_2: Image.Image, y2) -> Image.Image:
    fondo = Image.open("images/duelos/arena.png").convert("RGBA")
    imagen_jugador_2 = ImageOps.mirror(imagen_jugador_2)
    fondo.paste(imagen_jugador_1, (100, y), imagen_jugador_1 )
    fondo.paste(imagen_jugador_2, (1050, y2), imagen_jugador_2)
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
