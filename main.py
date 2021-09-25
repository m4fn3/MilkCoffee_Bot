import logging
import os
from os.path import join, dirname

import discord
from dotenv import load_dotenv

from Cogs.help import Help
from Cogs.milkcoffee import MilkCoffee

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PSWD = os.getenv("DB_PSWD")

logging.basicConfig(level=logging.INFO)

PREFIX = "m!"
PREFIXES = ["m! ", "m！ ", "ｍ! ", "ｍ！ ", "m!　", "m！　", "ｍ!　", "ｍ！　", "m!", "m！", "ｍ!", "ｍ！", "M! ", "M！ ", "Ｍ! ", "Ｍ！ ", "M!　", "M！　", "Ｍ!　", "Ｍ！　", "M!", "M！", "Ｍ!", "Ｍ！", "."]

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.typing = False
    bot = MilkCoffee(PREFIX, [DB_NAME, DB_USER, DB_PSWD], command_prefix=PREFIXES, help_command=Help(), status=discord.Status.dnd, activity=discord.Game("Starting..."), intents=intents)
    bot.run(TOKEN)
