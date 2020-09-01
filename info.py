from discord.ext import commands
import discord, datetime, time


class Information(commands.Cog):
    """BOTに関する情報を表示します。"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    @commands.command(aliases=["inv"], usage="invite", description="BOTの招待リンクを表示します。")
    async def invite(self, ctx):
        text = f"__**BOTの招待用URL**__:\n{self.bot.datas['invite']}\n" \
               f"__**サポート用サーバー(公式サーバー)**__:\n{self.bot.datas['server']}"
        await ctx.send(text)

    @commands.command(aliases=["about"], usage="info", description="BOTに関する情報を表示します。")
    async def info(self, ctx):
        td = datetime.timedelta(seconds=int(time.time() - self.bot.uptime))
        m, s = divmod(td.seconds, 60); h, m = divmod(m, 60); d = td.days
        embed = discord.Embed(title="このBOTについて")
        embed.description = f"BOTをご使用いただき、ありがとうございます！\n" \
                            f"このBOTはMilkChocoをプレイする人達の、Discordサーバーのために `{self.bot.datas['author']}` によって作成されました。\n" \
                            f"詳しい使い方は `{ctx.prefix}help` で確認して下さい。"
        embed.add_field(name="ステータス", value=f"```導入サーバー数: {len(self.bot.guilds)}\nBOTが認識しているユーザー数:{len(self.bot.users)}```", inline=False)
        embed.add_field(name="稼働時間", value=f"{d}日 {h}時間 {m}分 {s}秒", inline=False)
        embed.add_field(name="各種URL", value=f"[BOT招待用URL]({self.bot.datas['invite']}) | [サポート用サーバー]({self.bot.datas['server']})", inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
