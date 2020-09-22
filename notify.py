from discord.ext import commands
import asyncio, discord, json


class Notify(commands.Cog):
    """お知らせの設定するよ!"""

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open('./assets/emoji_data.json', 'r', encoding="utf-8") as f:
            self.emoji = json.load(f)

    async def cog_before_invoke(self, ctx):
        if self.bot.maintenance and str(ctx.author.id) not in self.bot.ADMIN:
            await ctx.send(f"現在BOTはメンテナンス中です。\n理由: {self.bot.maintenance}\n詳しい情報については公式サーバーにてご確認ください。")
            raise commands.CommandError("maintenance-error")

    async def on_GM_update(self, message):
        if message.channel.id == self.bot.datas["GM_update_channel"][0]:  # Twitter
            for channel_id in self.bot.GM_update["twitter"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["twitter"].remove(channel_id)
        elif message.channel.id == self.bot.datas["GM_update_channel"][1]:  # FaceBook
            for channel_id in self.bot.GM_update["facebook"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook"].remove(channel_id)
        elif message.channel.id == self.bot.datas["GM_update_channel"][2]:  # YouTube
            for channel_id in self.bot.GM_update["youtube"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["youtube"].remove(channel_id)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"引数が不足しているよ!.\n使い方: `{self.bot.PREFIX}{ctx.command.usage}`\n詳しくは `{self.bot.PREFIX}help {ctx.command.qualified_name}`")
        else:
            await ctx.send(f"エラーが発生しました。管理者にお尋ねください。\n{error}")

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
        cmd = ctx.message.content.split()
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if len(cmd) == 1 or (len(cmd) == 2 and cmd[1] not in ["twitter", "facebook", "youtube"]):
            embed = discord.Embed(title="MilkChoco運営の更新情報通知の設定!")
            embed.description = f"""
下のリアクションを押すと通知チャンネルに設定していなかった場合は設定、すでに設定していた場合は解除するよ!
{self.emoji["notify"]["twitter"]} ... Twitterでの投稿
{self.emoji["notify"]["facebook"]} ... FaceBookでの投稿
{self.emoji["notify"]["youtube"]} ... YouTubeでの投稿
"""
            msg = await ctx.send(embed=embed)
            await msg.add_reaction(self.emoji["notify"]["twitter"])
            await msg.add_reaction(self.emoji["notify"]["facebook"])
            await msg.add_reaction(self.emoji["notify"]["youtube"])

            def check(r, u):
                return r.message.id == msg.id and u == ctx.author and str(r.emoji) in [self.emoji["notify"]["twitter"], self.emoji["notify"]["facebook"], self.emoji["notify"]["youtube"]]

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                    if str(reaction.emoji) == self.emoji["notify"]["twitter"]:
                        await self.setup_message(ctx.channel, target_channel, "twitter")
                    elif str(reaction.emoji) == self.emoji["notify"]["facebook"]:
                        await self.setup_message(ctx.channel, target_channel, "facebook")
                    elif str(reaction.emoji) == self.emoji["notify"]["youtube"]:
                        await self.setup_message(ctx.channel, target_channel, "youtube")
                except asyncio.TimeoutError:
                    await msg.remove_reaction(self.emoji["notify"]["twitter"], self.bot.user)
                    await msg.remove_reaction(self.emoji["notify"]["facebook"], self.bot.user)
                    await msg.remove_reaction(self.emoji["notify"]["youtube"], self.bot.user)
                    break

    async def setup_message(self, channel, target_channel, update_type):
        if target_channel.id not in self.bot.GM_update[update_type]:
            self.bot.GM_update[update_type].append(target_channel.id)
            await channel.send(f"{target_channel.mention} を{update_type}更新通知用チャンネルに設定したよ!")
        else:
            self.bot.GM_update[update_type].remove(target_channel.id)
            await channel.send(f"{target_channel.mention} の{update_type}更新通知設定を解除したよ!")

    @commands.command(usage="ads", description="次広告が見れるまでの10分間のタイマーを設定するよ!広告見ようとはおもってるけど、忘れちゃう人向け。")
    async def ads(self, ctx):
        await ctx.send("10分後にまたお知らせするね!")
        await asyncio.sleep(10*60)
        await ctx.send(f"{ctx.author.mention}さん!\n10分経ったよ!")

def setup(bot):
    bot.add_cog(Notify(bot))
