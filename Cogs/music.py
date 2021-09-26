import re

from discord.ext import commands
import discord
import youtube_dl
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
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_options)


class YTDLSource(discord.PCMVolumeTransformer):

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
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=search, download=False, process=process))
        return data

    @classmethod
    async def stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=data["webpage_url"], download=False))

        return cls(
            discord.FFmpegPCMAudio(
                data['url'], **ffmpeg_options
            ), data=data
        )


class Player:
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
        self.task = ctx.bot.loop.create_task(
            self.player_loop()
        )

    async def player_loop(self):
        while True:
            self.next.clear()
            try:
                async with timeout(300):
                    data = await self.queue.get()
            except asyncio.TimeoutError:
                await warning_embed(self.channel, "一定時間、操作がなかったため接続を切りました。")
                return self.destroy(self.guild)
            try:
                source = await YTDLSource.stream(data, loop=self.bot.loop)
            except asyncio.CancelledError:
                return
            except:
                await error_embed(self.channel, f"音楽の処理中にエラーが発生しました\n```{traceback2.format_exc()}```")
                continue
            source.volume = self.volume
            self.current = source
            self.guild.voice_client.play(
                source,
                after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set)
            )
            await self.next.wait()
            source.cleanup()
            self.current = None
            if self.loop_queue:
                await self.queue.put(data)
            elif self.loop:
                self.queue._queue.appendleft(data)

    def destroy(self, guild):
        return self.bot.loop.create_task(guild.voice_client.disconnect())


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

    def duration_to_text(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            return "%d:%02d:%02d" % (hour, minutes, seconds)
        else:
            return "%02d:%02d" % (minutes, seconds)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, "必須の引数が不足しています!\n正しい使い方: `{0}{1}`\n詳しくは `{0}help {2}`".format(self.bot.PREFIX,
                                                                                                 ctx.command.usage.split(
                                                                                                     "^")[0],
                                                                                                 ctx.command.qualified_name))
        elif isinstance(error, commands.errors.CommandNotFound):
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
                    del self.players[member.guild.id]
                except:
                    pass
            # MEMO: memberインテントがオフであるため正常にキャッシュが動作せず人数が正しいとは限らない
            # elif bot_member in before.channel.members:  # この操作に関係がある
            #     voice_members = before.channel.members
            #     real_members = discord.utils.get(voice_members, bot=False)
            #     if len(voice_members) == 1 or real_members is None:
            #         if member.guild.id in self.players:
            #             player = self.get_player(member)
            #             player.destroy(member.guild)
            #             await player.channel.send("全員が退出したので便乗しました")
            #         else:
            #             await member.guild.voice_client.disconnect()

    @commands.command(aliases=["p"], usage=cmd_data.play.usage, description=cmd_data.play.description,
                      brief=cmd_data.play.brief)
    async def play(self, ctx, *, search):
        try:
            if ctx.voice_client is None:
                if await ctx.invoke(self.join) is not None:
                    return
            player = self.get_player(ctx)
            wait_msg = await normal_embed(ctx, "読込中...")
            async with ctx.typing():
                if search.startswith(("http://", "https://")) and "list=" in search:  # playlist
                    match = re.search("[a-zA-Z0-9_-]{34}", search)
                    if match is not None:
                        search = "https://www.youtube.com/playlist?list=" + match.group()
                    data = await YTDLSource.create_source(search, loop=self.bot.loop, process=False)
                else:  # video, search
                    data = await YTDLSource.create_source(search, loop=self.bot.loop)
                # import json,time;f = open(f"{time.time()}.json", "w");json.dump(data, f);f.close()
            await wait_msg.delete()
            if data is None:
                return await error_embed(ctx, "一致する検索結果はありませんでした")
            elif data["extractor"] in ["youtube", "youtube:search"]:
                if data["extractor"] == "youtube:search":
                    if not data["entries"]:
                        return await error_embed(ctx, "一致する検索結果はありませんでした")
                    data = data["entries"][0]
                await player.queue.put(data)
                await success_embed(ctx, f"{data['title']}を追加しました")
            elif data["extractor"] == "youtube:tab":
                meta_count = 0
                for meta in data["entries"]:
                    meta["webpage_url"] = "https://www.youtube.com/watch?v=" + meta["id"]
                    await player.queue.put(meta)
                    meta_count += 1
                await success_embed(ctx, f"{data['title']}から{meta_count}曲を追加しました")
        except:
            print(traceback2.format_exc())

    @commands.command(aliases=["j"], usage=cmd_data.join.usage, description=cmd_data.join.description,
                      brief=cmd_data.join.brief)
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
        elif voice_client is None or not voice_client.is_connected:
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

    @commands.command(aliases=["dc", "dis", "leave", "lv"], usage=cmd_data.disconnect.usage,
                      description=cmd_data.disconnect.description, brief=cmd_data.disconnect.brief)
    async def disconnect(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        await ctx.voice_client.disconnect()
        await success_embed(ctx, "切断しました")

    @commands.command(aliases=["q"], usage=cmd_data.queue.usage, description=cmd_data.queue.description,
                      brief=cmd_data.queue.brief)
    async def queue(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")

        text = ""
        player = self.get_player(ctx)
        if voice_client.source is not None:
            text += f"\n再生中:\n [{voice_client.source.title}]({voice_client.source.url}) | {self.duration_to_text(voice_client.source.duration)}\n"
        elif player.queue.empty():
            return await error_embed(ctx, "現在予約された曲はありません")

        for i, d in enumerate(player.queue._queue):
            cache = text
            text += f"\n{i + 1}. [{d['title']}]({d['webpage_url']}) | {self.duration_to_text(d['duration'])}"
            if len(text) >= 4000:
                text = cache + "\n等..."
                break
        text += f"\n\n現在{len(player.queue._queue)}曲が予約されています"

        embed = discord.Embed(description=text)
        if player.loop and player.loop_queue:
            embed.set_footer(text="現在再生中の曲、予約した曲全体の繰り返し機能が有効です(loopとloop_queue)")
        elif player.loop:
            embed.set_footer(text="現在再生中の曲の繰り返し機能が有効です(loop)")
        elif player.loop_queue:
            embed.set_footer(text="予約した曲全体の繰り返し機能が有効です(loop_queue)")
        await ctx.send(embed=embed)

    @commands.command(aliases=["ps", "stop"], usage=cmd_data.pause.usage, description=cmd_data.pause.description,
                      brief=cmd_data.pause.brief)
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await error_embed(ctx, "現在再生中の音楽はありません")
        elif voice_client.is_paused():
            return await error_embed(ctx, "既に再生が一時停止されています")
        voice_client.pause()
        await success_embed(ctx, "音楽の再生を一時停止しました")

    @commands.command(aliases=["re", "rs", "res"], usage=cmd_data.resume.usage, description=cmd_data.resume.description,
                      brief=cmd_data.resume.brief)
    async def resume(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "現在再生中の音楽はありません")
        elif not voice_client.is_paused():
            return await error_embed(ctx, "既に再生を再開しています")
        voice_client.resume()
        await success_embed(ctx, "音楽の再生を再開しました")

    @commands.command(aliases=["s"], usage=cmd_data.skip.usage, description=cmd_data.skip.description,
                      brief=cmd_data.skip.brief)
    async def skip(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await error_embed(ctx, "現在再生中の音楽はありません")
        voice_client.stop()
        await success_embed(ctx, "音楽をスキップしました")

    @commands.command(aliases=["np"], usage=cmd_data.now_playing.usage, description=cmd_data.now_playing.description,
                      brief=cmd_data.now_playing.brief)
    async def now_playing(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if player.current is None:
            return await error_embed(ctx, "現在再生中の音楽はありません")
        duration = self.duration_to_text(voice_client.source.duration)
        embed = discord.Embed(
            description=f"[{voice_client.source.title}]({voice_client.source.url})\n\n{duration}"
        )
        embed.set_thumbnail(url=voice_client.source["thumbnails"][0]["url"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["rm"], usage=cmd_data.remove.usage, description=cmd_data.remove.description,
                      brief=cmd_data.remove.brief)
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

    @commands.command(aliases=["cl"], usage=cmd_data.clear.usage, description=cmd_data.clear.description,
                      brief=cmd_data.clear.brief)
    async def clear(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        player.queue._queue.clear()
        await success_embed(ctx, "予約された曲を全て削除しました")

    @commands.command(usage=cmd_data.shuffle.usage, description=cmd_data.shuffle.description,
                      brief=cmd_data.shuffle.brief)
    async def shuffle(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if player.queue.empty():
            return await error_embed(ctx, "現在予約された曲はありません")
        random.shuffle(player.queue._queue)
        await success_embed(ctx, "予約された曲をシャッフルしました")

    @commands.command(aliases=["l"], usage=cmd_data.loop.usage, description=cmd_data.loop.description,
                      brief=cmd_data.loop.brief)
    async def loop(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if not player.loop and player.loop_queue:
            player.loop_queue = False
        player.loop = not player.loop
        await success_embed(ctx, f"現在再生中の曲の繰り返しを{'有効' if player.loop else '無効'}にしました")

    @commands.command(aliases=["lq", "loopqueue"], usage=cmd_data.loop_queue.usage,
                      description=cmd_data.loop_queue.description, brief=cmd_data.loop_queue.brief)
    async def loop_queue(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await error_embed(ctx, "BOTはまだボイスチャンネルに接続していません")
        player = self.get_player(ctx)
        if player.loop and not player.loop_queue:
            player.loop = False
        player.loop_queue = not player.loop_queue
        await success_embed(ctx, f"予約された曲全体の繰り返しを{'有効' if player.loop_queue else '無効'}にしました")


def setup(bot):
    bot.add_cog(Music(bot))
