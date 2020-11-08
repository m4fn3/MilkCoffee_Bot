import difflib
import io
import random
import re
from typing import Any

import asyncio
import discord
import traceback2
from PIL import Image
from discord.ext import commands

from .utils.item_parser import *

from .data.command_data import CmdData
from .menu import Menu
from .milkcoffee import MilkCoffee
from .utils.messenger import error_embed, success_embed
from .utils.multilingual import *

cmd_data = CmdData()


class Costume(commands.Cog):
    """装飾シミュレータを操作できます^Operate the costume simulator^코의상 시뮬레이터 작동^Operar el simulador de vestuario"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee
        self.menu_channels = set()
        self.menu_users = set()

    def find_item(self, item_name: str, index=False, item_type="") -> (int, Any):
        """アイテムを名前または番号で検索"""
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
        """imageオブジェクトをbyteに変換"""
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    def save_canvas_data(self, user_id, data: str) -> None:
        # TODO: db
        """ canvasのデータを保存 """
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

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    async def make_image(self, ctx, base_id: int, character_id: int, weapon_id: int, head_id: int, body_id: int, back_id: int) -> None:
        """ アイテム番号から画像を構築 """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        base = Image.open(f"./Assets/base/{base_id}.png")
        character = Image.open(f"./Assets/character/{base_id}/{character_id}.png")
        weapon = Image.open(f"./Assets/weapon/{weapon_id}.png")
        head_img = Image.open(f"./Assets/head/{head_id}.png")
        body_img = Image.open(f"./Assets/body/{body_id}.png")
        back_img = Image.open(f"./Assets/back/{back_id}.png")
        base.paste(character, (0, 0), character)
        base.paste(head_img, (0, 0), head_img)
        base.paste(body_img, (0, 0), body_img)
        base.paste(back_img, (0, 0), back_img)
        base.paste(weapon, (0, 0), weapon)
        base = self.convert_to_bytes(base)
        embed = discord.Embed(color=0x9effce)
        code = list_to_code([base_id, character_id, weapon_id, head_id, body_id, back_id])
        desc = self.bot.data.emoji.num + " " + self.bot.text.menu_code[user_lang] + ": `" + code + "`\n"
        desc += self.bot.data.emoji.base + " " + self.bot.text.menu_base[user_lang] + f"{str(base_id).rjust(3)}` {getattr(self.bot.data.base.emoji, 'e' + str(base_id))} {getattr(self.bot.data.base.name, 'n' + str(base_id))}\n"
        desc += self.bot.data.emoji.char + " " + self.bot.text.menu_character[user_lang] + f"{str(character_id).rjust(3)}` {getattr(self.bot.data.character.emoji, 'e' + str(character_id))} {getattr(self.bot.data.character.name, 'n' + str(character_id))}\n"
        desc += self.bot.data.emoji.weapon + " " + self.bot.text.menu_weapon[user_lang] + f"{str(weapon_id).rjust(3)}` {getattr(self.bot.data.weapon.emoji, 'e' + str(weapon_id))} {getattr(self.bot.data.weapon.name, 'n' + str(weapon_id))}\n"
        desc += self.bot.data.emoji.head + " " + self.bot.text.menu_head[user_lang] + f"{str(head_id).rjust(3)}` {getattr(self.bot.data.head.emoji, 'e' + str(head_id))} {getattr(self.bot.data.head.name, 'n' + str(head_id))}\n"
        desc += self.bot.data.emoji.body + " " + self.bot.text.menu_body[user_lang] + f"{str(body_id).rjust(3)}` {getattr(self.bot.data.body.emoji, 'e' + str(body_id))} {getattr(self.bot.data.body.name, 'n' + str(body_id))}\n"
        desc += self.bot.data.emoji.back + " " + self.bot.text.menu_back[user_lang] + f"{str(back_id).rjust(3)}` {getattr(self.bot.data.back.emoji, 'e' + str(back_id))} {getattr(self.bot.data.back.name, 'n' + str(back_id))}\n"
        embed.description = desc
        await ctx.send(embed=embed, file=discord.File(fp=io.BytesIO(base), filename=f"{code}.png"))

    async def page_reaction_mover(self, message, author: int, max_page: int, now_page: int) -> (int, Any):
        """ リアクションページ移動処理 """
        new_page: int
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=lambda r, u: r.message.id == message.id and u == author and str(r.emoji) in ["◀️", "▶️"])
            if str(reaction.emoji) == "▶️":
                if now_page == max_page:
                    new_page = 1
                else:
                    new_page = now_page + 1
            elif str(reaction.emoji) == "◀️":
                if now_page == 1:
                    new_page = max_page
                else:
                    new_page = now_page - 1
            else:
                new_page = now_page
            return 1, new_page
        except asyncio.TimeoutError:
            await message.remove_reaction("◀️", self.bot.user)
            await message.remove_reaction("▶️", self.bot.user)
            return 0, None

    @commands.command(aliases=["m"], usage=cmd_data.menu.usage, description=cmd_data.menu.description, brief=cmd_data.menu.brief)
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

    @commands.command(usage=cmd_data.random.usage, description=cmd_data.random.description, brief=cmd_data.random.brief)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def random(self, ctx):
        num_base = random.randint(self.bot.data.base.min, self.bot.data.base.max)
        num_character = random.randint(self.bot.data.character.min, self.bot.data.character.max)
        num_weapon = random.randint(self.bot.data.weapon.min, self.bot.data.weapon.max)
        num_head = random.randint(self.bot.data.head.min, self.bot.data.head.max)
        num_body = random.randint(self.bot.data.body.min, self.bot.data.body.max)
        num_back = random.randint(self.bot.data.back.min, self.bot.data.back.max)
        await self.make_image(ctx, num_base, num_character, num_weapon, num_head, num_body, num_back)

    @commands.command(aliases=["mylist"], usage=cmd_data.my.usage, description=cmd_data.my.description, brief=cmd_data.my.brief)
    async def my(self, ctx) -> None:
        """ 保存した作品を表示 """
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
            item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["data"]
            item_list = code_to_list(item_id)
            getattr(self.bot.data.base.emoji, 'e'+str(item_list[0]))
            text = f"{item_id}  {getattr(self.bot.data.base.emoji, 'e'+str(item_list[0]))} {getattr(self.bot.data.character.emoji, 'e'+str(item_list[1]))} {getattr(self.bot.data.weapon.emoji, 'e'+str(item_list[2]))} {getattr(self.bot.data.head.emoji, 'e'+str(item_list[3]))} {getattr(self.bot.data.body.emoji, 'e'+str(item_list[4]))} {getattr(self.bot.data.back.emoji, 'e'+str(item_list[5]))}"
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
                item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["data"]
                item_list = code_to_list(item_id)
                text = f"{item_id}  {getattr(self.bot.data.base.emoji, 'e'+str(item_list[0]))} {getattr(self.bot.data.character.emoji, 'e'+str(item_list[1]))} {getattr(self.bot.data.weapon.emoji, 'e'+str(item_list[2]))} {getattr(self.bot.data.head.emoji, 'e'+str(item_list[3]))} {getattr(self.bot.data.body.emoji, 'e'+str(item_list[4]))} {getattr(self.bot.data.back.emoji, 'e'+str(item_list[5]))}"
                embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['costume']['save'][index - 1]['name']}", value=text, inline=False)
            await message.edit(embed=embed)

    @commands.command(aliases=["remove", "del", "rm"], usage=cmd_data.delete.usage, description=cmd_data.delete.description, brief=cmd_data.delete.brief)
    async def delete(self, ctx, *, index) -> None:
        """ 保存した画像を削除 """
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

    @commands.command(usage=cmd_data.load.usage, description=cmd_data.load.description, bried=cmd_data.load.brief)
    async def load(self, ctx, *, index: str) -> None:
        """ 保存された作品を作業場に読み込む """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        item_index: int
        if index.isdigit() and 1 <= int(index) <= 20:
            item_count = len(self.bot.database[str(ctx.author.id)]["costume"]["save"])
            if 0 <= int(index) <= item_count:
                item_index = int(index) - 1
            else:
                return await error_embed(ctx, self.bot.text.no_th_saved_work[user_lang].format(index))
        elif index.isdigit():
            return await error_embed(ctx, self.bot.text.specify_between_1_20[user_lang])
        else:
            used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
            if index in used_name_list:
                item_index = used_name_list.index(index)
            else:
                return await error_embed(ctx, self.bot.text.not_found_with_name[user_lang])
        self.bot.database[str(ctx.author.id)]["costume"]["canvas"] = self.bot.database[str(ctx.author.id)]["costume"]["save"][item_index]["data"]
        await success_embed(ctx, self.bot.text.loaded_work[user_lang].format(item_index + 1, self.bot.database[str(ctx.author.id)]['costume']['save'][item_index]['name']))

    @commands.command(usage=cmd_data.save.usage, description=cmd_data.save.description, brief=cmd_data.save.brief)
    async def save(self, ctx) -> None:
        """
        現在の装飾を保存
        Args:
            ctx: Context
        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        name: str
        listed = ctx.message.content.split(" ", 1)
        if len(self.bot.database[str(ctx.author.id)]["costume"]["save"]) == 20:
            return await error_embed(ctx, self.bot.text.save_up_to_20[user_lang])
        used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
        if len(listed) == 1:
            count = 1
            while True:
                if f"Untitled{count}" not in used_name_list:
                    name = f"Untitled{count}"
                    break
                count += 1
        else:
            if listed[1].isdigit():
                return await error_embed(ctx, self.bot.text.int_only_name_not_allowed[user_lang])
            elif listed[1] in used_name_list:
                return await error_embed(ctx, self.bot.text.name_already_used[user_lang])
            elif len(listed[1]) < 1 or 20 < len(listed[1]):
                return await error_embed(ctx, self.bot.text.name_length_between_1_20[user_lang])
            name = listed[1]
        self.bot.database[str(ctx.author.id)]["costume"]["save"].append(
            {
                "name": name,
                "data": self.bot.database[str(ctx.author.id)]["costume"]["canvas"]
            }
        )
        await success_embed(ctx, self.bot.text.saved_work[user_lang].format(name))

    @commands.command(usage=cmd_data.set.usage, description=cmd_data.set.description, help=cmd_data.set.help, brief=cmd_data.set.brief)
    async def set(self, ctx, *, code) -> None:
        """ 装飾コードまたは各装飾の番号から全種類のアイテムを一括で登録 """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        item = code_to_list(code)
        if item is None:
            await error_embed(ctx, self.bot.text.wrong_costume_code[user_lang])
        elif (self.bot.data.base.min <= item[0] <= self.bot.data.base.max) and (self.bot.data.character.min <= item[1] <= self.bot.data.character.max) and \
                (self.bot.data.weapon.min <= item[2] <= self.bot.data.weapon.max) and (self.bot.data.head.min <= item[3] <= self.bot.data.head.max) and \
                (self.bot.data.body.min <= item[4] <= self.bot.data.body.max) and (self.bot.data.back.min <= item[5] <= self.bot.data.back.max):
            await self.make_image(ctx, *item)
            # TODO: db にコードを保存: code
        else:
            await error_embed(ctx, self.bot.text.wrong_costume_code[user_lang])


def setup(bot):
    bot.add_cog(Costume(bot))
