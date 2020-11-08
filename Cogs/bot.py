import asyncio

import discord
from discord.ext import commands

from .data.command_data import CmdData
from .milkcoffee import MilkCoffee
from .utils.messenger import error_embed, success_embed
from .utils.multilingual import *

cmd_data = CmdData()


class Bot(commands.Cog):
    """BOTの情報や設定です^BOT information and settings^BOT 정보 나 설정입니다^Información y configuración de BOT"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee

    async def cog_before_invoke(self, ctx):
        """コマンド実行の前処理"""
        if str(ctx.author.id) in self.bot.BAN:  # BANされたユーザーの場合
            await error_embed(ctx, self.bot.text.your_account_banned[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.static_data.appeal_channel))
            raise Exception("Your Account Banned")  # 実行停止
        elif ctx.author.id not in self.bot.cache_users:  # 未登録ユーザーの場合
            await self.bot.on_new_user(ctx)

    async def cog_command_error(self, ctx, error):
        """エラー発生時"""
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):  # 引数不足
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):  # クルーダウン
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:  # 未知のエラー
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    @commands.command(aliases=["inv", "about", "info"], usage=cmd_data.invite.usage, description=cmd_data.invite.description, brief=cmd_data.invite.brief)
    async def invite(self, ctx):
        """招待リンクを送信"""
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        embed = discord.Embed(title="MilkCoffee", color=0xffffa8, url=self.bot.static_data.invite)
        embed.description = self.bot.text.invite_description[user_lang]
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name=self.bot.text.invite_url[user_lang], value=self.bot.static_data.invite, inline=False)
        embed.add_field(name=self.bot.text.invite_server[user_lang], value=self.bot.static_data.server, inline=False)
        embed.add_field(name=self.bot.text.invite_add[user_lang], value=f"[{self.bot.text.invite_vote[user_lang]}]({self.bot.static_data.top_gg})")
        embed.set_footer(text="Powered by mafu#7582 with discord.py", icon_url="https://cdn.discordapp.com/emojis/769855038964891688.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=["lang"], usage=cmd_data.language.usage, description=cmd_data.language.description, brief=cmd_data.language.brief)
    async def language(self, ctx):
        """言語を設定"""
        text = ctx.message.content.split()
        if len(text) == 1:  # 引数がない場合,選択画面を表示
            await self.language_selector(ctx)
        else:  # 言語が指定されている場合
            lang = text[1].lower()  # TODO: db ここからさき
            if lang in ["region", "server", "guild", "auto", "サーバー", "地域", "サーバー地域", "0"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value
                await success_embed(ctx, f"{self.bot.data.emoji.region} Set language to [Server Region]!")
            elif lang in ["ja", "jp", "japanese", "jpn", "日本語", "1"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value
                await success_embed(ctx, ":flag_jp: 言語を __日本語__ に設定しました!")
            elif lang in ["en", "eng", "english", "2"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value
                await success_embed(ctx, ":flag_au: Set language to __English__")
            elif lang in ["ko", "kr", "korean", "kor", "한국어", "3"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.KOREAN.value
                await success_embed(ctx, ":flag_kr: 언어를 __한국어__ 로 설정했습니다!")
            elif lang in ["es", "sp", "spa", "spanish", "Español", "4"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.SPANISH.value
                await success_embed(ctx, ":flag_es: Establecer idioma en __Español__!")
            else:
                await error_embed(ctx, self.bot.text.lang_not_found[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)])

    async def language_selector(self, ctx):
        """言語選択画面"""
        embed = discord.Embed(color=0xff7fff)  # 選択画面作成
        embed.description = f"{self.bot.data.emoji.region} Server Region\n"
        embed.description += ":flag_jp: 日本語 Japanese\n"
        embed.description += ":flag_au: English English\n"
        embed.description += ":flag_kr: 한국어 Korean\n"
        embed.description += ":flag_es: Español Spanish\n"
        msg = await ctx.send(":wave:" + ctx.author.mention, embed=embed)
        emoji_task = self.bot.loop.create_task(self.add_selector_emoji(msg))
        try:  # リアクション待機
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=lambda r, u: r.message.id == msg.id and u == ctx.author and str(r.emoji) in [self.bot.data.emoji.region, "🇯🇵", "🇦🇺", "🇰🇷", "🇪🇸"])
            emoji_task.cancel()
            if str(reaction.emoji) == self.bot.data.emoji.region:  # サーバー地域
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value  # TODO: db
                await success_embed(ctx, f"{self.bot.data.emoji.region} Set language to [Server Region]!")
            elif str(reaction.emoji) == "🇯🇵":  # 日本語
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value  # TODO: db
                await success_embed(ctx, ":flag_jp: 言語を __日本語__ に設定しました!")
            elif str(reaction.emoji) == "🇦🇺":  # 英語
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value  # TODO: db
                await success_embed(ctx, ":flag_au: Set language to __English__")
            elif str(reaction.emoji) == "🇰🇷":  # 韓国語
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.KOREAN.value  # TODO: db
                await success_embed(ctx, ":flag_kr: 언어를 __한국어__ 로 설정했습니다!")
            elif str(reaction.emoji) == "🇪🇸":  # スペイン語
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.SPANISH.value  # TODO: db
                await success_embed(ctx, ":flag_es: Establecer idioma en __Español__!")
        except asyncio.TimeoutError:
            pass
        finally:
            try:
                await msg.clear_reactions()
            except:
                pass

    async def add_selector_emoji(self, msg):
        """選択画面に選択肢の絵文字を追加"""
        await asyncio.gather(
            msg.add_reaction(self.bot.data.emoji.region),
            msg.add_reaction("🇯🇵"),
            msg.add_reaction("🇦🇺"),
            msg.add_reaction("🇰🇷"),
            msg.add_reaction("🇪🇸")
        )


def setup(bot):
    bot.add_cog(Bot(bot))
