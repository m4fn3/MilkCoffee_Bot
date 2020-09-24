from discord.ext import commands
from multilingual import *

class Language(commands.Cog):
    """lang_emoji"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    async def cog_before_invoke(self, ctx):
        if self.bot.maintenance and str(ctx.author.id) not in self.bot.ADMIN:
            await ctx.send(["現在BOTはメンテナンス中です。\n理由: {}\n詳しい情報については公式サーバーにてご確認ください。", "BOT is currently under maintenance. \nReason: {}\nPlease check the official server for more information.", "BOT는 현재 점검 중입니다.\n이유 : {}\n자세한 내용은 공식 서버를 확인하십시오.", "BOT se encuentra actualmente en mantenimiento.\nRazón: {}\nConsulte el servidor oficial para obtener más información."][get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.maintenance))
            raise commands.CommandError("maintenance-error")
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(["あなたのアカウントはBANされています(´;ω;｀)\nBANに対する異議申し立ては、公式サーバーの <#{}> にてご対応させていただきます。", "Your account is banned (´; ω;`)\nIf you have an objection to BAN, please use the official server <#{}>.", "당신의 계정은 차단되어 있습니다 ( '; ω;`)\n차단에 대한 이의 신청은 공식 서버 <#{}> 에서 대응하겠습니다.", "Su cuenta está prohibida (´; ω;`)\nSi tiene una objeción a la BAN, utilice <#{}> en el servidor oficial."][get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.datas['appeal_channel']))
            raise commands.CommandError("Your Account Banned")

    @commands.command(aliases=["lang"])
    async def language(self, ctx):
        text = ctx.message.content.split()
        if len(text) == 1:
            pass
            # 言語リスト
        else:
            lang = text[1].lower()
            if lang in ["ja", "jp", "japanese", "jpn", "日本語"]:
                LanguageCode.JAPANESE
            elif lang in ["en", "eng", "english"]:
                LanguageCode.ENGLISH
            elif lang in ["ko", "kr", "korean", "kor", "한국어"]:
                LanguageCode.KOREAN
            elif lang in ["es", "sp", "spa", "spanish", "Español"]:
                LanguageCode.SPANISH
            else:
                await ctx.send("言語が見つかりませんでした。")

def setup(bot):
    bot.add_cog(Language(bot))

