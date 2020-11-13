import asyncio
import difflib
import io
import math
import random
import re
from typing import Any

import discord
from PIL import Image
from discord.ext import commands

from .data.command_data import CmdData
from .menu import Menu
from .milkcoffee import MilkCoffee
from .utils.item_parser import *
from .utils.messenger import error_embed, success_embed

cmd_data = CmdData()


class Costume(commands.Cog):
    """装飾シミュレータを操作できます^Operate the costume simulator^코의상 시뮬레이터 작동^Operar el simulador de vestuario"""

    def __init__(self, bot: MilkCoffee) -> None:
        self.bot = bot
        self.menu_channels = set()
        self.menu_users = set()

    def find_item(self, item_name: str, index=False, item_type="") -> (int, Any):
        """アイテムを名前または番号で検索"""
        type_list: list
        if index and item_name.isdigit():  # 番号指定の場合
            if getattr(self.bot.data, item_type).min <= int(item_name) <= getattr(self.bot.data, item_type).max:
                return 1, [item_type, item_name]
            else:  # 間違った番号の場合
                return 0, self.bot.text.wrong_item_index
        elif index:  # 対象の種類名
            type_list = [item_type]
        else:  # 全アイテム(全種類)対象の場合
            type_list = [type_name for type_name in self.bot.data.regex]
        match_per = -1
        item_info = []
        for i in type_list:  # それぞれのアイテム名との一致率を計算
            for j in self.bot.data.regex[i]:
                match_obj = re.search(self.bot.data.regex[i][j], item_name, re.IGNORECASE)
                if match_obj is not None:
                    diff_per = difflib.SequenceMatcher(None, getattr(getattr(self.bot.data, i).name, "n" + str(j)).lower(), match_obj.group()).ratio()
                    if diff_per > match_per:
                        match_per = diff_per
                        item_info = [i, j]
        if match_per == -1:  # マッチしなかった場合
            return 0, self.bot.text.item_not_found
        else:  # 見つかった場合
            return 1, item_info

    def convert_to_bytes(self, image: Image) -> bytes:
        """imageオブジェクトをbyteに変換"""
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        return imgByteArr.getvalue()

    def get_list(self, item_type: str, page: int) -> str:
        """指定した種類のアイテムリストテキストを生成"""
        item_count = getattr(self.bot.data, item_type).max  # そのアイテムの最大数
        text = ""
        start_index = getattr(self.bot.data, item_type).min + 10 * (page - 1)
        for item_index in range(start_index, start_index + 10):  # その範囲での番号リストを取得
            if item_index > item_count:  # 範囲を超えた場合
                break
            emoji = getattr(getattr(self.bot.data, item_type).emoji, "e" + str(item_index))
            name = getattr(getattr(self.bot.data, item_type).name, "n" + str(item_index))
            text += f"`{str(item_index).ljust(3)}:` {emoji} {name}\n"
        return text

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """コマンド実行の前処理"""
        if ctx.author.id not in self.bot.cache_users:  # 未登録ユーザーの場合
            await self.bot.on_new_user(ctx)  # 新規登録

    async def cog_command_error(self, ctx: commands.Context, error) -> None:
        """エラー発生時"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):  # 引数不足
            await error_embed(ctx, self.bot.text.missing_arguments[user_lang].format(self.bot.PREFIX, ctx.command.usage.split("^")[user_lang], ctx.command.qualified_name))
        elif isinstance(error, commands.CommandOnCooldown):  # クールダウン
            await error_embed(ctx, self.bot.text.interval_too_fast[user_lang].format(error.retry_after))
        else:  # 未知のエラー
            await error_embed(ctx, self.bot.text.error_occurred[user_lang].format(error))

    async def make_image(self, ctx: commands.Context, base_id: int, character_id: int, weapon_id: int, head_id: int, body_id: int, back_id: int) -> None:
        """ アイテム番号から画像を構築 """
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        # 対象の画像を取得
        base = Image.open(f"./Assets/base/{base_id}.png")
        character = Image.open(f"./Assets/character/{base_id}/{character_id}.png")
        weapon = Image.open(f"./Assets/weapon/{weapon_id}.png")
        head_img = Image.open(f"./Assets/head/{head_id}.png")
        body_img = Image.open(f"./Assets/body/{body_id}.png")
        back_img = Image.open(f"./Assets/back/{back_id}.png")
        # 画像を結合
        base.paste(character, (0, 0), character)
        base.paste(head_img, (0, 0), head_img)
        base.paste(body_img, (0, 0), body_img)
        base.paste(back_img, (0, 0), back_img)
        base.paste(weapon, (0, 0), weapon)
        base = self.convert_to_bytes(base)
        # 本体の作成
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

    @commands.command(aliases=["m"], usage=cmd_data.menu.usage, description=cmd_data.menu.description, brief=cmd_data.menu.brief)
    async def menu(self, ctx: commands.Context) -> None:
        """シミュレータ操作メニューを作成"""
        if ctx.author.id in self.menu_users:  # 既に実行中のユーザーの場合
            return await error_embed(ctx, "あなたは既にメニューを実行中です！既存のメニューを閉じてから再実行してね!")
        elif ctx.channel.id in self.menu_channels:  # 既に実行中のチャンネルの場合
            return await error_embed(ctx, "このチャンネルでは,現在他の人がメニューを実行中です!他のチャンネルで再実行してね!")
        self.menu_users.add(ctx.author.id)  # 実行中のリストに追加
        self.menu_channels.add(ctx.channel.id)
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        menu = Menu(ctx, self.bot, user_lang)  # メニュー初期化
        await menu.run()  # メニュー開始
        self.menu_users.remove(ctx.author.id)  # 実行中のリストから削除
        self.menu_channels.remove(ctx.channel.id)

    @commands.command(usage=cmd_data.show.usage, description=cmd_data.show.description, brief=cmd_data.show.brief)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def show(self, ctx: commands.Context) -> None:
        """保存番号または保存名称から画像を生成"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        args = ctx.message.content.split(" ", 1)  # 名称に空白が含まれることを苦慮して,1回のみ区切る
        code: str
        if len(args) == 1:  # 引数がない場合,作業場の画像を表示
            code = await self.bot.db.get_canvas(ctx.author.id)
        else:
            cond = args[1]  # 条件を取得 (名前はまたは番号)
            save_data = await self.bot.db.get_save_work(ctx.author.id)
            if cond.isdigit():  # 数字->インデックスの場合
                if 1 <= int(cond) <= len(save_data):  # 番号が保存済みの範囲である場合
                    code = save_data[int(cond)]["code"]
                else:  # 番号にあった作品がない場合
                    return await error_embed(ctx, self.bot.text.no_th_saved_work[user_lang].format(int(cond)))
            else:  # 名前の場合
                filtered_data = [d["code"] for d in save_data if d["name"] == cond]
                if filtered_data:  # 名前にあった作品が見つかった場合
                    code = filtered_data[0]
                else:  # 名前にあった作品がない場合
                    return await error_embed(ctx, self.bot.text.not_found_with_name[user_lang])
        await self.make_image(ctx, *(code_to_list(code)))

    @commands.command(usage=cmd_data.random.usage, description=cmd_data.random.description, brief=cmd_data.random.brief)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def random(self, ctx: commands.Context) -> None:
        """ランダムな装飾を表示"""
        # ランダムな各部位の番号を生成
        num_base = random.randint(self.bot.data.base.min, self.bot.data.base.max)
        num_character = random.randint(self.bot.data.character.min, self.bot.data.character.max)
        num_weapon = random.randint(self.bot.data.weapon.min, self.bot.data.weapon.max)
        num_head = random.randint(self.bot.data.head.min, self.bot.data.head.max)
        num_body = random.randint(self.bot.data.body.min, self.bot.data.body.max)
        num_back = random.randint(self.bot.data.back.min, self.bot.data.back.max)
        await self.make_image(ctx, num_base, num_character, num_weapon, num_head, num_body, num_back)

    @commands.command(aliases=["mylist"], usage=cmd_data.my.usage, description=cmd_data.my.description, brief=cmd_data.my.brief)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def my(self, ctx: commands.Context) -> None:
        """保存済みの作品リストを表示"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        save_data = await self.bot.db.get_save_work(ctx.author.id)
        total_pages = math.ceil(len(save_data) / 5)  # 必要なページ数を取得
        if total_pages == 0:  # 保存済み作品がない場合
            return await error_embed(ctx, self.bot.text.no_any_saved_work[user_lang])
        current_page = 1
        msg = await ctx.send(embed=self.my_embed(user_lang, save_data, current_page, total_pages, user_lang))
        if total_pages == 1:
            return  # 1ページのみの場合ページは不要なので終了
        await self.my_add_emoji(msg)
        while True:
            try:  # リアクション待機
                react, user = await self.bot.wait_for("reaction_add", timeout=30, check=lambda r, u: r.message.id == msg.id and u == ctx.author and str(r.emoji) in [self.bot.data.emoji.right, self.bot.data.emoji.left])
            except asyncio.TimeoutError:  # タイムアウト時
                try:  # リアクション削除
                    await msg.clear_reactions()
                except:
                    pass
                return
            try:  # 簡便のためユーザーのリアクションを削除
                await msg.remove_reaction(react, user)
            except:
                pass
            if str(react.emoji) == self.bot.data.emoji.right:
                if current_page == total_pages:
                    current_page = 1
                else:
                    current_page += 1
            elif str(react.emoji) == self.bot.data.emoji.left:
                if current_page == 1:
                    current_page = total_pages
                else:
                    current_page -= 1
            await msg.edit(embed=self.my_embed(user_lang, save_data, current_page, total_pages, user_lang))

    def my_embed(self, lang: int, save: dict, current: int, total: int, user_lang: int) -> discord.Embed:
        """myでのEmbedを作成"""
        embed = discord.Embed(title=self.bot.text.my_title[lang])
        desc = ""
        for index in range(current * 5 - 5, current * 5):  # 0~4, 5~9 ...と代入
            if index >= len(save):  # 保存数以上の場合終了
                break
            item_list = code_to_list(save[index]["code"])
            desc += f"`{str(index + 1).ljust(3)}:` **{save[index]['name']}**\n" \
                    f"`{str(save[index]['code']).rjust(10)}` {getattr(self.bot.data.base.emoji, 'e' + str(item_list[0]))} {getattr(self.bot.data.character.emoji, 'e' + str(item_list[1]))} {getattr(self.bot.data.weapon.emoji, 'e' + str(item_list[2]))} " \
                    f"{getattr(self.bot.data.head.emoji, 'e' + str(item_list[3]))} {getattr(self.bot.data.body.emoji, 'e' + str(item_list[4]))} {getattr(self.bot.data.back.emoji, 'e' + str(item_list[5]))}\n"
        embed.description = desc
        embed.set_footer(text=self.bot.text.showing_page[user_lang].format(current, total))
        return embed

    async def my_add_emoji(self, msg: discord.Message):
        """myでの絵文字追加"""
        await asyncio.gather(
            msg.add_reaction(self.bot.data.emoji.left),
            msg.add_reaction(self.bot.data.emoji.right)
        )

    @commands.command(aliases=["del", "remove", "rm"], usage=cmd_data.delete.usage, description=cmd_data.delete.description, brief=cmd_data.delete.brief)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete(self, ctx: commands.Context, *, cond: str) -> None:
        """保存済みの作品を削除"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        save_data = await self.bot.db.get_save_work(ctx.author.id)  # 保存済み作品の取得
        index: int
        if cond.isdigit():  # 数字->インデックスの場合
            if 1 <= int(cond) <= len(save_data):  # 番号が保存済みの範囲である場合
                index = int(cond) - 1
            else:  # 番号にあった作品がない場合
                return await error_embed(ctx, self.bot.text.no_th_saved_work[user_lang].format(int(cond)))
        else:  # 名前の場合
            filtered_data = [save_data.index(d) for d in save_data if d["name"] == cond]
            if filtered_data:  # 名前にあった作品が見つかった場合
                index = filtered_data[0]
            else:  # 名前にあった作品がない場合
                return await error_embed(ctx, self.bot.text.not_found_with_name[user_lang])
        rm_work = save_data.pop(index)  # 対象データの削除
        await self.bot.db.update_save_work(ctx.author.id, save_data)  # データを更新
        await success_embed(ctx, self.bot.text.deleted_work[user_lang].format(index + 1, rm_work["name"]))

    @commands.command(usage=cmd_data.load.usage, description=cmd_data.load.description, brief=cmd_data.load.brief)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def load(self, ctx: commands.Context, *, cond: str) -> None:
        """保存済み作品を読み込み"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        save_data = await self.bot.db.get_save_work(ctx.author.id)  # 保存済みデータの読み込み
        load_data: dict
        if cond.isdigit():  # 数字->インデックスの場合
            if 1 <= int(cond) <= len(save_data):  # 番号が保存済みの範囲である場合
                load_data = save_data[int(cond) - 1]
            else:  # 番号にあった作品がない場合
                return await error_embed(ctx, self.bot.text.no_th_saved_work[user_lang].format(int(cond)))
        else:  # 名前の場合
            filtered_data = [d for d in save_data if d["name"] == cond]
            if filtered_data:  # 名前にあった作品が見つかった場合
                load_data = filtered_data[0]
            else:  # 名前にあった作品がない場合
                return await error_embed(ctx, self.bot.text.not_found_with_name[user_lang])
        await self.bot.db.set_canvas(ctx.author.id, load_data["code"])  # 作業場データを更新
        await success_embed(ctx, self.bot.text.loaded_work[user_lang].format(save_data.index(load_data) + 1, load_data["name"]))

    @commands.command(usage=cmd_data.save.usage, description=cmd_data.save.description, brief=cmd_data.save.brief)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def save(self, ctx: commands.Context, *, cond: str) -> None:
        """作品を保存"""
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        save_data = await self.bot.db.get_save_work(ctx.author.id)  # 保存済みデータの取得
        if len(save_data) >= 20:
            return await error_embed(ctx, self.bot.text.save_up_to_20[user_lang])
        used_names = [data["name"] for data in save_data]  # 使用済みの名前のリストを取得
        if cond in used_names:  # 使用済みの場合
            return await error_embed(ctx, self.bot.text.name_already_used[user_lang])
        elif cond.isdigit():  # 数字のみの場合
            return await error_embed(ctx, self.bot.text.int_only_name_not_allowed[user_lang])
        elif not (1 <= len(cond) <= 20):  # 1~20文字を超過している場合
            return await error_embed(ctx, self.bot.text.name_length_between_1_20[user_lang])
        save_data.append({  # 新規データを追加
            "name": cond,
            "code": await self.bot.db.get_canvas(ctx.author.id)  # 現在の作業場のデータを取得
        })
        await self.bot.db.update_save_work(ctx.author.id, save_data)  # データを保存
        await success_embed(ctx, self.bot.text.saved_work[user_lang].format(cond))

    @commands.command(usage=cmd_data.set.usage, description=cmd_data.set.description, help=cmd_data.set.help, brief=cmd_data.set.brief)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def set(self, ctx: commands.Context, *, code: str) -> None:
        """ 装飾コードまたは各装飾の番号から全種類のアイテムを一括で登録 """
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        item = code_to_list(code)  # 指定されたコードをリストに変換
        if item is None:  # 不正な装飾コードの場合
            await error_embed(ctx, self.bot.text.wrong_costume_code[user_lang])
        elif (self.bot.data.base.min <= item[0] <= self.bot.data.base.max) and (self.bot.data.character.min <= item[1] <= self.bot.data.character.max) and \
                (self.bot.data.weapon.min <= item[2] <= self.bot.data.weapon.max) and (self.bot.data.head.min <= item[3] <= self.bot.data.head.max) and \
                (self.bot.data.body.min <= item[4] <= self.bot.data.body.max) and (self.bot.data.back.min <= item[5] <= self.bot.data.back.max):
            await self.bot.db.set_canvas(ctx.author.id, code)
            await self.make_image(ctx, *item)
        else:  # 各装飾番号が不正な場合
            await error_embed(ctx, self.bot.text.wrong_costume_code[user_lang])

    @commands.group(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def list(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
            await ctx.send(self.bot.text.missing_subcommand[user_lang].format(self.bot.PREFIX, "list"))

    @list.command(name="base")
    async def list_base(self, ctx: commands.Context):
        await self.list_selector(ctx, "base")

    @list.command(name="character")
    async def list_character(self, ctx: commands.Context):
        await self.list_selector(ctx, "character")

    @list.command(name="weapon")
    async def list_weapon(self, ctx: commands.Context):
        await self.list_selector(ctx, "weapon")

    @list.command(name="head")
    async def list_head(self, ctx: commands.Context):
        await self.list_selector(ctx, "head")

    @list.command(name="body")
    async def list_body(self, ctx: commands.Context):
        await self.list_selector(ctx, "body")

    @list.command(name="back")
    async def list_back(self, ctx: commands.Context):
        await self.list_selector(ctx, "back")

    async def list_selector(self, ctx, item_type):
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        max_page = getattr(self.bot.data, item_type).page
        embed = discord.Embed(title=self.bot.text.list_base_title[user_lang], color=0xffce9e)
        embed.description = self.get_list(item_type, 1)
        embed.set_footer(text=self.bot.text.showing_page[user_lang].format(1, max_page))
        msg = await ctx.send(embed=embed)
        if max_page == 1:
            return
        selector_emoji = [self.bot.data.emoji.left, self.bot.data.emoji.right]
        self.bot.loop.create_task(self.list_selector_emoji(msg, selector_emoji))
        page = 1
        while True:
            try:
                react, user = await self.bot.wait_for("reaction_add", timeout=30, check=lambda r, u: str(r.emoji) in selector_emoji and r.message.id == msg.id and u == ctx.author)
            except asyncio.TimeoutError:
                try:
                    await msg.clear_reactions()
                except:
                    pass
                finally:
                    return
            try:  # 簡便のためユーザーのリアクションを削除
                await msg.remove_reaction(react, user)
            except:
                pass
            if str(react.emoji) == self.bot.data.emoji.right:
                if page == max_page:
                    page = 1
                else:
                    page += 1
            elif str(react.emoji) == self.bot.data.emoji.left:
                if page == 1:
                    page = max_page
                else:
                    page -= 1
            embed = discord.Embed(title=getattr(self.bot.text, f"list_{item_type}_title")[user_lang], color=0xffce9e)
            embed.description = self.get_list(item_type, page)
            embed.set_footer(text=self.bot.text.showing_page[user_lang].format(page, max_page))
            await msg.edit(embed=embed)

    async def list_selector_emoji(self, msg, emoji_list):
        for emoji in emoji_list:
            await msg.add_reaction(emoji)

    @commands.group(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def add(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
            await ctx.send(self.bot.text.missing_subcommand[user_lang].format(self.bot.PREFIX, "add"))

    @add.command(name="base")
    async def add_base(self, ctx, *, cond):
        await self.add_selector(ctx, "base", cond)

    @add.command(name="character")
    async def add_character(self, ctx, *, cond):
        await self.add_selector(ctx, "character", cond)

    @add.command(name="weapon")
    async def add_weapon(self, ctx, *, cond):
        await self.add_selector(ctx, "weapon", cond)

    @add.command(name="head")
    async def add_head(self, ctx, *, cond):
        await self.add_selector(ctx, "head", cond)

    @add.command(name="body")
    async def add_body(self, ctx, *, cond):
        await self.add_selector(ctx, "body", cond)

    @add.command(name="back")
    async def add_back(self, ctx, *, cond):
        await self.add_selector(ctx, "back", cond)

    async def add_selector(self, ctx, item_type, cond):
        user_lang = await self.bot.db.get_lang(ctx.author.id, ctx.guild.region)
        code, result = self.find_item(cond, index=True, item_type=item_type)
        if code == 0:  # アイテムが見つかりませんでした
            await error_embed(ctx, result[user_lang])
        else:
            item = code_to_list(await self.bot.db.get_canvas(ctx.author.id))
            item[getattr(self.bot.data, result[0]).index] = int(result[1])
            await self.bot.db.set_canvas(ctx.author.id, list_to_code(item))
            await self.make_image(ctx, *item)


def setup(bot: MilkCoffee) -> None:
    bot.add_cog(Costume(bot))
