import asyncio
from typing import Optional

import aiohttp
import nextcord as discord
import traceback2
from nextcord.ext import commands

from .data.command_data import CmdData
from .milkcoffee import MilkCoffee
from .utils.messenger import error_embed, success_embed

cmd_data = CmdData()


class Notify(commands.Cog):
    """お知らせの設定します^Setup the notification^알림설정하기^Establece notificaciones"""

    def __init__(self, bot: MilkCoffee) -> None:
        self.bot = bot

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """コマンド実行の前処理"""
        if ctx.author.id not in self.bot.cache_users:  # 未登録ユーザーの場合
            await self.bot.on_new_user(ctx)  # 新規登録

    async def on_GM_update(self, message: discord.Message) -> None:
        """運営からの通知が届いた場合"""
        if message.channel.id == self.bot.static_data.GM_update_channel[0]:  # Twitter
            for channel_id in await self.bot.db.get_notify_channels("twitter"):
                try:
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    print(traceback2.format_exc())
                    pass
        elif message.channel.id == self.bot.static_data.GM_update_channel[1]:  # FaceBookJP
            for channel_id in await self.bot.db.get_notify_channels("facebook_jp"):
                try:
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    print(traceback2.format_exc())
                    pass
        elif message.channel.id == self.bot.static_data.GM_update_channel[2]:  # FaceBookEN
            for channel_id in await self.bot.db.get_notify_channels("facebook_en"):
                try:
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    print(traceback2.format_exc())
                    pass
        elif message.channel.id == self.bot.static_data.GM_update_channel[3]:  # FaceBookKR
            for channel_id in await self.bot.db.get_notify_channels("facebook_kr"):
                try:
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    print(traceback2.format_exc())
                    pass
        elif message.channel.id == self.bot.static_data.GM_update_channel[4]:  # FaceBookES
            for channel_id in await self.bot.db.get_notify_channels("facebook_es"):
                try:
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    print(traceback2.format_exc())
                    pass
        elif message.channel.id == self.bot.static_data.GM_update_channel[5]:  # YouTube
            for channel_id in await self.bot.db.get_notify_channels("youtube"):
                try:
                    await self.bot.get_channel(channel_id).send(message.content)
                except:
                    print(traceback2.format_exc())
                    pass

    async def cog_command_error(self, ctx: commands.Context, error) -> None:
        """エラー発生時"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):  # 引数不足
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):  # クールダウン
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        elif isinstance(error, aiohttp.ClientOSError):
            await error_embed(ctx, self.bot.text.server_error[user_lang])
        else:  # 未知のエラー
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    @commands.command(usage=cmd_data.follow.usage, description=cmd_data.follow.description, brief=cmd_data.follow.brief)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def follow(self, ctx: commands.Context) -> None:
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        if not ctx.author.guild_permissions.manage_webhooks:  # webhook管理権限が不足している場合
            ctx.command.reset_cooldown()
            return await error_embed(ctx, self.bot.text.follow_perm_error[user_lang])
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:  # ない場合,送信されたチャンネルを指定
            target_channel = ctx.channel
        if target_channel.permissions_for(ctx.guild.me).manage_webhooks:  # BOTにwebhook管理権限があるならば
            await self.bot.get_channel(self.bot.static_data.announce_channel).follow(destination=target_channel)
            await success_embed(ctx, self.bot.text.followed_channel[user_lang].format(target_channel.mention))
        else:  # ない場合はエラー
            await error_embed(ctx, self.bot.text.missing_manage_webhook[user_lang].format(self.bot.static_data.announce_channel))

    @commands.command(usage=cmd_data.notice.usage, description=cmd_data.notice.description, brief=cmd_data.notice.brief)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def notice(self, ctx: commands.Context) -> None:
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        if not ctx.author.guild_permissions.manage_messages:  # メッセージ管理権限がない場合は終了
            return await error_embed(ctx, self.bot.text.notice_perm_error[user_lang])
        facebook = "facebook_" + ("jp" if user_lang == 0 else "en" if user_lang == 1 else "kr" if user_lang == 2 else "es")
        notify = await self.bot.db.get_notify_data(ctx.guild.id)  # 通知設定情報を取得
        is_new_guild = False  # 未登録のサーバーであるか
        if notify is None:  # 未登録の場合
            notify = {"twitter": None, "facebook_jp": None, "facebook_en": None, "facebook_kr": None, "facebook_es": None, "youtube": None}
            is_new_guild = True
        while True:
            # 選択画面の作成
            embed = discord.Embed(title=self.bot.text.notice_title[user_lang])
            embed.description = self.bot.text.notice_description[user_lang] + "\n"
            embed.description += f"{self.bot.data.emoji.twitter} `Twitter  :` {'<#' + str(notify['twitter']) + '>' if notify['twitter'] else ':x:'}\n"
            embed.description += f"{self.bot.data.emoji.facebook} `FaceBook :` {'<#' + str(notify[facebook]) + '>' if notify[facebook] else ':x:'}\n"
            embed.description += f"{self.bot.data.emoji.youtube} `YouTube  :` {'<#' + str(notify['youtube']) + '>' if notify['youtube'] else ':x:'}\n"
            msg = await ctx.send(embed=embed)
            emoji_task = self.bot.loop.create_task(self.add_notice_emoji(msg))  # リアクション追加
            try:  # リアクション待機
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=lambda r, u: r.message.id == msg.id and u == ctx.author and str(r.emoji) in [self.bot.data.emoji.twitter, self.bot.data.emoji.facebook, self.bot.data.emoji.youtube])
                res = None
                if str(reaction.emoji) == self.bot.data.emoji.twitter:  # Twitter
                    res = await self.setup_notify(ctx, "twitter", notify, user_lang)
                elif str(reaction.emoji) == self.bot.data.emoji.facebook:  # Facebook
                    res = await self.setup_notify(ctx, facebook, notify, user_lang)
                elif str(reaction.emoji) == self.bot.data.emoji.youtube:  # YouTube
                    res = await self.setup_notify(ctx, "youtube", notify, user_lang)
                if res is None:  # チャンネル入力のタイムアウト時
                    break
                notify = res
                emoji_task.cancel()
                await msg.delete()
            except asyncio.TimeoutError:  # タイムアウトした場合
                try:  # リアクションを削除
                    await msg.clear_reactions()
                except:
                    pass
                break
        # データ保存
        if is_new_guild:  # 新規サーバーの場合は新規追加
            await self.bot.db.set_notify_data(ctx.guild.id, notify)
        else:  # 既存サーバーの場合は更新
            await self.bot.db.update_notify_data(ctx.guild.id, notify)

    async def setup_notify(self, ctx: commands.Context, notify_type: str, notify: dict, user_lang: int) -> Optional[dict]:
        try:  # チャンネル選択画面作成
            embed = discord.Embed(title=self.bot.text.notice_select_channel[user_lang])
            embed.description = self.bot.text.notice_select_desc[user_lang].format(ctx.channel.mention)
            desc_msg = await ctx.send(embed=embed)
            # 入力待機
            message = await self.bot.wait_for("message", timeout=30, check=lambda m: m.author == ctx.message.author and m.channel == ctx.channel)
            target_channel: Optional[discord.TextChannel]
            if message.content.lower() == "off":  # offの場合無効化する
                target_channel = None
            elif message.channel_mentions:  # チャンネルメンションの場合
                target_channel = message.channel_mentions[0]
            elif discord.utils.get(ctx.guild.channels, name=message.content):  # チャンネル名の場合
                target_channel = discord.utils.get(ctx.guild.channels, name=message.content)
            else:  # チャンネルが見つからなかった場合
                await error_embed(ctx, self.bot.text.notice_channel_not_found[user_lang])
                return notify  # 変更せずにそのまま返す
            if target_channel is None:  # offの場合
                notify[notify_type] = None
                await success_embed(ctx, self.bot.text.notice_off[user_lang].format(notify_type))
            else:  # チャンネルが選択された場合
                if not target_channel.permissions_for(ctx.guild.me).send_messages:  # メッセージの送信権がない場合
                    await error_embed(ctx, self.bot.text.notice_perm_send[user_lang].format(target_channel.mention))
                    return notify  # 変更せずにそのまま返す
                notify[notify_type] = target_channel.id
                await success_embed(ctx, self.bot.text.notice_success[user_lang].format(notify_type, target_channel.mention))
            await desc_msg.delete()
            return notify  # 更新されたデータを返す
        except asyncio.TimeoutError:  # タイムアウト時
            return None

    async def add_notice_emoji(self, msg: discord.message) -> None:
        await asyncio.gather(
            msg.add_reaction(self.bot.data.emoji.twitter),
            msg.add_reaction(self.bot.data.emoji.facebook),
            msg.add_reaction(self.bot.data.emoji.youtube)
        )

    @commands.command(usage=cmd_data.ads.usage, description=cmd_data.ads.description, brief=cmd_data.ads.brief)
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def ads(self, ctx: commands.Context) -> None:
        """10分のタイマーを設定"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        await success_embed(ctx, self.bot.text.tell_you_after_10_min[user_lang])
        await asyncio.sleep(10 * 60)  # 10分待機
        embed = discord.Embed(description=self.bot.text.passed_10_min[user_lang], color=discord.Color.blue())
        await ctx.send(ctx.author.mention, embed=embed)


def setup(bot: MilkCoffee) -> None:
    bot.add_cog(Notify(bot))
