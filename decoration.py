from discord.ext import commands
from PIL import Image
import discord, io


class Decoration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "current": 0,
                "canvas": [
                    {
                        "name": "canvas1",
                        "data": 10101010101
                    }
                ]
            }

    async def make_image(self, ctx, base_id: int, character_id: int, weapon_id: int, head_id: int, body_id: int, back_id: int):
        base = Image.open(f"./assets/base/{base_id}.png")
        character = Image.open(f"./assets/character/{base_id}/{character_id}.png")
        weapon = Image.open(f"./assets/weapon/{weapon_id}.png")
        head = Image.open(f"./assets/head/{head_id}.png")
        body = Image.open(f"./assets/body/{body_id}.png")
        back = Image.open(f"./assets/back/{back_id}.png")
        base.paste(character, (0, 0), character)
        base.paste(head, (0, 0), head)
        base.paste(body, (0, 0), body)
        base.paste(back, (0, 0), back)
        base.paste(weapon, (0, 0), weapon)
        base = self.convert_to_bytes(base)
        await ctx.send(file=discord.File(fp=io.BytesIO(base), filename="result.png"))
        return

    def convert_to_bytes(self, image):
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    @commands.command()
    async def make(self, ctx, base: int, character: int, weapon: int, head_id: int, body_id: int):
        await self.make_image(ctx, base, character, weapon, head_id, body_id)

    @commands.command()
    async def set(self, ctx, *, item):
        item_list = item.split()
        if len(item_list) == 1 and item.isdigit() and len(str(item)) == 11:
            code, result = self.parse_item_id(item)
            if code == 0:
                return await ctx.send(f"アイテム番号が間違っています.詳細:{result}")
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])

    def parse_item_id(self, item: str):
        if int(item[0:1]) not in [0, 1]:
            return 0, "wrong_base_id"
        if not 0 <= int(item[1:3]) <= 20:
            return 0, "wrong_char_id"
        if not 1 <= int(item[3:5]) <= 34:
            return 0, "wrong_weapon_id"
        if not 1 <= int(item[5:7]) <= 55:
            return 0, "wrong_head_id"
        if not 1 <= int(item[7:9]) <= 61:
            return 0, "wrong_body_id"
        if not 1 <= int(item[9:11]) <= 56:
            return 0, "wrong_back_id"
        return 1, [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]



def setup(bot):
    bot.add_cog(Decoration(bot))

