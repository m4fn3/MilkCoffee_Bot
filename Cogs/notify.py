import asyncio

import discord
from discord.ext import commands

from .data.command_data import CmdData
from .milkcoffee import MilkCoffee
from .utils.messenger import error_embed, success_embed
from .utils.multilingual import *

cmd_data = CmdData()


class Notify(commands.Cog):
    """お知らせの設定します^Setup the notification^알림설정하기^Establece notificaciones"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await error_embed(ctx, self.bot.text.your_account_banned[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.static_data.appeal_channel))
            raise Exception("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0,
            }
            await self.bot.get_cog("Bot").language_selector(ctx)

    async def on_GM_update(self, message):
        if message.channel.id == self.bot.static_data.GM_update_channel[0]:  # Twitter
            for channel_id in self.bot.GM_update["twitter"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["twitter"].remove(channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[1]:  # FaceBookJP
            for channel_id in self.bot.GM_update["facebook_jp"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_jp"].remove(channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[2]:  # FaceBookEN
            for channel_id in self.bot.GM_update["facebook_en"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_en"].remove(channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[3]:  # FaceBookKR
            for channel_id in self.bot.GM_update["facebook_kr"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_kr"].remove(channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[4]:  # FaceBookES
            for channel_id in self.bot.GM_update["facebook_es"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["facebook_es"].remove(channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[5]:  # YouTube
            for channel_id in self.bot.GM_update["youtube"]:
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    self.bot.GM_update["youtube"].remove(channel_id)

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    @commands.command(usage=cmd_data.follow.usage, description=cmd_data.follow.description)
    async def follow(self, ctx):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if target_channel.permissions_for(ctx.guild.me).manage_webhooks:
            await self.bot.get_channel(self.bot.static_data.announce_channel).follow(destination=target_channel)
            await success_embed(ctx, self.bot.text.followed_channel[user_lang].format(target_channel.mention))
        else:
            await error_embed(ctx, self.bot.text.missing_manage_webhook[user_lang].format(self.bot.static_data.announce_channel))

    @commands.command(usage=cmd_data.notice.usage, description=cmd_data.notice.description)
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
{self.bot.data.emoji.twitter} ... Twitter
{self.bot.data.emoji.facebook} ... FaceBook
{self.bot.data.emoji.youtube} ... YouTube
"""
            msg = await ctx.send(embed=embed)
            await msg.add_reaction(self.bot.data.emoji.twitter)
            await msg.add_reaction(self.bot.data.emoji.facebook)
            await msg.add_reaction(self.bot.data.emoji.youtube)

            def check(r, u):
                return r.message.id == msg.id and u == ctx.author and str(r.emoji) in [self.bot.data.emoji.twitter, self.bot.data.emoji.facebook, self.bot.data.emoji.youtube]

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                    if str(reaction.emoji) == self.bot.data.emoji.twitter:
                        await self.setup_message(ctx, target_channel, "twitter")
                    elif str(reaction.emoji) == self.bot.data.emoji.facebook:
                        await self.setup_message(ctx, target_channel, "facebook_" + language_text)
                    elif str(reaction.emoji) == self.bot.data.emoji.youtube:
                        await self.setup_message(ctx, target_channel, "youtube")
                except asyncio.TimeoutError:
                    await msg.remove_reaction(self.bot.data.emoji.twitter, self.bot.user)
                    await msg.remove_reaction(self.bot.data.emoji.facebook, self.bot.user)
                    await msg.remove_reaction(self.bot.data.emoji.youtube, self.bot.user)
                    break

    async def setup_message(self, ctx, target_channel, update_type):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if target_channel.id not in self.bot.GM_update[update_type]:
            self.bot.GM_update[update_type].append(target_channel.id)
            await success_embed(ctx, self.bot.text.subscribe_update[user_lang].format(target_channel.mention, update_type))
        else:
            self.bot.GM_update[update_type].remove(target_channel.id)
            await error_embed(ctx, self.bot.text.unsubscribe_update[user_lang].format(target_channel.mention, update_type))

    @commands.command(usage=cmd_data.ads.usage, description=cmd_data.ads.description)
    async def ads(self, ctx):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        await success_embed(ctx, self.bot.text.tell_you_after_10_min[user_lang])
        await asyncio.sleep(10 * 60)
        await ctx.send(self.bot.text.passed_10_min[user_lang].format(ctx.author.mention))


def setup(bot):
    bot.add_cog(Notify(bot))
