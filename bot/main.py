import os
import importlib
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
# Definir los intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Carpeta con los módulos de comandos
commands_folder = "commands"

# Cargar automáticamente los módulos
for filename in os.listdir(commands_folder):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{commands_folder}.{filename[:-3]}"
        module = importlib.import_module(module_name)
        if hasattr(module, "setup"):
            module.setup(bot)

@bot.event
async def on_ready():
    await bot.tree.sync()  
    print(f"Bot listo como {bot.user}")

# Ejecutar el bot
bot.run(os.getenv("TOKEN"))