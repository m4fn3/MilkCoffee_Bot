import re

from discord.ext import commands
import discord
import yt_dlp as youtube_dl
import asyncio
from async_timeout import timeout
import random
import traceback2
from .data.command_data import CmdData
from .utils.messenger import error_embed, success_embed, warning_embed, normal_embed

cmd_data = CmdData()
ytdl_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # ipv6 addresses cause issues sometimes
    'cookiefile': 'cookies.txt'
}

ffmpeg_options = {
    'before_options': '-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_options)


class YTDLSource(discord.PCMVolumeTransformer):
    """youtube-dl操作"""

    def __init__(self, source, *, data):
        super().__init__(source)
        self.data = data

        self.title = data["title"]
        self.url = data["webpage_url"]
        self.duration = data["duration"]

    def __getitem__(self, item):
        return self.data[item]

    @classmethod
    async def create_source(cls, search: str, *, loop, process=True):
        """動画データの取得"""
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=search, download=False, process=process))
        return data

    @classmethod
    async def stream(cls, data, *, loop):
        """動画ストリーム用データ取得"""
        loop = loop or asyncio.get_event_loop()

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=data["webpage_url"], download=False))

        return cls(
            discord.FFmpegPCMAudio(
                data['url'], **ffmpeg_options
            ), data=data
        )


class Player:
    """再生操作全般を行うプレイヤー"""

    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.volume = 1
        self.loop = False
        self.loop_queue = False
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.current = None
        self.menu = None
        self.task = ctx.bot.loop.create_task(
            self.player_loop()
        )

    async def player_loop(self):
        """音楽再生のメインループ"""
        while True:
            self.next.clear()
            try:
                if len(self.queue._queue) == 0 and self.menu is not None:
                    await self.menu.update()  # 予約曲が0でメニューがある場合
                async with timeout(300):
                    data = await self.queue.get()
            except asyncio.TimeoutError:  # 自動切断
                await warning_embed(self.channel, "一定時間、操作がなかったため接続を切りました。")
                return self.destroy(self.guild)
            try:
                source = await YTDLSource.stream(data, loop=self.bot.loop)
            except asyncio.CancelledError:
                return
            except:
                await error_embed(self.channel, f"音楽の処理中にエラーが発生しました\n```py\n{traceback2.format_exc()}```")
                continue
            source.volume = self.volume
            self.current = source
            self.guild.voice_client.play(
                source,
                after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set)
            )
            if self.menu:  # 再生中の曲はソースから情報を取得するため再生処理の後に実行
                await self.menu.update()
            await self.next.wait()
            source.cleanup()
            self.current = None
            if self.loop_queue:
                await self.queue.put(data)
            elif self.loop:
                self.queue._queue.appendleft(data)

    def destroy(self, guild):
        return self.bot.loop.create_task(guild.voice_client.disconnect())


