from discord.ext import commands, tasks
import discord, logging, os, json, io, time
from os.path import join, dirname
from dotenv import load_dotenv

from help import Help

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

PREFIX = "m!"


class Bot(commands.Bot):

    def __init__(self, command_prefix, help_command):
        super().__init__(command_prefix, help_command)
        self.bot_cogs = ["costume", "developer", "global_chat", "info"]
        for cog in self.bot_cogs:
            self.load_extension(cog)
        with open('error_text.json', 'r', encoding='utf-8') as f:
            self.error_text = json.load(f)
        self.database = {}
        self.ADMIN = {}
        self.BAN = {}
        self.MUTE = {}
        self.LOCK = {}
        self.Contributor = {}
        self.global_channels = []
        self.global_chat_log = {}
        self.global_chat_day = {}
        self.maintenance = True
        self.invites = []
        self.uptime = time.time()
        self.datas = {
            "server": "https://discord.gg/RbzSSrw",
            "invite": "https://discord.com/api/oauth2/authorize?client_id=742952261176655882&permissions=8&scope=bot",
            "author": "mafu#7582",
            "server_id": 565434676877983772,
            "notice_channel": 750947806558289960,
            "appeal_channel": 723170714907312129,
            "log_channel": 744466739542360064,
            "global_chat_log_channel": 751025181367205899,
            "database_channel": 744466393356959785,
            "global_chat_log_save_channel": 751053982100619275,
            "links_check_channel": 752875973044863057
        }

    async def on_ready(self):
        await self.change_presence(status=discord.Status.dnd, activity=discord.Game("起動中..."))
        print(f"Logged in to {self.user}")
        db_dict: dict
        database_channel = self.get_channel(self.datas["database_channel"])
        database_msg = await database_channel.fetch_message(database_channel.last_message_id)
        database_file = database_msg.attachments[0]
        db_byte = await database_file.read()
        db_dict = json.loads(db_byte)
        self.database = db_dict["user"]
        self.ADMIN = db_dict["role"]["ADMIN"]
        self.BAN = db_dict["role"]["BAN"]
        self.MUTE = db_dict["global"]["MUTE"]
        self.LOCK = db_dict["global"]["LOCK"]
        self.global_channels = db_dict["global"]["channels"]
        self.Contributor = db_dict["role"]["Contributor"]
        self.maintenance = db_dict["system"]["maintenance"]
        self.invites = [invite.code for invite in await self.get_guild(self.datas["server_id"]).invites()]
        database_channel = self.get_channel(self.datas["global_chat_log_save_channel"])
        database_msg = await database_channel.fetch_message(database_channel.last_message_id)
        database_file = database_msg.attachments[0]
        db_byte = await database_file.read()
        db_dict = json.loads(db_byte)
        self.global_chat_log = db_dict["log"]
        self.global_chat_day = db_dict["day"]
        if not self.save_database.is_running():
            self.save_database.start()
        if not self.save_global_chat_log.is_running():
            self.save_global_chat_log.start()
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.command_prefix}help | {len(self.guilds)}servers | {self.datas['server']}"))

    async def on_message(self, message):
        if not self.is_ready():
            return
        elif message.author.bot:
            return
        elif message.guild is None:
            global_chat_cog = self.get_cog("GlobalChat")
            await global_chat_cog.on_dm_message(message)
        elif message.content == f"<@!{self.user.id}>":
            return await message.channel.send(f"このBOTのprefixは `{self.command_prefix}` です!\n`{self.command_prefix}help` で詳しい使い方を確認できます。")
        elif message.channel.id in self.global_channels:
            global_chat_cog = self.get_cog("GlobalChat")
            await global_chat_cog.on_global_message(message)
        else:
            await self.process_commands(message)

    async def on_guild_join(self, guild):
        embed = discord.Embed(title=f"{guild.name} に参加しました。", color=0x00ffff)
        embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        await self.get_channel(self.datas["log_channel"]).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.command_prefix}help | {len(self.guilds)}servers | {self.datas['server']}"))

    async def on_guild_remove(self, guild):
        embed = discord.Embed(title=f"{guild.name} を退出しました。", color=0xff1493)
        embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        await self.get_channel(self.datas["log_channel"]).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.command_prefix}help | {len(self.guilds)}servers | {self.datas['server']}"))

    @tasks.loop(seconds=30.0)
    async def save_database(self):
        db_dict = {
            "user": self.database,
            "role": {
                "ADMIN": self.ADMIN,
                "BAN": self.BAN,
                "Contributor": self.Contributor
            },
            "global": {
                "channels": self.global_channels,
                "MUTE": self.MUTE,
                "LOCK": self.LOCK
            },
            "system": {
                "maintenance": self.maintenance
            }
        }
        database_channel = self.get_channel(self.datas["database_channel"])
        db_bytes = json.dumps(db_dict, indent=2)
        await database_channel.send(file=discord.File(fp=io.StringIO(db_bytes), filename="database.json"))

    @tasks.loop(seconds=60.0)
    async def save_global_chat_log(self):
        db_dict = {
            "day": self.global_chat_day,
            "log": self.global_chat_log
        }
        save_channel = self.get_channel(self.datas["global_chat_log_save_channel"])
        db_bytes = json.dumps(db_dict, indent=2)
        await save_channel.send(file=discord.File(io.StringIO(db_bytes), filename="global_chat_log.json"))


if __name__ == '__main__':
    bot = Bot(command_prefix=PREFIX, help_command=Help())
    bot.run(TOKEN)
