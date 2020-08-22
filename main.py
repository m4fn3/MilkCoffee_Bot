from discord.ext import commands, tasks
import discord, logging, os, json
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)


class Bot(commands.Bot):

    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        cogs = ["costume", "developer"]
        for cog in cogs:
            self.load_extension(cog)
        with open('error_text.json', 'r', encoding='utf-8') as f:
            self.error_text = json.load(f)
        self.database = {}
        self.ADMIN = []
        self.BAN = []
        self.Contributor = []
        self.maintenance = True

    async def on_ready(self):
        print(f"Logged in to {self.user}")
        db_dict: dict
        with open('database.json', 'r', encoding='utf-8') as f:
            db_dict = json.load(f)
        self.database = db_dict["user"]
        self.ADMIN = db_dict["role"]["ADMIN"]
        self.BAN = db_dict["role"]["BAN"]
        self.Contributor = db_dict["role"]["Contributor"]
        self.maintenance = db_dict["system"]["maintenance"]
        if not self.save_database.is_running():
            self.save_database.start()

    @tasks.loop(seconds=30.0)
    async def save_database(self):
        db_dict = {
            "user": self.database,
            "role": {
                "ADMIN": self.ADMIN,
                "BAN": self.BAN,
                "Contributor": self.Contributor
            },
            "system": {
                "maintenance": self.maintenance
            }
        }
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(db_dict, f, indent=2)


if __name__ == '__main__':
    bot = Bot(command_prefix="m!")
    bot.run(TOKEN)
