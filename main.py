import logging
import os
from os.path import join, dirname

import discord
from dotenv import load_dotenv

from Cogs.bot import MilkCoffee
from Cogs.help import Help

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

PREFIX = "m!"
PREFIXES = ["m! ", "m！ ", "ｍ! ", "ｍ！ ", "m!　", "m！　", "ｍ!　", "ｍ！　", "m!", "m！", "ｍ!", "ｍ！"]

if __name__ == '__main__':
    bot_intents = discord.Intents.default()
    bot = MilkCoffee(PREFIX, command_prefix=PREFIXES, help_command=Help(), status=discord.Status.dnd, activity=discord.Game("Starting..."), intents=bot_intents)
    bot.run(TOKEN)
