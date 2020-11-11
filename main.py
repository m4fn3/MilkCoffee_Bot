import logging
import os
from os.path import join, dirname

import discord
from dotenv import load_dotenv

from Cogs.milkcoffee import MilkCoffee
from Cogs.help import Help

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")
DB_URL = os.getenv("DB_URL")

logging.basicConfig(level=logging.INFO)

PREFIX = "m!"
PREFIXES = ["m! ", "m！ ", "ｍ! ", "ｍ！ ", "m!　", "m！　", "ｍ!　", "ｍ！　", "m!", "m！", "ｍ!", "ｍ！"]

# NOTE: テスト
PREFIXES += ["m?"]

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.typing = False
    bot = MilkCoffee(PREFIX, DB_URL, command_prefix=PREFIXES, help_command=Help(), status=discord.Status.dnd, activity=discord.Game("Starting..."), intents=intents)
    bot.run(TOKEN)
