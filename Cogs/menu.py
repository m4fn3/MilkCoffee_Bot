import asyncio
import difflib
import io
import re
from typing import Any

import discord
from PIL import Image

from .milkcoffee import MilkCoffee
from .utils.item_parser import *
from .utils.messenger import error_embed, success_embed


class Menu:
    def __init__(self, ctx, bot, lang):
        self.ctx = ctx
        self.bot = bot  # type: MilkCoffee
        self.lang = lang
        self.code: str = ""
        self.item: list = []
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
        self.code = await self.bot.db.get_canvas(self.ctx.author.id)
        self.item = code_to_list(self.code)
        embed = discord.Embed(color=0x9effce)
        desc = self.bot.data.emoji.num + " " + self.bot.text.menu_code[self.lang] + ": `" + self.code + "`\n"
        desc += self.bot.data.emoji.base + " " + self.bot.text.menu_base[self.lang] + f"{str(self.item[0]).rjust(3)}` {getattr(self.bot.data.base.emoji, 'e' + str(self.item[0]))} {getattr(self.bot.data.base.name, 'n' + str(self.item[0]))}\n"
        desc += self.bot.data.emoji.char + " " + self.bot.text.menu_character[self.lang] + f"{str(self.item[1]).rjust(3)}` {getattr(self.bot.data.character.emoji, 'e' + str(self.item[1]))} {getattr(self.bot.data.character.name, 'n' + str(self.item[1]))}\n"
        desc += self.bot.data.emoji.weapon + " " + self.bot.text.menu_weapon[self.lang] + f"{str(self.item[2]).rjust(3)}` {getattr(self.bot.data.weapon.emoji, 'e' + str(self.item[2]))} {getattr(self.bot.data.weapon.name, 'n' + str(self.item[2]))}\n"
        desc += self.bot.data.emoji.head + " " + self.bot.text.menu_head[self.lang] + f"{str(self.item[3]).rjust(3)}` {getattr(self.bot.data.head.emoji, 'e' + str(self.item[3]))} {getattr(self.bot.data.head.name, 'n' + str(self.item[3]))}\n"
        desc += self.bot.data.emoji.body + " " + self.bot.text.menu_body[self.lang] + f"{str(self.item[4]).rjust(3)}` {getattr(self.bot.data.body.emoji, 'e' + str(self.item[4]))} {getattr(self.bot.data.body.name, 'n' + str(self.item[4]))}\n"
        desc += self.bot.data.emoji.back + " " + self.bot.text.menu_back[self.lang] + f"{str(self.item[5]).rjust(3)}` {getattr(self.bot.data.back.emoji, 'e' + str(self.item[5]))} {getattr(self.bot.data.back.name, 'n' + str(self.item[5]))}\n"
        embed.description = desc
        img = self.make_image(*self.item)
        self.msg = await self.ctx.send(embed=embed, file=img)
        # リアクションを追加
        emoji_add_task = self.bot.loop.create_task(self.add_menu_reaction())
        # リアクション待機
        menu_emoji = [self.bot.data.emoji.base, self.bot.data.emoji.char, self.bot.data.emoji.weapon, self.bot.data.emoji.head, self.bot.data.emoji.body, self.bot.data.emoji.back, self.bot.data.emoji.search, self.bot.data.emoji.num, self.bot.data.emoji.config, self.bot.data.emoji.exit]
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
            self.msg.add_reaction(self.bot.data.emoji.base),
            self.msg.add_reaction(self.bot.data.emoji.char),
            self.msg.add_reaction(self.bot.data.emoji.weapon),
            self.msg.add_reaction(self.bot.data.emoji.head),
            self.msg.add_reaction(self.bot.data.emoji.body),
            self.msg.add_reaction(self.bot.data.emoji.back),
            self.msg.add_reaction(self.bot.data.emoji.search),
            self.msg.add_reaction(self.bot.data.emoji.num),
            self.msg.add_reaction(self.bot.data.emoji.config),
            self.msg.add_reaction(self.bot.data.emoji.exit)
        )

    async def emoji_task(self, emoji):
        """各絵文字に対する挙動"""
        flag = 1
        if emoji == self.bot.data.emoji.base:
            flag = await self.selector("base")
        elif emoji == self.bot.data.emoji.char:
            flag = await self.selector("character")
        elif emoji == self.bot.data.emoji.weapon:
            flag = await self.selector("weapon")
        elif emoji == self.bot.data.emoji.head:
            flag = await self.selector("head")
        elif emoji == self.bot.data.emoji.body:
            flag = await self.selector("body")
        elif emoji == self.bot.data.emoji.back:
            flag = await self.selector("back")
        elif emoji == self.bot.data.emoji.search:
            flag = await self.searcher()
        elif emoji == self.bot.data.emoji.num:
            flag = await self.code_input()
        elif emoji == self.bot.data.emoji.config:
            flag = await self.config()
        elif emoji == self.bot.data.emoji.exit:
            return False
        if flag == 1:  # タイムアウト
            return False
        elif flag == 2:  # メインメニューを表示
            return True

    async def selector(self, item_type):
        """選択画面"""
        # 選択画面作成
        max_page = getattr(self.bot.data, item_type).page
        embed = discord.Embed(title=self.bot.text.list_base_title[self.lang], color=0xffce9e)
        embed.description = self.bot.text.list_description[self.lang] + self.get_list(item_type, 1)
        embed.set_footer(text=self.bot.text.showing_page_1[self.lang].format(max_page))
        msg = await self.ctx.send(embed=embed)
        selector_emoji = []
        if max_page == 1:
            selector_emoji = [self.bot.data.emoji.goback]
        else:
            selector_emoji = [self.bot.data.emoji.left, self.bot.data.emoji.right, self.bot.data.emoji.goback]
        emoji_task = self.bot.loop.create_task(self.add_selector_emoji(msg, selector_emoji))
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
                if (max_page == 1) or str(reaction.emoji) == self.bot.data.emoji.goback:
                    flag = 2  # back
                    break
                try:
                    await msg.remove_reaction(reaction, user)
                except:
                    pass
                if str(reaction.emoji) == self.bot.data.emoji.right:
                    if page == max_page:
                        page = 1
                    else:
                        page += 1
                elif str(reaction.emoji) == self.bot.data.emoji.left:
                    if page == 1:
                        page = max_page
                    else:
                        page -= 1
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
                    self.item[getattr(self.bot.data, result[0]).index] = int(result[1])
                    await self.bot.db.set_canvas(self.ctx.author.id, list_to_code(self.item))
                    # 新版で画像を生成してメニューを新しく表示
                    flag = 2
                    break
        emoji_task.cancel()
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
        searcher_emoji = [self.bot.data.emoji.goback]
        emoji_task = self.bot.loop.create_task(self.add_selector_emoji(msg, searcher_emoji))
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
                    self.item[getattr(self.bot.data, result[0]).index] = int(result[1])
                    await self.bot.db.set_canvas(self.ctx.author.id, list_to_code(self.item))
                    # 新版で画像を生成してメニューを新しく表示
                    flag = 2
                    break
        emoji_task.cancel()
        await msg.delete()
        return flag

    async def code_input(self):
        """名前からアイテムを検索"""
        embed = discord.Embed(title="装飾コードで設定", color=0xffce9e)
        embed.description = "装飾コードを入力してください"  # TODO: 多言語対応 - セレクタ―のdescriptionに説明文
        msg = await self.ctx.send(embed=embed)
        searcher_emoji = [self.bot.data.emoji.goback]
        emoji_task = self.bot.loop.create_task(self.add_selector_emoji(msg, searcher_emoji))
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
                elif (self.bot.data.base.min <= item[0] <= self.bot.data.base.max) and (self.bot.data.character.min <= item[1] <= self.bot.data.character.max) and \
                        (self.bot.data.weapon.min <= item[2] <= self.bot.data.weapon.max) and (self.bot.data.head.min <= item[3] <= self.bot.data.head.max) and \
                        (self.bot.data.body.min <= item[4] <= self.bot.data.body.max) and (self.bot.data.back.min <= item[5] <= self.bot.data.back.max):
                    await self.bot.db.set_canvas(self.ctx.author.id, self.code)
                    # 新版で画像を生成してメニューを新しく表示
                    flag = 2
                    break
                else:
                    count += 1
                    await error_embed(self.ctx, self.bot.text.wrong_costume_code[self.lang])
                    if count == 3:
                        flag = 2
                        break
        emoji_task.cancel()
        await msg.delete()
        return flag

    async def config(self):
        embed = discord.Embed(title=self.bot.text.menu_config[self.lang], color=0xffce9e)
        embed.description = self.bot.text.menu_config_description[self.lang].format(self.bot.data.emoji.save, self.bot.data.emoji.load)
        msg = await self.ctx.send(embed=embed)
        emoji_task = self.bot.loop.create_task(self.add_config_emoji(msg))
        react: discord.Reaction
        try:
            react, _ = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in [self.bot.data.emoji.load, self.bot.data.emoji.save, self.bot.data.emoji.goback] and r.message.id == msg.id and u == self.ctx.author, timeout=30)
            emoji_task.cancel()
        except asyncio.TimeoutError:
            emoji_task.cancel()
            await msg.delete()
            return 1  # タイムアウト
        await msg.delete()
        if str(react.emoji) == self.bot.data.emoji.goback:
            return 2  # back
        elif str(react.emoji) == self.bot.data.emoji.load:
            return await self.load()
        elif str(react.emoji) == self.bot.data.emoji.save:
            return await self.save()

    async def save(self):
        """作品を保存"""
        embed = discord.Embed(title=self.bot.text.menu_save[self.lang], color=0xd1a3ff)
        embed.description = self.bot.text.menu_save_description[self.lang]
        msg = await self.ctx.send(embed=embed)
        config_emoji = [self.bot.data.emoji.goback]
        emoji_task = self.bot.loop.create_task(self.add_selector_emoji(msg, config_emoji))
        save_data = await self.bot.db.get_save_work(self.ctx.author.id)
        if len(save_data) >= 20:
            await error_embed(self.ctx, self.bot.text.save_up_to_20[self.lang])
            return 2
        used_names = [data["name"] for data in save_data]  # 使用済みの名前のリストを取得
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
                cond = rmsg.content
                error = False
                if cond in used_names:  # 使用済みの場合
                    await error_embed(self.ctx, self.bot.text.name_already_used[self.lang])
                    error = True
                elif cond.isdigit():  # 数字のみの場合
                    await error_embed(self.ctx, self.bot.text.int_only_name_not_allowed[self.lang])
                    error = True
                elif not (1 <= len(cond) <= 20):  # 1~20文字を超過している場合
                    await error_embed(self.ctx, self.bot.text.name_length_between_1_20[self.lang])
                    error = True
                if error:
                    count += 1
                    if count == 3:
                        flag = 2
                        break
                else:
                    save_data.append({
                        "name": cond,
                        "code": await self.bot.db.get_canvas(self.ctx.author.id)
                    })
                    await self.bot.db.update_save_work(self.ctx.author.id, save_data)
                    await success_embed(self.ctx, self.bot.text.saved_work[self.lang].format(cond))
                    flag = 2
                    break
        emoji_task.cancel()
        await msg.delete()
        return flag

    async def load(self):
        """作品を読み込み"""
        embed = discord.Embed(title=self.bot.text.menu_load[self.lang], color=0xd1a3ff)
        embed.description = self.bot.text.menu_load_description[self.lang]
        msg = await self.ctx.send(embed=embed)
        config_emoji = [self.bot.data.emoji.goback]
        emoji_task = self.bot.loop.create_task(self.add_selector_emoji(msg, config_emoji))
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
                cond = rmsg.content
                save_data = await self.bot.db.get_save_work(self.ctx.author.id)
                error = False
                load_data = {}
                if cond.isdigit():  # 数字->インデックスの場合
                    if 1 <= int(cond) <= len(save_data):  # 番号が保存済みの範囲である場合
                        load_data = save_data[int(cond) - 1]
                    else:  # 番号にあった作品がない場合
                        await error_embed(self.ctx, self.bot.text.no_th_saved_work[self.lang].format(int(cond)))
                        error = True
                else:  # 名前の場合
                    filtered_data = [d for d in save_data if d["name"] == cond]
                    if filtered_data:  # 名前にあった作品が見つかった場合
                        load_data = filtered_data[0]
                    else:  # 名前にあった作品がない場合
                        await error_embed(self.ctx, self.bot.text.not_found_with_name[self.lang])
                        error = True
                if error:  # エラーの場合
                    count += 1
                    if count == 3:
                        flag = 2
                        break
                else:
                    await self.bot.db.set_canvas(self.ctx.author.id, load_data["code"])
                    await success_embed(self.ctx, self.bot.text.loaded_work[self.lang].format(save_data.index(load_data) + 1, load_data["name"]))
                    flag = 2
                    break

        emoji_task.cancel()
        await msg.delete()
        return flag

    async def add_config_emoji(self, msg):
        await asyncio.gather(
            msg.add_reaction(self.bot.data.emoji.load),
            msg.add_reaction(self.bot.data.emoji.save),
            msg.add_reaction(self.bot.data.emoji.goback)
        )

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

    def find_item(self, item_name: str, index=False, item_type="") -> (int, Any):
        """アイテムを検索"""
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

    def make_image(self, base_id: int, character_id: int, weapon_id: int, head_id: int, body_id: int, back_id: int) -> discord.File:
        """画像を作成"""
        base = Image.open(f"./Assets/base/{base_id}.png")
        character = Image.open(f"./Assets/character/{base_id}/{character_id}.png")
        weapon = Image.open(f"./Assets/weapon/{weapon_id}.png")
        head_img = Image.open(f"./Assets/head/{head_id}.png")
        body_img = Image.open(f"./Assets/body/{body_id}.png")
        back_img = Image.open(f"./Assets/back/{back_id}.png")
        base.paste(character, (0, 0), character)
        base.paste(head, (0, 0), head_img)
        base.paste(body, (0, 0), body_img)
        base.paste(back, (0, 0), back_img)
        base.paste(weapon, (0, 0), weapon)
        imgByteArr = io.BytesIO()
        base.save(imgByteArr, format=base.format)
        base = imgByteArr.getvalue()
        return discord.File(fp=io.BytesIO(base), filename="result.png")
