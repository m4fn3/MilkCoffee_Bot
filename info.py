from discord.ext import commands
import discord, datetime, time


class Information(commands.Cog):
    """BOTに関する情報を表示します。"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(f"あなたのアカウントはBANされています。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
            raise commands.CommandError("Your Account Banned")

    @commands.command(aliases=["inv"], usage="invite", description="BOTの招待リンクを表示します。")
    async def invite(self, ctx):
        text = f"__**BOTの招待用URL**__:\n{self.bot.datas['invite']}\n" \
               f"__**サポート用サーバー(公式サーバー)**__:\n{self.bot.datas['server']}"
        await ctx.send(text)

    @commands.command(aliases=["about"], usage="info", description="BOTに関する情報を表示します。")
    async def info(self, ctx):
        td = datetime.timedelta(seconds=int(time.time() - self.bot.uptime))
        m, s = divmod(td.seconds, 60); h, m = divmod(m, 60); d = td.days
        embed = discord.Embed(title="このBOTについて")
        embed.description = f"BOTをご使用いただき、ありがとうございます！\n" \
                            f"このBOTはMilkChocoをプレイする人達の、Discordサーバーのために `{self.bot.datas['author']}` によって作成されました。\n" \
                            f"詳しい使い方は `{ctx.prefix}help` で確認して下さい。"
        embed.add_field(name="ステータス", value=f"```導入サーバー数: {len(self.bot.guilds)}\nBOTが認識しているユーザー数:{len(self.bot.users)}```", inline=False)
        embed.add_field(name="稼働時間", value=f"{d}日 {h}時間 {m}分 {s}秒", inline=False)
        embed.add_field(name="各種URL", value=f"[BOT招待用URL]({self.bot.datas['invite']}) | [サポート用サーバー]({self.bot.datas['server']})", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["pg"], usage="ping", description="BOTの反応速度を計測します。")
    async def ping(self, ctx):
        before = time.monotonic()
        message = await ctx.send("Pong")
        ping = (time.monotonic() - before) * 1000
        await message.delete()
        await ctx.send(f"反応速度: `{int(ping)}`[ms]")

    @commands.command(aliases=["notice"], usage="follow (チャンネル)", description="BOTのお知らせチャンネルをフォローします。チャンネルを設定しなかった場合、コマンドぞ実行したチャンネルに設定します。")
    async def follow(self, ctx):
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if target_channel.permissions_for(ctx.guild.get_member(self.bot.user.id)).manage_webhooks:
            await self.bot.get_channel(self.bot.datas['notice_channel']).follow(destination=target_channel)
            await ctx.send(f"{target_channel.mention}で公式サーバーのBOTお知らせ用チャンネルをフォローしました。")
        else:
            await ctx.send(f"`manage_webhooks(webhookの管理)`権限が不足しています。\n代わりに公式サーバーの<#{self.bot.datas['notice_channel']}>を手動でフォローすることもできます。")


def setup(bot):
    bot.add_cog(Information(bot))
