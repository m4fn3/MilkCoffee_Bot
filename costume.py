from discord.ext import commands
from PIL import Image
from typing import Any
import asyncio, discord, io, json, re, difflib, traceback2
from item_parser import *


class Costume(commands.Cog):
    """装飾シミュレータを操作できます。"""

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
            await ctx.send(f"あなたのアカウントはBANされています。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
            raise commands.CommandError("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "costume": {
                    "canvas": "1o4s3k",
                    "save": []
                }
            }
        elif "costume" not in self.bot.database[str(ctx.author.id)]:
            self.bot.database[str(ctx.author.id)]["costume"] = {
                "canvas": "1o4s3k",
                "save": []
            }

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

    @commands.command(usage="set [装飾コード|各装飾の番号]", description="装飾コードまたは各装飾の番号で設定します.", help="これら二つはともにミルクアサルト初期武器(装飾無し)になります。\n`<prefix>set 1o4s3k` ... 装飾コード1o4s3kで設定\n`<prefix>set 0 1 1 0 0 0` ... 各アイテムの番号で設定\n装飾コードは他の人の装飾を真似する際に便利です。")
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

    @commands.command(usage="show (保存番号|保存名称)", description="現在の装飾を表示します。保存番号を指定した場合は、保存した作品の中から番号にあった作品を表示します。", help="`<prefix>show` ... 現在の装飾を表示`\n<prefix>show 1` ... 1番目に保存された装飾を表示\n`<prefix>show 無題1` ... 無題1という名前で保存された装飾を表示")
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
                    return await ctx.send(f"{index}番目に保存された作品はありません.")
            elif index.isdigit():
                return await ctx.send("1~20の間で指定してください.")
            else:
                used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
                if index in used_name_list:
                    item_index = used_name_list.index(index)
                else:
                    return await ctx.send("そのような名前の作品はありません.")
            item_code = self.bot.database[str(ctx.author.id)]["costume"]["save"][item_index]["data"]
        items = parse_item_code_to_list(item_code)
        await self.make_image(ctx, items[0], items[1], items[2], items[3], items[4], items[5])

    @commands.command(usage="load [保存番号|保存名称]", description="保存した作品を番号または名称で指定し、現在の作業場に読み込みます。", help="`<prefix>load 1` ... 1番目に保存された作品を読み込む\n`<prefix>load 無題1` ... 無題1という名前で保存された作品を読み込む")
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
                return await ctx.send(f"{index}番目に保存された作品はありません.")
        elif index.isdigit():
            return await ctx.send("1~20の間で指定してください.")
        else:
            used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
            if index in used_name_list:
                item_index = used_name_list.index(index)
            else:
                return await ctx.send("そのような名前の作品はありません.")
        self.bot.database[str(ctx.author.id)]["costume"]["canvas"] = self.bot.database[str(ctx.author.id)]["costume"]["save"][item_index]["data"]
        await ctx.send(f"{item_index + 1}番目の\"{self.bot.database[str(ctx.author.id)]['costume']['save'][item_index]['name']}\"を読み込みました.")

    @commands.command(usage="save (保存名称)", description="現在の装飾を保存します。保存名称を指定しなかった場合は、'無題1'のようになります。", help="`<prefix>save` ... 作品を保存します(名前は自動で無題1のように付けられます)\n`<prefix>save 新作品` ... 新作品という名前で作品を保存します")
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
            return await ctx.send("保存できるのは20個までです. 不要なものを削除してから保存して下さい!")
        used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
        if len(listed) == 1:
            count = 1
            while True:
                if f"無題{count}" not in used_name_list:
                    name = f"無題{count}"
                    break
                count += 1
        else:
            if listed[1].isdigit():
                return await ctx.send("数字のみの名前は使用できません.")
            elif listed[1] in used_name_list:
                return await ctx.send("この名前は既に使用しています.")
            elif len(listed[1]) < 1 or 20 < len(listed[1]):
                return await ctx.send("名称は1文字以上20文字以下で指定して下さい.")
            name = listed[1]
        self.bot.database[str(ctx.author.id)]["costume"]["save"].append(
            {
                "name": name,
                "data": self.bot.database[str(ctx.author.id)]["costume"]["canvas"]
            }
        )
        await ctx.send(f"保存しました. 名称: '{name}'")

    @commands.command(aliases=["mylist"], usage="my (ページ)", description="保存した作品の一覧を表示します。ページを指定しなかった場合は、1ページ目が表示されます。", help="`<prefix>my` ... 保存した作品集の1ページ目を表示します\n`<prefix>my 2` ... 保存した作品集の2ページ目を表示します")
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
            return await ctx.send("ページ数は1~4で指定してください!")
        else:
            return await ctx.send("ページ数は整数で1~4で指定してください!")
        item_count = len(self.bot.database[str(ctx.author.id)]["costume"]["save"])
        embed = discord.Embed(title=f"保存した作品集 ({page} / 4 ページ)")
        embed.description = "左の数字が保存番号、その横の名前が保存名称です。その下の英数字6,7桁の文字列が装飾コードです。"
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
            embed.description = "左の数字が保存番号、その横の名前が保存名称です。その下の英数字6,7桁の文字列が装飾コードです。"
            for index in range(page * 5 - 4, page * 5 + 1):  # 1-5 6-10 11-15 16-20
                if index > item_count:
                    break
                item_id = self.bot.database[str(ctx.author.id)]["costume"]["save"][index - 1]["data"]
                item_list = parse_item_code_to_list(item_id)
                text = f"{item_id}  {self.emoji['base'][str(item_list[0])]} {self.emoji['character'][str(item_list[1])]} {self.emoji['weapon'][str(item_list[2])]} {self.emoji['head'][str(item_list[3])]} {self.emoji['body'][str(item_list[4])]} {self.emoji['back'][str(item_list[5])]}"
                embed.add_field(name=f"{index} {self.bot.database[str(ctx.author.id)]['costume']['save'][index - 1]['name']}", value=text, inline=False)
            await message.edit(embed=embed)

    @commands.command(aliases=["remove", "del", "rm"], usage="delete [保存番号|保存名称]", description="保存した作品を番号または名称で指定して、削除します。", help="`<prefix>delete 1` ... 1番目に保存された作品を削除します\n`<prefix>delete 旧作品`... 旧作品という名前の作品を削除します")
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
                await ctx.send(f"{index}番目の{old_data['name']}を削除しました.")
            else:
                await ctx.send(f"{index}番目に保存された作品はありません.")
        elif index.isdigit():
            await ctx.send("1~20の間で指定してください.")
        else:
            used_name_list = [d.get("name") for d in self.bot.database[str(ctx.author.id)]["costume"]["save"]]
            if index in used_name_list:
                item_index = used_name_list.index(index)
                old_data = self.bot.database[str(ctx.author.id)]["costume"]["save"].pop(item_index)
                await ctx.send(f"{item_index + 1}番目の{old_data['name']}を削除しました.")
            else:
                await ctx.send("そのような名前の作品はありません.")

    @commands.group(usage="add [種類] [番号|名称]", description="アイテムを追加します。\n1つ目の'種類'にはbase/character/weapon/head/body/back(詳しくはhelpコマンドの?リアクションを押して確認)のいずれかを指定して、\n2つ目の'番号|名称'にはアイテムの名前または番号を指定してください。", help="`<prefix>add weapon AT` ... ATという名前の武器を追加します\n`<prefix>add head 1` ... 1番の頭装飾を追加します")
    async def add(self, ctx) -> None:
        """
        アイテムを追加
        Args:
            ctx: Context

        Returns:
            None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"サブコマンドが不足しています。\n`{ctx.prefix}help add`で使い方を確認できます。")

    @add.command(name="item", aliases=["i"], usage="add item [名称]", description="アイテムを追加します。名称を指定して、全種類の中から検索します。", help="検索対象が全種類と広いので、思っているものと違うアイテムとマッチする可能性があります。全種類対応なので各種類のアイテム番号は使用できません。\n`<prefix>add item myocat` ... myocatという名前のアイテムを全種類から検索して追加します")
    async def add_item(self, ctx, *, text) -> None:
        """
        全アイテムから条件に合ったアイテムを探索
        Args:
            ctx: Context
            text: 名称

        Returns:
            None
        """
        code, result = self.find_item(text)
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="base", aliases=["s", "bs"], usage="add base [番号|名称]", description="白黒を設定します。", help="`<prefix>add base 0` ... 0番目の色を設定します(白色)\n`<prefix>add base choco` ... chocoを設定します（黒色)")
    async def add_base(self, ctx, *, text) -> None:
        """
        baseの中から条件に合ったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:

        """
        code, result = self.find_item(text, index=True, item_type="base")
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="character", aliases=["c", "ch", "char"], usage="add character [番号|名称]", description="キャラクターを設定します。", help="`<prefix>add character 2` ... 2番目のキャラクターを設定します\n`<prefix>add character air` ... キャラクターをairに設定します")
    async def add_character(self, ctx, *, text):
        """
        characterの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        code, result = self.find_item(text, index=True, item_type="character")
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="weapon", aliases=["w", "wp", "weap"], usage="add weapon [番号|名称]", description="武器を設定します。", help="`<prefix>add weapon 3` ... 3番目の武器を設定します\n`<prefix>add weapon spyra` ... spyraを武器に設定します")
    async def add_weapon(self, ctx, *, text) -> None:
        """
        weaponの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        code, result = self.find_item(text, index=True, item_type="weapon")
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="head", aliases=["h", "hd"], usage="add head [番号|名称]", description="頭装飾を設定します。", help="`<prefix>add head 4` ... 4番目の頭装飾を設定します\n`<prefix>add head M.CHIKEN` ... M.CHIKENという名前の頭装飾を設定します")
    async def add_head(self, ctx, *, text) -> None:
        """
        headの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        code, result = self.find_item(text, index=True, item_type="head")
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="body", aliases=["d", "bd", "by"], usage="add body [番号|名称]", description="体装飾を設定します。", help="`<prefix>add body 5`...番目の体装飾を設定します\n`<prefix>add body n.s.suit` ... n.s.suitという名前の体装飾を設定します")
    async def add_body(self, ctx, *, text) -> None:
        """
        bodyの中から条件にあったアイテムを探索
        Args:
            ctx: Context
            text: アイテム名 or アイテム番号

        Returns:
            None
        """
        code, result = self.find_item(text, index=True, item_type="body")
        if code == 0:
            return await ctx.send(self.bot.error_text[result])
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @add.command(name="back", aliases=["b", "bk", "bc"], usage="add back [番号|名称]", description="背中装飾を指定します。", help="`<prefix>add back 6`...6番目の背中装飾を設定します\n`<prefix>add back B.MOUSE` ... B.MOUSEという名前の背中装飾を設定します")
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
        await ctx.send(f"見つかったアイテム: {self.name[result[0]][result[1]]} {self.emoji[result[0]][result[1]]}")
        item_list = parse_item_code_to_list(self.bot.database[str(ctx.author.id)]["costume"]["canvas"])
        item_list[self.item_info[result[0]]["index"]] = int(result[1])
        self.save_canvas_data(str(ctx.author.id), parse_item_list_to_code(item_list))
        await self.make_image(ctx, item_list[0], item_list[1], item_list[2], item_list[3], item_list[4], item_list[5])

    @commands.group(usage="list [種類]", description="その種類のアイテム一覧を表示します。", help="`<prefix>list character` ... キャラクターのリストを表示します\n`<prefix>list weapon` ... 武器のリストを表示します")
    async def list(self, ctx) -> None:
        """
        アイテム一覧を表示
        Args:
            ctx: Context

        Returns:
            None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"サブコマンドが不足しています。\n`{ctx.prefix}help list`で使い方を確認できます。")

    @list.command(name="base", aliases=["s", "bs"], usage="list base", description="白黒のリストを表示します。", help="`<prefix>list base` ... キャラ色のリストを表示します")
    async def list_base(self, ctx) -> None:
        """
        baseのアイテム一覧を検索
        Args:
            ctx: Context

        Returns:
            None
        """
        embed = discord.Embed(title="色一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("base", 1)
        embed.set_footer(text="1 / 1 ページを表示中")
        await ctx.send(embed=embed)

    @list.command(name="weapon", aliases=["w", "wp", "weap"], usage="list weapon", description="武器のリストを表示します。", help="`<prefix>list character` ...キャラクターのリストを表示します")
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
            return await ctx.send("ページ数は1~4で指定してください!")
        else:
            return await ctx.send("ページ数は整数で1~4で指定してください!")
        embed = discord.Embed(title="武器一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("weapon", page)
        embed.set_footer(text=f"{page} / 4 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 4, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("weapon", page)
            embed.set_footer(text=f"{page} / 4 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="character", aliases=["c", "ch", "char"], usage="list character", description="キャラクターのリストを表示します。", help="`<prefix>list weapon` ... 武器のリストを表示します")
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
            return await ctx.send("ページ数は1~3で指定してください!")
        else:
            return await ctx.send("ページ数は整数で1~3で指定してください!")
        embed = discord.Embed(title="キャラ一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("character", page)
        embed.set_footer(text=f"{page} / 3 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 3, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("character", page)
            embed.set_footer(text=f"{page} / 3 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="head", aliases=["h", "hd"], usage="list head", description="頭装飾のリストを表示します。", help="`<prefix>list head` ... 頭装飾のリストを表示します")
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
            return await ctx.send("ページ数は1~6で指定してください!")
        else:
            return await ctx.send("ページ数は整数で1~6で指定してください!")
        embed = discord.Embed(title="頭装飾一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("head", page)
        embed.set_footer(text=f"{page} / 6 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 6, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("head", page)
            embed.set_footer(text=f"{page} / 6 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="body", aliases=["d", "bd", "by"], usage="list body", description="体装飾のリストを表示します。", help="`<prefix>list body` ... 体装飾のリストを表示します")
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
            return await ctx.send("ページ数は1~7で指定してください!")
        else:
            return await ctx.send("ページ数は整数で1~7で指定してください!")
        embed = discord.Embed(title="体装飾一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("body", page)
        embed.set_footer(text=f"{page} / 7 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 7, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("body", page)
            embed.set_footer(text=f"{page} / 7 ページを表示中")
            await message.edit(embed=embed)

    @list.command(name="back", aliases=["b", "bc", "bk"], usage="list back", description="背中装飾のリストを表示します。", help="`<prefix>list back` ... 背中装飾のリストを表示します")
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
            return await ctx.send("ページ数は1~6で指定してください!")
        else:
            return await ctx.send("ページ数は整数で1~6で指定してください!")
        embed = discord.Embed(title="背中装飾一覧")
        embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("back", page)
        embed.set_footer(text=f"{page} / 6 ページを表示中")
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            code, new_page = await self.page_reaction_mover(message, ctx.author, 6, page)
            if code == 0:
                break
            page = new_page
            embed.description = "左の数字がアイテム番号、その横の名前がアイテム名称です。\n" + self.get_list("head", page)
            embed.set_footer(text=f"{page} / 6 ページを表示中")
            await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(Costume(bot))

