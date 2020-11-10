import asyncio
from typing import Optional

import discord
from discord.ext import commands

from .data.command_data import CmdData
from .milkcoffee import MilkCoffee
from .utils.messenger import error_embed, success_embed

cmd_data = CmdData()


class Notify(commands.Cog):
    """お知らせの設定します^Setup the notification^알림설정하기^Establece notificaciones"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee

    async def cog_before_invoke(self, ctx):
        if ctx.author.id not in self.bot.cache_users:  # 未登録ユーザーの場合
            await self.bot.on_new_user(ctx)

    async def on_GM_update(self, message):
        if message.channel.id == self.bot.static_data.GM_update_channel[0]:  # Twitter
            for channel_id in await self.bot.db.get_notify_channels("twitter"):
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    await self.bot.db.remove_notify_channel("twitter", channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[1]:  # FaceBookJP
            for channel_id in await self.bot.db.get_notify_channels("facebook_jp"):
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    await self.bot.db.remove_notify_channel("facebook_jp", channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[2]:  # FaceBookEN
            for channel_id in await self.bot.db.get_notify_channels("facebook_en"):
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    await self.bot.db.remove_notify_channel("facebook_en", channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[3]:  # FaceBookKR
            for channel_id in await self.bot.db.get_notify_channels("facebook_kr"):
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    await self.bot.db.remove_notify_channel("facebook_kr", channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[4]:  # FaceBookES
            for channel_id in await self.bot.db.get_notify_channels("facebook_es"):
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    await self.bot.db.remove_notify_channel("facebook_es", channel_id)
        elif message.channel.id == self.bot.static_data.GM_update_channel[5]:  # YouTube
            for channel_id in await self.bot.db.get_notify_channels("youtube"):
                try:
                    self.bot.get_channel(channel_id)
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    await self.bot.db.remove_notify_channel("youtube", channel_id)

    async def cog_command_error(self, ctx, error):
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    @commands.command(usage=cmd_data.follow.usage, description=cmd_data.follow.description, brief=cmd_data.follow.brief)
    async def follow(self, ctx):
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
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

    @commands.command(usage=cmd_data.notice.usage, description=cmd_data.notice.description, brief=cmd_data.notice.brief)
    async def notice(self, ctx):
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        if not ctx.author.guild_permissions.manage_messages:
            return await error_embed(ctx, self.bot.text.notice_perm_error[user_lang])
        facebook = "facebook_" + ("jp" if user_lang == 0 else "en" if user_lang == 1 else "kr" if user_lang == 2 else "es")
        notify = await self.bot.db.get_notify_data(ctx.guild.id)  # 通知設定情報を取得
        is_new_guild = False  # 未登録のサーバーであるか
        if notify is None:  # 未登録の場合
            notify = {"twitter": None, "facebook_jp": None, "facebook_en": None, "facebook_kr": None, "facebook_es": None, "youtube": None}
            is_new_guild = True
        # 選択画面の作成
        while True:
            embed = discord.Embed(title=self.bot.text.notice_title[user_lang])
            embed.description = self.bot.text.notice_description[user_lang] + "\n"
            embed.description += f"{self.bot.data.emoji.twitter} `Twitter  :` {'<#' + str(notify['twitter']) + '>' if notify['twitter'] else ':x:'}\n"
            embed.description += f"{self.bot.data.emoji.facebook} `FaceBook :` {'<#' + str(notify[facebook]) + '>' if notify[facebook] else ':x:'}\n"
            embed.description += f"{self.bot.data.emoji.youtube} `YouTube  :` {'<#' + str(notify['youtube']) + '>' if notify['youtube'] else ':x:'}\n"
            msg = await ctx.send(embed=embed)
            emoji_task = self.bot.loop.create_task(self.add_notice_emoji(msg))
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=lambda r, u: r.message.id == msg.id and u == ctx.author and str(r.emoji) in [self.bot.data.emoji.twitter, self.bot.data.emoji.facebook, self.bot.data.emoji.youtube])
                res = None
                if str(reaction.emoji) == self.bot.data.emoji.twitter:
                    res = await self.setup_notify(ctx, "twitter", notify, user_lang)
                elif str(reaction.emoji) == self.bot.data.emoji.facebook:
                    res = await self.setup_notify(ctx, facebook, notify, user_lang)
                elif str(reaction.emoji) == self.bot.data.emoji.youtube:
                    res = await self.setup_notify(ctx, "youtube", notify, user_lang)
                if res is None:
                    break
                notify = res
                emoji_task.cancel()
                await msg.delete()
            except asyncio.TimeoutError:
                try:
                    await msg.clear_reactions()
                except:
                    pass
                break
        # データ保存
        if is_new_guild:
            await self.bot.db.set_notify_data(ctx.guild.id, notify)
        else:
            await self.bot.db.update_notify_data(ctx.guild.id, notify)

    async def setup_notify(self, ctx, notify_type, notify, user_lang):
        try:
            embed = discord.Embed(title=self.bot.text.notice_select_channel[user_lang])
            embed.description = self.bot.text.notice_select_desc[user_lang].format(ctx.channel.mention)
            desc_msg = await ctx.send(embed=embed)
            message = await self.bot.wait_for("message", timeout=30, check=lambda m: m.author == ctx.message.author and m.channel == ctx.channel)
            target_channel: Optional[discord.TextChannel]
            if message.content.lower() == "off":
                target_channel = None
            elif message.channel_mentions:
                target_channel = message.channel_mentions[0]
            elif ch := discord.utils.get(ctx.guild.channels, name=message.content):
                target_channel = ch
            else:
                await error_embed(ctx, self.bot.text.notice_channel_not_found[user_lang])
                return notify
            if target_channel is None:
                notify[notify_type] = None
                await success_embed(ctx, self.bot.text.notice_off[user_lang].format(notify_type))
            else:
                if not target_channel.permissions_for(ctx.guild.me).send_messages:
                    await error_embed(ctx, self.bot.text.notice_perm_send[user_lang].format(target_channel.mention))
                    return notify
                notify[notify_type] = target_channel.id if target_channel else None
                await success_embed(ctx, self.bot.text.notice_success[user_lang].format(notify_type, target_channel.mention))
            await desc_msg.delete()
            return notify
        except asyncio.TimeoutError:
            return None

    async def add_notice_emoji(self, msg):
        await asyncio.gather(
            msg.add_reaction(self.bot.data.emoji.twitter),
            msg.add_reaction(self.bot.data.emoji.facebook),
            msg.add_reaction(self.bot.data.emoji.youtube)
        )

    async def setup_message(self, ctx, target_channel, update_type):
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        if target_channel.id not in await self.bot.db.get_notify_channels(update_type):
            await self.bot.db.add_notify_channel(update_type, target_channel.id)
            await success_embed(ctx, self.bot.text.subscribe_update[user_lang].format(target_channel.mention, update_type))
        else:
            await self.bot.db.remove_notify_channel(update_type, target_channel.id)
            await error_embed(ctx, self.bot.text.unsubscribe_update[user_lang].format(target_channel.mention, update_type))

    @commands.command(usage=cmd_data.ads.usage, description=cmd_data.ads.description, brief=cmd_data.ads.brief)
    async def ads(self, ctx):
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        await success_embed(ctx, self.bot.text.tell_you_after_10_min[user_lang])
        await asyncio.sleep(10 * 60)
        await ctx.send(self.bot.text.passed_10_min[user_lang].format(ctx.author.mention))


def setup(bot):
    bot.add_cog(Notify(bot))
