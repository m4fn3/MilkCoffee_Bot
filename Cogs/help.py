import asyncio

import discord
from discord.ext import commands

from .milkcoffee import MilkCoffee
from .utils.multilingual import *


class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "Help"
        self.command_attrs["description"] = "コマンド一覧を表示します"
        self.command_attrs["help"] = "BOTのヘルプコマンドです"
        self.description_message = ["\n分からないことがあれば、[サポート用サーバー]({})まで！", "If you have any questions, go to [Support Server]({})!", "모르는 것이 있으면, [지원용 서버]({})까지!", "Si tiene alguna pregunta, comuníquese con [Support Server]({})."]
        self.footer_message = ["{}help (コマンド名) でさらに詳しいコマンドの説明が見れるよ!", "See {} help (command name) for more detailed command instructions!", "{}help (명령 이름) 에서 자세한 명령의 설명을 볼 수 있어요!", "Consulte la ayuda sobre algún comando utilizando {}help (nombre de comando) para obtener instrucciones más detalladas acerca del comando."]

    async def send_bot_help(self, mapping) -> None:
        """
         引数なしでhelpコマンドが実行された時に表示
        Args:
            mapping: Cogが辞書形式で含まれるデータ

        Returns:
            None
        """
        if str(self.context.author.id) not in self.context.bot.database:
            await self.new_user()
        cogs: list
        page = 1
        user_lang = get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)
        cogs = ["Bot", "Notify", "Costume"]
        cog = discord.utils.get(mapping, qualified_name=cogs[page - 1])
        cmds = cog.get_commands()
        embed = discord.Embed(title=cog.qualified_name, color=0x00ff00)
        embed.description = cog.description.split("^")[user_lang] + self.description_message[user_lang].format(self.context.bot.static_data.server)
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage.split('^')[user_lang]}", value=f"```{cmd.description.split('^')[user_lang]}```", inline=False)
        embed.set_footer(text=self.footer_message[user_lang].format(self.context.bot.PREFIX))
        message = await self.get_destination().send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("❔")

        def check(r, u):
            return r.message.id == message.id and u == self.context.author and str(r.emoji) in ["◀️", "▶️", "❔"]

        while True:
            try:
                reaction, user = await self.context.bot.wait_for("reaction_add", timeout=60, check=check)
                try:
                    await message.remove_reaction(reaction, user)
                except:
                    pass
                if str(reaction.emoji) == "▶️":
                    if page == len(cogs):
                        page = 1
                    else:
                        page += 1
                elif str(reaction.emoji) == "◀️":
                    if page == 1:
                        page = len(cogs)
                    else:
                        page -= 1
                elif str(reaction.emoji) == "❔":
                    embed = discord.Embed(title=["コマンド説明の見方", "How to read the command description", "명령 설명 견해", "Cómo leer la descripción del comando"][user_lang], color=0x00ff00)
                    embed.description = f"{['メッセージ下にあるリアクションを押してページ移動できるよ！', 'You can move the page by pressing the reaction below the message', '메시지의 반응을 눌러 페이지 이동 할 수 있어!', '¡Puede leer más acerca del comando presionando la reacción debajo del mensaje!'][user_lang]}\n{self.description_message[user_lang].format(self.context.bot.static_data.server)}"
                    embed.add_field(name=["[引数]", "[argument]", "인수", "argumento"][user_lang], value=["__**必須**__の引数だよ", "__**required**__ argument", "__**필수**__ 인수야", "__**requerido**__ argumento"][user_lang], inline=False)
                    embed.add_field(name=["(引数)", "(argument)", "인수", "argumento"][user_lang], value=["__**オプション**__の引数だよ", "__**option**__", "__**옵션**__ 인수야", "__**opción**__ argumento"][user_lang], inline=False)
                    embed.add_field(name="[A|B]", value=["AまたはBのいずれかを指定してね", "either A or B", "A 또는 B 중 하나를 지정주세요", "especificar A o B"][user_lang], inline=False)
                    embed.add_field(name=["'種類'", "'type'", "'종류'", "'tipo'"][user_lang], value=["base(白黒)/character(キャラ)/weapon(武器)/head(頭装飾)/body(体装飾)/back(背中装飾) のいずれかを指定してね(例: base)", "Specify one of base (black and white) / character (character) / weapon (weapon) / head (head decoration) / body (body decoration) / back (back decoration)! (example: base)",
                                                                                                 "base (밀크, 초코) / character (캐릭터) / weapon (무기) / head (머리 코스튬) / body (몸 코스튬) / back (등 코스튬) 중 하나를 지정하세요 (예 : base)",
                                                                                                 "base (milk o choco) / character (personaje) / weapon (arma) / head (decoración de la cabeza) / body (decoración del cuerpo/traje) / back (decoración de la espalda). Especifique (Por ejemplo: base)"][user_lang], inline=False)
                    embed.set_footer(text=self.footer_message[user_lang].format(self.context.bot.PREFIX))
                    await message.edit(embed=embed)
                    continue

                cog = discord.utils.get(mapping, qualified_name=cogs[page - 1])
                cmds = cog.get_commands()
                embed = discord.Embed(title=cog.qualified_name, color=0x00ff00)
                embed.description = cog.description.split("^")[user_lang] + self.description_message[user_lang].format(self.context.bot.static_data.server)
                for cmd in await self.filter_commands(cmds, sort=True):
                    description = cmd.brief.split('^')[user_lang] if cmd.brief is not None else cmd.description.split('^')[user_lang]
                    embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage.split('^')[user_lang]}", value=f"```{description}```", inline=False)
                embed.set_footer(text=self.footer_message[user_lang].format(self.context.bot.PREFIX))
                await message.edit(embed=embed)
            except asyncio.TimeoutError:
                await message.remove_reaction("◀️", self.context.bot.user)
                await message.remove_reaction("▶️", self.context.bot.user)
                await message.remove_reaction("❔", self.context.bot.user)
                break

    async def send_cog_help(self, cog) -> None:
        """
        コグの説明を表示
        Args:
            cog: Cog

        Returns:
            None
        """
        if str(self.context.author.id) not in self.context.bot.database:
            await self.new_user()
        user_lang = get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)
        cmds = cog.get_commands()
        embed = discord.Embed(title=cog.qualified_name, color=0x00ff00)
        embed.description = cog.description.split("^")[user_lang]
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage.split('^')[user_lang]}", value=f"```{cmd.description.split('^')[user_lang]}```", inline=False)
        embed.set_footer(text=self.footer_message[user_lang].format(self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        """
        コマンドグループの説明を表示
        Args:
            group: group

        Returns:
            None
        """
        if str(self.context.author.id) not in self.context.bot.database:
            await self.new_user()
        user_lang = get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)
        embed = discord.Embed(title=f"{self.context.bot.PREFIX}{group.usage.split('^')[user_lang]}", color=0x00ff00)
        embed.description = f"```{group.description.split('^')[user_lang]}```"
        if group.aliases:
            embed.add_field(name=["略記(エイリアス) :", "Abbreviation (alias) :", "단축 (별칭) :", "Abreviatura (alias):"][user_lang], value="`" + "`, `".join(group.aliases) + "`", inline=False)
        if group.help:
            embed.add_field(name=["使用例 :", "Example of use :", "사용 예 :", "Ejemplo de uso :"][user_lang], value=group.help.split("^")[user_lang].format(self.context.bot.PREFIX), inline=False)
        cmds = group.walk_commands()
        embed.add_field(name=["サブコマンド :", "Subcommand :", "명령어 :", "Subcomando:"][user_lang], value=f"{sum(1 for _ in await self.filter_commands(group.walk_commands()))}")
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage.split('^')[user_lang]}", value=f"{cmd.description.split('^')[user_lang]}", inline=False)
        embed.set_footer(text=self.footer_message[user_lang].format(self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command) -> None:
        """
        コマンドの説明を表示
        Args:
            command: Command

        Returns:
            None
        """
        if str(self.context.author.id) not in self.context.bot.database:
            await self.new_user()
        user_lang = get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)
        embed = discord.Embed(title=f"{self.context.bot.PREFIX}{command.usage.split('^')[user_lang]}", color=0x00ff00)
        embed.description = f"```{command.description.split('^')[user_lang]}```"
        if command.aliases:
            embed.add_field(name=["略記(エイリアス) :", "Abbreviation (alias) :", "단축 (별칭) :", "Abreviatura (alias):"][user_lang], value="`" + "`, `".join(command.aliases) + "`", inline=False)
        if command.help:
            embed.add_field(name=["使用例 :", "Example of use :", "사용 예 :", "Ejemplo de uso :"][user_lang], value=command.help.split("^")[user_lang].format(self.context.bot.PREFIX), inline=False)
        embed.set_footer(text=self.footer_message[user_lang].format(self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error) -> None:
        """
        コマンドが存在しないときに表示
        Args:
            error:

        Returns:
            None
        """
        if str(self.context.author.id) not in self.context.bot.database:
            await self.new_user()
        user_lang = get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)
        embed = discord.Embed(title=["ヘルプ表示のエラー", "Error displaying help", "도움말 표시 오류", "Ayuda mostrando error"][user_lang], description=error, color=0xff0000)
        embed.set_footer(text=self.footer_message[user_lang].format(self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    def command_not_found(self, string):
        user_lang = get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)
        return ["`{}` というコマンドは見つからなかったよ。コマンド名を再確認してね!", "Couldn't find the command `{}`. Double check the command name!", "`{}`명령을 찾을 수 없습니다. 명령 이름을 다시 확인하십시오!", "No pude encontrar el comando {}. ¡Verifique el nombre del comando!"][user_lang].format(string)

    def subcommand_not_found(self, cmd, string):
        user_lang = get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)
        if isinstance(cmd, commands.Group) and len(cmd.all_commands) > 0:
            return ["`{1}` に `{0}` というサブコマンドは登録されていないよ。`{2}help {1}` で使い方を確認してね！", "The subcommand `{0}` is not registered in `{1}`. Please check the usage with `{2}help {1}`!", "하위 명령어`{0}`이 (가)`{1}`에 등록되지 않았습니다. `{2}help {1}`로 사용법을 확인하세요!", "El subcomando `{0}` no está registrado en `{1}`. ¡Compruebe el uso con la `{2}help {1}`!"][user_lang].format(string, cmd.qualified_name,
                                                                                                                                                                                                                                                                                                                                                                 self.context.bot.PREFIX)
        return ["`{0}` にサブコマンドは登録されていないよ。`{1}help {0}` で使い方を確認してね！", "No subcommands are registered in `{0}`. Please check the usage with `{1}help {0}`!", "`{0}`에 등록 된 하위 명령이 없습니다.`{1}help {0}`로 사용법을 확인하세요!", "No hay subcomandos registrados en `{0}`.¡Compruebe el uso con la `{1}help {0}`!"][user_lang].format(cmd.qualified_name, self.context.bot.PREFIX)

    async def new_user(self):
        if str(self.context.author.id) not in self.context.bot.database:
            self.context.bot.database[str(self.context.author.id)] = {
                "language": 0,
                "costume": {
                    "canvas": "1o4s3k",
                    "save": []
                }
            }
            await self.context.bot.get_cog("Bot").language_selector(self.context)
