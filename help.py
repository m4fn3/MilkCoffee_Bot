import discord
from discord.ext import commands


class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "Help"
        self.command_attrs["description"] = "コマンド一覧を表示します"
        self.command_attrs["help"] = "BOTのヘルプコマンドです"

    async def send_bot_help(self, mapping):
        # TODO: リアクションページ移動つきCogヘルプ表示コマンド
        # TODO: ? に [] () | "種類" の意味を説明する
        embed = discord.Embed(title="helpコマンド", color=0x00ff00)
        if self.context.bot.description:
            # もしBOTに description 属性が定義されているなら、それも埋め込みに追加する
            embed.description = self.context.bot.description
        for cog in mapping:
            if cog:
                cog_name = cog.qualified_name
            else:
                # mappingのキーはNoneになる可能性もある
                # もしキーがNoneなら、自身のno_category属性を参照する
                cog_name = self.no_category

            command_list = await self.filter_commands(mapping[cog], sort=True)
            content = ""
            for cmd in command_list:
                content += f"`{self.context.prefix}{cmd.name}`\n {cmd.description}\n"
            embed.add_field(name=cog_name, value=content, inline=False)

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        cmds = cog.get_commands()
        embed = discord.Embed(title=cog.qualified_name)
        embed.description = cog.description
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.prefix}{cmd.usage}", value=f"```{cmd.description}```", inline=False)
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=f"{self.context.prefix}{group.usage}", color=0x00ff00)
        embed.description = group.description
        if group.aliases:
            embed.add_field(name="略記(エイリアス) :", value="`" + "`, `".join(group.aliases) + "`", inline=False)
        if group.help:
            embed.add_field(name="使用例 :", value=group.help, inline=False)
        cmds = group.walk_commands()
        for cmd in await self.filter_commands(cmds, sort=True):
            embed.add_field(name=f"{self.context.prefix}{cmd.usage}", value=f"{cmd.description}", inline=False)
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"{self.context.prefix}{command.usage}", color=0x00ff00)
        embed.description = f"```{command.description}```"
        if command.aliases:
            embed.add_field(name="略記(エイリアス) :", value="`" + "`, `".join(command.aliases) + "`", inline=False)
        if command.help:
            embed.add_field(name="使用例 :", value=command.help, inline=False)
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="ヘルプ表示のエラー", description=error, color=0xff0000)
        await self.get_destination().send(embed=embed)

    def command_not_found(self, string):
        return f"`{string}` というコマンドは存在しません。コマンド名を再確認してください。"

    def subcommand_not_found(self, cmd, string):
        if isinstance(cmd, commands.Group) and len(cmd.all_commands) > 0:
            return f"`{cmd.qualified_name}` に `{string}` というサブコマンドは登録されていません。`{self.context.prefix}help {cmd.qualified_name}` で使い方を確認してください。"
        return f"`{cmd.qualified_name}` にサブコマンドは登録されていません。`{self.context.prefix}help {cmd.qualified_name}` で使い方を確認してください。"
