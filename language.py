from discord.ext import commands
from multilingual import *

class Language(commands.Cog):
    """lang_emoji"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

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