class MenuView(discord.ui.View):
    """playerコマンドの再生メニュー用Viewクラス"""

    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.cog = ctx.bot.get_cog("Music")

    @discord.ui.button(emoji="⏸")
    async def play(self, button: discord.ui.Button, interaction: discord.Interaction):
        voice_client = self.ctx.voice_client
        if not voice_client or not voice_client.is_connected():  # 未接続
            msg = await error_embed(self.ctx, "現在再生中の音楽はありません")
        elif voice_client.is_playing():
            button.emoji = "▶"
            button.style = discord.ButtonStyle.green
            voice_client.pause()
            msg = await success_embed(self.ctx, "音楽の再生を一時停止しました")
        elif voice_client.is_paused():
            button.emoji = "⏸"
            button.style = discord.ButtonStyle.grey
            voice_client.resume()
            msg = await success_embed(self.ctx, "音楽の再生を再開しました")
        else:
            msg = await error_embed(self.ctx, "現在再生中の音楽はありません")
        await self.update(msg)

    @discord.ui.button(emoji="⏭")
    async def skip(self, button: discord.ui.Button, interaction: discord.Interaction):
        msg = await self.ctx.invoke(self.cog.skip)
        await self.update(msg)

    @discord.ui.button(emoji="🔄")
    async def loop(self, button: discord.ui.Button, interaction: discord.Interaction):
        msg = await self.ctx.invoke(self.cog.loop_queue)
        button.style = discord.ButtonStyle.green if self.cog.get_player(self.ctx).loop_queue else discord.ButtonStyle.grey
        await self.update(msg)

    @discord.ui.button(emoji="🔀")
    async def shuffle(self, button: discord.ui.Button, interaction: discord.Interaction):
        msg = await self.ctx.invoke(self.cog.shuffle)
        await self.update(msg)

    @discord.ui.button(label="■", style=discord.ButtonStyle.red)
    async def stop_(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.ctx.invoke(self.cog.disconnect)

    async def update(self, msg):  # 各アクション実行後に画面更新&メッセージ削除
        await self.cog.get_player(self.ctx).menu.update(self)
        await msg.delete(delay=3)


class Menu:
    """playerコマンドの再生メニュー"""

    def __init__(self, ctx):
        self.ctx = ctx
        self.msg = None
        self.msg2 = None
        self.view = None
        self.task = None

    async def initialize(self):
        self.msg2 = await self.ctx.send(embed=discord.Embed(description=f"__パネルを閉じるまで<#{self.ctx.channel.id}>のチャットは全て曲名として扱われます!終了するには■を押してください.__", color=discord.Color.red()))
        self.view = MenuView(self.ctx)
        self.msg = await self.ctx.send("読込中...", view=self.view)
        await self.update()
        self.task = self.ctx.bot.loop.create_task(
            self.wait_message()
        )

    async def wait_message(self):
        while True:
            def check(m):
                return m.channel.id == self.ctx.channel.id and m.author.id != self.ctx.bot.user.id and m.content != "" and not m.content.startswith(tuple(self.ctx.bot.command_prefix))

            msg = await self.ctx.bot.wait_for('message', check=check)
            await msg.delete()
            msg = await self.ctx.invoke(self.ctx.bot.get_cog("Music").play, query=msg.content)
            await self.update()
            await msg.delete(delay=3)

    async def update(self, view=None):
        player = self.ctx.cog.get_player(self.ctx)
        voice_client = self.ctx.voice_client
        text = ""
        if voice_client.source is not None:
            text += f"\n再生中:\n [{voice_client.source.title}]({voice_client.source.url}) | {duration_to_text(voice_client.source.duration)}\n"
            text += "-------------------------------------------------"
        elif player.queue.empty():
            text += "まだ曲が追加されていません"

        for i in range(min(len(player.queue._queue), 10)):  # 最大10曲
            d = player.queue._queue[i]
            text += f"\n{i + 1}. [{d['title']}]({d['webpage_url']}) | {duration_to_text(d['duration'])}"
        if len(player.queue._queue) > 10:
            text += "\n等..."

        embed = discord.Embed(description=text, color=discord.Color.blurple())
        embed.set_footer(text=f"\n\n現在{len(player.queue._queue)}曲が予約されています")

        if view is None:
            await self.msg.edit(content=None, embed=embed)
        else:
            await self.msg.edit(content=None, embed=embed, view=view)

    async def destroy(self):
        self.task.cancel()
        self.view.stop()
        self.view.clear_items()
        await self.msg.delete()
        await self.msg2.delete()


def duration_to_text(seconds):
    if seconds == 0:
        return "LIVE"
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    print(seconds)
    if hour > 0:
        return "%d:%02d:%02d" % (hour, minutes, seconds)
    else:
        return "%02d:%02d" % (minutes, seconds)


class Music(commands.Cog):
    """音楽再生関連機能^音楽再生関連機能^音楽再生関連機能^音楽再生関連機能"""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = Player(ctx)
            self.players[ctx.guild.id] = player
        return player

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, "必須の引数が不足しています!\n正しい使い方: `{0}{1}`\n詳しくは `{0}help {2}`".format(
                self.bot.PREFIX, ctx.command.usage.split("^")[0], ctx.command.qualified_name)
                              )
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            print(error)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None and after.channel is None:  # 退出
            bot_member = member.guild.get_member(self.bot.user.id)
            if member == bot_member:  # botの退出
                try:
                    self.players[member.guild.id].task.cancel()
                    if self.players[member.guild.id].menu is not None:
                        self.bot.loop.create_task(self.players[member.guild.id].menu.destroy())
                    del self.players[member.guild.id]
                except:
                    pass
            # MEMO: memberインテントが必要
            # 自動切断
            elif bot_member in before.channel.members:  # BOT接続しているVC
                voice_members = before.channel.members
                real_members = discord.utils.get(voice_members, bot=False)
                if len(voice_members) == 1 or real_members is None:
                    # if member.guild.id in self.players:
                    #     player = self.get_player(member)
                    #     await player.channel.send("")
                    await member.guild.voice_client.disconnect()

    @commands.command(name="player", aliases=["pl"], usage=cmd_data.player.usage, description=cmd_data.player.description, brief=cmd_data.player.brief)
    async def player_(self, ctx):
        # VCに接続していることを確認
        if ctx.voice_client is None:
            if await ctx.invoke(self.join) is not None:
                return
        player = self.get_player(ctx)
        if player.menu is not None:  # 前のメニューを破棄
            old_menu = player.menu  # destroy()してからmenuがNoneになるまでの間にplayer_loopがメッセージを編集しようとするのを防ぐ
            player.menu = None  # 先にNone化
            await old_menu.destroy()
        menu = Menu(ctx)
        await menu.initialize()  # 初期化完了後にメニュー登録
        player.menu = menu

    async def process(self, ctx, search, supress):
        player = self.get_player(ctx)
        async with ctx.typing():
            if search.startswith(("http://", "https://")) and "list=" in search:  # playlist
                match = re.search("[a-zA-Z0-9_-]{34}", search)
                if match is not None:  # プレイリストのリンクは専用の形式に変換 / ミックスリストはそのままでOK
                    search = "https://www.youtube.com/playlist?list=" + match.group()
                data = await YTDLSource.create_source(search, loop=self.bot.loop, process=False)
            else:  # video, search
                data = await YTDLSource.create_source(search, loop=self.bot.loop)
        if data is None:
            return 0 if supress else await error_embed(ctx, f"一致する検索結果はありませんでした:\n {search}")
        elif data["extractor"] in ["youtube", "youtube:search"]:  # URL指定または検索
            if data["extractor"] == "youtube:search":  # 検索
                if not data["entries"]:
                    return 0 if supress else await error_embed(ctx, f"一致する検索結果はありませんでした:\n {search}")
                data = data["entries"][0]
            await player.queue.put(data)
            return 1 if supress else await success_embed(ctx, f"{data['title']}を追加しました")
        elif data["extractor"] == "youtube:tab":  # プレイリスト
            meta_count = 0
            for meta in data["entries"]:
                meta["webpage_url"] = "https://www.youtube.com/watch?v=" + meta["id"]
                await player.queue.put(meta)
                meta_count += 1
            return meta_count if supress else await success_embed(ctx, f"{data['title']}から{meta_count}曲を追加しました")

    @commands.command(aliases=["p"], usage=cmd_data.play.usage, description=cmd_data.play.description, brief=cmd_data.play.brief)
    async def play(self, ctx, *, query):
        if ctx.voice_client is None:
            if await ctx.invoke(self.join) is not None:
                return
        wait_msg = await normal_embed(ctx, "読込中...")
        query = [q for q in query.split("\n") if q != ""]
        ret_msg = None
        if len(query) == 1:
            ret_msg = await self.process(ctx, query[0], False)
        else:  # 複数曲対応
            # TODO: 途中で切断処理が入った場合に停止する
            count = 0
            for search in query:
                count += await self.process(ctx, search, True)
            ret_msg = await success_embed(ctx, f"合計{count}曲を追加しました")
        await wait_msg.delete()
        return ret_msg

    @commands.command(aliases=["j"], usage=cmd_data.join.usage, description=cmd_data.join.description, brief=cmd_data.join.brief)
    async def join(self, ctx):
        if ctx.guild.id not in self.bot.cache_guilds:
            embed = discord.Embed(
                description=f"負荷対策のため音楽機能はサーバーごとの承認制になっています。\n__**ミルクチョコプレイヤーの方**__は基本誰でも許可しますので、\n1. __上の番号__(コピペでok)\n2. __ミルクチョコをしていることがわかるもの(ゲームのスクショやツイッターなど)__\nとともに[公式サーバー](https://discord.gg/h2ZNX9mSSN)の<#887981017539944498>でお伝えください！",
                color=discord.Color.blue()
            )
            return await ctx.send(f"{ctx.guild.id}\nhttps://discord.gg/h2ZNX9mSSN", embed=embed)

        voice_client = ctx.voice_client
        if ctx.author.voice is None:
            return await error_embed(ctx, "先にボイスチャンネルに接続してください!")
        elif voice_client is None or not voice_client.is_connected():
            if voice_client is not None:  # VoiceClientがあるがis_connectedがfalseの場合 -> 一度強制切断
                await ctx.voice_client.disconnect(force=True)
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()
            await success_embed(ctx, f"{voice_channel.name}に接続しました")
            if voice_channel.type == discord.ChannelType.stage_voice and voice_channel.permissions_for(
                    ctx.me).manage_channels:
                await ctx.me.edit(suppress=False)
        elif voice_client.channel.id != ctx.author.voice.channel.id:
            await voice_client.move_to(ctx.author.voice.channel)
            await success_embed(ctx, f"{ctx.author.voice.channel.name}に移動しました")
        else:
            await warning_embed(ctx, f"既に{ctx.author.voice.channel.name}に接続しています")

    @commands.command(aliases=["dc", "dis", "leave", "lv"], usage=cmd_data.disconnect.usage, description=cmd_data.disconnect.description, brief=cmd_data.disconnect.brief)
    async def disconnect(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client:
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        elif not voice_client.is_connected():  # VoiceClientがあるがis_connectedがfalseの場合 -> 一度強制切断
            await ctx.voice_client.disconnect(force=True)
            return await error_embed(ctx, "異常な状況が検出されたので強制的に切断しました")
        await ctx.voice_client.disconnect()
        await success_embed(ctx, "切断しました")

    @commands.command(aliases=["q"], usage=cmd_data.queue.usage, description=cmd_data.queue.description, brief=cmd_data.queue.brief)
    async def queue(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")

        text = ""
        player = self.get_player(ctx)
        if voice_client.source is not None:
            text += f"\n再生中:\n [{voice_client.source.title}]({voice_client.source.url}) | {duration_to_text(voice_client.source.duration)}\n"
        elif player.queue.empty():
            return await error_embed(ctx, "現在予約された曲はありません")

        for i, d in enumerate(player.queue._queue):
            cache = text
            text += f"\n{i + 1}. [{d['title']}]({d['webpage_url']}) | {duration_to_text(d['duration'])}"
            # text += f"\n{i + 1}.) {d['title']} | {duration_to_text(d['duration'])}"
            if len(text) >= 4000:
                text = cache + "\n等..."
                break
        text += f"\n\n現在{len(player.queue._queue)}曲が予約されています"

        embed = discord.Embed(description=text, color=discord.Color.blurple())
        if player.loop:
            embed.set_footer(text="現在再生中の曲の繰り返し機能が有効です(loop)")
        elif player.loop_queue:
            embed.set_footer(text="予約した曲全体の繰り返し機能が有効です(loop_queue)")
        await ctx.send(embed=embed)

        # embed = discord.Embed(color=discord.Color.blurple())
        # embed.set_footer(text=text)
        # await ctx.send(embed=embed)

    @commands.command(aliases=["ps", "stop"], usage=cmd_data.pause.usage, description=cmd_data.pause.description, brief=cmd_data.pause.brief)
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await error_embed(ctx, "現在再生中の音楽はありません")
        elif voice_client.is_paused():
            return await error_embed(ctx, "既に再生が一時停止されています")
        voice_client.pause()
        return await success_embed(ctx, "音楽の再生を一時停止しました")

    @commands.command(aliases=["re", "rs", "res"], usage=cmd_data.resume.usage, description=cmd_data.resume.description, brief=cmd_data.resume.brief)
    async def resume(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "現在再生中の音楽はありません")
        elif not voice_client.is_paused():
            return await error_embed(ctx, "既に再生を再開しています")
        voice_client.resume()
        return await success_embed(ctx, "音楽の再生を再開しました")

    @commands.command(aliases=["s"], usage=cmd_data.skip.usage, description=cmd_data.skip.description, brief=cmd_data.skip.brief)
    async def skip(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await error_embed(ctx, "現在再生中の音楽はありません")
        voice_client.stop()
        return await success_embed(ctx, "音楽をスキップしました")

    @commands.command(aliases=["np"], usage=cmd_data.now_playing.usage, description=cmd_data.now_playing.description, brief=cmd_data.now_playing.brief)
    async def now_playing(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if player.current is None:
            return await error_embed(ctx, "現在再生中の音楽はありません")
        duration = duration_to_text(voice_client.source.duration)
        embed = discord.Embed(
            description=f"[{voice_client.source.title}]({voice_client.source.url})\n\n{duration}",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=voice_client.source["thumbnails"][0]["url"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["rm"], usage=cmd_data.remove.usage, description=cmd_data.remove.description, brief=cmd_data.remove.brief)
    async def remove(self, ctx, idx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        if not idx.isdigit():
            return await error_embed(ctx, "整数で位置の番号を指定してください")
        player = self.get_player(ctx)
        if player.queue.empty():
            return await error_embed(ctx, "現在予約された曲はありません")
        idx = int(idx) - 1
        if 0 <= idx <= len(player.queue._queue) - 1:
            data = player.queue._queue[idx]
            del player.queue._queue[idx]
            await success_embed(ctx, f"予約された曲から{data['title']}を削除しました")
        else:
            await error_embed(ctx, "指定された位置にあった音楽が存在しません")

    @commands.command(aliases=["cl"], usage=cmd_data.clear.usage, description=cmd_data.clear.description, brief=cmd_data.clear.brief)
    async def clear(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        player.queue._queue.clear()
        await success_embed(ctx, "予約された曲を全て削除しました")

    @commands.command(usage=cmd_data.shuffle.usage, description=cmd_data.shuffle.description, brief=cmd_data.shuffle.brief)
    async def shuffle(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if player.queue.empty():
            return await error_embed(ctx, "現在予約された曲はありません")
        random.shuffle(player.queue._queue)
        return await success_embed(ctx, "予約された曲をシャッフルしました")

    @commands.command(aliases=["l"], usage=cmd_data.loop.usage, description=cmd_data.loop.description, brief=cmd_data.loop.brief)
    async def loop(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if not player.loop and player.loop_queue:
            player.loop_queue = False
        player.loop = not player.loop
        await success_embed(ctx, f"現在再生中の曲の繰り返しを{'有効' if player.loop else '無効'}にしました")

    @commands.command(aliases=["lq", "loopqueue"], usage=cmd_data.loop_queue.usage, description=cmd_data.loop_queue.description, brief=cmd_data.loop_queue.brief)
    async def loop_queue(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if player.loop and not player.loop_queue:
            player.loop = False
        player.loop_queue = not player.loop_queue
        return await success_embed(ctx, f"予約された曲全体の繰り返しを{'有効' if player.loop_queue else '無効'}にしました")


def setup(bot):
    bot.add_cog(Music(bot))
