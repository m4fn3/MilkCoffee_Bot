import asyncio
import difflib
import io
import random
import re
from typing import Any

import discord
import traceback2
from PIL import Image
from discord.ext import commands

from .milkcoffee import MilkCoffee
from .data.item_data import ItemData
from .utils.item_parser import *
from .utils.messenger import error_embed, success_embed, normal_embed
from .utils.multilingual import *
from .menu import Menu
from .data.command_data import CmdData

cmd_data = CmdData()

class Costume(commands.Cog):
    """装飾シミュレータを操作できるよ！好みの組合せを探そう！^You can operate the costume simulator! Find your favorite combination!^코스튬 시뮬레이터를 조작 할 수 있어! 원하는 조합을 찾자!^¡Bienvenido al simulador de drisfraces!"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee
        self.menu_channels = set()
        self.menu_users = set()

    def find_item(self, item_name: str, index=False, item_type="") -> (int, Any):
        """
        アイテムをアイテムリストから名前または番号で取得
        Args:
            item_name (str): アイテムの名称または番号
            index (bool): 種類を指定しているかどうか
            item_type (str): アイテムの種類

        Returns:
            int, Any:
             0 ... 異常発生, エラーコード (str)
             1 ... 正常, [種類, 番号]　(list)
        """
        type_list: list
        if index and item_name.isdigit():
            if getattr(self.bot.data, item_type).min <= int(item_name) <= getattr(self.bot.data, item_type).max:
                return 1, [item_type, item_name]
            else:
                return 0, self.bot.text.wrong_item_index
        elif index:
            type_list = [item_type]
        else:
            type_list = [type_name for type_name in self.bot.data.regex]
        match_per = -1
        item_info = []
        for i in type_list:
            for j in self.bot.data.regex[i]:
                match_obj = re.search(self.bot.data.regex[i][j], item_name, re.IGNORECASE)
                if match_obj is not None:
                    diff_per = difflib.SequenceMatcher(None, getattr(getattr(self.bot.data, i).name, "n" + str(j)).lower(), match_obj.group()).ratio()
                    if diff_per > match_per:
                        match_per = diff_per
                        item_info = [i, j]
        if match_per == -1:
            return 0, self.bot.text.item_not_found
        else:
            return 1, item_info

    def convert_to_bytes(self, image: Image) -> bytes:
        """
        imageオブジェクトをbyteに変換
        Args:
            image: 変換したいImageオブジェクト

        Returns:
            bytes: 画像のバイト
        """
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    def save_canvas_data(self, user_id, data: str) -> None:
        # TODO: db
        """
        canvasのデータを保存
        Args:
            user_id : ユーザーID
            data (str): 装飾コード

        Returns:
            None
        """
        self.bot.database[str(user_id)]["costume"]["canvas"] = data

    def get_list(self, item_type: str, page: int) -> str:
        """指定した種類のアイテムリストテキストを生成"""
        item_count = getattr(self.bot.data, item_type).max
        text = ""
        start_index = getattr(self.bot.data, item_type).min + 10 * (page - 1)
        for item_index in range(start_index, start_index + 10):
            if item_index > item_count:
                break
            emoji = getattr(getattr(self.bot.data, item_type).emoji, "e" + str(item_index))
            name = getattr(getattr(self.bot.data, item_type).name, "n" + str(item_index))
            text += f"`{str(item_index).rjust(3)}` {emoji} {name}\n"
        return text

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await error_embed(ctx, self.bot.text.your_account_banned[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.static_data.appeal_channel))
            raise Exception("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0,
                "costume": {
                    "canvas": "1o4s3k",
                    "save": []
                }
            }
            await self.bot.get_cog("Bot").language_selector(ctx)
            await self.process_new_user(ctx.message)
        elif "costume" not in self.bot.database[str(ctx.author.id)]:
            self.bot.database[str(ctx.author.id)]["costume"] = {
                "canvas": "1o4s3k",
                "save": []
            }
            await self.process_new_user(ctx.message)

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    async def process_new_user(self, message):
        user_lang = get_lg(self.bot.database[str(message.author.id)]["language"], message.guild.region)
        embed = discord.Embed(title=self.bot.text.welcome_to_costume_title[user_lang], color=0x00ffff)
        embed.description = self.bot.text.welcome_to_costume_description[user_lang].format(self.bot.PREFIX)
        await message.channel.send(message.author.mention, embed=embed)

    @commands.command(aliases=["m"], usage=cmd_data.menu.usage, description=cmd_data.menu.description)
    async def menu(self, ctx):
        try:
            if ctx.author.id in self.menu_users:
                return await error_embed(ctx, "あなたは既にメニューを実行中です！既存のメニューを閉じてから再実行してね!")
            elif ctx.channel.id in self.menu_channels:
                return await error_embed(ctx, "このチャンネルでは,現在他の人がメニューを実行中です!他のチャンネルで再実行してね!")
            self.menu_users.add(ctx.author.id)
            self.menu_channels.add(ctx.channel.id)
            code = "41ihuiq3m"  # TODO: ユーザーの作業場の装飾コードで初期化 - db
            user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
            menu = Menu(ctx, self.bot, user_lang, code)
            await menu.run()
            self.menu_users.remove(ctx.author.id)
            self.menu_channels.remove(ctx.channel.id)
        except:
            print(traceback2.format_exc())

    @commands.command(usage=cmd_data.set.usage, description=cmd_data.set.description, help=cmd_data.set.help)
    async def set(self, ctx, *, item) -> None:
        """
        装飾コードまたは各装飾の番号から全種類のアイテムを一括で登録
        Args:
            ctx: Context
            item: 装飾コード or 各装飾の番号

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        item_list = item.split()
        if len(item_list) == 1:
            code, result = check_item_id(item)
            if code == 0:
                return await error_embed(ctx, result[user_lang])
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_canvas_data(ctx.author.id, parse_item_list_to_code(result))
        else:
            code, result = check_item_list(item_list)
            if code == 0:
                return await error_embed(ctx, result[user_lang])
            await self.make_image(ctx, result[0], result[1], result[2], result[3], result[4], result[5])
            self.save_canvas_data(ctx.author.id, parse_item_list_to_code(result))

    @commands.command(aliases=["mylist"], usage=cmd_data.my.usage, description=cmd_data.my.description)
    async def my(self, ctx) -> None:
        """
        保存した作品を表示
        Args:
            ctx: Context

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        listed = ctx.message.content.split()
        page_length = 4
        page: int
        if len(listed) == 1:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 4:
            page = int(listed[1])
        elif listed[1].isdigit():
            return await error_embed(ctx, self.bot.text.page_number_between[user_lang].format(page_length))
        else:
            return await error_embed(ctx, self.bot.text.page_number_integer_between[user_lang].format(page_length))
        item_count = len(self.bot.database[str(ctx.author.id)]["costume"]["save"])
        embed = discord.Embed(title=self.bot.text.my_title[user_lang].format(page))
        embed.description = self.bot.text.my_description[user_lang]
        for index in range(page * 5 - 4, page * 5 + 1):  # 1-5 6-10 11-15 16-20
            if index > item_count:
                break
            item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["static_data"]
            item_list = parse_item_code_to_list(item_id)
            text = f"{item_id}  {self.emoji['base'][str(item_list[0])]} {self.emoji['character'][str(item_list[1])]} {self.emoji['weapon'][str(item_list[2])]} {self.emoji['head'][str(item_list[3])]} {self.emoji['body'][str(item_list[4])]} {self.emoji['back'][str(item_list[5])]}"
            embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['costume']['save'][index - 1]['name']}", value=text, inline=False)
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 4, page)
            if code == 0:
                break
            page = new_page
            embed = discord.Embed(title=self.bot.text.my_title[user_lang].format(page))
            embed.description = self.bot.text.my_description[user_lang]
            for index in range(page * 5 - 4, page * 5 + 1):  # 1-5 6-10 11-15 16-20
                if index > item_count:
                    break
                item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["static_data"]
                item_list = parse_item_code_to_list(item_id)
                text = f"{item_id}  {self.emoji['base'][str(item_list[0])]} {self.emoji['character'][str(item_list[1])]} {self.emoji['weapon'][str(item_list[2])]} {self.emoji['head'][str(item_list[3])]} {self.emoji['body'][str(item_list[4])]} {self.emoji['back'][str(item_list[5])]}"
                embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['costume']['save'][index - 1]['name']}", value=text, inline=False)
            await message.edit(embed=embed)

    @commands.command(aliases=["remove", "del", "rm"], usage=cmd_data.delete.usage, description=cmd_data.delete.description)
    async def delete(self, ctx, *, index) -> None:
        """
        保存した画像を削除
        Args:
            ctx: Context
            index: 保存番号 or 保存名称

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if index.isdigit() and 1 <= int(index) <= 20:
            item_count = len(self.bot.database[str(ctx.author.id)]["costume"]["save"])
            if 0 <= int(index) <= item_count:
                old_data = self.bot.database[str(ctx.author.id)]["costume"]["save"].pop(int(index) - 1)
                await success_embed(ctx, self.bot.text.deleted_work[user_lang].format(index, old_data["name"]))
            else:
                await error_embed(ctx, self.bot.text.not_found_with_number[user_lang].format(index))
        elif index.isdigit():
            await error_embed(ctx, self.bot.text.specify_between_1_20[user_lang])
        else:
            used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
            if index in used_name_list:
                item_index = used_name_list.index(index)
                old_data = self.bot.database[str(ctx.author.id)]["costume"]["save"].pop(item_index)
                await success_embed(ctx, self.bot.text.deleted_work[user_lang].format(item_index + 1, old_data["name"]))

            else:
                await error_embed(ctx, self.bot.text.not_found_with_name[user_lang])

    @commands.command(usage=cmd_data.random.usage, description=cmd_data.random.description)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def random(self, ctx):
        num_base = random.randint(self.bot.data.base.min, self.bot.data.base.max)
        num_character = random.randint(self.bot.data.character.min, self.bot.data.character.max)
        num_weapon = random.randint(self.bot.data.weapon.min, self.bot.data.weapon.max)
        num_head = random.randint(self.bot.data.head.min, self.bot.data.head.max)
        num_body = random.randint(self.bot.data.body.min, self.bot.data.body.max)
        num_back = random.randint(self.bot.data.back.min, self.bot.data.back.max)
        await self.make_image(ctx, num_base, num_character, num_weapon, num_head, num_body, num_back)


def setup(bot):
    bot.add_cog(Costume(bot))
