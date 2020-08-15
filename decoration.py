from discord.ext import commands
from PIL import Image
import cv2, discord, io


class Decoration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    async def make_image(self, ctx, base: int, character: int, weapon: int):
        base = Image.open(f"./assets/base/{base}.png")
        character = Image.open(f"./assets/character/{character}.png")
        weapon = Image.open(f"./assets/weapon/{weapon}.png")
        base.paste(character, (0, 0), character)
        base.paste(weapon, (0, 0), weapon)
        base = self.convert_to_bytes(base)
        await ctx.send(file=discord.File(fp=io.BytesIO(base), filename="result.png"))
        return

    def convert_to_bytes(self, image):
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    @commands.command()
    async def make(self, ctx, base: int, character: int, weapon: int):
        await self.make_image(ctx, base, character, weapon)


def setup(bot):
    bot.add_cog(Decoration(bot))

