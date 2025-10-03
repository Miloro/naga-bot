import os
import importlib
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

commands_folder = "commands"

# Cargar paquetes (subcarpetas con __init__.py)
for folder in os.listdir(commands_folder):
    folder_path = os.path.join(commands_folder, folder)
    if os.path.isdir(folder_path) and "__init__.py" in os.listdir(folder_path):
        module_name = f"{commands_folder}.{folder}"
        module = importlib.import_module(module_name)
        if hasattr(module, "setup"):
            module.setup(bot)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot listo como {bot.user}")

bot.run(os.getenv("TOKEN"))