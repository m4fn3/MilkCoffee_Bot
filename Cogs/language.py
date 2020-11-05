import asyncio
import json

import discord
from discord.ext import commands

from .bot import MilkCoffee
from .utils.messenger import error_embed
from .utils.multilingual import *


class Language(commands.Cog):
    """言語を設定するよ!^Set up language!^언어를 설정합니다!^Configurar idioma!"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee
        with open('./Assets/emoji_data.json', 'r', encoding="utf-8") as f:
            self.emoji = json.load(f)

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await error_embed(ctx, self.bot.text.your_account_banned[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.data.appeal_channel))
            raise Exception("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0
            }
            await self.language_selector(ctx)  # languageコマンドが最初のコマンドの場合lang画面が2回表示されるのを防ぐ
            if ctx.command.name == "language":
                raise Exception("初回languageの停止")

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    async def language_selector(self, ctx):
        embed = discord.Embed(title=f"{self.emoji['language']['language']} Select language:")
        embed.add_field(name=f"{self.emoji['language']['region']} Server Region", value="m!lang region")
        embed.add_field(name=":flag_jp: 日本語 Japanese", value="m!lang ja")
        embed.add_field(name=":flag_au: English English", value="m!lang en")
        embed.add_field(name=":flag_kr: 한국어 Korean", value="m!lang ko")
        embed.add_field(name=":flag_es: Español Spanish", value="m!lang es")
        msg_obj = await ctx.send(ctx.author.mention, embed=embed)
        await msg_obj.add_reaction(self.emoji['language']['region'])
        await msg_obj.add_reaction("🇯🇵")
        await msg_obj.add_reaction("🇦🇺")
        await msg_obj.add_reaction("🇰🇷")
        await msg_obj.add_reaction("🇪🇸")

        def check(r, u):
            return r.message.id == msg_obj.id and u == ctx.author and str(r.emoji) in [self.emoji['language']['region'], "🇯🇵", "🇦🇺", "🇰🇷", "🇪🇸"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
            print(str(reaction.emoji))
            if str(reaction.emoji) == self.emoji['language']['region']:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value
                await ctx.send(f"{self.emoji['language']['region']} Set language to [Server Region]!")
            elif str(reaction.emoji) == "🇯🇵":
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value
                await ctx.send(":flag_jp: 言語を __日本語__ に設定しました!")
            elif str(reaction.emoji) == "🇦🇺":
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value
                await ctx.send(":flag_au: Set language to __English__")
            elif str(reaction.emoji) == "🇰🇷":
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.KOREAN.value
                await ctx.send(":flag_kr: 언어를 __한국어__ 로 설정했습니다!")
            elif str(reaction.emoji) == "🇪🇸":
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.SPANISH.value
                await ctx.send(":flag_es: Establecer idioma en __Español__!")
        except asyncio.TimeoutError:
            pass
        finally:
            await msg_obj.remove_reaction(self.emoji['language']['region'], self.bot.user)
            await msg_obj.remove_reaction("🇯🇵", self.bot.user)
            await msg_obj.remove_reaction("🇦🇺", self.bot.user)
            await msg_obj.remove_reaction("🇰🇷", self.bot.user)
            await msg_obj.remove_reaction("🇪🇸", self.bot.user)

    @commands.command(aliases=["lang"], usage="lang (言語)^lang (language)^lang (언어)^lang (idioma)", description="言語を設定するよ!^Set up language!^언어를 설정합니다!^Configurar idioma!")
    async def language(self, ctx):
        text = ctx.message.content.split()
        if len(text) == 1:
            await self.language_selector(ctx)
        else:
            lang = text[1].lower()
            if lang in ["region", "server", "guild", "auto", "サーバー", "地域", "サーバー地域", "0"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value
                await ctx.send(f"{self.emoji['language']['region']} Set language to [Server Region]!")
            elif lang in ["ja", "jp", "japanese", "jpn", "日本語", "1"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value
                await ctx.send(":flag_jp: 言語を __日本語__ に設定しました!")
            elif lang in ["en", "eng", "english", "2"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value
                await ctx.send(":flag_au: Set language to __English__")
            elif lang in ["ko", "kr", "korean", "kor", "한국어", "3"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.KOREAN.value
                await ctx.send(":flag_kr: 언어를 __한국어__ 로 설정했습니다!")
            elif lang in ["es", "sp", "spa", "spanish", "Español", "4"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.SPANISH.value
                await ctx.send(":flag_es: Establecer idioma en __Español__!")
            else:
                await ctx.send(self.bot.text.lang_not_found[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)])


def setup(bot):
    bot.add_cog(Language(bot))
