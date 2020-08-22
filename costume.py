from discord.ext import commands
from PIL import Image
from typing import Any
import discord, io, json
from item_parser import *


class Costume(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open('./assets/emoji_data.json', 'r') as f:
            self.emoji = json.load(f)

    def initialize_user_data(self, user_id: str):
        self.bot.database[user_id] = {
                "current": 0,
                "canvas": [
                    {
                        "name": "canvas1",
                        "data": "10101010101"
                    }
                ]
            }

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) not in self.bot.database:
            self.initialize_user_data(str(ctx.author.id))

    async def make_image(self, ctx, base_id: int, character_id: int, weapon_id: int, head_id: int, body_id: int, back_id: int) -> None:
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

    def convert_to_bytes(self, image: Image) -> bytes:
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    def save_data_to_database(self, user_id, data: str) -> None:
        current = self.bot.database[str(user_id)]["current"]
        self.bot.database[str(user_id)]["canvas"][current]["data"] = data

    @commands.command()
    async def set(self, ctx, *, item):
        item_list = item.split()
        if len(item_list) == 1 and item.isdigit() and len(str(item)) == 11:
            code, result = check_item_id(item)
            if code == 0:
                return await ctx.send(self.bot.error_text[result])
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_data_to_database(ctx.author.id, parse_item_list_to_code(result))
        else:
            code, result = check_item_list(item_list)
            if code == 0:
                return await ctx.send(self.bot.error_text[result])
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_data_to_database(ctx.author.id, item)

    @commands.command()
    async def canvas(self, ctx):
        for cvs in self.bot.database[str(ctx.author.id)]["canvas"]:
            pass

    @commands.command()
    async def show(self, ctx) -> None:
        current = self.bot.database[str(ctx.author.id)]["current"]
        item_code = self.bot.database[str(ctx.author.id)]["canvas"][current]["data"]
        items = parse_item_code_to_list(item_code)
        await self.make_image(ctx, items[0], items[1], items[2], items[3], items[4], items[5])

    # TODO: ランダムで作成する機能を追加



def setup(bot):
    bot.add_cog(Costume(bot))
