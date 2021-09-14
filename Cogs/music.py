from discord.ext import commands
import discord
import youtube_dl
import asyncio
from async_timeout import timeout
import random
from .data.command_data import CmdData

cmd_data = CmdData()
ytdl_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
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

    @classmethod
    async def create_source(cls, search: str, *, loop):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=search, download=False))
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
                await self.channel.send("一定時間操作がなかったため切断しました")
                return self.destroy(self.guild)
            try:
                source = await YTDLSource.stream(data, loop=self.bot.loop)
            except Exception as e:
                await self.channel.send(f"音楽処理エラー\n```{e}```")
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
        return self.bot.loop.create_task(self.cog.cleanup(guild))


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
            await ctx.send("引数不足")
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        else:
            print(error)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None and member.guild.get_member(self.bot.user.id) in before.channel.members:
            voice_members = before.channel.members
            if len(voice_members) == 1:  # or not [u for u in voice_members if not u.bot]:
                if member.guild.id in self.players:
                    player = self.get_player(member)
                    player.destroy(member.guild)
                    await player.channel.send("全員が退出したので便乗しました")
                else:
                    await self.cleanup(member.guild)

    @commands.command(aliases=["p"], usage=cmd_data.play.usage, description=cmd_data.play.description, brief=cmd_data.play.brief)
    async def play(self, ctx, *, search):
        if ctx.voice_client is None:
            await ctx.invoke(self.join)
        player = self.get_player(ctx)
        async with ctx.typing():
            data = await YTDLSource.create_source(search, loop=self.bot.loop)
        if "entries" not in data:
            await player.queue.put(data)
            await ctx.send(f"音楽追加完了\n{data['title']}")
        else:
            for meta in data["entries"]:
                await player.queue.put(meta)
            await ctx.send(f"{len(data['entries'])}曲追加完了")

    @commands.command(aliases=["j"], usage=cmd_data.join.usage, description=cmd_data.join.description, brief=cmd_data.join.brief)
    async def join(self, ctx):
        voice_client = ctx.voice_client
        if ctx.author.voice is None:
            await ctx.send("VC未接続")
        elif voice_client is None or not voice_client.is_connected:
            await ctx.author.voice.channel.connect()
            await ctx.send("接続完了")
        elif voice_client.channel.id != ctx.author.voice.channel.id:
            await voice_client.move_to(ctx.author.voice.channel)
            await ctx.send("移動完了")
        else:
            await ctx.send("既に接続済")

    @commands.command(aliases=["dc", "dis", "leave", "lv"], usage=cmd_data.disconnect.usage, description=cmd_data.disconnect.description, brief=cmd_data.disconnect.brief)
    async def disconnect(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        await self.cleanup(ctx.guild)
        await ctx.send("切断完了")

    @commands.command(aliases=["q"], usage=cmd_data.queue.usage, description=cmd_data.queue.description, brief=cmd_data.queue.brief)
    async def queue(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        text = "予約済み曲一覧"
        if voice_client.source is not None:
            text = f"\n[再生中] {voice_client.source.title}"
        player = self.get_player(ctx)
        for i, d in enumerate(player.queue._queue):
            text += f"\n[{i + 1}] {d['title']}"
        if player.loop: text += "\n[ループ有効]"
        if player.loop_queue: text += "\n[キューループ有効]"
        await ctx.send(text)

    @commands.command(aliases=["ps", "stop"], usage=cmd_data.pause.usage, description=cmd_data.pause.description, brief=cmd_data.pause.brief)
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await ctx.send("再生無")
        elif voice_client.is_paused():
            return await ctx.send("既に一時停止済")
        voice_client.pause()
        await ctx.send("一時停止完了")

    @commands.command(aliases=["rs", "res"], usage=cmd_data.resume.usage, description=cmd_data.resume.description, brief=cmd_data.resume.brief)
    async def resume(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("再生無")
        elif not voice_client.is_paused():
            return await ctx.send("既に再開済")
        voice_client.resume()
        await ctx.send("再開完了")

    @commands.command(aliases=["s"], usage=cmd_data.skip.usage, description=cmd_data.skip.description, brief=cmd_data.skip.brief)
    async def skip(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            return await ctx.send("再生無")
        voice_client.stop()
        await ctx.send("スキップ完了")

    @commands.command(aliases=["np"], usage=cmd_data.now_playing.usage, description=cmd_data.now_playing.description, brief=cmd_data.now_playing.brief)
    async def now_playing(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        player = self.get_player(ctx)
        if player.current is None:
            return await ctx.send("再生無")
        text = f"曲名: {voice_client.source.title}\nURL: {voice_client.source.url}"
        await ctx.send(text)

    @commands.command(aliases=["rm"], usage=cmd_data.remove.usage, description=cmd_data.remove.description, brief=cmd_data.remove.brief)
    async def remove(self, ctx, idx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        player = self.get_player(ctx)
        if player.current is None:
            return await ctx.send("再生無")
        if not idx.isdigit():
            return await ctx.send("整数で位置番号指定")
        player = self.get_player(ctx)
        idx = int(idx) - 1
        if 0 <= idx <= len(player.queue._queue) - 1:
            data = player.queue._queue[idx]
            del player.queue._queue[idx]
            await ctx.send(f"削除完了\n{data['title']}")
        else:
            await ctx.send("範囲外の位置番号")

    @commands.command(aliases=["cl"], usage=cmd_data.clear.usage, description=cmd_data.clear.description, brief=cmd_data.clear.brief)
    async def clear(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        player = self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.send("クリア完了")

    @commands.command(usage=cmd_data.shuffle.usage, description=cmd_data.shuffle.description, brief=cmd_data.shuffle.brief)
    async def shuffle(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.sned("予約曲無")
        random.shuffle(player.queue._queue)
        await ctx.send("シャッフル完了")

    @commands.command(aliases=["l"], usage=cmd_data.loop.usage, description=cmd_data.loop.description, brief=cmd_data.loop.brief)
    async def loop(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        player = self.get_player(ctx)
        player.loop = not player.loop
        await ctx.send(f"ループ{'オン' if player.loop else 'オフ'}完了")

    @commands.command(aliases=["lq", "loopqueue"], usage=cmd_data.loop_queue.usage, description=cmd_data.loop_queue.description, brief=cmd_data.loop_queue.brief)
    async def loop_queue(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send("VC未接続")
        player = self.get_player(ctx)
        player.loop_queue = not player.loop_queue
        await ctx.send(f"キューループ{'オン' if player.loop_queue else 'オフ'}完了")

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except Exception as e:
            pass
        try:
            self.players[guild.id].task.cancel()
            del self.players[guild.id]
        except Exception as e:
            pass


def setup(bot):
    bot.add_cog(Music(bot))
