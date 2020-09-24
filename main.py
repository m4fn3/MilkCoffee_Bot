from discord.ext import commands, tasks
import discord, logging, os, json, io, time
from os.path import join, dirname
from dotenv import load_dotenv
from multilingual import *

from help import Help

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

PREFIX = "m!"
PREFIXES = ["m! ", "m！ ", "ｍ! ", "ｍ！ ", "m!　", "m！　", "ｍ!　", "ｍ！　", "m!", "m！", "ｍ!", "ｍ！"]


class Bot(commands.Bot):

    def __init__(self, command_prefix, help_command, status, activity):
        super().__init__(command_prefix, help_command, status=status, activity=activity)
        self.bot_cogs = ["costume", "developer", "global_chat", "info", "notify"]
        self.PREFIX = PREFIX
        for cog in self.bot_cogs:
            self.load_extension(cog)
        self.database = {}
        self.ADMIN = {}
        self.BAN = {}
        self.MUTE = {}
        self.LOCK = {}
        self.Contributor = {}
        self.global_channels = []
        self.global_chat_log = {}
        self.global_chat_day = {}
        self.maintenance = "Starting..."
        self.invites = []
        self.GM_update = {
            "twitter": [],
            "youtube": [],
            "facebook": []
        }
        self.uptime = time.time()
        self.datas = {
            "server": "https://discord.gg/RbzSSrw",
            "invite": "https://discord.com/oauth2/authorize?client_id=742952261176655882&permissions=-8&redirect_uri=https%3A%2F%2Fmilkcoffee.cf&scope=bot",
            "author": "mafu#7582",
            "server_id": 565434676877983772,
            "notice_channel": 750947806558289960,
            "appeal_channel": 723170714907312129,
            "log_channel": 744466739542360064,
            "global_chat_log_channel": 751025181367205899,
            "database_channel": 744466393356959785,
            "global_chat_log_save_channel": 751053982100619275,
            "links_check_channel": 752875973044863057,
            "GM_update_channel": [753897253743362068, 757583425736540190, 757592252238528512],
            "system-log-channel": 755016319660720188,
            "command_log_channel": 755433660483633182,
            "web": "https://milkcoffee.cf/"
        }

    async def on_ready(self):
        print(f"Logged in to {self.user}")
        if self.user.id != 742952261176655882:
            print("テスト環境モード")
            self.command_prefix.append("m?")
            self.datas = {
                "server": "https://discord.gg/RbzSSrw",
                "invite": "https://discord.com/oauth2/authorize?client_id=742952261176655882&permissions=-8&redirect_uri=https%3A%2F%2Fmilkcoffee.cf&scope=bot",
                "author": "mafu#7582",
                "server_id": 565434676877983772,
                "notice_channel": 750947806558289960,
                "appeal_channel": 723170714907312129,
                "log_channel": 754986353850187797,
                "global_chat_log_channel": 754986353850187797,
                "database_channel": 744466393356959785,
                "global_chat_log_save_channel": 751053982100619275,
                "GM_update_channel": [754980772326408222, 757602418115608588, 757602427103870987],
                "system-log-channel": 755016319660720188,
                "command_log_channel": 755433660483633182,
                "web": "https://milkcoffee.cf/"
            }
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
        self.GM_update["twitter"] = db_dict["notify"]["twitter"]
        self.GM_update["youtube"] = db_dict["notify"]["youtube"]
        self.GM_update["facebook"] = db_dict["notify"]["facebook"]
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
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.datas['server']}"))
        if self.user.id != 742952261176655882:
            self.GM_update = {
                "twitter": [],
                "youtube": [],
                "facebook": []
            }
            self.global_channels = []

    async def on_message(self, message):
        if not self.is_ready():
            return
        elif message.channel.id in self.datas["GM_update_channel"]:
            notify_cog = self.get_cog("Notify")
            await notify_cog.on_GM_update(message)
        elif message.author.bot:
            return
        elif message.guild is None:
            global_chat_cog = self.get_cog("GlobalChat")
            await global_chat_cog.on_dm_message(message)
        elif message.content == f"<@!{self.user.id}>":
            return await message.channel.send(["このBOTのprefixは`{}`です!\n`{}help`で詳しい使い方を確認できます。", "The prefix for this bot is `{}`! \n`{}help` for more details on how to use it.", "이 봇의 접두사는`{}`입니다! 사용 방법에 대한 자세한 내용은 \n` {} 도움말`을 참조하세요.", "¡El prefijo de este bot es `{}`! \n`{}help` para obtener más detalles sobre cómo usarlo."][get_lg(self.database[str(message.author.id)]["language"], message.guild.region)].format(self.PREFIX, self.PREFIX))
        elif message.channel.id in self.global_channels:
            global_chat_cog = self.get_cog("GlobalChat")
            await global_chat_cog.on_global_message(message)
        else:
            await self.process_commands(message)

    async def on_guild_join(self, guild):
        embed = discord.Embed(title=f"{guild.name} に参加しました。", color=0x00ffff)
        embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        await self.get_channel(self.datas["log_channel"]).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.datas['server']}"))

    async def on_guild_remove(self, guild):
        embed = discord.Embed(title=f"{guild.name} を退出しました。", color=0xff1493)
        embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        await self.get_channel(self.datas["log_channel"]).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.datas['server']}"))

    async def on_command(self, ctx):
        await self.get_channel(self.datas["command_log_channel"]).send(f"`{ctx.message.content}` | {str(ctx.author)} ({ctx.author.id}) | {ctx.guild.name} ({ctx.guild.id}) | {ctx.channel.name} ({ctx.channel.id})")

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
            "notify": {
                "twitter": self.GM_update["twitter"],
                "youtube": self.GM_update["youtube"],
                "facebook": self.GM_update["facebook"]
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
    bot = Bot(command_prefix=PREFIXES, help_command=Help(), status=discord.Status.dnd, activity=discord.Game("Starting..."))
    bot.run(TOKEN)
