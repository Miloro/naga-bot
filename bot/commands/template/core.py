import discord
from discord import app_commands


async def ping(interaction: discord.Interaction):
    try:
        await interaction.response.send_message(f"pong")
    except Exception as e:
        await interaction.response.send_message(f"Ocurrió un error: {e}")


def setup(bot):

    bot.tree.add_command(app_commands.Command(name="ping", description="hace pong", callback=ping))