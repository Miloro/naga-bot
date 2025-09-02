import discord
from discord.ext import commands
import gspread
from google.oauth2.service_account import Credentials
from credentials import config
from PIL import Image
import io

intents = discord.Intents.default()
intents.message_content = True

# Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials/credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
SPREADSHEET_ID = config.id_excel
spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet = spreadsheet.worksheet(config.hoja_excel)

# Inicializar bot (¡ojo! sin prefijo, ya que usaremos slash commands)
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Slash Commands ---
@bot.tree.command(name="lider", description="Muestra qué equipo va primero en la tabla")
async def lider(interaction: discord.Interaction):
    try:
        values = worksheet.get_values('E2:E5')
        cuyffindor, llamapuff, palomaclaw, asnotherin = [row[0] for row in values]
        data = [
            ('Cuyffindor', int(cuyffindor)),
            ('Llamapuff', int(llamapuff)),
            ('Palomaclaw', int(palomaclaw)),
            ('Asnotherin', int(asnotherin))
        ]
        data.sort(key=lambda item: item[1], reverse=True)
        await interaction.response.send_message(f"El equipo más pijudo es: 🏆 **{data[0][0]}** 🏆")
    except Exception as e:
        await interaction.response.send_message(f"Ocurrió un error: {e}")

@bot.tree.command(name="podio", description="Muestra el podio de las casas")
async def podio(interaction: discord.Interaction):
    try:
        values = worksheet.get_values('E2:E5')
        cuyffindor, llamapuff, palomaclaw, asnotherin = [row[0] for row in values]

        data = [
            ('images/casas/cuyffindor.png', int(cuyffindor)),
            ('images/casas/llamapuff.png', int(llamapuff)),
            ('images/casas/palomaclaw.png', int(palomaclaw)),
            ('images/casas/asnotherin.png', int(asnotherin))
        ]
        data.sort(key=lambda item: item[1], reverse=True)
        
        fondo = Image.open("images/memes/meme_pool.jpg").convert("RGBA")

        naga = Image.open("images/naga/naga.png").convert("RGBA").resize((150, 150))
        fondo.paste(naga, (690, 255), naga)

        puestos = [
            (data[0][0], (415, 185), (100, 100)),   # 1°
            (data[1][0], (130, 420), (200, 200)),   # 2°
            (data[2][0], (440, 730), (100, 100)),   # 3°
            (data[3][0], (750, 1100), (100, 100))   # 4°
        ]

        for img_path, (x, y), size in puestos:
            img = Image.open(img_path).convert("RGBA").resize(size)
            fondo.paste(img, (x, y), img)

        with io.BytesIO() as image_binary:
            fondo.save(image_binary, "PNG")
            image_binary.seek(0)
            await interaction.response.send_message(
                file=discord.File(fp=image_binary, filename="meme_final.png")
            )

    except Exception as e:
        await interaction.response.send_message(f"Ocurrió un error {e}")

# Evento on_ready
@bot.event
async def on_ready():
    await bot.tree.sync()  # Importante para que aparezcan en Discord
    print(f"Bot listo como {bot.user}")

bot.run(config.TOKEN)