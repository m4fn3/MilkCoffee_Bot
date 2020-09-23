from discord.ext import commands
from PIL import Image
from typing import Any
import asyncio, discord, io, json, re, difflib, traceback2
from item_parser import *
from multilingual import *


class Costume(commands.Cog):
    """装飾シミュレータを操作できるよ！好みの組合せを探そう！^You can operate the decoration simulator! Find your favorite combination!^코스튬 시뮬레이터를 조작 할 수 있어! 원하는 조합을 찾자!^¡Establece notificaciones!"""

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
        if self.bot.maintenance and str(ctx.author.id) not in self.bot.ADMIN:
            await ctx.send(f"現在BOTはメンテナンス中です。\n理由: {self.bot.maintenance}\n詳しい情報については公式サーバーにてご確認ください。")
            raise commands.CommandError("maintenance-error")
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(f"あなたのアカウントはBANされています(´;ω;｀)\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
            raise commands.CommandError("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "costume": {
                    "canvas": "1o4s3k",
                    "save": []
                }
            }
            await self.process_new_user(ctx.message)
        elif "costume" not in self.bot.database[str(ctx.author.id)]:
            self.bot.database[str(ctx.author.id)]["costume"] = {
                "canvas": "1o4s3k",
                "save": []
            }
            await self.process_new_user(ctx.message)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"引数が不足しているよ!.\n使い方: `{self.bot.PREFIX}{ctx.command.usage}`\n詳しくは `{self.bot.PREFIX}help {ctx.command.qualified_name}`")
        else:
            await ctx.send(f"エラーが発生しました。管理者にお尋ねください。\n{error}")

    async def process_new_user(self, message):
        embed = discord.Embed(title="装飾シミュレータへようこそ!", color=0x00ffff)
        embed.description = f"""
装飾シミュレータ操作用コマンドのリストは`{self.bot.PREFIX}help Costume`で確認できるよ!
m!add (base/character/weapon/head/body/back) 番号 
m!list (base/character/weapon/head/body/back)
例:
`m!list character`
`m!add character 1`
実際に上の例にあるコマンドを使ってみてね！
もっと知りたいって人はこの動画を見てね！
[https://www.youtube.com/watch?v=WgZ83Dt955s](https://www.youtube.com/watch?v=WgZ83Dt955s)
        """
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

    @commands.command(usage="set [装飾コード|各装飾の番号]^set [decoration code | number of each decoration]^set [장식 코드 | 각 장식 번호]^set [código de decoración | número de cada decoración]", description="装飾コードまたは各装飾の番号で設定できるよ!^You can set it with the decoration code or the number of each decoration!^코스튬 코드 또는 각 코스튬의 번호로 설정할 수 있어!^¡Puedes configurarlo con el código de decoración o el número de cada decoración!", help="この二つのコマンドは両方ミルクアサルト初期武器(装飾無し)になるよ!。\n`{}set 1o4s3k` ... 装飾コード1o4s3kで設定\n`{}set 0 1 1 0 0 0` ... 各アイテムの番号で設定\n装飾コードは他の人の装飾を真似する際に便利だよ!^Both of these commands will be Milk Assault initial weapons (no decoration)!\n`{} set 1o4s3k` ... Set with decoration code 1o4s3k\n`{} set 0 1 1 0 0 0` ... Set by the number of each item\nThe decoration code is useful for imitating other people's decorations!^이 두 명령은 모두 밀크팀, 기본총(코스튬 없음)일거야!\n`{} set 1o4s3k` ... 장식 코드 1o4s3k로 설정\n`{} set 0 1 1 0 0 0` ... 각 항목의 번호로 설정\n장식 코드는 다른 사람의 코사튬을 따라하는데 유용할거야!^¡Ambos comandos serán armas iniciales de Milk Assault (sin decoración)!\n`{} set 1o4s3k` ... Set con código de decoración 1o4s3k\n`{} set 0 1 1 0 0 0` ... Establecido por el número de cada elemento\n¡El código de decoración es útil para imitar la decoración de otras personas!")
    async def set(self, ctx, *, item) -> None:
        """
        装飾コードまたは各装飾の番号から全種類のアイテムを一括で登録
        Args:
            ctx: Context
            item: 装飾コード or 各装飾の番号

        Returns:
            None
        """
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

    @commands.command(usage="show (保存番号|保存名称)^show (save number | save name)^show (저장 번호 | 저장 명칭)^show (guardar número | guardar nombre)", brief="現在の装飾を表示できるよ!^Show the current decoration!^현재의 장식을 표시 할  수있어!^¡Puede mostrar la decoración actual!", description="現在の装飾を表示できるよ!保存番号を指定したら、保存した作品の中から番号にあった作品を表示してあげる!^Show the current decoration! After specifying the save number, the works that match the number will be displayed from the saved works!^현재의 장식을 표시 할  수있어! 저장 번호를 지정한 후 저장 한 작품 중에서 번호에 있던 작품을 보여주지!^¡Puede mostrar la decoración actual! Después de especificar el número de guardado, las obras que coincidan con el número se mostrarán de las obras guardadas.", help="`{}show` ... 現在の装飾を表示`\n{}show 1` ... 1番目に保存された装飾を表示\n`{}show Untitled1` ... Untitled1という名前で保存された装飾を表示^`<prefix>show` ... Show current decoration`/n<prefix>show 1` ... Show the first saved decoration\n`<prefix>show Untitled 1` ... Show decorations saved as Untitled 1^`<prefix>show` ... 현재의 장식을 표시`\n<prefix>show 1` ... 첫번째로 저장된 장식을 표시\n`<prefix>show 제목 1` ... 제목 1로 저장 된 장식을 표시^`<prefijo>show` ... Mostrar decoración actual`\n<prefijo>show 1` ... Mostrar la primera decoración guardada\n`<prefijo>show Untitled 1` ... Muestra las decoraciones guardadas con el nombre Untitled 1")
    async def show(self, ctx) -> None:
        """
        保存番号または保存名称から保存された画像または、作業中の画像を表示
        Args:
            ctx: Context

        Returns:
            None
        """
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
                    return await ctx.send(f"{index}番目に保存された作品はないよ!.")
            elif index.isdigit():
                return await ctx.send("1~20の間で指定してね!.")
            else:
                used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
                if index in used_name_list:
                    item_index = used_name_list.index(index)
                else:
                    return await ctx.send("そのような名前の作品はないよ!.")
            item_code = self.bot.database[str(ctx.author.id)]["costume"]["save"][item_index]["data"]
        items = parse_item_code_to_list(item_code)
        await self.make_image(ctx, items[0], items[1], items[2], items[3], items[4], items[5])

    @commands.command(usage="load [保存番号|保存名称]^load [save number | save name]^load [저장 번호 | 저장 명칭]^load [guardar número | guardar nombre]", brief="保存した作品を作業場に読み込むよ!^Load the saved work into the current workshop!^저장된 작업을 현재 작업장에로드하십시오!^¡Carga el trabajo guardado en el taller actual!", description="保存した作品を番号または名称で指定して、現在の作業場に読み込むよ!^Load the saved work  into the current workshop  by number or name!^저장 한 작품을 번호 또는 이름을 지정하여 현재 작업 공간에 불러와요!^Especifique el trabajo guardado por número o nombre y cárguelo en el lugar de trabajo actual.", help="`{}load 1` ... 1番目に保存された作品を読み込む\n`{}load Untitled1` ... Untitled1という名前で保存された作品を読み込む^`<prefix> load 1` ... Load the first saved work\n`<prefix>load Untitled 1` ... Load the work saved under the name Untitled 1^`<prefix>load 1` ... 1 번째로 저장된 작품을 읽어!\n`<prefix>load 제목 1` ... 제목 1로 저장 된 작품을 읽어!^`<prefijo>load 1` ... Carga el primer trabajo guardado\n`<prefijo>load Untitled 1` ... Carga el trabajo guardado con el nombre Untitled 1")
    async def load(self, ctx, *, index: str) -> None:
        """
        保存された作品を作業場に読み込む
        Args:
            ctx: Context
            index (str): 保存番号 or 保存名称

        Returns:
            None
        """
        item_index: int
        if index.isdigit() and 1 <= int(index) <= 20:
            item_count = len(self.bot.database[str(ctx.author.id)]["costume"]["save"])
            if 0 <= int(index) <= item_count:
                item_index = int(index) - 1
            else:
                return await ctx.send(f"{index}番目に保存された作品はないよ!.")
        elif index.isdigit():
            return await ctx.send("1~20の間で指定してね!.")
        else:
            used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
            if index in used_name_list:
                item_index = used_name_list.index(index)
            else:
                return await ctx.send("そのような名前の作品はないよ!")
        self.bot.database[str(ctx.author.id)]["costume"]["canvas"] = self.bot.database[str(ctx.author.id)]["costume"]["save"][item_index]["data"]
        await ctx.send(f"{item_index + 1}番目の\"{self.bot.database[str(ctx.author.id)]['costume']['save'][item_index]['name']}\"を読み込みました.")

    @commands.command(usage="save (保存名称)^save (save name)^save (저장 명칭)^save (guardar nombre)", brief="現在の装飾を保存できるよ!^Save the current decoration!^현재의 장식을 저장 할 수 있어!^¡Puede guardar la decoración actual!", description="現在の装飾を保存できるよ!保存名称を指定しなかったら、'Untitled1'みたいな名前を自動でつけとくね!^Save the current decoration! If you don't specify a save name, I automatically give it a name like 'Untitled 1'!^현재의 장식을 저장 할 수 있어! 저장할 이름을 지정하지 않으면, 'Untitled 1'같은 이름을 자동으로 저장할거야!^¡Puede guardar la decoración actual! Si no especifica un nombre para guardar, puede darle automáticamente un nombre como 'Untitled 1'.", help="`{}save` ... 作品を保存します(名前は自動でUntitled1のように付けられます)\n`{}save 新作品` ... 新作品という名前で作品を保存します^`<prefix> save` ... Save your work (named automatically like Untitled 1)\n`<prefix>save new work` ... Save the work with the name new work^`<prefix> save` ... 작품을 저장합니다 (이름은 자동으로 제목 1과 같이 지정됩니다)\n`<prefix>save 새로운 작품`... 새로운 작품이라는 이름으로 작품을 저장합니다^`<prefijo>save` ... Guarda tu trabajo (nombrado automáticamente como Sin título 1)\n`<prefijo>save nuevo trabajo` ... Guardar el trabajo con el nombre nuevo trabajo")
    async def save(self, ctx) -> None:
        """
        現在の装飾を保存
        Args:
            ctx: Context

        Returns:
            None
        """
        name: str
        listed = ctx.message.content.split(" ", 1)
        if len(self.bot.database[str(ctx.author.id)]["costume"]["save"]) == 20:
            return await ctx.send("保存できるのは20個までだよ! 不要なものを削除してから保存してね!")
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
                return await ctx.send("数字のみの名前は使用できないよ!")
            elif listed[1] in used_name_list:
                return await ctx.send("この名前は既に他の作品についてるよ!.")
            elif len(listed[1]) < 1 or 20 < len(listed[1]):
                return await ctx.send("名称は1文字以上20文字以下で指定してね!.")
            name = listed[1]
        self.bot.database[str(ctx.author.id)]["costume"]["save"].append(
            {
                "name": name,
                "data": self.bot.database[str(ctx.author.id)]["costume"]["canvas"]
            }
        )
        await ctx.send(f"保存したよ!. 名称: '{name}'")

    @commands.command(aliases=["mylist"], usage="my (ページ)^my (page)^my (페이지)^my (página)", brief="保存した作品の一覧を表示するよ!^Display a list of saved works!^저장된 작업 목록을 표시 할 수 있어!^¡Puedes mostrar una lista de trabajos guardados!", description="保存した作品の一覧を表示できるよ!ページを指定しなかったら、1ページ目から表示するよ!でも、リアクションを押してページ移動もできるから心配しないでね!^Display a list of saved works! If you do not specify a page, it will be displayed from the first page! But don't worry because you can also move pages by pressing reaction!^저장된 작업 목록을 표시 할 수 있어! 페이지를 지정하지 않으면, 1 페이지에서 볼 수 있어!하지만 반응을 눌러 페이지 이동도 할 수 있으니까 걱정하지 마!^¡Puedes mostrar una lista de trabajos guardados! Si no especificas una página, se mostrará desde la primera página ¡Pero no te preocupes porque también puedes mover páginas presionando reacción!", help="`{}my` ... 保存した作品集の1ページ目を表示します\n`{}my 2` ... 保存した作品集の2ページ目を表示します^`<prefix>my` ... Displays the first page of the saved work collection\n`<prefix>my 2` ... Displays the second page of the saved work collection^`<prefix>my` ... 저장된 작품집의 첫 페이지를 표시합니다\n`<prefix>my 2` ... 저장된 작품집의 두 번째 페이지를 표시합니다^`<prefijo>my` ... Muestra la primera página de la colección de trabajo guardada\n`<prefijo>my 2` ... Muestra la segunda página de la colección de trabajo guardada")
    async def my(self, ctx) -> None:
        """
        保存した作品を表示
        Args:
            ctx: Context

        Returns:
            None
        """
        listed = ctx.message.content.split()
        page: int
        if len(listed) == 1:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 4:
            page = int(listed[1])
        elif listed[1].isdigit():
            return await ctx.send("ページ数は1~4で指定してね!")
        else:
            return await ctx.send("ページ数は整数で1~4で指定してね!")
        item_count = len(self.bot.database[str(ctx.author.id)]["costume"]["save"])
        embed = discord.Embed(title=f"保存した作品集 ({page} / 4 ページ)")
        embed.description = "左の数字が保存番号、その横の名前が保存名称だよ!。その下の英数字6,7桁の文字列が装飾コードだよ!"
        for index in range(page*5-4, page*5+1):  # 1-5 6-10 11-15 16-20
            if index > item_count:
                break
            item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index-1]["data"]
            item_list = parse_item_code_to_list(item_id)
            text = f"{item_id}  {self.emoji['base'][str(item_list[0])]} {self.emoji['character'][str(item_list[1])]} {self.emoji['weapon'][str(item_list[2])]} {self.emoji['head'][str(item_list[3])]} {self.emoji['body'][str(item_list[4])]} {self.emoji['back'][str(item_list[5])]}"
            embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['costume']['save'][index-1]['name']}", value=text, inline=False)
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 4, page)
            if code == 0:
                break
            page = new_page
            embed = discord.Embed(title=f"保存した作品集 ({page} / 4 ページ)")
            embed.description = "左の数字が保存番号、その横の名前が保存名称だよ!。その下の英数字6,7桁の文字列が装飾コードだよ!"
            for index in range(page * 5 - 4, page * 5 + 1):  # 1-5 6-10 11-15 16-20
                if index > item_count:
                    break
                item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["data"]
                item_list = parse_item_code_to_list(item_id)
                text = f"{item_id}  {self.emoji['base'][str(item_list[0])]} {self.emoji['character'][str(item_list[1])]} {self.emoji['weapon'][str(item_list[2])]} {self.emoji['head'][str(item_list[3])]} {self.emoji['body'][str(item_list[4])]} {self.emoji['back'][str(item_list[5])]}"
                embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['costume']['save'][index - 1]['name']}", value=text, inline=False)
            await message.edit(embed=embed)

    @commands.command(aliases=["remove", "del", "rm"], usage="delete [保存番号|保存名称]^delete [save number | save name]^delete 저장 번호 | 저장 명칭]^delete [guardar número | guardar nombre]", brief="保存した作品を削除するよ!^Delete the saved work by number or name!^저장 한 작품에 번호 또는 이름을 지정하고 삭제하는거야!Elimina el trabajo guardado especificando el número o el nombre^", description="保存した作品を番号または名称で指定して削除するよ!一度削除したらその作品は戻せないから気を付けてね!^Delete the saved work by number or name! Be careful because once you delete it, you cannot restore it!^저장 한 작품에 번호 또는 이름을 지정하고 삭제하는거야! 한 번 삭제하면 그 작품은 되돌릴 수 없기 때문에 조심해줘!^Elimina el trabajo guardado especificando el número o el nombre ¡Ten cuidado porque una vez eliminado, el trabajo no se puede restaurar!", help="`{}delete 1` ... 1番目に保存された作品を削除します\n`{}delete 旧作品`... 旧作品という名前の作品を削除します^`<prefix>delete 1` ... Delete the first saved work\n`<prefix>delete Old work` ... Deletes the work named Old work^`<prefix>delete 1` ... 1 번째에 저장된 작업을 삭제합니다\n`<prefix>delete 이전 작품`... 이전 작품이라는 작품을 삭제합니다^`<prefijo>delete 1` ... Elimina el primer trabajo guardado\n`<prefijo>delete Old work` ... Elimina el trabajo llamado Old work")
    async def delete(self, ctx, *, index) -> None:
        """
        保存した画像を削除
        Args:
            ctx: Context
            index: 保存番号 or 保存名称

        Returns:
            None
        """
        if index.isdigit() and 1 <= int(index) <= 20:
            item_count = len(self.bot.database[str(ctx.author.id)]["costume"]["save"])
            if 0 <= int(index) <= item_count:
                old_data = self.bot.database[str(ctx.author.id)]["costume"]["save"].pop(int(index)-1)
                await ctx.send(f"{index}番目の{old_data['name']}を削除したよ!")
            else:
                await ctx.send(f"{index}番目に保存された作品はないよ!")
        elif index.isdigit():
            await ctx.send("1~20の間で指定してね!")
        else:
            used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
            if index in used_name_list:
                item_index = used_name_list.index(index)
                old_data = self.bot.database[str(ctx.author.id)]["costume"]["save"].pop(item_index)
                await ctx.send(f"{item_index + 1}番目の{old_data['name']}を削除したよ!")
            else:
                await ctx.send("そのような名前の作品はないよ!")

    @commands.group(usage="add [種類] [番号|名称]^add [type] [number | name]^add [종류] [번호 | 명칭]^add [tipo] [número | nombre]", brief="アイテムを追加するよ!", description="アイテムを追加するよ!\n1つ目の'種類'にはbase/character/weapon/head/body/back(詳しくはhelpコマンドの?リアクションを押して確認してね)のいずれかを指定して、\n2つ目の'番号|名称'にはアイテムの名前または番号を指定してね!^Add an item!\nFor the first'type', specify one of base / character / weapon / head / body / back (for details, press the? Reaction of the help command to check).\nFor the second'number | name', specify the item's name or number!^항목을 추가 해요!\n첫 번째 '종류'는 base / character / weapon / head / body / back (자세한 내용은 help 명령어의 리액션을 눌러 확인주세요) 중 하나를 지정해\n두 번째 '번호 | 명칭'은 아이템의 이름 또는 번호를 지정해줘!^¡Agregaré un artículo!\nPara el primer 'tipo', especifique uno de base / character / weapon / head / body / back (para más detalles, presione? Reacción del comando de ayuda para verificar).\nPara el segundo 'número | nombre', especifique el nombre o número del artículo.", help="`{}add weapon AT` ... ATという名前の武器を追加します\n`{}add head 1` ... 1番の頭装飾を追加します^`<prefix>add weapon AT` ... Add a weapon named AT\n`<prefix>add head 1` ... Add the first head decoration^`<prefix>add weapon AT-43` ... AT-43이라는 무기를 추가합니다\n`<prefix>add head 1` ... 1 번 머리 코스튬을 추가합니다^`<prefijo>add weapon AT` ... Agregar un arma llamada AT\n`<prefijo>add head 1` ... Agregar la primera decoración de la cabeza")
    async def add(self, ctx) -> None:
        """
        アイテムを追加
        Args:
            ctx: Context

        Returns:
            None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"サブコマンドが不足しているよ!\n`{ctx.prefix}help add`で使い方を確認してね!")

    @add.command(name="item", aliases=["i"], usage="add item [名称]^add item [name]^add item [명칭]^add item [nombre]", description="アイテムを追加できるよ!名前を教えてくれたら、全種類の中から探すからね!^You can add items! If you tell me your name, I'll look for it in all types!^항목을 추가 할 수 있어! 이름을 가르쳐 주면 모든 종류 중에서 찾으니까!^¡Puedes agregar artículos! Si me dices tu nombre, ¡lo buscaré en todos los tipos!", help="検索対象が全種類で広いから、思っているものと違うアイテムとマッチする可能性もあるよ>< また、全種類対応だから各種類のアイテム番号は使えないよ.。\n`{}add item myocat` ... myocatという名前のアイテムを全種類から検索して追加します^Since the search target is wide for all types, there is a possibility that it will match items that are different from what you think.> <Also, since all types are supported, you cannot use each type of item number.\n`{}add item myocat` ... Search for and add an item named myocat from all types^검색 대상이 모든 종류기 때문에, 생각하는 것과 다른 아이템과 매치 할 가능성도 있어요> <또한 모든 종류에 대응하기 때문에 각 유형의 항목 번호는 사용할 수 없어 ..\n`{}add item myocat` ... myocat라는 항목을 모든 종류에서 검색하여 추가합니다^Dado que el objetivo de búsqueda es amplio para todos los tipos, existe la posibilidad de que coincida con elementos que son diferentes de lo que cree.\n`{}add item myocat` ... Buscar y agregar un elemento llamado myocat de todos los tipos")
    async def add_item(self, ctx, *, text) -> None:
        """
        全アイテムから条件に合ったアイテムを探索
        Args:
            ctx: Context
            text: 名称

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        code, result = self.find_item(text)
        if code == 0:
            return await ctx.send(result[user_lang])
        await ctx.send(f"このアイテムが見つかったよ!: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="base", aliases=["s", "bs"], usage="add base [番号|名称]^add base [number | name]^add base [번호 | 제목]^add base [número | nombre]", description="白黒を設定できるよ!^Set base color(black and white)!^밀크와 초코를 설정 할 수있어!^¡Puede configurar blanco y negro!", help="`{}add base 0` ... 0番目の色を設定します(白色)\n`{}add base choco` ... chocoを設定します（黒色)^`<prefix> add base 0` ... Set the 0th color (white)\n`<prefix> add base choco` ... Set choco (black)^`<prefix> add base 0` ... 0 번째 색상을 설정합니다 (밀크)\n`<prefix> add base choco` ... choco을 설정합니다 (초코)^`<prefijo> agregar base 0` ... Establecer el color 0 (blanco)\n`<prefijo> agregar base choco` ... Establecer choco (negro)")
    async def add_base(self, ctx, *, text) -> None:
        """
        baseの中から条件に合ったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:

        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        code, result = self.find_item(text, index=True, item_type="base")
        if code == 0:
            return await ctx.send(result[user_lang])
        await ctx.send(f"このアイテムが見つかったよ!: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="character", aliases=["c", "ch", "char"], usage="add character [番号|名称]", description="キャラクターを設定できるよ!。", help="`{}add character 2` ... 2番目のキャラクターを設定します\n`{}add character air` ... キャラクターをairに設定します")
    async def add_character(self, ctx, *, text):
        """
        characterの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        code, result = self.find_item(text, index=True, item_type="character")
        if code == 0:
            return await ctx.send(result[user_lang])
        await ctx.send(f"このアイテムが見つかったよ!: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="weapon", aliases=["w", "wp", "weap"], usage="add weapon [番号|名称]^add weapon [number | name]^add weapon [번호 | 제목]^add weapon [número | nombre]", description="武器を設定できるよ!^Set the weapon!^무기를 설정 할 수 있어!^¡Puedes configurar tu arma!", help="`{}add weapon 3` ... 3番目の武器を設定します\n`{}add weapon spyra` ... spyraを武器に設定します^`{}add weapon 3` ... Set the third weapon\n`{}add weapon spyra` ... Set spyra as a weapon^`{}add weapon 3` ... 3 번째 무기를 설정합니다\n`{}add weapon spyra` ... spyra을 무기로 설정합니다^`{}add weapon 3` ... Establecer la tercera arma\n`{}add weapon spyra` ... Establecer spyra como arma")
    async def add_weapon(self, ctx, *, text) -> None:
        """
        weaponの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        code, result = self.find_item(text, index=True, item_type="weapon")
        if code == 0:
            return await ctx.send(result[user_lang])
        await ctx.send(f"このアイテムが見つかったよ!: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="head", aliases=["h", "hd"], usage="add head [番号|名称]^add head [number | name]^add head [번호 | 제목]^add head [número | nombre]", description="頭装飾を設定できるよ!^Set the head decoration!^머리 장식을 설정 할 수 있어!^¡Puedes configurar la decoración de la cabeza!", help="`{}add head 4` ... 4番目の頭装飾を設定します\n`{}add head M.CHIKEN` ... M.CHIKENという名前の頭装飾を設定します^`{}add head 4` ... Set the 4th head decoration\n`{}add head M.CHIKEN` ... Set the head decoration named M.CHIKEN^`{}add head 4` ... 4 번째 머리 코스튬을 설정합니다\n`{}add head M.CHIKEN` ... M.CHIKEN라는 머리 코스튬을 설정합니다^`{}add head 4` ... Establecer la decoración de la cuarta cabeza\n`{}add head M.CHIKEN` ... Establecer la decoración de la cabeza llamada M.CHIKEN")
    async def add_head(self, ctx, *, text) -> None:
        """
        headの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        code, result = self.find_item(text, index=True, item_type="head")
        if code == 0:
            return await ctx.send(result[user_lang])
        await ctx.send(f"このアイテムが見つかったよ!: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="body", aliases=["d", "bd", "by"], usage="add body [番号|名称]^add body [number | name]^add body [번호 | 제목]^add body [número | nombre]", description="体装飾を設定できるよ!^Set the body decoration!^몸 장식을 설정 할 수있어!^¡Puedes configurar la decoración del cuerpo!", help="`{}add body 5`...番目の体装飾を設定します\n`{}add body n.s.suit` ... n.s.suitという名前の体装飾を設定します^`<prefix>add body 5` ... sets the third body decoration\n`<prefix> add body n.s.suit` ... Set a body decoration named n.s.suit\n^`<prefix> add body 5` ... 5번째 신체 장식을 설정합니다\n`<prefix> add body n.s.suit` ... n.s.suit라는 신체 코스튬을 설정합니다\n`<prefijo>add body 5` ... establece la decoración del tercer cuerpo\n`<prefijo>add body n.s.suit` ... Establece la decoración del cuerpo llamada n.s.suit")
    async def add_body(self, ctx, *, text) -> None:
        """
        bodyの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        code, result = self.find_item(text, index=True, item_type="body")
        if code == 0:
            return await ctx.send(result[user_lang])
        await ctx.send(f"このアイテムが見つかったよ!: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="back", aliases=["b", "bk", "bc"], usage="add back [番号|名称]^add back [number | name]^add back [번호 | 제목]^add back [número | nombre]", description="背中装飾を指定できるよ!^Set the back decoration!^허리 장식을 지정할 수 있어요!^¡Puedes especificar la decoración de la espalda!", help="`{}add back 6`...6番目の背中装飾を設定します\n`{}add back B.MOUSE` ... B.MOUSEという名前の背中装飾を設定します^`<prefix>add back 6` ... Set the 6th back decoration\n`<prefix>add back B.MOUSE` ... Set the back decoration named B.MOUSE^`<prefix>add back 6` ... 6 번째 등 코스튬을 설정합니다\n`<prefix>add back B.MOUSE` ... B.MOUSE라는 등 코스튬을 설정합니다^`<prefijo>add back 6` ... Establecer la sexta decoración trasera\n`<prefijo>add back B.MOUSE` ... Establecer la decoración de la espalda llamada B.MOUSE")
    async def add_back(self, ctx, *, text) -> None:
        """
        backの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        code, result = self.find_item(text, index=True, item_type="back")
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"このアイテムが見つかったよ!: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @commands.group(usage="list [種類]^list [type]^list [종류]^lista [tipo]", description="その種類のアイテム一覧を表示するよ!^Show a list of items of that type!^이 유형의 항목을 나열합니다!^¡Mostraré una lista de elementos de ese tipo!", help="`{}list character` ... キャラクターのリストを表示します\n`{}list weapon` ... 武器のリストを表示します^`{}list character` ... Show a list of characters\n`{}list weapon` ... Shows a list of weapons^`{}list character` ... 캐릭터의 목록을 표시합니다\n`{}list weapon` ... 무기의 목록을 표시합니다^`{}list character` ... Muestra una lista de caracteres\n`{}list weapon` ... Muestra una lista de armas")
    async def list(self, ctx) -> None:
        """
        アイテム一覧を表示
        Args:
            ctx: Context

        Returns:
            None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"サブコマンドが不足しているよ!\n`{ctx.prefix}help list`で使い方を確認できます。")

    @list.command(name="base", aliases=["s", "bs"], usage="list base^list base^list base^list base", description="白黒のリストを表示するよ!この場合は白と黒の二つしかないんだけどね💦^Show the base color list (black and white)! In this case there are only two, white and black 💦^색상의 목록을 표시합니다! 이 경우에는 밀크와 초코 밖에 없지만 💦^¡Te mostraré una lista en blanco y negro! En este caso solo hay dos, blanco y negro 💦", help="`{}list base` ... キャラ色のリストを表示します^`{}list base` ... Display a list of character colors^`{}list base` ... 캐릭터 색상의 목록을 표시합니다^`{}list base` ... Muestra una lista de colores de caracteres")
    async def list_base(self, ctx) -> None:
        """
        baseのアイテム一覧を検索
        Args:
            ctx: Context

        Returns:
            None
        """
        embed = discord.Embed(title="色一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("base", 1)
        embed.set_footer(text="1 / 1 ページを表示中")
        await ctx.send(embed=embed)

    @list.command(name="weapon", aliases=["w", "wp", "weap"], usage="list weapon^list weapon^list weapon^list weapon", description="武器のリストを表示するよ!^Show a list of weapons!^무기의 목록을 표시합니다!^¡Muestra una lista de armas!", help="``{}list weapon` ... 武器のリストを表示します^`{}list weapon` ... Shows a list of weapons^`{}list weapon` ... 무기의 목록을 표시합니다^`{}list weapon` ... Muestra una lista de armas")
    async def list_weapon(self, ctx) -> None:
        """
        weaponのアイテム一覧を検索
        Args:
            ctx: Context

        Returns:
            None
        """
        listed = ctx.message.content.split()
        page: int
        if len(listed) == 2:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 4:
            page = int(listed[1])
        elif listed[1].isdigit():
            return await ctx.send("ページ数は1~4で指定してね!")
        else:
            return await ctx.send("ページ数は整数で1~4で指定してね!")
        embed = discord.Embed(title="武器一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("weapon", page)
        embed.set_footer(text=f"{page} / 4 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 4, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("weapon", page)
            embed.set_footer(text=f"{page} / 4 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="character", aliases=["c", "ch", "char"], usage="list character^list character^list character^list character", description="キャラクターのリストを表示するよ!^Show the list of characters!^캐릭터의 목록을 표시합니다!^¡Muestre la lista de personajes!", help="`{}list character` ...キャラクターのリストを表示します^`{}list character` ... Show a list of characters^`{}list character` ... 캐릭터의 목록을 표시합니다^`{}list character` ... Muestra una lista de caracteres")
    async def list_character(self, ctx):
        """
        characterのアイテム一覧を検索
        Args:
            ctx: Context

        Returns:
            None
        """
        listed = ctx.message.content.split()
        page: int
        if len(listed) == 2:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 3:
            page = int(listed[1])
        elif listed[1].isdigit():
            return await ctx.send("ページ数は1~3で指定してね!")
        else:
            return await ctx.send("ページ数は整数で1~3で指定してね!")
        embed = discord.Embed(title="キャラ一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("character", page)
        embed.set_footer(text=f"{page} / 3 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 3, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("character", page)
            embed.set_footer(text=f"{page} / 3 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="head", aliases=["h", "hd"], usage="list head^list head^list head^list head", description="頭装飾のリストを表示するよ!^Show a list of headdresses!^머리 코스튬의 목록을 표시합니다!^¡Muestra una lista de tocados!", help="`{}list head` ... 頭装飾のリストを表示します^`{}list head` ... Shows a list of head decorations^`{}list head` ... 머리 코스튬의 목록을 표시합니다^`{}list head` ... Muestra una lista de decoraciones de cabeza")
    async def list_head(self, ctx):
        """
        headのアイテム一覧を検索
        Args:
            ctx: Context

        Returns:
            None
        """
        listed = ctx.message.content.split()
        page: int
        if len(listed) == 2:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 6:
            page = int(listed[1])
        elif listed[1].isdigit():
            return await ctx.send("ページ数は1~6で指定してね!")
        else:
            return await ctx.send("ページ数は整数で1~6で指定してね!")
        embed = discord.Embed(title="頭装飾一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("head", page)
        embed.set_footer(text=f"{page} / 6 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 6, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("head", page)
            embed.set_footer(text=f"{page} / 6 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="body", aliases=["d", "bd", "by"], usage="list body^list body^list body^list body", description="体装飾のリストを表示するよ!^Show a list of body decorations!^몸 코스튬의 목록을 표시합니다!^¡Muestre una lista de decoraciones corporales!", help="`{}list body` ... 体装飾のリストを表示します^`{}list body` ... Shows a list of body decorations^`{}list body` ... 몸 코스튬의 목록을 표시합니다^`{}list body` ... Muestra una lista de decoraciones corporales")
    async def list_body(self, ctx):
        """
        bodyのアイテム一覧を検索
        Args:
            ctx: Context

        Returns:
            None
        """
        listed = ctx.message.content.split()
        page: int
        if len(listed) == 2:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 7:
            page = int(listed[1])
        elif listed[1].isdigit():
            return await ctx.send("ページ数は1~7で指定してね!")
        else:
            return await ctx.send("ページ数は整数で1~7で指定してね!")
        embed = discord.Embed(title="体装飾一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("body", page)
        embed.set_footer(text=f"{page} / 7 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 7, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("body", page)
            embed.set_footer(text=f"{page} / 7 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="back", aliases=["b", "bc", "bk"], usage="list back^list back^list back^list back", description="背中装飾のリストを表示するよ!^Show a list of back decorations!^등 코스튬의 목록을 표시합니다!^¡Muestre una lista de decoraciones traseras!", help="`{}list back` ... 背中装飾のリストを表示します^`{}list back` ... Shows a list of back decorations^`{}list back` ... 등 코스튬의 목록을 표시합니다^¡Muestre una lista de decoraciones traseras!")
    async def list_back(self, ctx):
        """
        backのアイテム一覧を検索
        Args:
            ctx: Context

        Returns:
            None
        """
        listed = ctx.message.content.split()
        page: int
        if len(listed) == 2:
            page = 1
        elif listed[1].isdigit() and 1 <= int(listed[1]) <= 6:
            page = int(listed[1])
        elif listed[1].isdigit():
            return await ctx.send("ページ数は1~6で指定してね!")
        else:
            return await ctx.send("ページ数は整数で1~6で指定してね!")
        embed = discord.Embed(title="背中装飾一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("back", page)
        embed.set_footer(text=f"{page} / 6 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 6, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称だよ!\n" + self.get_list("back", page)
            embed.set_footer(text=f"{page} / 6 ページを表示中")
            await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(Costume(bot))

