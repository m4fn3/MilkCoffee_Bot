import asyncio
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
        emoji = await self.main_menu()
        if emoji is None:
            return  # メインメニューのタイムアウト
        res = await self.emoji_task(emoji)
        if not res:
            return  # Exit絵文字

    async def main_menu(self):
        """メインメニューの作成"""
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
        if emoji == self.data.emoji.base:
            await self.base_selector()
        elif emoji == self.data.emoji.char:
            pass
        elif emoji == self.data.emoji.weapon:
            pass
        elif emoji == self.data.emoji.head:
            pass
        elif emoji == self.data.emoji.body:
            pass
        elif emoji == self.data.emoji.back:
            pass
        elif emoji == self.data.emoji.search:
            pass
        elif emoji == self.data.emoji.exit:
            return False

    async def base_selector(self):
        pass
        
