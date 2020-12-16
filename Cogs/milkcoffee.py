import io
import os
import time

import aiohttp
import discord
from discord.ext import commands, tasks

from .SQLManager import SQLManager
from .data.item_data import ItemData
from .data.static_data import StaticData
from .data.strings import Strings
from .utils.messenger import normal_embed


class MilkCoffee(commands.Bot):

    def __init__(self, main_prefix, db_url, command_prefix, help_command, status, activity, intents) -> None:
        super().__init__(command_prefix, help_command, status=status, activity=activity, intents=intents)
        self.bot_cogs = ["Cogs.costume", "Cogs.notify", "Cogs.bot", "Cogs.developer"]
        self.PREFIX = main_prefix  # メインPREFIXを設定

        self.db_ready = False  # データベース準備フラグ

        # データベース接続
        self.db = SQLManager(db_url, self.loop)
        self.cache_users = set()  # 登録済みユーザーのリスト

        # 読み込み
        self.static_data = StaticData()  # 固定データを読み込み
        self.text = Strings()  # 言語別文字列データを読み込み
        self.data = ItemData()  # 絵文字,アイテムデータを読み込み

        for cog in self.bot_cogs:  # Cogの読み込み
            self.load_extension(cog)

        self.uptime = time.time()  # 起動時間の記録
        self.commands_run = 0
        self.aiohttp_session = aiohttp.ClientSession(loop=self.loop)

    async def on_ready(self) -> None:
        """キャッシュ準備完了"""
        print(f"Logged in to [{self.user}]")
        if not self.db.is_connected():  # データベースに接続しているか確認
            await self.db.connect()  # データベースに接続
            self.cache_users = self.cache_users.union(set(await self.db.get_registered_users()))
            self.db_ready = True  # データベース接続完了フラグ
        if not self.backup_database.is_running():
            self.backup_database.start()
        # ステータスを変更
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.static_data.server}"))

    async def on_message(self, message: discord.Message) -> None:
        """メッセージ送信時"""
        if not (self.is_ready() and self.db_ready):  # 準備が完了していない場合
            return
        elif message.channel.id in self.static_data.GM_update_channel:  # 更新通知チャンネルの場合
            notify_cog = self.get_cog("Notify")
            await notify_cog.on_GM_update(message)  # 運営の更新通知メッセージを処理
        elif message.author.bot:  # BOTからのメッセージの場合
            return
        elif message.content == f"<@!{self.user.id}>":  # BOTがメンションされた時
            return await normal_embed(message.channel, self.text.prefix_of_the_bot[await self.db.get_lang(message.author.id, message.guild.region)].format(self.PREFIX, self.PREFIX))
        else:  # コマンドとして処理
            await self.process_commands(message)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """サーバー参加時"""
        # サーバー参加ログを送信
        embed = discord.Embed(title=f"{guild.name} に参加しました。", color=0x00ffff)
        # TODO: インテント修正後に修正
        # embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        embed.description = f"サーバーID: {guild.id}"
        await self.get_channel(self.static_data.log_channel).send(embed=embed)
        # ステータスを更新
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.static_data.server}"))

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """サーバー退出時"""
        # サーバー退出ログを送信
        embed = discord.Embed(title=f"{guild.name} を退出しました。", color=0xff1493)
        # TODO: インテント修正後に修正
        # embed.description = f"サーバーID: {guild.id}\nメンバー数: {len(guild.members)}\nサーバー管理者: {str(guild.owner)} ({guild.owner.id})"
        embed.description = f"サーバーID: {guild.id}"
        await self.get_channel(self.static_data.log_channel).send(embed=embed)
        # ステータスを更新
        await self.change_presence(status=discord.Status.online, activity=discord.Game(f"{self.PREFIX}help | {len(self.guilds)}servers | {self.static_data.server}"))

    async def on_command(self, ctx: commands.Context) -> None:
        """コマンド実行時"""
        self.commands_run += 1
        embed = discord.Embed(description=f"[{ctx.message.content}]({ctx.message.jump_url}) | {str(ctx.author)} | {ctx.channel.name} | {ctx.guild.name}", color=discord.Color.dark_theme())
        content = {"embeds": [embed.to_dict()]}
        headers = {'Content-Type': 'application/json'}
        await self.aiohttp_session.post(os.getenv("LOG_WH"), json=content, headers=headers)

    async def on_new_user(self, ctx: commands.Context) -> None:
        """新規ユーザーが使用した時"""
        self.cache_users.add(ctx.author.id)  # キャッシュに追加
        await self.db.register_new_user(ctx.author.id)  # ユーザー登録
        await self.get_cog("Bot").language_selector(ctx)  # 言語選択

    @tasks.loop(hours=1)
    async def backup_database(self):
        output = await self.get_cog("Developer").run_subprocess(f"pg_dump {os.getenv('DB_URL')}")
        output = "\n".join(output)
        await self.get_channel(self.static_data.backup_channel).send(
            file=discord.File(fp=io.StringIO(output), filename="dump")
        )
