from discord.ext import commands
from contextlib import redirect_stdout
import asyncio, datetime, discord, io, os, subprocess, sys, textwrap, time, traceback2, re
try:
    import psutil
except:
    psutil_available = False
else:
    psutil_available = True


# class
class Developer(commands.Cog, command_attrs=dict(hidden=True)):
    """BOTのシステムを管理します。(ADMIN以上の権限が必要です)"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        self._last_result = None
        try:
            import psutil
        except:
            self.psutil = False
        else:
            self.psutil = True

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) not in self.bot.ADMIN:
            raise Exception("Developer-Admin-Error")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"引数が足りません。\nエラー詳細:\n{error}")
        else:
            await ctx.send(f"エラーが発生しました:\n{error}")

    @commands.command(aliases=["mtn", "mt"])
    async def maintenance(self, ctx, *, reason):
        self.bot.maintenance = reason
        await ctx.send(f"メンテナンスを設定しました。\n理由: {reason}")

    @commands.command(aliases=["unmtn", "unmt"])
    async def unmaintenance(self, ctx):
        self.bot.maintenance = ""
        await ctx.send("メンテナンスを解除しました。")

    @commands.command()
    async def admin(self, ctx, user_id, *, reason):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if str(user.id) in self.bot.ADMIN:
            return await ctx.send("このユーザーはすでにADMINです.")
        self.bot.ADMIN[str(user.id)] = reason
        await ctx.send(f"該当ユーザーをADMINにしました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がADMINになりました。", color=0xffa500)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command()
    async def deadmin(self, ctx, user_id, *, reason):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if str(user.id) not in self.bot.ADMIN:
            await ctx.send("このユーザーはADMINではありません。")
        del self.bot.ADMIN[str(user.id)]
        await ctx.send(f"該当ユーザーをADMINから削除しました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がADMINから削除されました。", color=0xc71585)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command()
    async def is_admin(self, ctx, user_id):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if user_id not in self.bot.ADMIN:
            await ctx.send(f"このユーザーはADMINではありません。(ユーザー情報: {str(user)} ({user.id}))")
        else:
            await ctx.send(f"このユーザーはADMINです。(ユーザー情報: {str(user)} ({user.id}))\n理由:{self.bot.ADMIN[user_id]}")

    @commands.command(aliases=["con"])
    async def contributor(self, ctx, user_id, *, reason):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if str(user.id) in self.bot.Contributor:
            return await ctx.send("このユーザーはすでにContributorです.")
        self.bot.Contributor[str(user.id)] = reason
        await ctx.send(f"該当ユーザーをContributorにしました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がContributorになりました。", color=0xe6e6fa)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command(aliases=["decon"])
    async def decontributor(self, ctx, user_id, *, reason):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if str(user.id) not in self.bot.Contributor:
            await ctx.send("このユーザーはContributorではありません。")
        del self.bot.Contributor[str(user.id)]
        await ctx.send(f"該当ユーザーをContributorから削除しました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がContributorから削除されました。", color=0xffe4e1)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command(aliases=["is_con"])
    async def is_contributor(self, ctx, user_id):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if user_id not in self.bot.Contributor:
            await ctx.send(f"このユーザーはContributorではありません。(ユーザー情報: {str(user)} ({user.id}))")
        else:
            await ctx.send(f"このユーザーはContributorです。(ユーザー情報: {str(user)} ({user.id}))\n理由:{self.bot.Contributor[user_id]}")

    @commands.command()
    async def ban(self, ctx, user_id, *, reason):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if str(user.id) in self.bot.BAN:
            return await ctx.send("このユーザーはすでにBANされています.")
        self.bot.BAN[str(user.id)] = reason
        await ctx.send(f"該当ユーザーをBANしました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がBANされました。", color=0xdc143c)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command()
    async def unban(self, ctx, user_id, *, reason):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if str(user.id) not in self.bot.BAN:
            await ctx.send("このユーザーはBANされていません。")
        del self.bot.BAN[str(user.id)]
        await ctx.send(f"該当ユーザーをBAN解除しました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がBAN解除されました。", color=0x4169e1)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command(aliases=["banned", "baned"])
    async def is_ban(self, ctx, user_id):
        user: discord.User
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user_id.isdigit():
            try:
                user = await self.bot.fetch_user(int(user_id))
            except discord.errors.NotFound:
                return await ctx.send("このユーザーIDを持つユーザーは存在しません。")
        else:
            return await ctx.send("ユーザーIDは数字で指定してください。")
        if user_id not in self.bot.BAN:
            await ctx.send(f"このユーザーはBANされていません。(ユーザー情報: {str(user)} ({user.id}))")
        else:
            await ctx.send(f"このユーザーはBANされています。(ユーザー情報: {str(user)} ({user.id}))\n理由:{self.bot.BAN[user_id]}")

    @commands.group(aliases=["sys"])
    async def system(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("reload <Cog> | restart | quit")

    @system.command(aliases=["rl"])
    async def reload(self, ctx, text):
        if text in self.bot.bot_cogs:
            try:
                self.bot.reload_extension(text)
            except:
                await ctx.send(f"{text}の再読み込みに失敗しました\n{traceback2.format_exc()}.")
            else:
                await ctx.send(f"{text}の再読み込みに成功しました.")
            if text == "global_chat":
                await self.bot.get_cog("GlobalChat").initialize_cog()
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["l"])
    async def load(self, ctx, text):
        if text in self.bot.bot_cogs:
            try:
                self.bot.load_extension(text)
            except:
                await ctx.send(f"{text}の読み込みに失敗しました\n{traceback2.format_exc()}.")
            else:
                await ctx.send(f"{text}の読み込みに成功しました.")
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["u"])
    async def unload(self, ctx, text):
        if text in self.bot.bot_cogs:
            try:
                self.bot.unload_extension(text)
            except:
                await ctx.send(f"{text}の切り離しに失敗しました\n{traceback2.format_exc()}.")
            else:
                await ctx.send(f"{text}の切り離しに成功しました.")
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["re"])
    async def restart(self, ctx):
        await ctx.send(":closed_lock_with_key:BOTを再起動します.")
        python = sys.executable
        os.execl(python, python, * sys.argv)

    @system.command(aliases=["q"])
    async def quit(self, ctx):
        await ctx.send(":closed_lock_with_key:BOTを停止します.")
        sys.exit()

    @commands.command()
    async def exe(self, ctx, *, body: str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback2.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command(aliases=["pr"])
    async def process(self, ctx):
        td = datetime.timedelta(seconds=int(time.time() - self.bot.uptime))
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        d = td.days
        uptime = f"{d}d {h}h {m}m {s}s"
        if psutil_available:
            cpu_per = psutil.cpu_percent()
            mem_total = psutil.virtual_memory().total / 10**9
            mem_used = psutil.virtual_memory().used / 10**9
            mem_per = psutil.virtual_memory().percent
            swap_total = psutil.swap_memory().total / 10**9
            swap_used = psutil.swap_memory().used / 10**9
            swap_per = psutil.swap_memory().percent
        guilds = len(self.bot.guilds)
        users = len(self.bot.users)
        vcs = len(self.bot.voice_clients)
        text_channels = 0
        voice_channels = 0
        for channel in self.bot.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                text_channels += 1
            elif isinstance(channel, discord.VoiceChannel):
                voice_channels += 1
        latency = self.bot.latency
        embed = discord.Embed(title="Process")
        if psutil_available:
            embed.add_field(name="Server", value=f"```yaml\nCPU: [{cpu_per}%]\nMemory:[{mem_per}%] {mem_used:.2f}GiB / {mem_total:.2f}GiB\nSwap: [{swap_per}%] {swap_used:.2f}GiB / {swap_total:.2f}GiB\n```", inline=False)
        embed.add_field(name="Discord", value=f"```yaml\nServers:{guilds}\nTextChannels:{text_channels}\nVoiceChannels:{voice_channels}\nUsers:{users}\nConnectedVC:{vcs}```", inline=False)
        embed.add_field(name="Run", value=f"```yaml\nUptime: {uptime}\nLatency: {latency:.2f}[s]\n```")
        await ctx.send(embed=embed)

    @commands.command()
    async def cmd(self, ctx, *, text):
        msg = ""
        try:
            output = await self.run_subprocess(text, loop=self.bot.loop)
            for i in range(len(output)):
                msg += output[i]
            await ctx.send(msg)
        except:
            await ctx.send(file=discord.File(fp=io.StringIO(msg), filename="output.txt"))

    async def run_subprocess(self, cmd, loop=None):
        loop = loop or asyncio.get_event_loop()
        try:
            process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except NotImplementedError:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as process:
                try:
                    result = await loop.run_in_executor(None, process.communicate)
                except Exception:  # muh pycodestyle
                    def kill():
                        process.kill()
                        process.wait()
                    await loop.run_in_executor(None, kill)
                    raise
        else:
            result = await process.communicate()

        return [res.decode('utf-8') for res in result]

    @commands.command(hidden=True)
    async def make_trans(self, ctx):
        f = open("strings.txt", "w")
        cogs = ["GlobalChat", "Notify", "Costume", "Information"]
        for cog in cogs:
            target_cog = self.bot.get_cog(name=cog)
            f.write(f"""
{target_cog.qualified_name}
{target_cog.description}
""")
            for cmd in self.bot.get_cog(name=cog).walk_commands():
                if cmd.usage is None:
                    continue
                f.write("--" + cmd.name + "\n")
                f.write(cmd.usage + "\n")
                try:
                    if cmd.breif is not None:
                        f.write(cmd.breif + "\n")
                except:
                    pass
                try:
                    if cmd.description is not None:
                        f.write(cmd.description + "\n")
                except:
                    pass
                try:
                    if cmd.help is not None:
                        f.write(cmd.help + "\n")
                except:
                    pass
        f.close()
        await ctx.send("完了")

    @commands.command(hidden=True)
    async def make_string(self, ctx):
        cogs = ["costume", "global_chat", "info", "notify"]
        log_f = open("string-log.txt", "w")
        text: str
        for cog_name in cogs:
            print(cog_name)
            with open(f"{cog_name}.py") as f:
                text = f.read()
            mch = re.finditer(r"await ctx.send\((.+)\)", text)
            for i in mch:
                log_f.write(i.group(1) + "\n")
        log_f.close()
        await ctx.send("完了")

    @commands.command(hidden=True)
    async def make_html(self, ctx):
        f = open("commands_html.txt", "w")
        cogs = ["GlobalChat", "Notify", "Costume", "Information"]
        for cog in cogs:
            coga = self.bot.get_cog(name=cog)
            f.write(f"""
          <div id="{coga.qualified_name}">
            <h1>m!{coga.qualified_name}</h1>
            <p>{coga.description}</p>
                """)
            for cmd in self.bot.get_cog(name=cog).walk_commands():
                if cmd.usage is None:
                    continue
                desc = cmd.description.replace("<prefix>", "m!").replace("`", "").replace("\n", "<br>")
                alias = ""
                if cmd.aliases:
                    alias = ", ".join(cmd.aliases)
                    alias = f"\n            <p>略記: {alias}</p>"
                help = ""
                if cmd.help:
                    help = "\n" + cmd.help.replace("<prefix>", "m!").replace("`", "").replace("\n", "<br>")
                    help = f"\n             <p>{help}</p>"
                f.write(f"""
                <div class="command_box" id="open_command">
                  <p>{cmd.usage}</p>
                  <div class="command_description">
                    <p>{desc}</p>{alias}{help}
                  </div>
                </div>
                    """)
            f.write("""
          </div>
                """)
        f.close()
        await ctx.send("完了")


def setup(bot):
    bot.add_cog(Developer(bot))
