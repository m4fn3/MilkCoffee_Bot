import datetime
import time

import asyncio
import discord
from discord.ext import commands

from .data.command_data import CmdData
from .milkcoffee import MilkCoffee
from .utils.messenger import error_embed
from .utils.multilingual import *

cmd_data = CmdData()


class Bot(commands.Cog):
    """色々な情報の設定をします^For various information!^다양한 정보를 설정하는것입니다!^¡Estableceré diversa información!"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await error_embed(ctx, self.bot.text.your_account_banned[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.static_data.appeal_channel))
            raise Exception("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0
            }
            await self.bot.get_cog("Bot").language_selector(ctx)

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    @commands.command(aliases=["inv"], usage=cmd_data.invite.usage, description=cmd_data.invite.description)
    async def invite(self, ctx):
        text = self.bot.text.invite_links[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(
            self.bot.static_data.invite, self.bot.static_data.server)
        await ctx.send(text)

    @commands.command(aliases=["about"], usage=cmd_data.info.usage, description=cmd_data.info.description)
    async def info(self, ctx):
        td = datetime.timedelta(seconds=int(time.time() - self.bot.uptime))
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        d = td.days
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        embed = discord.Embed(title=["このBOTについて", "About this BOT", "봇 정보", "Acerca de este BOT"][user_lang])
        embed.description = [
            "BOTをご使用いただき、ありがとうございます！\nこのBOTはMilkChocoをプレイする人達の、Discordサーバーのために `{0}` によって作成されました。\n詳しい使い方は `{1}help` で確認して下さい。\n機能リクエストにもできる限り、ご対応させていただきます!",
            "Thank you for using BOT!\nThis BOT was created by `{0}` for the Discord server of MilkChoco players.\nFor detailed usage, see `{1}help`\nWe will respond to function requests as much as possible!",
            "봇을 사용해 주셔서 감사합니다!\n이 봇은 밀크초코를 플레이하는 사람들의 디스코드 서버의 `{0}` 에 의해 작성되었습니다.\n자세한 사용법은 `{1}help` 에서 확인하십시오.\n기능 추가에도 가능한 한 대응하겠습니다!",
            "¡Gracias por usar BOT! \nEste BOT fue creado por `{0}` para el servidor de Discord de aquellos que juegan Milk Choco.\nPara obtener detalles sobre cómo usarlo, consulte `{1}help`.\n¡Responderemos a las solicitudes de funciones tanto como sea posible!"
        ][user_lang].format(self.bot.get_user(self.bot.static_data.author), self.bot.PREFIX)
        embed.add_field(name=["ステータス", "status", "상태", "estado"][user_lang],
                        value=["```導入サーバー数: {0}\nBOTが認識しているユーザー数:{1}```", "```Number of installed servers: {0}\nNumber of users recognized by BOT: {1}```", "```도입 서버 수 : {0}\nBOT가 인식하고있는 사용자 수 : {1}```", "```Número de servidores instalados: {0}\nNúmero de usuarios reconocidos por BOT: {1} ```"][user_lang].format(len(self.bot.guilds), len(self.bot.users)), inline=False)
        embed.add_field(name=["稼働時間", "uptime", "가동 시간", "uptime"][user_lang], value=["{0}日 {1}時間 {2}分 {3}秒", "{0} days {1} hours {2} minutes {3} seconds", "{0} 일 {1} 시간 {2} 분 {3} 초", "{0} días {1} horas {2} minutos {3} segundos"][user_lang].format(d, h, m, s), inline=False)
        embed.add_field(name=["各種URL", "URLs", "각종 URL", "URLs"][user_lang],
                        value=["[BOT招待用URL]({0}) | [サポート用サーバー]({1}) | [公式サイト]({2})", "[BOT invitation URL]({0}) | [Support server]({1}) | [Official Site]({2}) ", "[봇 초대 링크]({0}) | [지원용 서버]({1}) | [공식 사이트]({2})", "[URL de invitación BOT]({0}) | [Servidor de asistencia]({1}) | [Sitio oficial]({2}) "][user_lang].format(self.bot.static_data.invite, self.bot.static_data.server, self.bot.static_data.web),
                        inline=False)
        await ctx.send(embed=embed)

    async def language_selector(self, ctx):
        embed = discord.Embed(title=f"{self.bot.data.emoji.language} Select language:")
        embed.add_field(name=f"{self.bot.data.emoji.region} Server Region", value="m!lang region")
        embed.add_field(name=":flag_jp: 日本語 Japanese", value="m!lang ja")
        embed.add_field(name=":flag_au: English English", value="m!lang en")
        embed.add_field(name=":flag_kr: 한국어 Korean", value="m!lang ko")
        embed.add_field(name=":flag_es: Español Spanish", value="m!lang es")
        msg_obj = await ctx.send(ctx.author.mention, embed=embed)
        await msg_obj.add_reaction(self.bot.data.emoji.region)
        await msg_obj.add_reaction("🇯🇵")
        await msg_obj.add_reaction("🇦🇺")
        await msg_obj.add_reaction("🇰🇷")
        await msg_obj.add_reaction("🇪🇸")

        def check(r, u):
            return r.message.id == msg_obj.id and u == ctx.author and str(r.emoji) in [self.bot.data.emoji.region, "🇯🇵", "🇦🇺", "🇰🇷", "🇪🇸"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
            print(str(reaction.emoji))
            if str(reaction.emoji) == self.bot.data.emoji.region:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value
                await ctx.send(f"{self.bot.data.emoji.region} Set language to [Server Region]!")
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
            await msg_obj.remove_reaction(self.bot.data.emoji.region, self.bot.user)
            await msg_obj.remove_reaction("🇯🇵", self.bot.user)
            await msg_obj.remove_reaction("🇦🇺", self.bot.user)
            await msg_obj.remove_reaction("🇰🇷", self.bot.user)
            await msg_obj.remove_reaction("🇪🇸", self.bot.user)

    @commands.command(aliases=["lang"], usage=cmd_data.language.usage, description=cmd_data.language.description)
    async def language(self, ctx):
        text = ctx.message.content.split()
        if len(text) == 1:
            await self.language_selector(ctx)
        else:
            lang = text[1].lower()
            if lang in ["region", "server", "guild", "auto", "サーバー", "地域", "サーバー地域", "0"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value
                await ctx.send(f"{self.bot.data.emoji.region} Set language to [Server Region]!")
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
    bot.add_cog(Bot(bot))
