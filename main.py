from os.path import join, dirname

import discord
import json
import logging
import os
import time
from discord.ext import commands
from dotenv import load_dotenv

from .Cogs.help import Help
from .Tools.multilingual import *

load_dotenv(verbose=True)
load_dotenv(join(dirname(__file__), '.env'))

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

PREFIX = "m!"
PREFIXES = ["m! ", "m！ ", "ｍ! ", "ｍ！ ", "m!　", "m！　", "ｍ!　", "ｍ！　", "m!", "m！", "ｍ!", "ｍ！"]


class Bot(commands.Bot):

    def __init__(self, command_prefix, help_command, status, activity, intents):
        super().__init__(command_prefix, help_command, status=status, activity=activity, intents=intents)
        self.bot_cogs = ["language", "costume", "developer", "info", "notify"]
        self.PREFIX = PREFIX  # メインPREFIXを設定
        for cog in self.bot_cogs:  # Cog読み込み
            self.load_extension(cog)
        self.database = {}  # TODO: db化
        self.ADMIN = {}  # TODO: db化
        self.BAN = {}  # TODO: db化
        self.Contributor = {}  # TODO: db化
        self.maintenance = "Starting..."  # NOTE: maintenanceをどうするか
        self.GM_update = {  # TODO: db化
            "twitter": [],
            "youtube": [],
            "facebook_jp": [],
            "facebook_en": [],
            "facebook_kr": [],
            "facebook_es": []
        }
        self.uptime = time.time()
        self.datas = {
            "server": "https://discord.gg/RbzSSrw",
            "invite": "https://discord.com/oauth2/authorize?client_id=742952261176655882&permissions=-8&scope=bot",
            "author": "mafu#7582",
            "server_id": 565434676877983772,
            "notice_channel": 750947806558289960,
            "appeal_channel": 723170714907312129,
            "log_channel": 744466739542360064,
            "database_channel": 744466393356959785,
            "links_check_channel": 752875973044863057,
            "GM_update_channel": [753897253743362068, 758122589255893042, 757583425736540190, 758122790527172608, 758122772864958484, 757592252238528512],
            "system-log-channel": 755016319660720188,
            "command_log_channel": 755433660483633182,
            "web": "https://milkcoffee.cf/"
        }

    async def on_ready(self):
        self.maintenance = ""
        print(f"Logged in to {self.user}")
        if self.user.id != 742952261176655882:
            print("テスト環境モード")
            self.command_prefix.append("m?")
            self.datas = {
                "server": "https://discord.gg/RbzSSrw",
                "invite": "https://discord.com/oauth2/authorize?client_id=742952261176655882&permissions=-8&scope=bot",
                "author": "mafu#7582",
                "server_id": 565434676877983772,
                "notice_channel": 750947806558289960,
                "appeal_channel": 723170714907312129,
                "log_channel": 754986353850187797,
                "database_channel": 744466393356959785,
                "GM_update_channel": [754980772326408222, 757602418115608588, 757602418115608588, 757602418115608588, 757602418115608588, 757602427103870987],
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
        self.GM_update["twitter"] = db_dict["notify"]["twitter"]
        self.GM_update["youtube"] = db_dict["notify"]["youtube"]
        self.GM_update["facebook_jp"] = db_dict["notify"]["facebook_jp"]
        self.GM_update["facebook_en"] = db_dict["notify"]["facebook_en"]
        self.GM_update["facebook_kr"] = db_dict["notify"]["facebook_kr"]
        self.GM_update["facebook_es"] = db_dict["notify"]["facebook_es"]
        self.Contributor = db_dict["role"]["Contributor"]
        self.maintenance = db_dict["system"]["maintenance"]
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.datas['server']}"))
        if self.user.id != 742952261176655882:
            self.GM_update = {
                "twitter": [],
                "youtube": [],
                "facebook_jp": [],
                "facebook_en": [],
                "facebook_kr": [],
                "facebook_es": []
            }

    async def on_message(self, message):
        if not self.is_ready():
            return
        elif message.channel.id in self.datas["GM_update_channel"]:
            notify_cog = self.get_cog("Notify")
            await notify_cog.on_GM_update(message)
        elif message.author.bot:
            return
        elif message.content == f"<@!{self.user.id}>":
            return await message.channel.send(
                ["このBOTのprefixは`{}`です!\n`{}help`で詳しい使い方を確認できます。", "The prefix for this bot is `{}`! \n`{}help` for more details on how to use it.", "이 봇의 접두사는`{}`입니다! 사용 방법에 대한 자세한 내용은 \n` {} 도움말`을 참조하세요.", "¡El prefijo de este bot es `{}`! \n`{}help` para obtener más detalles sobre cómo usarlo."][get_lg(self.database[str(message.author.id)]["language"], message.guild.region)].format(self.PREFIX,
                                                                                                                                                                                                                                                                                                                                                                                                   self.PREFIX))
        else:
            await self.process_commands(message)

    async def on_guild_join(self, guild):
        embed = discord.Embed(title=f"{guild.name} に参加しました。", color=0x00ffff)
        # TODO: インテント修正後に修正
        # embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        embed.description = f"サーバーID: {guild.id}"
        await self.get_channel(self.datas["log_channel"]).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.datas['server']}"))

    async def on_guild_remove(self, guild):
        embed = discord.Embed(title=f"{guild.name} を退出しました。", color=0xff1493)
        # TODO: インテント修正後に修正
        # embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        embed.description = f"サーバーID: {guild.id}"
        await self.get_channel(self.datas["log_channel"]).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.datas['server']}"))

    async def on_command(self, ctx):
        pass  # await self.get_channel(self.datas["command_log_channel"]).send(f"`{ctx.message.content}` | {str(ctx.author)} ({ctx.author.id}) | {ctx.guild.name} ({ctx.guild.id}) | {ctx.channel.name} ({ctx.channel.id})")
        # TODO: 一時無効化

    # NOTE: db化
    # @tasks.loop(seconds=30.0)
    # async def save_database(self):
    #     db_dict = {
    #         "user": self.database,
    #         "role": {
    #             "ADMIN": self.ADMIN,
    #             "BAN": self.BAN,
    #             "Contributor": self.Contributor
    #         },
    #         "notify": {
    #             "twitter": self.GM_update["twitter"],
    #             "youtube": self.GM_update["youtube"],
    #             "facebook_jp": self.GM_update["facebook_jp"],
    #             "facebook_en": self.GM_update["facebook_en"],
    #             "facebook_es": self.GM_update["facebook_es"],
    #             "facebook_kr": self.GM_update["facebook_kr"]
    #         },
    #         "system": {
    #             "maintenance": self.maintenance
    #         }
    #     }
    #     database_channel = self.get_channel(self.datas["database_channel"])
    #     db_bytes = json.dumps(db_dict, indent=2)
    #     await database_channel.send(file=discord.File(fp=io.StringIO(db_bytes), filename="database.json"))


if __name__ == '__main__':
    intents = discord.Intents.default()
    bot = Bot(command_prefix=PREFIXES, help_command=Help(), status=discord.Status.dnd, activity=discord.Game("Starting..."), intents=intents)
    bot.run(TOKEN)
