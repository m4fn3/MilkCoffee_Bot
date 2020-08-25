from discord.ext import commands
from PIL import Image
from typing import Any
import discord, io, json, re, difflib
from item_parser import *


class Costume(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open('./assets/emoji_data.json', 'r', encoding="utf-8") as f:
            self.emoji = json.load(f)
        with open('./assets/name_data.json', 'r', encoding="utf-8") as f:
            self.name = json.load(f)
        with open('./assets/name_regular_expression.json', 'r', encoding="utf-8") as f:
            self.name_re = json.load(f)
        with open('./assets/item_info.json') as f:
            self.item_info = json.load(f)

    def initialize_user_data(self, user_id: str):
        self.bot.database[user_id] = {
                "canvas": "1O4ZW5",
                "save": []
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
        embed = discord.Embed()
        item_id = parse_item_list_to_code([base_id, character_id, weapon_id, head_id, body_id, back_id])
        text = f"{self.emoji['base'][str(base_id)]} {self.emoji['character'][str(character_id)]} {self.emoji['weapon'][str(weapon_id)]} {self.emoji['head'][str(head_id)]} {self.emoji['body'][str(body_id)]} {self.emoji['back'][str(back_id)]}"#f"装飾コード: {item_id}"
        embed.add_field(name="ベース色", value=f"{base_id} {self.emoji['base'][str(base_id)]} {self.name['base'][str(base_id)]}")
        embed.add_field(name="キャラクター", value=f"{character_id} {self.emoji['character'][str(character_id)]} {self.name['character'][str(character_id)]}")
        embed.add_field(name="武器", value=f"{weapon_id} {self.emoji['weapon'][str(weapon_id)]} {self.name['weapon'][str(weapon_id)]}")
        embed.add_field(name="頭装飾", value=f"{head_id} {self.emoji['head'][str(head_id)]} {self.name['head'][str(head_id)]}")
        embed.add_field(name="体装飾", value=f"{body_id} {self.emoji['body'][str(body_id)]} {self.name['body'][str(body_id)]}")
        embed.add_field(name="背中装飾", value=f"{back_id} {self.emoji['back'][str(back_id)]} {self.name['back'][str(back_id)]}")
        embed.set_footer(text=f"装飾コード: {item_id}", icon_url="http://zorba.starfree.jp/MilkChoco/icon.png")
        await ctx.send(text, embed=embed, file=discord.File(fp=io.BytesIO(base), filename="result.png"))
        return

    def convert_to_bytes(self, image: Image) -> bytes:
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    def save_canvas_data(self, user_id, data: str) -> None:
        self.bot.database[str(user_id)]["canvas"] = data

    @commands.command()
    async def set(self, ctx, *, item):
        item_list = item.split()
        if len(item_list) == 1:
            code, result = check_item_id(item)
            if code == 0:
                return await ctx.send(self.bot.error_text[result])
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_canvas_data(ctx.author.id, parse_item_list_to_code(result))
        else:
            code, result = check_item_list(item_list)
            if code == 0:
                return await ctx.send(self.bot.error_text[result])
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_canvas_data(ctx.author.id, parse_item_list_to_code(result))

    @commands.command()
    async def canvas(self, ctx):
        for cvs in self.bot.database[str(ctx.author.id)]["canvas"]:
            pass

    @commands.command()
    async def show(self, ctx) -> None:
        item_code = self.bot.database[str(ctx.author.id)]["canvas"]
        items = parse_item_code_to_list(item_code)
        await self.make_image(ctx, items[0], items[1], items[2], items[3], items[4], items[5])

    @commands.command()
    async def save(self, ctx):
        name: str
        listed = ctx.message.content.split(" ", 1)
        if len(self.bot.database[str(ctx.author.id)]["save"]) == 20:
            return await ctx.send("保存できるのは20個までです. 不要なものを削除してから保存して下さい!")
        used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["save"]]
        if len(listed) == 1:
            count = 1
            while True:
                if f"無題{count}" not in used_name_list:
                    name = f"無題{count}"
                    break
                count += 1
        else:
            if listed[1] in used_name_list:
                return await ctx.send("この名前は既に使用しています。")
            elif len(listed[1]) < 1 or 20 < len(listed[1]):
                return await ctx.send("名称は1文字以上20文字以下で指定して下さい.")
            name = listed[1]
        self.bot.database[str(ctx.author.id)]["save"].append(
            {
                "name": name,
                "data": self.bot.database[str(ctx.author.id)]["canvas"]
            }
        )
        await ctx.send(f"保存しました. 名称: '{name}'")

    @commands.command()
    async def list(self, ctx):
        listed = ctx.message.content.split()
        page: int
        if len(listed) == 1:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 4:
            page = int(listed[1])
        elif listed[1].isdigit():
            await ctx.send("ページ数は1~4で指定してください!")
        else:
            await ctx.send("ページ数は整数で1~4で指定してください!")
        item_count = len(self.bot.database[str(ctx.author.id)]["save"])
        embed = discord.Embed(title=f"保存した作品集 ({page} / 4 ページ)")
        for index in range(page*5-4, page*5+1):  # 1-5 6-10 11-15 16-20
            if index > (item_count - 1):
                break
            item_id = self.bot.database[str(ctx.author.id)]["save"][index-1]["data"]
            item_list = parse_item_code_to_list(item_id)
            text = f"{item_id}  {self.emoji['base'][str(item_list[0])]} {self.emoji['character'][str(item_list[1])]} {self.emoji['weapon'][str(item_list[2])]} {self.emoji['head'][str(item_list[3])]} {self.emoji['body'][str(item_list[4])]} {self.emoji['back'][str(item_list[5])]}"
            embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['save'][index-1]['name']}", value=text, inline=False)
        await ctx.send(embed=embed)

    # TODO: show関数に保存したものを表示する機能
    # TODO: 保存したものを読み込むもの load
    # TODO: 保存したものをさくじょするもの delete/remove

    def find_item(self, item_name: str, index=False, item_type="") -> (int, Any):
        type_list: list
        if index and item_name.isdigit():
            if self.item_info[item_type]["min"] <= int(item_name) <= self.item_info[item_type]["max"]:
                return 1, [item_type, item_name]
            else:
                return 0, "wrong_item_index"
        elif index:
            type_list = [item_type]
        else:
            type_list = [type_name for type_name in self.name_re]
        match_per = -1
        item_info = []
        for i in type_list:
            for j in self.name_re[i]:
                match_obj = re.search(self.name_re[i][j], item_name, re.IGNORECASE)
                if match_obj is not None:
                    diff_per = difflib.SequenceMatcher(None, self.name[i][j].lower(), match_obj.group()).ratio()
                    if diff_per > match_per:
                        match_per = diff_per
                        item_info = [i, j]
        if match_per == -1:
            return 0, "no_match"
        else:
            return 1, item_info

    @commands.command()
    async def item(self, ctx, *, text):
        code, result = self.find_item(text)
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])



def setup(bot):
    bot.add_cog(Costume(bot))


# TODO: ランダムで作成する機能を追加
