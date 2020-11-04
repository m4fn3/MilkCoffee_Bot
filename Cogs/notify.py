import asyncio
import json

import discord
from discord.ext import commands

from .utils.multilingual import *
from .bot import MilkCoffee


class Notify(commands.Cog):
    """お知らせの設定するよ!^I'll set the notification!^알림설정하기!^¡Establece notificaciones!"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee
        with open('./Assets/emoji_data.json', 'r', encoding="utf-8") as f:
            self.emoji = json.load(f)

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(["あなたのアカウントはBANされています(´;ω;｀)\nBANに対する異議申し立ては、公式サーバーの <#{}> にてご対応させていただきます。", "Your account is banned (´; ω;`)\nIf you have an objection to BAN, please use the official server <#{}>.", "당신의 계정은 차단되어 있습니다 ( '; ω;`)\n차단에 대한 이의 신청은 공식 서버 <#{}> 에서 대응하겠습니다.", "Su cuenta está prohibida (´; ω;`)\nSi tiene una objeción a la BAN, utilice <#{}> en el servidor oficial."][
                               get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.data.appeal_channel))
            raise Exception("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0,
            }
            await self.bot.get_cog("Language").language_selector(ctx)

    async def on_GM_update(self, message):
        if message.channel.id == self.bot.data.GM_update_channel[0]:  # Twitter
            for channel_id in self.bot.GM_update["twitter"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["twitter"].remove(channel_id)
        elif message.channel.id == self.bot.data.GM_update_channel[1]:  # FaceBookJP
            for channel_id in self.bot.GM_update["facebook_jp"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_jp"].remove(channel_id)
        elif message.channel.id == self.bot.data.GM_update_channel[2]:  # FaceBookEN
            for channel_id in self.bot.GM_update["facebook_en"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_en"].remove(channel_id)
        elif message.channel.id == self.bot.data.GM_update_channel[3]:  # FaceBookKR
            for channel_id in self.bot.GM_update["facebook_kr"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_kr"].remove(channel_id)
        elif message.channel.id == self.bot.data.GM_update_channel[4]:  # FaceBookES
            for channel_id in self.bot.GM_update["facebook_es"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_es"].remove(channel_id)
        elif message.channel.id == self.bot.data.GM_update_channel[5]:  # YouTube
            for channel_id in self.bot.GM_update["youtube"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["youtube"].remove(channel_id)

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang],
                                                                                                                                                                                                                                                                                                                                             ctx.command.qualified_name))
        else:
            await ctx.send(self.bot.text.error_occurred[user_lang].format(error))

    @commands.command(usage="follow (チャンネル)^follow (channel)^follow (채널)^follow (canal)",
                      description="BOTのお知らせをあなたのサーバーのチャンネルにお届けするよ!チャンネルを指定しなかったら、コマンドを実行したチャンネルにお知らせするよ!^Receive BOT updates to the channel on your server! If you do not specify a channel, we will setup to the channel that command executed^봇의 소식을 당신의 서버에 제공합니다! 채널을 지정하지 않으면 명령을 실행한 채널에 공지합니다!^¡Un BOT enviará una notificación al canal en su servidor! Si no especifica un canal, ¡notificaremos al canal donde se ejecutó el comando!")
    async def follow(self, ctx):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if target_channel.permissions_for(ctx.guild.me).manage_webhooks:
            await self.bot.get_channel(self.bot.data.announce_channel).follow(destination=target_channel)
            await ctx.send(self.bot.text.followed_channel[user_lang].format(target_channel.mention))
        else:
            await ctx.send(self.bot.text.missing_manage_webhook[user_lang].format(self.bot.data.announce_channel))

    @commands.command(usage="notice (チャンネル)^notice (channel)^notice (채널)^notice (canal)", description="MilkChoco運営の更新情報をあなたのサーバーのチャンネルにお届けするよ!^Receive MilkChoco updates on your server's channel!^밀크초코 운영의 업데이트 정보를 당신의 서버의 채널에 제공합니다!^¡Lo mantendremos informado sobre las operaciones de MilkChoco en su canal de servidor!")
    async def notice(self, ctx):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        language_text = "en"
        if user_lang == (LanguageCode.JAPANESE.value - 1):
            language_text = "jp"
        elif user_lang == (LanguageCode.KOREAN.value - 1):
            language_text = "kr"
        elif user_lang == (LanguageCode.SPANISH.value - 1):
            language_text = "es"
        cmd = ctx.message.content.split()
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if len(cmd) == 1 or (len(cmd) == 2 and cmd[1] not in ["twitter", "facebook", "youtube"]):
            embed = discord.Embed(title=self.bot.text.notice_title[user_lang])
            embed.description = f"""
{self.bot.text.notice_description[user_lang]}
{self.emoji["notify"]["twitter"]} ... Twitter
{self.emoji["notify"]["facebook"]} ... FaceBook
{self.emoji["notify"]["youtube"]} ... YouTube
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
                        await self.setup_message(ctx, target_channel, "twitter")
                    elif str(reaction.emoji) == self.emoji["notify"]["facebook"]:
                        await self.setup_message(ctx, target_channel, "facebook_" + language_text)
                    elif str(reaction.emoji) == self.emoji["notify"]["youtube"]:
                        await self.setup_message(ctx, target_channel, "youtube")
                except asyncio.TimeoutError:
                    await msg.remove_reaction(self.emoji["notify"]["twitter"], self.bot.user)
                    await msg.remove_reaction(self.emoji["notify"]["facebook"], self.bot.user)
                    await msg.remove_reaction(self.emoji["notify"]["youtube"], self.bot.user)
                    break

    async def setup_message(self, ctx, target_channel, update_type):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if target_channel.id not in self.bot.GM_update[update_type]:
            self.bot.GM_update[update_type].append(target_channel.id)
            await ctx.send(self.bot.text.subscribe_update[user_lang].format(target_channel.mention, update_type))
        else:
            self.bot.GM_update[update_type].remove(target_channel.id)
            await ctx.send(self.bot.text.unsubscribe_update[user_lang].format(target_channel.mention, update_type))

    @commands.command(usage="ads^ads^ads^ads", description="次広告が見れるまでの10分間のタイマーを設定するよ!広告見ようとはおもってるけど、忘れちゃう人向け。^Set a 10-minute timer to see the next ad! For those who want to see the ad but forget it.^다음 광고가 생길때까지 10분 타이머를 설정해! 광고를 보려고 생각하고 있지만, 잊어 버리는 사람을위해서!^¡Establezca un temporizador de 10 minutos para ver el próximo anuncio! Para aquellos que quieren ver el anuncio pero lo olvidan.")
    async def ads(self, ctx):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        await ctx.send(self.bot.text.tell_you_after_10_min[user_lang])
        await asyncio.sleep(10 * 60)
        await ctx.send(self.bot.text.passed_10_min[user_lang].format(ctx.author.mention))


def setup(bot):
    bot.add_cog(Notify(bot))
