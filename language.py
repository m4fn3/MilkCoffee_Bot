from discord.ext import commands
from multilingual import *

class Language(commands.Cog):
    """# TODO:^# TODO:^# TODO:^# TODO:"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

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
            pass
            # 言語リスト
        else:
            lang = text[1].lower()
            if lang in ["ja", "jp", "japanese", "jpn", "日本語"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value
            elif lang in ["en", "eng", "english"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value
            elif lang in ["ko", "kr", "korean", "kor", "한국어"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.KOREAN.value
            elif lang in ["es", "sp", "spa", "spanish", "Español"]:
                self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.SPANISH.value
            else:
                await ctx.send("言語が見つかりませんでした。")

def setup(bot):
    bot.add_cog(Language(bot))

