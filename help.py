import asyncio, discord
from discord.ext import commands
from multilingual import *

class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "Help"
        self.command_attrs["description"] = "コマンド一覧を表示します"
        self.command_attrs["help"] = "BOTのヘルプコマンドです"
        self.footer_message = ["<prefix>help (コマンド名) でさらに詳しいコマンドの説明が見れるよ!", "See <prefix> help (command name) for more detailed command instructions!", "<prefix>help (명령 이름)에서 자세한 명령의 설명을 볼 수 있어요!", "Consulte la ayuda sobre algún comando utilizando <prefix>help (nombre de comando) para obtener instrucciones más detalladas acerca del comando."]

    async def send_bot_help(self, mapping) -> None:
        """
         引数なしでhelpコマンドが実行された時に表示
        Args:
            mapping: Cogが辞書形式で含まれるデータ

        Returns:
            None
        """
        cogs = ["GlobalChat", "Notify", "Costume", "Information"]
        page = 1

        cog = discord.utils.get(mapping, qualified_name=cogs[page - 1])
        cmds = cog.get_commands()
        embed = discord.Embed(title=cog.qualified_name, color=0x00ff00)
        embed.description = cog.description + [f"\n分からないことがあれば、[サポート用サーバー]({self.context.bot.datas['server']})まで！", f"If you have any questions, go to [Support Server]({self.context.bot.datas['server']})!", f"모르는 것이 있으면, [지원용 서버]({self.context.bot.datas['server']})까지!", f"Si tiene alguna pregunta, comuníquese con [Support Server]({self.context.bot.datas['server']})."][get_lg(self.context.bot.database[str(self.context.author.id)]["language"], self.context.guild.region)]
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage}", value=f"```{cmd.description}```", inline=False)
        embed.set_footer(text=self.footer_message.replace("<prefix>", self.context.bot.PREFIX))
        message = await self.get_destination().send(embed=embed)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("❔")

        def check(r, u):
            return r.message.id == message.id and u == self.context.author and str(r.emoji) in ["◀️", "▶️", "❔"]

        while True:
            try:
                reaction, user = await self.context.bot.wait_for("reaction_add", timeout=60, check=check)
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
                    embed = discord.Embed(title="コマンド説明の見方", color=0x00ff00)
                    embed.description = f"メッセージ下にあるリアクションを押してページ移動できるよ！\n分からないことがあれば、[サポート用サーバー]({self.context.bot.datas['server']})まで来てね！"
                    embed.add_field(name="[引数]", value="__**必須**__の引数だよ", inline=False)
                    embed.add_field(name="(引数)", value="__**オプション**__の引数だよ", inline=False)
                    embed.add_field(name="[A|B]", value="AまたはBのいずれかを指定してね", inline=False)
                    embed.add_field(name="'種類'", value="base(白黒)/character(キャラ)/weapon(武器)/head(頭装飾)/body(体装飾)/back(背中装飾) のいずれかを指定してね(例: base)", inline=False)
                    embed.set_footer(text=self.footer_message.replace("<prefix>", self.context.bot.PREFIX))
                    await message.edit(embed=embed)
                    continue

                cog = discord.utils.get(mapping, qualified_name=cogs[page - 1])
                cmds = cog.get_commands()
                embed = discord.Embed(title=cog.qualified_name, color=0x00ff00)
                embed.description = cog.description + f"分からないことがあれば、[サポート用サーバー]({self.context.bot.datas['server']})までお越しください！"
                for cmd in await self.filter_commands(cmds, sort=True):
                    descriptinon = cmd.brief if cmd.brief is not None else cmd.description
                    embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage}", value=f"```{descriptinon}```", inline=False)
                embed.set_footer(text=self.footer_message.replace("<prefix>", self.context.bot.PREFIX))
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
        cmds = cog.get_commands()
        embed = discord.Embed(title=cog.qualified_name, color=0x00ff00)
        embed.description = cog.description
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage}", value=f"```{cmd.description}```", inline=False)
        embed.set_footer(text=self.footer_message.replace("<prefix>", self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        """
        コマンドグループの説明を表示
        Args:
            group: group

        Returns:
            None
        """
        embed = discord.Embed(title=f"{self.context.bot.PREFIX}{group.usage}", color=0x00ff00)
        embed.description = f"```{group.description}```"
        if group.aliases:
            embed.add_field(name="略記(エイリアス) :", value="`" + "`, `".join(group.aliases) + "`", inline=False)
        if group.help:
            embed.add_field(name="使用例 :", value=group.help.replace("<prefix>", self.context.bot.PREFIX), inline=False)
        cmds = group.walk_commands()
        embed.add_field(name="サブコマンド :", value=f"{sum(1 for _ in await self.filter_commands(group.walk_commands()))}個")
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.bot.PREFIX}{cmd.usage}", value=f"{cmd.description}", inline=False)
        embed.set_footer(text=self.footer_message.replace("<prefix>", self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command) -> None:
        """
        コマンドの説明を表示
        Args:
            command: Command

        Returns:
            None
        """
        embed = discord.Embed(title=f"{self.context.bot.PREFIX}{command.usage}", color=0x00ff00)
        embed.description = f"```{command.description}```"
        if command.aliases:
            embed.add_field(name="略記(エイリアス) :", value="`" + "`, `".join(command.aliases) + "`", inline=False)
        if command.help:
            embed.add_field(name="使用例 :", value=command.help.replace("<prefix>", self.context.bot.PREFIX), inline=False)
        embed.set_footer(text=self.footer_message.replace("<prefix>", self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error) -> None:
        """
        コマンドが存在しないときに表示
        Args:
            error:

        Returns:
            None
        """
        embed = discord.Embed(title="ヘルプ表示のエラー", description=error, color=0xff0000)
        embed.set_footer(text=self.footer_message.replace("<prefix>", self.context.bot.PREFIX))
        await self.get_destination().send(embed=embed)

    def command_not_found(self, string):
        return f"`{string}` というコマンドは見つからなかったよ。コマンド名を再確認してね!"

    def subcommand_not_found(self, cmd, string):
        if isinstance(cmd, commands.Group) and len(cmd.all_commands) > 0:
            return f"`{cmd.qualified_name}` に `{string}` というサブコマンドは登録されていないよ。`{self.context.bot.PREFIX}help {cmd.qualified_name}` で使い方を確認してね！"
        return f"`{cmd.qualified_name}` にサブコマンドは登録されていないよ。`{self.context.bot.PREFIX}help {cmd.qualified_name}` で使い方を確認してね！"

