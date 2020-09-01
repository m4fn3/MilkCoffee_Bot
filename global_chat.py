from discord.ext import commands


class GlobalChat(commands.Cog):
    """他のサーバーに居る人と、設定したチャンネルでお話しできます。(現在開発中)"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot


def setup(bot):
    bot.add_cog(GlobalChat(bot))