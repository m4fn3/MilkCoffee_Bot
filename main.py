from discord.ext import commands, tasks
import discord, logging, os, json, io, time
from os.path import join, dirname
from dotenv import load_dotenv

from help import Help

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)


class Bot(commands.Bot):

    def __init__(self, command_prefix, help_command):
        super().__init__(command_prefix, help_command)
        self.bot_cogs = ["costume", "developer", "global_chat", "info"]
        for cog in self.bot_cogs:
            self.load_extension(cog)
        with open('error_text.json', 'r', encoding='utf-8') as f:
            self.error_text = json.load(f)
        self.database = {}
        self.ADMIN = []
        self.BAN = []
        self.Contributor = []
        self.maintenance = True
        self.uptime = time.time()
        self.datas = {
            "server": "https://discord.gg/RbzSSrw",
            "invite": "https://discord.com/api/oauth2/authorize?client_id=742952261176655882&permissions=8&scope=bot",
            "author": "mafu#7582"
        }

    async def on_ready(self):
        print(f"Logged in to {self.user}")
        db_dict: dict
        database_channel = self.get_channel(744466393356959785)
        database_msg = await database_channel.fetch_message(database_channel.last_message_id)
        database_file = database_msg.attachments[0]
        db_byte = await database_file.read()
        db_dict = json.loads(db_byte)
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
        database_channel = self.get_channel(744466393356959785)
        db_bytes = json.dumps(db_dict, indent=2)
        await database_channel.send(file=discord.File(fp=io.StringIO(db_bytes), filename="database.json"))


if __name__ == '__main__':
    bot = Bot(command_prefix="m!", help_command=Help())
    bot.run(TOKEN)