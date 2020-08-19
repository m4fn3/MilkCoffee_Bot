from discord.ext import commands
from PIL import Image
from typing import Any
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
                        "data": "10101010101"
                    }
                ]
            }

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
            code, result = self.check_item_id(item)
            if code == 0:
                return await ctx.send(f"アイテム番号が間違っています.詳細:{result}")
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_data_to_database(ctx.author.id, self.parse_item_list_to_code(result))
        else:
            code, result = self.check_item_list(item_list)
            if code == 0:
                return await ctx.send(f"アイテム番号が間違っています.詳細:{result}")
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_data_to_database(ctx.author.id, item)

    @commands.command()
    async def show(self, ctx) -> None:
        current = self.bot.database[str(ctx.author.id)]["current"]
        item_code = self.bot.database[str(ctx.author.id)]["canvas"][current]["data"]
        items = self.parse_item_code_to_list(item_code)
        await self.make_image(ctx, items[0], items[1], items[2], items[3], items[4], items[5])

    # TODO: ランダムで作成する機能を追加

    # TODO: 別クラスに分離
    def check_item_id(self, item: str) -> (int, Any):
        """ 装飾コードのリストの形式を確認して、装飾コードのリストを返す """
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

    def check_item_list(self, item: list) -> (int, Any):
        """ 装飾コードの形式を確認して、装飾コードのリストに変換 """
        if len(item) != 6:
            return 0, "missing_required_arguments"
        if not item[0].isdigit() and int(item[0]) in [0, 1]:
            return 0, "wrong_base_id"
        if not item[1].isdigit() and 0 <= int(item[1]) <= 20:
            return 0, "wrong_char_id"
        if not item[2].isdigit() and 1 <= int(item[2]) <= 34:
            return 0, "wrong_weapon_id"
        if not item[3].isdigit() and 1 <= int(item[3]) <= 55:
            return 0, "wrong_head_id"
        if not item[4].isdigit() and 1 <= int(item[4]) <= 61:
            return 0, "wrong_body_id"
        if not item[5].isdigit() and 1 <= int(item[5]) <= 56:
            return 0, "wrong_back_id"
        return 1, [int(item[0]), int(item[1]), int(item[2]), int(item[3]), int(item[4]), int(item[5])]

    def parse_item_list_to_code(self, item: list) -> str:
        return f"{item[0]}{item[1]}{item[2]}{item[3]}{item[4]}{item[5]}"

    def parse_item_code_to_list(self, item: str) -> list:
        return [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]


def setup(bot):
    bot.add_cog(Decoration(bot))

