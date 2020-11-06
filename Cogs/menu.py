import asyncio
import difflib
import re
from typing import Any

import discord

from .data.item_data import ItemData
from .utils.item_parser import *


class Menu:
    def __init__(self, ctx, bot, lang, code):
        self.ctx = ctx
        self.bot = bot
        self.lang = lang
        self.item = code_to_list(code)
        self.data = ItemData()
        self.msg = None

    def __del__(self):
        self.bot.loop.create_task(self.clear_menu_reaction())

    async def run(self):
        """メニュー開始"""
        while True:
            emoji = await self.main_menu()
            if emoji is None:
                return  # メインメニューのタイムアウト
            res = await self.emoji_task(emoji)
            if not res:
                return  # Exit絵文字

    async def main_menu(self):
        """メインメニューの作成"""
        if self.msg is not None:
            await self.msg.delete()
        embed = discord.Embed()
        desc = "最上部テキスト(仮)\n"
        desc += self.data.emoji.base + " " + self.bot.text.menu_base[self.lang] + f"{str(self.item[0]).rjust(3)}` {getattr(self.data.base.emoji, 'e' + str(self.item[0]))} {getattr(self.data.base.name, 'n' + str(self.item[0]))}\n"
        desc += self.data.emoji.char + " " + self.bot.text.menu_character[self.lang] + f"{str(self.item[1]).rjust(3)}` {getattr(self.data.character.emoji, 'e' + str(self.item[1]))} {getattr(self.data.character.name, 'n' + str(self.item[1]))}\n"
        desc += self.data.emoji.weapon + " " + self.bot.text.menu_weapon[self.lang] + f"{str(self.item[2]).rjust(3)}` {getattr(self.data.weapon.emoji, 'e' + str(self.item[2]))} {getattr(self.data.weapon.name, 'n' + str(self.item[2]))}\n"
        desc += self.data.emoji.head + " " + self.bot.text.menu_head[self.lang] + f"{str(self.item[3]).rjust(3)}` {getattr(self.data.head.emoji, 'e' + str(self.item[3]))} {getattr(self.data.head.name, 'n' + str(self.item[3]))}\n"
        desc += self.data.emoji.body + " " + self.bot.text.menu_body[self.lang] + f"{str(self.item[4]).rjust(3)}` {getattr(self.data.body.emoji, 'e' + str(self.item[4]))} {getattr(self.data.body.name, 'n' + str(self.item[4]))}\n"
        desc += self.data.emoji.back + " " + self.bot.text.menu_back[self.lang] + f"{str(self.item[5]).rjust(3)}` {getattr(self.data.back.emoji, 'e' + str(self.item[5]))} {getattr(self.data.back.name, 'n' + str(self.item[5]))}\n"
        embed.description = desc
        self.msg = await self.ctx.send(embed=embed)
        # リアクションを追加
        emoji_add_task = self.bot.loop.create_task(self.add_menu_reaction())
        # リアクション待機
        menu_emoji = [self.data.emoji.base, self.data.emoji.char, self.data.emoji.weapon, self.data.emoji.head, self.data.emoji.body, self.data.emoji.back, self.data.emoji.search, self.data.emoji.exit]
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
            self.msg.add_reaction(self.data.emoji.exit),
        )

    async def clear_menu_reaction(self):
        """メッセージのリアクションを削除"""
        await asyncio.gather(
            self.msg.remove_reaction(self.data.emoji.base, self.ctx.guild.me),
            self.msg.remove_reaction(self.data.emoji.char, self.ctx.guild.me),
            self.msg.remove_reaction(self.data.emoji.weapon, self.ctx.guild.me),
            self.msg.remove_reaction(self.data.emoji.head, self.ctx.guild.me),
            self.msg.remove_reaction(self.data.emoji.body, self.ctx.guild.me),
            self.msg.remove_reaction(self.data.emoji.back, self.ctx.guild.me),
            self.msg.remove_reaction(self.data.emoji.search, self.ctx.guild.me),
            self.msg.remove_reaction(self.data.emoji.exit, self.ctx.guild.me),
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
        embed = discord.Embed(title=self.bot.text.list_base_title[self.lang])
        embed.description = self.bot.text.list_description[self.lang] + self.get_list(item_type, 1)
        embed.set_footer(text=self.bot.text.showing_page_1[self.lang].format(max_page))
        msg = await self.ctx.send(embed=embed)
        selector_emoji = []
        if max_page == 1:
            selector_emoji = [self.data.emoji.goback]
        else:
            selector_emoji = ["◀️", "▶️", self.data.emoji.goback]
        self.bot.loop.create_task(self.add_selector_emoji(msg, selector_emoji))
        # 入力待機
        flag: int
        page = 1
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
                reaction, _ = done_task.result()
                if (max_page == 1) or str(reaction.emoji) == self.data.emoji.goback:
                    flag = 2  # back
                    break
                if str(reaction.emoji) == "▶️":
                    if page == max_page:
                        page = 1
                    else:
                        page = page + 1
                elif str(reaction.emoji) == "◀️":
                    if page == 1:
                        page = max_page
                    else:
                        page = page - 1
                embed = discord.Embed(title=getattr(self.bot.text, f"list_{item_type}_title")[self.lang])
                embed.description = self.bot.text.list_description[self.lang] + self.get_list(item_type, page)
                embed.set_footer(text=self.bot.text.showing_page[self.lang].format(page, max_page))
                await msg.edit(embed=embed)
            elif done_task.get_name() == "msg":
                rmsg = done_task.result()
                code, result = self.find_item(rmsg.content, index=True, item_type=item_type)
                if code == 0:
                    # アイテムが見つかりませんでした
                    await self.ctx.send("item not found <-re->")
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
        embed = discord.Embed(title="アイテム検索")
        embed.description = "アイテム名を入力してください"
        msg = await self.ctx.send(embed=embed)
        searcher_emoji = [self.data.emoji.goback]
        self.bot.loop.create_task(self.add_selector_emoji(msg, searcher_emoji))
        # 入力待機
        flag: int
        page = 1
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
                    # アイテムが見つかりませんでした
                    await self.ctx.send("item not found <-re->")
                else:
                    self.item[getattr(self.data, result[0]).index] = int(result[1])
                    # TODO: db にコードを保存
                    # 新版で画像を生成してメニューを新しく表示
                    flag = 2
                    break
        await msg.delete()
        return flag

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
                return 0, ["アイテム番号が間違っています. (番号が小さすぎるか大きすぎます)", "Wrong item number.(The number is too small or too large)", "항목 번호가 잘못되었습니다. (숫자가 너무 작거나 큽니다)", "Número de artículo incorrecto (el número es demasiado pequeño o demasiado grande)"]
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
                    diff_per = difflib.SequenceMatcher(None, getattr(getattr(self.data, i).name, "n"+str(j)).lower(), match_obj.group()).ratio()
                    if diff_per > match_per:
                        match_per = diff_per
                        item_info = [i, j]
        if match_per == -1:
            return 0, ["検索結果がありません.もう一度名前を確認してください.", "No results. Please check name again.", "결과가 없습니다. 이름을 다시 확인하십시오.", "No hay resultados. Vuelva a comprobar el nombre."]
        else:
            return 1, item_info
