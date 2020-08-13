from discord.ext import commands
import discord, logging, os

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)


class Bot(commands.Bot):

    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        cogs = ["decoration", "developer"]
        for cog in cogs:
            self.load_extension(cog)

    async def on_ready(self):
        print(f"Logged in to {self.user}")


if __name__ == '__main__':
    bot = Bot(command_prefix="m!")
    bot.run(TOKEN)
