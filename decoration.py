from discord.ext import commands
import discord


class Decoration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot


def setup(bot):
    bot.add_cog(Decoration(bot))
