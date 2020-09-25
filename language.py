from discord.ext import commands
import discord, json
from multilingual import *

class Language(commands.Cog):
    """# TODO:^# TODO:^# TODO:^# TODO:"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open('./assets/emoji_data.json', 'r', encoding="utf-8") as f:
            self.emoji = json.load(f)

    async def cog_before_invoke(self, ctx):
        if self.bot.maintenance and str(ctx.author.id) not in self.bot.ADMIN:
            await ctx.send(["現在BOTはメンテナンス中です。\n理由: {}\n詳しい情報については公式サーバーにてご確認ください。", "BOT is currently under maintenance. \nReason: {}\nPlease check the official server for more information.", "BOT는 현재 점검 중입니다.\n이유 : {}\n자세한 내용은 공식 서버를 확인하십시오.", "BOT se encuentra actualmente en mantenimiento.\nRazón: {}\nConsulte el servidor oficial para obtener más información."][get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.maintenance))
            raise commands.CommandError("maintenance-error")
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(["あなたのアカウントはBANされています(´;ω;｀)\nBANに対する異議申し立ては、公式サーバーの <#{}> にてご対応させていただきます。", "Your account is banned (´; ω;`)\nIf you have an objection to BAN, please use the official server <#{}>.", "당신의 계정은 차단되어 있습니다 ( '; ω;`)\n차단에 대한 이의 신청은 공식 서버 <#{}> 에서 대응하겠습니다.", "Su cuenta está prohibida (´; ω;`)\nSi tiene una objeción a la BAN, utilice <#{}> en el servidor oficial."][get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.datas['appeal_channel']))
            raise commands.CommandError("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0
            }

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(["引数が不足しているよ!\n使い方: `{0}{1}`\n詳しくは `{0}help {1}`", "Not enough arguments! \nUsage: `{0} {1}` \nFor more information `{0}help {1}", "f 인수가 충분하지 않습니다. \n사용법 :`{0} {1}`\n 자세한 내용은`{0}help {1}", "No hay suficientes argumentos. \nUso: {0} {1} \nPara obtener más información, `{0}help {1}"][user_lang].format(self.bot.PREFIX, ctx.command.usage, ctx.command.qualified_name))
        else:
            await ctx.send(["エラーが発生しました。管理者にお尋ねください。\n{}", "An error has occurred. Please ask the BOT administrator.\n{}", "오류가 발생했습니다.관리자에게 문의하십시오.\n{}", "Se ha producido un error. Pregunte al administrador.\n{}"][user_lang].format(error))

    @commands.command(aliases=["lang"])
    async def language(self, ctx):
        # TODO: 修正
        text = ctx.message.content.split()
        if len(text) == 1:
            embed = discord.Embed(title="WELCOME TO MilkCoffee!!")
            embed.description = f"{self.emoji['language']} Select language:"
            embed.add_field(name=f"{self.emoji['region']} Server Region", value="m!lang region")
            embed.add_field(name=":flag_jp: 日本語 Japanese", value="m!lang ja")
            embed.add_field(name=":flag_au: English English", value="m!lang en")
            embed.add_field(name=":flag_kr: 한국어 Korean", value="m!lang ko")
            embed.add_field(name=":flag_es: Español Spanish", value="m!lang es")
            msg_obj = await ctx.send(embed=embed)
            await msg_obj.add_reaction(self.emoji['region'])
            await msg_obj.add_reaction(":flag_jp:")
            await msg_obj.add_reaction(":flag_au:")
            await msg_obj.add_reaction(":flag_kr:")
            await msg_obj.add_reaction(":flag_es:")

            def check(r, u):
                return r.message.id == msg_obj.id and u == ctx.author and str(r.emoji) in [self.emoji['region'], ":flag_jp:", ":flag_au:", ":flag_kr:", ":flag_es:"]
            try:
                reaction, user = self.bot.wait_for("on_reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == self.emoji['region']:
                    self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value
                    await ctx.send(f"{self.emoji['region']} Set language to [Server Region]!")
                elif str(reaction.emoji) == "flag_jp":
                    self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value
                    await ctx.send(":flag_jp: 言語を [日本語] に設定しました!")
                elif str(reaction.emoji) == "flag_au":
                    self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value
                    await ctx.send(":flag_au: Set language to [English]")
                elif str(reaction.emoji) == "flag_kr":
                    self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.KOREAN.value
                    await ctx.send(":flag_kr: 언어를 [한국어] 로 설정했습니다!")
                elif str(reaction.emoji) == "flag_es":
                    self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.SPANISH.value
                    await ctx.send(":flag_es: Establecer idioma en [Español]!")
            except:
                pass
            finally:
                await msg_obj.remove_reaction(self.emoji['region'], self.bot.user)
                await msg_obj.remove_reaction(":flag_jp:", self.bot.user)
                await msg_obj.remove_reaction(":flag_au:", self.bot.user)
                await msg_obj.remove_reaction(":flag_kr:", self.bot.user)
                await msg_obj.remove_reaction(":flag_es:", self.bot.user)
        else:
            lang = text[1].lower()
            if lang in ["region", "server", "guild", "auto", "サーバー", "地域", "サーバー地域", "0"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.REGION.value
                await ctx.send(f"{self.emoji['region']} Set language to [Server Region]!")
            elif lang in ["ja", "jp", "japanese", "jpn", "日本語", "1"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value
                await ctx.send(":flag_jp: 言語を [日本語] に設定しました!")
            elif lang in ["en", "eng", "english", "2"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value
                await ctx.send(":flag_au: Set language to [English]")
            elif lang in ["ko", "kr", "korean", "kor", "한국어", "3"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.KOREAN.value
                await ctx.send(":flag_kr: 언어를 [한국어] 로 설정했습니다!")
            elif lang in ["es", "sp", "spa", "spanish", "Español", "4"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.SPANISH.value
                await ctx.send(":flag_es: Establecer idioma en [Español]!")
            else:
                await ctx.send(["言語が見つかりませんでした。", "The language was not found.", "언어를 찾을 수 없습니다.", "No se encontró el idioma."])

def setup(bot):
    bot.add_cog(Language(bot))

