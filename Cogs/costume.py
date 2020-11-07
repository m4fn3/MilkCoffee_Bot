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

from .bot import MilkCoffee
from .data.item_data import ItemData
from .utils.item_parser import *
from .utils.messenger import error_embed, success_embed, normal_embed
from .utils.multilingual import *
from .menu import Menu


class Costume(commands.Cog):
    """装飾シミュレータを操作できるよ！好みの組合せを探そう！^You can operate the costume simulator! Find your favorite combination!^코스튬 시뮬레이터를 조작 할 수 있어! 원하는 조합을 찾자!^¡Bienvenido al simulador de drisfraces!"""

    def __init__(self, bot):
        self.bot = bot  # type: MilkCoffee
        self.item = ItemData()

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
            if self.item_info[item_type]["min"] <= int(item_name) <= self.item_info[item_type]["max"]:
                return 1, [item_type, item_name]
            else:
                return 0, ["アイテム番号が間違っています. (番号が小さすぎるか大きすぎます)", "Wrong item number.(The number is too small or too large)", "항목 번호가 잘못되었습니다. (숫자가 너무 작거나 큽니다)", "Número de artículo incorrecto (el número es demasiado pequeño o demasiado grande)"]
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
            return 0, ["検索結果がありません.もう一度名前を確認してください.", "No results. Please check name again.", "결과가 없습니다. 이름을 다시 확인하십시오.", "No hay resultados. Vuelva a comprobar el nombre."]
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
        """
        指定した種類のアイテムリストを取得
        Args:
            item_type (str): アイテムの種類
            page (str): ページ

        Returns:
            str: アイテム一覧
        """
        item_count = self.item_info[item_type]["max"]
        text = ""
        start_index = self.item_info[item_type]["min"] + 10 * (page - 1)
        for item_index in range(start_index, start_index + 10):
            if item_index > item_count:
                break
            text += f"{item_index} {self.emoji[item_type][str(item_index)]} {self.name[item_type][str(item_index)]}\n"
        return text

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await error_embed(ctx, self.bot.text.your_account_banned[get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.data.appeal_channel))
            raise Exception("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0,
                "costume": {
                    "canvas": "1o4s3k",
                    "save": []
                }
            }
            await self.bot.get_cog("Language").language_selector(ctx)
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

    async def make_image(self, ctx, base_id: int, character_id: int, weapon_id: int, head_id: int, body_id: int, back_id: int) -> None:
        """
        アイテム番号から画像を構築
        Args:
            ctx: Context
            base_id (int): baseの番号
            character_id (int): characterの番号
            weapon_id (int): weaponの番号
            head_id (int): headの番号
            body_id (int): bodyの番号
            back_id (int): backの番号

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
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
        base = self.convert_to_bytes(base)
        embed = discord.Embed()
        item_id = parse_item_list_to_code([base_id, character_id, weapon_id, head_id, body_id, back_id])
        text = f"{self.emoji['base'][str(base_id)]} {self.emoji['character'][str(character_id)]} {self.emoji['weapon'][str(weapon_id)]} {self.emoji['head'][str(head_id)]} {self.emoji['body'][str(body_id)]} {self.emoji['back'][str(back_id)]}"  # f"装飾コード: {item_id}"
        embed.add_field(name=self.bot.text.costume_table_base[user_lang], value=f"{base_id} {self.emoji['base'][str(base_id)]} {self.name['base'][str(base_id)]}")
        embed.add_field(name=self.bot.text.costume_table_character[user_lang], value=f"{character_id} {self.emoji['character'][str(character_id)]} {self.name['character'][str(character_id)]}")
        embed.add_field(name=self.bot.text.costume_table_weapon[user_lang], value=f"{weapon_id} {self.emoji['weapon'][str(weapon_id)]} {self.name['weapon'][str(weapon_id)]}")
        embed.add_field(name=self.bot.text.costume_table_head[user_lang], value=f"{head_id} {self.emoji['head'][str(head_id)]} {self.name['head'][str(head_id)]}")
        embed.add_field(name=self.bot.text.costume_table_body[user_lang], value=f"{body_id} {self.emoji['body'][str(body_id)]} {self.name['body'][str(body_id)]}")
        embed.add_field(name=self.bot.text.costume_table_back[user_lang], value=f"{back_id} {self.emoji['back'][str(back_id)]} {self.name['back'][str(back_id)]}")
        embed.set_footer(text=self.bot.text.costume_table_code[user_lang].format(item_id), icon_url="http://zorba.starfree.jp/MilkChoco/milkchoco.jpg")
        await ctx.send(text, embed=embed, file=discord.File(fp=io.BytesIO(base), filename="result.png"))
        return  # TODO: リザルト画像色付ける

    async def page_reaction_mover(self, message, author: int, max_page: int, now_page: int) -> (int, Any):
        """
        リアクションページ移動処理
        Args:
            message: message
            author(int): コマンドの送信者
            max_page: 最大ページ
            now_page: 現在のページ

        Returns:
            int, Any:
                0 ... タイムアウト
                1 ... リアクションを検知, ページ数 (int)
        """
        new_page: int

        def check(r, u):
            return r.message.id == message.id and u == author and str(r.emoji) in ["◀️", "▶️"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=check)
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

    @commands.command(aliases=["m"])
    async def menu(self, ctx):
        try:
            code = "41ihuiq3m"  # TODO: ユーザーの作業場の装飾コードで初期化 - db
            user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
            menu = Menu(ctx, self.bot, user_lang, code)
            await menu.run()
        except:
            print(traceback2.format_exc())

    @commands.command(usage="set [装飾コード|各装飾の番号]^set [decoration code | number of each decoration]^set [장식 코드 | 각 장식 번호]^set [código de decoración | número de cada decoración]",
                      description="装飾コードまたは各装飾の番号で設定できるよ!^You can set it with the decoration code or the number of each decoration!^코스튬 코드 또는 각 코스튬의 번호로 설정할 수 있어!^¡Puedes configurarlo con el código de decoración o el número de cada decoración!",
                      help="この二つのコマンドは両方ミルクアサルト初期武器(装飾無し)になるよ!。\n`{0}set 1o4s3k` ... 装飾コード1o4s3kで設定\n`{0}set 0 1 1 0 0 0` ... 各アイテムの番号で設定\n装飾コードは他の人の装飾を真似する際に便利だよ!^Both of these commands will be Milk Assault initial weapons (no decoration)!\n`{0}set 1o4s3k` ... Set with decoration code 1o4s3k\n`{0}set 0 1 1 0 0 0` ... Set by the number of each item\nThe decoration code is useful for imitating other people's decorations!^이 두 명령은 모두 밀크팀, 기본총(코스튬 없음)일거야!\n`{0}set 1o4s3k` ... 장식 코드 1o4s3k로 설정\n`{0}set 0 1 1 0 0 0` ... 각 항목의 번호로 설정\n장식 코드는 다른 사람의 코사튬을 따라하는데 유용할거야!^¡Ambos comandos serán armas iniciales de Milk Assault (sin decoración)!\n`{0}set 1o4s3k` ... Set con código de decoración 1o4s3k\n`{0}set 0 1 1 0 0 0` ... Establecido por el número de cada elemento\n¡El código de decoración es útil para imitar la decoración de otras personas!")
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

    @commands.command(usage="show (保存番号|保存名称)^show (save number | save name)^show (저장 번호 | 저장 명칭)^show (guardar número | guardar nombre)", brief="現在の装飾を表示できるよ!^Show the current decoration!^현재의 장식을 표시 할 수 있어!^¡Puede mostrar la decoración actual!",
                      description="現在の装飾を表示できるよ!保存番号を指定したら、保存した作品の中から番号にあった作品を表示してあげる!^Show the current decoration! After specifying the save number, the works that match the number will be displayed from the saved works!^현재의 장식을 표시 할  수있어! 저장 번호를 지정한 후 저장 한 작품 중에서 번호에 있던 작품을 보여주지!^¡Puede mostrar la decoración actual! Después de especificar el número de guardado, las obras que coincidan con el número se mostrarán de las obras guardadas.",
                      help="`{0}show` ... 現在の装飾を表示`\n{0}show 1` ... 1番目に保存された装飾を表示\n`{0}show Untitled1` ... Untitled1という名前で保存された装飾を表示^`{0}show` ... Show current decoration`\n{0}show 1` ... Show the first saved decoration\n`{0}show Untitled 1` ... Show decorations saved as Untitled 1^`{0}show` ... 현재의 장식을 표시`\n{0}show 1` ... 첫번째로 저장된 장식을 표시\n`{0}show 제목 1` ... 제목 1로 저장 된 장식을 표시^`{0}show` ... Mostrar decoración actual`\n{0}show 1` ... Mostrar la primera decoración guardada\n`{0}show Untitled 1` ... Muestra las decoraciones guardadas con el nombre Untitled 1")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def show(self, ctx) -> None:
        """
        保存番号または保存名称から保存された画像または、作業中の画像を表示
        Args:
            ctx: Context

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        listed = ctx.message.content.split(" ", 1)
        item_code: str
        if len(listed) == 1:
            item_code = self.bot.database[str(ctx.author.id)]["costume"]["canvas"]
        else:
            index = listed[1]
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
            item_code = self.bot.database[str(ctx.author.id)]["costume"]["save"][item_index]["data"]
        items = parse_item_code_to_list(item_code)
        await self.make_image(ctx, items[0], items[1], items[2], items[3], items[4], items[5])

    @commands.command(usage="load [保存番号|保存名称]^load [save number | save name]^load [저장 번호 | 저장 명칭]^load [guardar número | guardar nombre]", brief="保存した作品を作業場に読み込むよ!^Load the saved work into the current workshop!^저장된 작업을 현재 작업장에로드하십시오!^¡Carga el trabajo guardado en el taller actual!",
                      description="保存した作品を番号または名称で指定して、現在の作業場に読み込むよ!^Load the saved work  into the current workshop  by number or name!^저장 한 작품을 번호 또는 이름을 지정하여 현재 작업 공간에 불러와요!^Especifique el trabajo guardado por número o nombre y cárguelo en el lugar de trabajo actual.",
                      help="`{0}load 1` ... 1番目に保存された作品を読み込む\n`{0}load Untitled1` ... Untitled1という名前で保存された作品を読み込む^`{0}load 1` ... Load the first saved work\n`{0}load Untitled 1` ... Load the work saved under the name Untitled 1^`{0}load 1` ... 1 번째로 저장된 작품을 읽어!\n`{0}load 제목 1` ... 제목 1로 저장 된 작품을 읽어!^`{0}load 1` ... Carga el primer trabajo guardado\n`{0}load Untitled 1` ... Carga el trabajo guardado con el nombre Untitled 1")
    async def load(self, ctx, *, index: str) -> None:
        """
        保存された作品を作業場に読み込む
        Args:
        Args:
            ctx: Context
            index (str): 保存番号 or 保存名称

        Returns:
            None
        """
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

    @commands.command(usage="save (保存名称)^save (save name)^save (저장 명칭)^save (guardar nombre)", brief="現在の装飾を保存できるよ!^Save the current decoration!^현재의 장식을 저장 할 수 있어!^¡Puede guardar la decoración actual!",
                      description="現在の装飾を保存できるよ!保存名称を指定しなかったら、'Untitled1'みたいな名前を自動でつけとくね!^Save the current decoration! If you don't specify a save name, I automatically give it a name like 'Untitled 1'!^현재의 장식을 저장 할 수 있어! 저장할 이름을 지정하지 않으면, 'Untitled 1'같은 이름을 자동으로 저장할거야!^¡Puede guardar la decoración actual! Si no especifica un nombre para guardar, puede darle automáticamente un nombre como 'Untitled 1'.",
                      help="`{0}save` ... 作品を保存します(名前は自動でUntitled1のように付けられます)\n`{0}save 新作品` ... 新作品という名前で作品を保存します^`{0} save` ... Save your work (named automatically like Untitled 1)\n`{0}save new work` ... Save the work with the name new work^`{0} save` ... 작품을 저장합니다 (이름은 자동으로 제목 1과 같이 지정됩니다)\n`{0}save 새로운 작품`... 새로운 작품이라는 이름으로 작품을 저장합니다^`{0}save` ... Guarda tu trabajo (nombrado automáticamente como Sin título 1)\n`{0}save nuevo trabajo` ... Guardar el trabajo con el nombre nuevo trabajo")
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
        await sucess_embed(ctx, self.bot.text.saved_work[user_lang].format(name))

    @commands.command(aliases=["mylist"], usage="my (ページ)^my (page)^my (페이지)^my (página)", brief="保存した作品の一覧を表示するよ!^Display a list of saved works!^저장된 작업 목록을 표시 할 수 있어!^¡Puedes mostrar una lista de trabajos guardados!",
                      description="保存した作品の一覧を表示できるよ!ページを指定しなかったら、1ページ目から表示するよ!でも、リアクションを押してページ移動もできるから心配しないでね!^Display a list of saved works! If you do not specify a page, it will be displayed from the first page! But don't worry because you can also move pages by pressing reaction!^저장된 작업 목록을 표시 할 수 있어! 페이지를 지정하지 않으면, 1 페이지에서 볼 수 있어!하지만 반응을 눌러 페이지 이동도 할 수 있으니까 걱정하지 마!^¡Puedes mostrar una lista de trabajos guardados! Si no especificas una página, se mostrará desde la primera página ¡Pero no te preocupes porque también puedes mover páginas presionando reacción!",
                      help="`{0}my` ... 保存した作品集の1ページ目を表示します\n`{0}my 2` ... 保存した作品集の2ページ目を表示します^`{0}my` ... Displays the first page of the saved work collection\n`{0}my 2` ... Displays the second page of the saved work collection^`{0}my` ... 저장된 작품집의 첫 페이지를 표시합니다\n`{0}my 2` ... 저장된 작품집의 두 번째 페이지를 표시합니다^`{0}my` ... Muestra la primera página de la colección de trabajo guardada\n`{0}my 2` ... Muestra la segunda página de la colección de trabajo guardada")
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
            item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["data"]
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
                item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["data"]
                item_list = parse_item_code_to_list(item_id)
                text = f"{item_id}  {self.emoji['base'][str(item_list[0])]} {self.emoji['character'][str(item_list[1])]} {self.emoji['weapon'][str(item_list[2])]} {self.emoji['head'][str(item_list[3])]} {self.emoji['body'][str(item_list[4])]} {self.emoji['back'][str(item_list[5])]}"
                embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['costume']['save'][index - 1]['name']}", value=text, inline=False)
            await message.edit(embed=embed)

    @commands.command(aliases=["remove", "del", "rm"], usage="delete [保存番号|保存名称]^delete [save number | save name]^delete 저장 번호 | 저장 명칭]^delete [guardar número | guardar nombre]", brief="保存した作品を削除するよ!^Delete the saved work by number or name!^저장 한 작품에 번호 또는 이름을 지정하고 삭제하는거야!^Elimina el trabajo guardado especificando el número o el nombre",
                      description="保存した作品を番号または名称で指定して削除するよ!一度削除したらその作品は戻せないから気を付けてね!^Delete the saved work by number or name! Be careful because once you delete it, you cannot restore it!^저장 한 작품에 번호 또는 이름을 지정하고 삭제하는거야! 한 번 삭제하면 그 작품은 되돌릴 수 없기 때문에 조심해줘!^Elimina el trabajo guardado especificando el número o el nombre ¡Ten cuidado porque una vez eliminado, el trabajo no se puede restaurar!",
                      help="`{0}delete 1` ... 1番目に保存された作品を削除します\n`{0}delete 旧作品`... 旧作品という名前の作品を削除します^`{0}delete 1` ... Delete the first saved work\n`{0}delete Old work` ... Deletes the work named Old work^`{0}delete 1` ... 1 번째에 저장된 작업을 삭제합니다\n`{0}delete 이전 작품`... 이전 작품이라는 작품을 삭제합니다^`{0}delete 1` ... Elimina el primer trabajo guardado\n`{0}delete Old work` ... Elimina el trabajo llamado Old work")
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

    @commands.command(usage="random^random^random^random", description="ランダムな装飾を作成します!^Make random costume!^무작위 의상을 만들 수 있습니다^puede hacer un disfraz al azar")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def random(self, ctx):
        num_base = random.randint(self.item_info["base"]["min"], self.item_info["base"]["max"])
        num_character = random.randint(self.item_info["character"]["min"], self.item_info["character"]["max"])
        num_weapon = random.randint(self.item_info["weapon"]["min"], self.item_info["weapon"]["max"])
        num_head = random.randint(self.item_info["head"]["min"], self.item_info["head"]["max"])
        num_body = random.randint(self.item_info["body"]["min"], self.item_info["body"]["max"])
        num_back = random.randint(self.item_info["back"]["min"], self.item_info["back"]["max"])
        await self.make_image(ctx, num_base, num_character, num_weapon, num_head, num_body, num_back)


def setup(bot):
    bot.add_cog(Costume(bot))
