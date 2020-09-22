from discord.ext import commands
import asyncio
from multilingual import *

class Notify(commands.Cog):
    """お知らせの設定するよ!"""

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    async def cog_before_invoke(self, ctx):
        if self.bot.maintenance and str(ctx.author.id) not in self.bot.ADMIN:
            await ctx.send(f"現在BOTはメンテナンス中です。\n理由: {self.bot.maintenance}\n詳しい情報については公式サーバーにてご確認ください。")
            raise commands.CommandError("maintenance-error")

    async def on_GM_update(self, message):
        for channel_id in self.bot.GM_update:
            try:
                self.bot.get_channel(channel_id)
                await self.bot.get_channel(channel_id).send(message.content)
            except:
                self.bot.GM_update.remove(channel_id)

    @commands.command(usage="follow (チャンネル)^follow (channel)^follow (채널)^follow (canal)", description="BOTのお知らせをあなたのサーバーのチャンネルにお届けするよ!チャンネルを指定しなかったら、コマンドを実行したチャンネルにお知らせするよ!^Receive BOT updates to the channel on your server! If you do not specify a channel, we will setup to the channel that command executed^봇의 소식을 당신의 서버에 제공합니다! 채널을 지정하지 않으면 명령을 실행한 채널에 공지합니다!^¡Un BOT enviará una notificación al canal en su servidor! Si no especifica un canal, ¡notificaremos al canal donde se ejecutó el comando!")
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

    @commands.command(usage="notice (チャンネル)^notice (channel)^notice (채널)^notice (canal)", description="MilkChoco運営の更新情報をあなたのサーバーのチャンネルにお届けするよ!^Receive MilkChoco updates on your server's channel!^밀크초코 운영의 업데이트 정보를 당신의 서버의 채널에 제공합니다!^¡Lo mantendremos informado sobre las operaciones de MilkChoco en su canal de servidor!")
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
