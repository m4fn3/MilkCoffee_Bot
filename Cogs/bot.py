import json
import time

import discord
from discord.ext import commands

from Cogs.utils.multilingual import *
from Cogs.Data.static_data import StaticData
from Cogs.Data.strings import Strings

from .utils.messenger import normal

class MilkCoffee(commands.Bot):

    def __init__(self, main_prefix, command_prefix, help_command, status, activity, intents):
        super().__init__(command_prefix, help_command, status=status, activity=activity, intents=intents)
        self.bot_cogs = ["Cogs.language", "Cogs.costume", "Cogs.developer", "Cogs.info", "Cogs.notify"]
        self.PREFIX = main_prefix  # メインPREFIXを設定
        self.data = StaticData()  # 固定データを読み込み
        self.text = Strings()
        for cog in self.bot_cogs:  # Cog読み込み
            self.load_extension(cog)
        self.database = {}  # TODO: db
        self.ADMIN = {}  # TODO: db
        self.BAN = {}  # TODO: db
        self.Contributor = {}  # TODO: db
        self.GM_update = {  # TODO: db
            "twitter": [],
            "youtube": [],
            "facebook_jp": [],
            "facebook_en": [],
            "facebook_kr": [],
            "facebook_es": []
        }
        self.uptime = time.time()

    async def on_ready(self):
        """キャッシュ準備完了"""
        print(f"Logged in to {self.user}")
        # ステータスを変更
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.data.server}"))

    async def on_message(self, message):
        """メッセージ送信時"""
        if not self.is_ready():
            return
        elif message.channel.id in self.data.GM_update_channel:  # 更新通知チャンネルの場合
            notify_cog = self.get_cog("Notify")
            await notify_cog.on_GM_update(message)  # 運営の更新通知メッセージを処理
        elif message.author.bot:  # BOTからのメッセージの場合
            return
        elif message.content == f"<@!{self.user.id}>":  # BOTがメンションされた時
            # TODO: 言語未登録時にエラー
            return await normal(message.channel, self.text.prefix_of_the_bot[get_lg(self.database[str(message.author.id)]["language"], message.guild.region)].format(self.PREFIX, self.PREFIX))
        else:  # コマンドとして処理
            await self.process_commands(message)

    async def on_guild_join(self, guild):
        """サーバー参加時"""
        # サーバー参加ログを送信
        embed = discord.Embed(title=f"{guild.name} に参加しました。", color=0x00ffff)
        # TODO: インテント修正後に修正
        # embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        embed.description = f"サーバーID: {guild.id}"
        await self.get_channel(self.data.log_channel).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.data.server}"))

    async def on_guild_remove(self, guild):
        """サーバー退出時"""
        # サーバー退出ログを送信
        embed = discord.Embed(title=f"{guild.name} を退出しました。", color=0xff1493)
        # TODO: インテント修正後に修正
        # embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        embed.description = f"サーバーID: {guild.id}"
        await self.get_channel(self.data.log_channel).send(embed=embed)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.data.server}"))

    async def on_command(self, ctx):
        """コマンド実行時"""
        pass  # await self.get_channel(self.datas["command_log_channel"]).send(f"`{ctx.message.content}` | {str(ctx.author)} ({ctx.author.id}) | {ctx.guild.name} ({ctx.guild.id}) | {ctx.channel.name} ({ctx.channel.id})")
        # TODO: テストのため一時無効化 - コマンドログ

    # TODO: db
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
