import asyncio
import difflib
import io
import re
from typing import Any

import discord
from PIL import Image

from .bot import MilkCoffee
from .data.item_data import ItemData
from .utils.item_parser import *
from .utils.messenger import error_embed, success_embed


class Menu:
    def __init__(self, ctx, bot, lang, code):
        self.ctx = ctx
        self.bot = bot  # type: MilkCoffee
        self.lang = lang
        self.code = code
        self.item = code_to_list(code)
        self.data = ItemData()
        self.msg: Optional[discord.Message] = None

    async def destroy(self):
        """リアクションを削除またはメッセージを削除して終了"""
        try:
            await self.msg.clear_reactions()
        except:
            try:
                await self.msg.delete()
            except:
                pass

    async def run(self):
        """メニュー開始"""
        while True:
            emoji = await self.main_menu()
            if emoji is None:
                return await self.destroy()  # メインメニューのタイムアウト
            res = await self.emoji_task(emoji)
            if not res:
                return await self.destroy()  # Exit絵文字

    async def main_menu(self):
        """メインメニューの作成"""
        if self.msg is not None:
            await self.msg.delete()
        embed = discord.Embed(color=0x9effce)
        desc = self.data.emoji.num + " " + self.bot.text.menu_code[self.lang] + ": `" + self.code + "`\n"
        desc += self.data.emoji.base + " " + self.bot.text.menu_base[self.lang] + f"{str(self.item[0]).rjust(3)}` {getattr(self.data.base.emoji, 'e' + str(self.item[0]))} {getattr(self.data.base.name, 'n' + str(self.item[0]))}\n"
        desc += self.data.emoji.char + " " + self.bot.text.menu_character[self.lang] + f"{str(self.item[1]).rjust(3)}` {getattr(self.data.character.emoji, 'e' + str(self.item[1]))} {getattr(self.data.character.name, 'n' + str(self.item[1]))}\n"
        desc += self.data.emoji.weapon + " " + self.bot.text.menu_weapon[self.lang] + f"{str(self.item[2]).rjust(3)}` {getattr(self.data.weapon.emoji, 'e' + str(self.item[2]))} {getattr(self.data.weapon.name, 'n' + str(self.item[2]))}\n"
        desc += self.data.emoji.head + " " + self.bot.text.menu_head[self.lang] + f"{str(self.item[3]).rjust(3)}` {getattr(self.data.head.emoji, 'e' + str(self.item[3]))} {getattr(self.data.head.name, 'n' + str(self.item[3]))}\n"
        desc += self.data.emoji.body + " " + self.bot.text.menu_body[self.lang] + f"{str(self.item[4]).rjust(3)}` {getattr(self.data.body.emoji, 'e' + str(self.item[4]))} {getattr(self.data.body.name, 'n' + str(self.item[4]))}\n"
        desc += self.data.emoji.back + " " + self.bot.text.menu_back[self.lang] + f"{str(self.item[5]).rjust(3)}` {getattr(self.data.back.emoji, 'e' + str(self.item[5]))} {getattr(self.data.back.name, 'n' + str(self.item[5]))}\n"
        embed.description = desc
        img = self.make_image(*self.item)
        self.msg = await self.ctx.send(embed=embed, file=img)
        # リアクションを追加
        emoji_add_task = self.bot.loop.create_task(self.add_menu_reaction())
        # リアクション待機
        menu_emoji = [self.data.emoji.base, self.data.emoji.char, self.data.emoji.weapon, self.data.emoji.head, self.data.emoji.body, self.data.emoji.back, self.data.emoji.search, self.data.emoji.num, self.data.emoji.config, self.data.emoji.exit]
        emoji: str
        try:
            react, _ = await self.bot.wait_for("reaction_add", timeout=60, check=lambda r, u: str(r.emoji) in menu_emoji and r.message.id == self.msg.id and u == self.ctx.author)
            emoji_add_task.cancel()
            return str(react.emoji)
        except asyncio.TimeoutError:
            return None

    async def add_menu_reaction(self):
        """メッセージにリアクションを追加"""
        await asyncio.gather(
            self.msg.add_reaction(self.data.emoji.base),
            self.msg.add_reaction(self.data.emoji.char),
            self.msg.add_reaction(self.data.emoji.weapon),
            self.msg.add_reaction(self.data.emoji.head),
            self.msg.add_reaction(self.data.emoji.body),
            self.msg.add_reaction(self.data.emoji.back),
            self.msg.add_reaction(self.data.emoji.search),
            self.msg.add_reaction(self.data.emoji.num),
            self.msg.add_reaction(self.data.emoji.config),
            self.msg.add_reaction(self.data.emoji.exit)
        )

    async def emoji_task(self, emoji):
        """各絵文字に対する挙動"""
        flag = 1
        if emoji == self.data.emoji.base:
            flag = await self.selector("base")
        elif emoji == self.data.emoji.char:
            flag = await self.selector("character")
        elif emoji == self.data.emoji.weapon:
            flag = await self.selector("weapon")
        elif emoji == self.data.emoji.head:
            flag = await self.selector("head")
        elif emoji == self.data.emoji.body:
            flag = await self.selector("body")
        elif emoji == self.data.emoji.back:
            flag = await self.selector("back")
        elif emoji == self.data.emoji.search:
            flag = await self.searcher()
        elif emoji == self.data.emoji.num:
            flag = await self.code_input()
        elif emoji == self.data.emoji.config:
            flag = await self.config()
        elif emoji == self.data.emoji.exit:
            return False
        if flag == 1:  # タイムアウト
            return False
        elif flag == 2:  # メインメニューを表示
            return True

    async def selector(self, item_type):
        """選択画面"""
        # 選択画面作成
        max_page = getattr(self.data, item_type).page
        embed = discord.Embed(title=self.bot.text.list_base_title[self.lang], color=0xffce9e)
        embed.description = self.bot.text.list_description[self.lang] + self.get_list(item_type, 1)
        embed.set_footer(text=self.bot.text.showing_page_1[self.lang].format(max_page))
        msg = await self.ctx.send(embed=embed)
        selector_emoji = []
        if max_page == 1:
            selector_emoji = [self.data.emoji.goback]
        else:
            selector_emoji = [self.data.emoji.left, self.data.emoji.right, self.data.emoji.goback]
        self.bot.loop.create_task(self.add_selector_emoji(msg, selector_emoji))
        # 入力待機
        flag: int
        page = 1
        count = 0
        while True:
            react_task = asyncio.create_task(self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in selector_emoji and r.message.id == msg.id and u == self.ctx.author, timeout=30), name="react")
            msg_task = asyncio.create_task(self.bot.wait_for("message", check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel, timeout=30), name="msg")
            done, _ = await asyncio.wait({react_task, msg_task}, return_when=asyncio.FIRST_COMPLETED)
            done_task = list(done)[0]
            react_task.cancel()
            msg_task.cancel()
            if isinstance(done_task.exception(), asyncio.TimeoutError):
                flag = 1  # タイムアウト
                break
            elif done_task.get_name() == "react":
                reaction, user = done_task.result()
                if (max_page == 1) or str(reaction.emoji) == self.data.emoji.goback:
                    flag = 2  # back
                    break
                try:
                    await msg.remove_reaction(reaction, user)
                except:
                    pass
                if str(reaction.emoji) == self.data.emoji.right:
                    if page == max_page:
                        page = 1
                    else:
                        page = page + 1
                elif str(reaction.emoji) == self.data.emoji.left:
                    if page == 1:
                        page = max_page
                    else:
                        page = page - 1
                embed = discord.Embed(title=getattr(self.bot.text, f"list_{item_type}_title")[self.lang], color=0xffce9e)
                embed.description = self.bot.text.list_description[self.lang] + self.get_list(item_type, page)
                embed.set_footer(text=self.bot.text.showing_page[self.lang].format(page, max_page))
                await msg.edit(embed=embed)
            elif done_task.get_name() == "msg":
                rmsg = done_task.result()
                code, result = self.find_item(rmsg.content, index=True, item_type=item_type)
                if code == 0:
                    count += 1
                    # アイテムが見つかりませんでした
                    await error_embed(self.ctx, result[self.lang])
                    if count == 3:
                        flag = 2
                        break
                else:
                    self.item[getattr(self.data, result[0]).index] = int(result[1])
                    # TODO: db にコードを保存
                    # 新版で画像を生成してメニューを新しく表示
                    flag = 2
                    break
        await msg.delete()
        return flag

    async def add_selector_emoji(self, msg, emoji_list):
        for emoji in emoji_list:
            await msg.add_reaction(emoji)

    async def searcher(self):
        """名前からアイテムを検索"""
        embed = discord.Embed(title=self.bot.text.menu_find_item[self.lang], color=0xffce9e)
        embed.description = self.bot.text.menu_find_description[self.lang]
        msg = await self.ctx.send(embed=embed)
        searcher_emoji = [self.data.emoji.goback]
        self.bot.loop.create_task(self.add_selector_emoji(msg, searcher_emoji))
        # 入力待機
        flag: int
        count = 0
        while True:
            react_task = asyncio.create_task(self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in searcher_emoji and r.message.id == msg.id and u == self.ctx.author, timeout=30), name="react")
            msg_task = asyncio.create_task(self.bot.wait_for("message", check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel, timeout=30), name="msg")
            done, _ = await asyncio.wait({react_task, msg_task}, return_when=asyncio.FIRST_COMPLETED)
            done_task = list(done)[0]
            react_task.cancel()
            msg_task.cancel()
            if isinstance(done_task.exception(), asyncio.TimeoutError):
                flag = 1  # タイムアウト
                break
            elif done_task.get_name() == "react":
                flag = 2  # back
                break
            elif done_task.get_name() == "msg":
                rmsg = done_task.result()
                code, result = self.find_item(rmsg.content)
                if code == 0:
                    count += 1
                    # アイテムが見つかりませんでした
                    await error_embed(self.ctx, result[self.lang])
                    if count == 3:
                        flag = 2
                        break
                else:
                    self.item[getattr(self.data, result[0]).index] = int(result[1])
                    # TODO: db にコードを保存
                    # 新版で画像を生成してメニューを新しく表示
                    flag = 2
                    break
        await msg.delete()
        return flag

    async def code_input(self):
        """名前からアイテムを検索"""
        embed = discord.Embed(title="装飾コードで設定", color=0xffce9e)
        embed.description = "装飾コードを入力してください"  # TODO: 多言語対応 - セレクタ―のdescriptionに説明文
        msg = await self.ctx.send(embed=embed)
        searcher_emoji = [self.data.emoji.goback]
        self.bot.loop.create_task(self.add_selector_emoji(msg, searcher_emoji))
        # 入力待機
        flag: int
        count = 0
        while True:
            react_task = asyncio.create_task(self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in searcher_emoji and r.message.id == msg.id and u == self.ctx.author, timeout=30), name="react")
            msg_task = asyncio.create_task(self.bot.wait_for("message", check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel, timeout=30), name="msg")
            done, _ = await asyncio.wait({react_task, msg_task}, return_when=asyncio.FIRST_COMPLETED)
            done_task = list(done)[0]
            react_task.cancel()
            msg_task.cancel()
            if isinstance(done_task.exception(), asyncio.TimeoutError):
                flag = 1  # タイムアウト
                break
            elif done_task.get_name() == "react":
                flag = 2  # back
                break
            elif done_task.get_name() == "msg":
                rmsg = done_task.result()
                item = code_to_list(rmsg.content.lower())
                if item is None:
                    await error_embed(self.ctx, self.bot.text.wrong_costume_code[self.lang])
                elif (self.data.base.min <= item[0] <= self.data.base.max) and (self.data.character.min <= item[1] <= self.data.character.max) and \
                        (self.data.weapon.min <= item[2] <= self.data.weapon.max) and (self.data.head.min <= item[3] <= self.data.head.max) and \
                        (self.data.body.min <= item[4] <= self.data.body.max) and (self.data.back.min <= item[5] <= self.data.back.max):
                    self.item = item
                    self.code = list_to_code(item)
                    # TODO: db にコードを保存
                    # 新版で画像を生成してメニューを新しく表示
                    flag = 2
                    break
                else:
                    count += 1
                    await error_embed(self.ctx, self.bot.text.wrong_costume_code[self.lang])
                    if count == 3:
                        flag = 2
                        break
        await msg.delete()
        return flag

    async def config(self):
        embed = discord.Embed(title=self.bot.text.menu_config[self.lang])
        embed.description = self.bot.text.menu_config_description[self.lang].format(self.data.emoji.save, self.data.emoji.load)
        msg = await self.ctx.send(embed=embed)
        emoji_task = self.bot.loop.create_task(self.add_config_emoji(msg))
        react: discord.Reaction
        try:
            react, _ = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in [self.data.emoji.load, self.data.emoji.save, self.data.emoji.goback] and r.message.id == msg.id and u == self.ctx.author, timeout=30)
            emoji_task.cancel()
        except asyncio.TimeoutError:
            await msg.delete()
            return 1  # タイムアウト
        await msg.delete()
        if str(react.emoji) == self.data.emoji.goback:
            return 2  # back
        elif str(react.emoji) == self.data.emoji.load:
            return await self.load()
        elif str(react.emoji) == self.data.emoji.save:
            return await self.save()

    async def save(self):
        """作品を保存"""
        embed = discord.Embed(title=self.bot.text.menu_save[self.lang])
        embed.description = self.bot.text.menu_save_description[self.lang]
        msg = await self.ctx.send(embed=embed)
        config_emoji = [self.data.emoji.goback]
        self.bot.loop.create_task(self.add_selector_emoji(msg, config_emoji))
        # TODO: db 既に20個保存されている場合
        # await error_embed(ctx, self.bot.text.save_up_to_20[user_lang])
        # return 2
        used_name_list = []  # TODO: db 保存された作品の名前のリスト
        # 入力待機
        flag: int
        count = 0
        while True:
            react_task = asyncio.create_task(self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in config_emoji and r.message.id == msg.id and u == self.ctx.author, timeout=30), name="react")
            msg_task = asyncio.create_task(self.bot.wait_for("message", check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel, timeout=30), name="msg")
            done, _ = await asyncio.wait({react_task, msg_task}, return_when=asyncio.FIRST_COMPLETED)
            done_task = list(done)[0]
            react_task.cancel()
            msg_task.cancel()
            if isinstance(done_task.exception(), asyncio.TimeoutError):
                flag = 1  # タイムアウト
                break
            elif done_task.get_name() == "react":
                flag = 2  # back
                break
            elif done_task.get_name() == "msg":
                rmsg = done_task.result()
                name = rmsg.content
                error = False
                if name.isdigit():
                    await error_embed(self.ctx, self.bot.text.int_only_name_not_allowed[self.lang])
                    error = True
                elif name in used_name_list:
                    await error_embed(self.ctx, self.bot.text.name_already_used[self.lang])
                    error = True
                elif len(name) < 1 or 20 < len(name):
                    await error_embed(self.ctx, self.bot.text.name_length_between_1_20[self.lang])
                    error = True
                if error:
                    count += 1
                    if count == 3:
                        flag = 2
                        break
                else:
                    # TODO: db nameでcanvasのデータを保存
                    await success_embed(self.ctx, self.bot.text.saved_work[self.lang].format(name))
                    flag = 2
                    break
        await msg.delete()
        return flag

    async def load(self):
        """作品を読み込み"""
        embed = discord.Embed(title=self.bot.text.menu_load[self.lang])
        embed.description = self.bot.text.menu_load_description[self.lang]
        msg = await self.ctx.send(embed=embed)
        config_emoji = [self.data.emoji.goback]
        self.bot.loop.create_task(self.add_selector_emoji(msg, config_emoji))
        # 入力待機
        flag: int
        count = 0
        while True:
            react_task = asyncio.create_task(self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in config_emoji and r.message.id == msg.id and u == self.ctx.author, timeout=30), name="react")
            msg_task = asyncio.create_task(self.bot.wait_for("message", check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel, timeout=30), name="msg")
            done, _ = await asyncio.wait({react_task, msg_task}, return_when=asyncio.FIRST_COMPLETED)
            done_task = list(done)[0]
            react_task.cancel()
            msg_task.cancel()
            if isinstance(done_task.exception(), asyncio.TimeoutError):
                flag = 1  # タイムアウト
                break
            elif done_task.get_name() == "react":
                flag = 2  # back
                break
            elif done_task.get_name() == "msg":
                rmsg = done_task.result()
                index = rmsg.content
                error = False
                item_index = 1
                # TODO: dbの部分はループ外で処理すると効率よいかも
                if index.isdigit() and 1 <= int(index) <= 20:
                    item_count = 1  # TODO db そのユーザーの保存数
                    if 0 <= int(index) <= item_count:
                        item_index = int(index) - 1
                    else:
                        await error_embed(self.ctx, self.bot.text.no_th_saved_work[self.lang].format(index))
                        error = True
                elif index.isdigit():
                    await error_embed(self.ctx, self.bot.text.specify_between_1_20[self.lang])
                    error = True
                else:
                    used_name_list = [d.get("name") for d in []]  # TODO: db []の部分にユーザーの保存されたデータリスト
                    if index in used_name_list:
                        item_index = used_name_list.index(index)
                    else:
                        await error_embed(self.ctx, self.bot.text.not_found_with_name[self.lang])
                        error = True
                if error:
                    count += 1
                    if count == 3:
                        flag = 2
                        break
                else:
                    # TODO: db 作業場データにitem_index番目に保存済みのデータを読み込む
                    await success_embed(self.ctx, self.bot.text.loaded_work[self.lang].format(item_index + 1, "読み込んだ作品の名前"))  # TODO: db 作品名
                    flag = 2
                    break
        await msg.delete()
        return flag

    async def add_config_emoji(self, msg):
        await asyncio.gather(
            msg.add_reaction(self.data.emoji.load),
            msg.add_reaction(self.data.emoji.save),
            msg.add_reaction(self.data.emoji.goback)
        )

    def get_list(self, item_type: str, page: int) -> str:
        """指定した種類のアイテムリストテキストを生成"""
        item_count = getattr(self.data, item_type).max
        text = ""
        start_index = getattr(self.data, item_type).min + 10 * (page - 1)
        for item_index in range(start_index, start_index + 10):
            if item_index > item_count:
                break
            emoji = getattr(getattr(self.data, item_type).emoji, "e" + str(item_index))
            name = getattr(getattr(self.data, item_type).name, "n" + str(item_index))
            text += f"`{str(item_index).rjust(3)}` {emoji} {name}\n"
        return text

    def find_item(self, item_name: str, index=False, item_type="") -> (int, Any):
        """アイテムを検索"""
        type_list: list
        if index and item_name.isdigit():
            if getattr(self.data, item_type).min <= int(item_name) <= getattr(self.data, item_type).max:
                return 1, [item_type, item_name]
            else:
                return 0, self.bot.text.wrong_item_index
        elif index:
            type_list = [item_type]
        else:
            type_list = [type_name for type_name in self.data.regex]
        match_per = -1
        item_info = []
        for i in type_list:
            for j in self.data.regex[i]:
                match_obj = re.search(self.data.regex[i][j], item_name, re.IGNORECASE)
                if match_obj is not None:
                    diff_per = difflib.SequenceMatcher(None, getattr(getattr(self.data, i).name, "n" + str(j)).lower(), match_obj.group()).ratio()
                    if diff_per > match_per:
                        match_per = diff_per
                        item_info = [i, j]
        if match_per == -1:
            return 0, self.bot.text.item_not_found
        else:
            return 1, item_info

    def make_image(self, base_id: int, character_id: int, weapon_id: int, head_id: int, body_id: int, back_id: int) -> discord.File:
        """画像を作成"""
        base = Image.open(f"./Assets/base/{base_id}.png")
        character = Image.open(f"./Assets/character/{base_id}/{character_id}.png")
        weapon = Image.open(f"./Assets/weapon/{weapon_id}.png")
        head = Image.open(f"./Assets/head/{head_id}.png")
        body = Image.open(f"./Assets/body/{body_id}.png")
        back = Image.open(f"./Assets/back/{back_id}.png")
        base.paste(character, (0, 0), character)
        base.paste(head, (0, 0), head)
        base.paste(body, (0, 0), body)
        base.paste(back, (0, 0), back)
        base.paste(weapon, (0, 0), weapon)
        imgByteArr = io.BytesIO()
        base.save(imgByteArr, format=base.format)
        base = imgByteArr.getvalue()
        return discord.File(fp=io.BytesIO(base), filename="result.png")
