from discord.ext import commands
import asyncio

class Notify(commands.Cog):
    """お知らせの設定するよ!"""

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    async def on_GM_update(self, message):
        for channel_id in self.bot.GM_update:
            await self.bot.get_channel(channel_id).send(message.content)

    @commands.command(usage="follow (チャンネル)", description="BOTのお知らせをあなたのサーバーのチャンネルにお届けするよ!チャンネルを指定しなかったら、コマンドを実行したチャンネルにお知らせするよ!")
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

    @commands.command(usage="notice (チャンネル)", description="MilkChoco運営の更新情報をあなたのサーバーのチャンネルにお届けするよ!")
    async def notice(self, ctx):
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if target_channel.id not in self.bot.GM_update:
            self.bot.GM_update.append(target_channel.id)
            await ctx.send(f"{target_channel.mention} を更新通知用チャンネルに設定したよ!")
        else:
            await ctx.send(f"{target_channel.mention} は既に更新通知用チャンネルに設定されているよ!")

    @commands.command(usage="unnotice (チャンネル)", description="MilkChoco運営の更新情報の受け取りを停止するよ!")
    async def unnotice(self, ctx):
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if target_channel.id in self.bot.GM_update:
            self.bot.GM_update.remove(target_channel.id)
            await ctx.send(f"{target_channel.mention} の更新通知設定を解除したよ!")
        else:
            await ctx.send(f"{target_channel.mention} は更新通知用チャンネルに設定されていないよ!")

    @commands.command(usage="ads", description="次広告が見れるまでの10分間のタイマーを設定するよ!広告見ようとはおもってるけど、忘れちゃう人向け。")
    async def ads(self, ctx):
        await ctx.send("10分後にまたお知らせするね!")
        await asyncio.sleep(10*60)
        await ctx.send(f"{ctx.author.mention}さん!\n10分経ったよ!")

def setup(bot):
    bot.add_cog(Notify(bot))
