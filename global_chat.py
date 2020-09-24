from discord.ext import commands, tasks
import discord, datetime, traceback2, time, pprint
from filter.filter import *
from multilingual import *


class GlobalChat(commands.Cog):
    """他のサーバーに居る人と、設定したチャンネルでお話しできるよ!"""

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        self.global_chat_log_channel = None
        self.sending_message = {}
        self.filter_obj = Filter(self.bot)
        self.global_chat_message_cache = {}
        self.command_list = []

    async def cog_command_error(self, ctx, error):
        user_lang = get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(["引数が不足しているよ!\n使い方: `{0}{1}`\n詳しくは `{0}help {1}`", "Not enough arguments! \nUsage: `{0} {1}` \nFor more information `{0}help {1}", "f 인수가 충분하지 않습니다. \n사용법 :`{0} {1}`\n 자세한 내용은`{0}help {1}", "No hay suficientes argumentos. \nUso: {0} {1} \nPara obtener más información, `{0}help {1}"][user_lang].format(self.bot.PREFIX, ctx.command.usage, ctx.command.qualified_name))
        else:
            await ctx.send(["エラーが発生しました。管理者にお尋ねください。\n{}", "An error has occurred. Please ask the BOT administrator.\n{}", "오류가 발생했습니다.관리자에게 문의하십시오.\n{}", "Se ha producido un error. Pregunte al administrador.\n{}"][user_lang].format(error))

    async def delete_global_message(self, message_id: int):
        if str(message_id) in self.bot.global_chat_log:
            if message_id in self.sending_message:
                if self.sending_message[message_id]:
                    self.sending_message[message_id] = False
                else:
                    task = self.sending_message[message_id]
                    task.cancel()
                    del self.sending_message[message_id]
            if message_id in self.global_chat_message_cache:
                for msg_obj in self.global_chat_message_cache[message_id]:
                    try:
                        await msg_obj.delete()
                    except:
                        pass
                del self.global_chat_message_cache[message_id]
            else:
                for msg_data in self.bot.global_chat_log[str(message_id)]["webhooks"]:
                    try:
                        channel = self.bot.get_channel(msg_data["channel"])
                        message = await channel.fetch_message(msg_data["message"])
                        await message.delete()
                    except:
                        pass
            msg_data = self.bot.global_chat_log[str(message_id)]
            embed = discord.Embed(color=0xff0000)
            embed.set_author(name=msg_data["sender"]["name"], icon_url=msg_data["sender"]["avatar"])
            embed.description = msg_data["content"]
            timestamp = msg_data["timestamp"]
            embed.timestamp = datetime.datetime.fromtimestamp(timestamp)
            guild = self.bot.get_guild(msg_data['guild'])
            embed.add_field(name="詳細情報", value=f"```メッセージID: {message_id}\n送信者情報: {msg_data['sender']['name']} ({msg_data['sender']['id']})\n送信元サーバー: {guild.name} ({guild.id})\n送信元チャンネル: {guild.get_channel(msg_data['channel'])} ({msg_data['channel']})```", inline=False)
            embed.add_field(name="日時", value=(datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(hours=9)).strftime('%Y/%m/%d %H:%M:%S'), inline=False)
            links = [link for link in msg_data['attachment']]
            await self.global_chat_log_channel.send(content="\n".join(links), embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.initialize_cog()

    async def initialize_cog(self):
        self.global_chat_log_channel = self.bot.get_channel(self.bot.datas["global_chat_log_channel"])
        self.command_list = [self.bot.PREFIX + str(cmd) for cmd in self.bot.walk_commands()]
        if not self.process_chat_log.is_running():
            self.process_chat_log.start()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.channel_id in self.bot.global_channels:
            await self.delete_global_message(payload.message_id)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if invite.guild.id == self.bot.datas["server_id"] and invite.code not in self.bot.invites:
            self.bot.invites.append(invite.code)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild.id == self.bot.datas["server_id"] and invite.code in self.bot.invites:
            self.bot.invites.remove(invite.code)

    async def cog_before_invoke(self, ctx):
        if self.bot.maintenance and str(ctx.author.id) not in self.bot.ADMIN:
            await ctx.send(["現在BOTはメンテナンス中です。\n理由: {}\n詳しい情報については公式サーバーにてご確認ください。", "BOT is currently under maintenance. \nReason: {}\nPlease check the official server for more information.", "BOT는 현재 점검 중입니다.\n이유 : {}\n자세한 내용은 공식 서버를 확인하십시오.", "BOT se encuentra actualmente en mantenimiento.\nRazón: {}\nConsulte el servidor oficial para obtener más información."][get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.maintenance))
            raise commands.CommandError("maintenance-error")
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(["あなたのアカウントはBANされています(´;ω;｀)\nBANに対する異議申し立ては、公式サーバーの <#{}> にてご対応させていただきます。", "Your account is banned (´; ω;`)\nIf you have an objection to BAN, please use the official server <#{}>.", "당신의 계정은 차단되어 있습니다 ( '; ω;`)\n차단에 대한 이의 신청은 공식 서버 <#{}> 에서 대응하겠습니다.", "Su cuenta está prohibida (´; ω;`)\nSi tiene una objeción a la BAN, utilice <#{}> en el servidor oficial."][get_lg(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)].format(self.bot.datas['appeal_channel']))
            raise commands.CommandError("Your Account Banned")
        elif str(ctx.author.id) not in self.bot.database:
            self.bot.database[str(ctx.author.id)] = {
                "language": 0
            }

    async def on_dm_message(self, message):
        if message.content == "unlock":
            if str(message.author.id) in self.bot.LOCK:
                del self.bot.LOCK[str(message.author.id)]
                await message.author.send("あなたのロックを解除しました。\n今後は特に言動に気を付けてお楽しみください。")
                embed = discord.Embed(title=f"{message.author.name} がロック解除されました。", color=0x4169e1)
                embed.description = f"ユーザー情報: {str(message.author)} ({message.author.id})\n理由: 対象ユーザーによる手動解除\n実行者: {str(message.author)} ({message.author.id})"
                await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.group(name="global", usage="global [サブコマンド]", description="グローバルチャットに関するコマンドだよ!\nグローバルチャット設定をするためには、BOTが manage_webhook(webhookを管理) の権限を持ってて、コマンドの実行者が manage_channel(チャンネルの管理) 権限を持っている必要があるよ!")
    async def global_command(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"サブコマンドが不足しています。\n`{ctx.prefix}help global`で使い方を確認できます。")

    @global_command.command(name="join", usage="global join (チャンネル)", description="グローバルチャットに接続するよ!。チャンネルを指定しなかったら、コマンドが実行されたチャンネルに設定するよ!。", help="`<prefix>global join` ... コマンドを打ったチャンネルをグローバルチャットに接続します。\n`<prefix>global join #チャンネル` ... 指定したチャンネルをグローバルチャットに接続します。")
    async def global_join(self, ctx):
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if not target_channel.permissions_for(ctx.author).manage_channels:
            return await ctx.send(f"あなたは {target_channel.mention} チャンネルで設定する権限がないよ!\nセキュリティ対策のため、チャンネルをグローバルチャットに接続するには、コマンドを実行するユーザーが`manage_channels(チャンネルを管理)`の権限を持っていないとだめだよ!\n権限に関しては、サーバーの管理者に依頼してね!")
        if target_channel.id in self.bot.global_channels:
            return await ctx.send(f"{target_channel.mention} は既にグローバルチャットに参加しています。")
        if target_channel.permissions_for(ctx.guild.get_member(self.bot.user.id)).manage_webhooks:
            channel_webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(channel_webhooks, name="global_chat_webhook_mafu")
            if webhook is None:
                await target_channel.create_webhook(name=f"global_chat_webhook_mafu")
            self.bot.global_channels.append(target_channel.id)
            await ctx.send(f"{target_channel.mention} がグローバルチャットに接続されたよ!")
            embed = discord.Embed(title=f"{ctx.channel.name} がグローバルチャットに参加しました。", color=0x2f4f4f)
            embed.description = f"サーバー情報: {ctx.guild.name} ({ctx.guild.id})\nチャンネル情報: {ctx.channel.name} ({ctx.channel.id})\n設定したユーザー: {str(ctx.author)} ({ctx.author.id})\nメンバー数: {len(ctx.guild.members)}\nサーバー管理者: {str(ctx.guild.owner)} ({ctx.guild.owner.id})"
            await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
        else:
            await ctx.send(f"BOTの`manage_webhooks(webhookの管理)`権限が不足しているよ!")

    @global_command.command(name="leave", usage="global leave [チャンネル]", description="指定したチャンネルをグローバルチャットから切断するよ!。(グローバルチャットに接続されているチャンネルではコマンドは実行できないから気を付けてね)", help="`<prefix>global leave #チャンネル` ... 指定したチャンネルをグローバルチャットから切断します。")
    async def global_leave(self, ctx):
        if ctx.message.channel_mentions:
            target_channel = ctx.message.channel_mentions[0]
            if not target_channel.permissions_for(ctx.author).manage_channels:
                return await ctx.send(f"あなたは {target_channel.mention} チャンネルで設定する権限がないよ!\nセキュリティ対策のため、チャンネルをグローバルチャットから切断するには、コマンドを実行するユーザーが`manage_channels(チャンネルを管理)`の権限を持っていないとだめだよ!\n権限に関しては、サーバーの管理者に依頼してね!")
            if target_channel.id in self.bot.global_channels:
                self.bot.global_channels.remove(target_channel.id)
                await ctx.send(f"{target_channel.mention} をグローバルチャットから切断したよ!")
            else:
                await ctx.send(f"{target_channel.mention} はフローバルチャットに接続されていないよ!")
        else:
            await ctx.send(f"チャンネルが指定されていないよ!詳しい使い方は `{ctx.prefix}help global leave` で確認してね!")

    @global_command.command(name="delete", hidden=True)
    async def global_delete(self, ctx, message_id):
        if str(ctx.author.id) not in self.bot.ADMIN:
            return
        if message_id.isdigit():
            await self.delete_global_message(int(message_id))
            await ctx.send(f"該当メッセージを削除しました。(メッセージID: {message_id})")
        else:
            await ctx.send("メッセージIDは数字で指定してください。")

    @global_command.command(usage="prohibitions", description="グローバルチャットでの禁止事項を表示するよ!")
    async def prohibitions(self, ctx):
        embed = discord.Embed(title="グローバルチャット禁止事項", color=0xcc66cc)
        embed.description = """
当サービスでのグローバルチャットでは以下の行為を禁止しています。
違反した場合、予告なくロック、ミュート処置をとることがあります。
```
・成人向けコンテンツまたはグロテスクな表現を含むコンテンツの送信
・誹謗中傷を含むコンテンツの送信
・サーバー招待URL等を送信して宣伝する行為
・短い間隔で何度も文章を送信し、負荷をかける行為
・BOTのコマンドを送信する行為
・その他当チームが極めて不適切だと判断するコンテンツ
```
        """
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def mute(self, ctx, user_id, *, reason):
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
        if str(user.id) in self.bot.MUTE:
            return await ctx.send("このユーザーはすでにミュートされています.")
        self.bot.MUTE[str(user.id)] = reason
        await ctx.send(f"該当ユーザーをミュートしました。(ユーザー情報: {str(user)} ({user.id}))")
        try:
            embed = discord.Embed(title="重要通知", color=0xdc143c)
            embed.description = f"あなたはグローバルチャットからミュートされました。\n理由:{reason}\n異議申し立ては、[公式サーバー]({self.bot.datas['server']})の<#{self.bot.datas['appeal_channel']}>にてご対応させていただきます。"
            await user.send(embed=embed)
        except:
            pass
        embed = discord.Embed(title=f"{user.name} がミュートされました。", color=0xdc143c)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command(hidden=True)
    async def unmute(self, ctx, user_id, *, reason):
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
        if str(user.id) not in self.bot.MUTE:
            return await ctx.send("このユーザーはミュートされていません。")
        del self.bot.MUTE[str(user.id)]
        await ctx.send(f"該当ユーザーをミュート解除しました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がミュート解除されました。", color=0x4169e1)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command(name="muted", hidden=True)
    async def is_mute(self, ctx, user_id):
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
        if user_id not in self.bot.MUTE:
            await ctx.send(f"このユーザーはミュートされていません。(ユーザー情報: {str(user)} ({user.id}))")
        else:
            await ctx.send(f"このユーザーはミュートされています。(ユーザー情報: {str(user)} ({user.id}))\n理由:{self.bot.MUTE[user_id]}")

    @commands.command(hidden=True)
    async def lock(self, ctx, user_id, *, reason):
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
        if str(user.id) in self.bot.LOCK:
            return await ctx.send("このユーザーはすでにロックされています.")
        self.bot.LOCK[str(user.id)] = reason
        try:
            embed = discord.Embed(title="重要通知", color=0xdc143c)
            embed.description = f"あなたのアカウントはグローバルチャットからロックされました。\n理由:{reason}\n異議申し立ては、[公式サーバー]({self.bot.datas['server']})の<#{self.bot.datas['appeal_channel']}>にてご対応させていただきます。"
            await user.send(embed=embed)
        except:
            pass
        await ctx.send(f"該当ユーザーをロックしました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がロックされました。", color=0xf4a460)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command(hidden=True)
    async def unlock(self, ctx, user_id, *, reason):
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
        if str(user.id) not in self.bot.LOCK:
            return await ctx.send("このユーザーはロックされていません。")
        del self.bot.LOCK[str(user.id)]
        await ctx.send(f"該当ユーザーをロック解除しました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がロック解除されました。", color=0x4169e1)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @commands.command(name="locked", hidden=True)
    async def is_lock(self, ctx, user_id):
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
        if user_id not in self.bot.LOCK:
            await ctx.send(f"このユーザーはロックされていません。(ユーザー情報: {str(user)} ({user.id}))")
        else:
            await ctx.send(f"このユーザーはロックされています。(ユーザー情報: {str(user)} ({user.id}))\n理由:{self.bot.LOCK[user_id]}")

    @commands.group(hidden=True)
    async def history(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("m!history <add|del|see>")

    @history.command(name="delete")
    async def history_delete(self, ctx, user_id, warn_id):
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
        if str(user.id) in self.bot.database and "global" in self.bot.database[str(user.id)]:
            if warn_id in self.bot.database[str(user.id)]["global"]["history"]:
                data = self.bot.database[str(user.id)]["global"]["history"].pop(warn_id)
                for warn in data:
                    self.bot.database[str(user.id)]["global"]["warning"] -= data[warn]
                if self.bot.database[str(user.id)]["global"]["warning"] < 0:
                    self.bot.database[str(user.id)]["global"]["warning"] = 0
                await ctx.send("正常に削除しました。")
            else:
                await ctx.send("そのような警告はありません。")
        else:
            await ctx.send("このユーザーはBOTに登録していません。")

    @history.command(name="add")
    async def history_add(self, ctx, user_id, reason, point):
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
        if str(user.id) in self.bot.database and "global" in self.bot.database[str(user.id)]:
            if not point.isdigit():
                return await ctx.send("ポイントは数字で指定してください")
            self.bot.database[str(user.id)]["global"]["history"][str(ctx.message.id)] = {reason: int(point)}
            self.bot.database[str(user.id)]["global"]["warning"] += int(point)
            embed = discord.Embed(title=f"{user.name} が警告を受けました。", color=0xffff00)
            embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n合計違反点数: {point}\n現在の合計点数: {self.bot.database[str(user.id)]['global']['warning']}\n警告番号: {ctx.message.id}\n実行者: {str(ctx.author)} ({ctx.author.id})"
            await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
            await self.check_point(ctx.message, reason, True)
        else:
            await ctx.send("このユーザーはBOTに登録していません。")

    @history.command(name="see")
    async def history_see(self, ctx, user_id):
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
        if str(user.id) in self.bot.database and "global" in self.bot.database[str(user.id)]:
            history = self.bot.database[str(user.id)]["global"]["history"]
            await ctx.send(pprint.pformat(history))
        else:
            await ctx.send("このユーザーはBOTに登録していません。")

    async def check_point(self, message, reason, dm=False):
        if self.bot.database[str(message.author.id)]["global"]["warning"] >= 10:
            embed = discord.Embed(title="重要通知", color=0xdc143c)
            embed.description = f"あなたは違反行為によりミュートされました。\n理由: {reason}の検出等\nミュートをご自身で解除されることはできません。\n尚、この通知が不服である場合(誤検出である等)はお手数ですが、[公式サーバー]({self.bot.datas['server']})の<#{self.bot.datas['appeal_channel']}>にて異議申し立てを行ってください。"
            if dm:
                await message.author.send(message.author.mention, embed=embed)
            else:
                await message.channel.send(message.author.mention, embed=embed)
            reason = f"自動ミュート({message.id}) " + reason
            self.bot.MUTE[str(message.author.id)] = reason
            embed = discord.Embed(title=f"{message.author.name} がミュートされました。", color=0xdc143c)
            embed.description = f"ユーザー情報: {str(message.author)} ({message.author.id})\n理由: {reason}\n実行者: {str(self.bot.user)} ({self.bot.user.id})"
            await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
            self.bot.database[str(message.author.id)]["global"]["warning"] = 0
            return 0
        elif self.bot.database[str(message.author.id)]["global"]["warning"] >= 5:
            embed = discord.Embed(title="重要通知", color=0xdc143c)
            embed.description = f"あなたは違反行為によりロックされました。\n理由: {reason}の検出等\nロックはご自身により解除が可能です。詳しくはDMに送信した詳細を確認してください。\n尚、この通知が不服である場合(誤検出である等)はお手数ですが、[公式サーバー]({self.bot.datas['server']})の<#{self.bot.datas['appeal_channel']}>にて異議申し立てを行ってください。"
            if dm:
                await message.author.send(message.author.mention, embed=embed)
            else:
                await message.channel.send(message.author.mention, embed=embed)
            embed = discord.Embed(title="重要通知", color=0x228b22)
            embed.description = f"あなたは違反行為によってロックされましたが、以下の手順で解除することができます:\n> 1.[禁止行為](https://milkcoffee.cf/usage#rules_of_globalchat)の再確認\n> 2.確認後に当BOTとのDMで `unlock` と送信する。\nロック解除後に違反行為を犯した場合は、ミュートされる可能性がありますので十分ご注意ください。(ミュート解除はご自身では行えません)"
            await message.author.send(embed=embed)
            reason = f"自動ロック({message.id}) " + reason
            self.bot.LOCK[str(message.author.id)] = reason
            embed = discord.Embed(title=f"{message.author.name} がロックされました。", color=0xf4a460)
            embed.description = f"ユーザー情報: {str(message.author)} ({message.author.id})\n理由: {reason}\n実行者: {str(self.bot.user)} ({self.bot.user.id})"
            await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
            return 0
        else:
            return 1

    async def process_message(self, message):
        try:
            if await self.filter_message(message) == 1:
                return
            day_head = datetime.datetime.now().strftime('%Y%m%d')
            if day_head not in self.bot.global_chat_day:
                self.bot.global_chat_day[day_head] = []
            self.bot.global_chat_day[day_head].append(message.id)
            self.bot.global_chat_log[str(message.id)] = {
                "sender": {
                    "id": message.author.id,
                    "name": message.author.name,
                    "avatar": str(message.author.avatar_url)
                },
                "guild": message.guild.id,
                "channel": message.channel.id,
                "content": message.content,
                "attachment": [],
                "webhooks": [],
                "timestamp": message.created_at.timestamp()
            }

            has_attachment = False
            if message.attachments:
                has_attachment = True
                attachment_embed = discord.Embed()
                file_list = []
                image_inserted = False
                for attachment in message.attachments:
                    if attachment.filename.endswith((".png", ".jpg", ".jpeg", ".gif")) and not image_inserted:
                        attachment_embed.set_image(url=attachment.url)
                        image_inserted = True
                    else:
                        file_list.append(f"[{attachment.filename}]({attachment.url})")
                attachment_embed.description = "\n".join(file_list)
                attachment_embed.set_footer(text="添付ファイル一覧だよ!ファイル名をクリックすると中身できるよ!")

            attachment_links = [attachment.proxy_url for attachment in message.attachments]
            self.bot.global_chat_log[str(message.id)]["attachment"] = attachment_links

            files = [await attachment.to_file() for attachment in message.attachments]
            embed = discord.Embed(color=0x0000ff)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed.description = message.content
            embed.timestamp = message.created_at
            embed.add_field(name="詳細情報", value=f"```メッセージID: {message.id}\n送信者情報: {str(message.author)} ({message.author.id})\n送信元サーバー: {message.guild.name} ({message.guild.id})\n送信元チャンネル: {message.channel.name} ({message.channel.id})```", inline=False)
            embed.add_field(name="日時", value=(message.created_at + datetime.timedelta(hours=9)).strftime('%Y/%m/%d %H:%M:%S'), inline=False)

            self.global_chat_message_cache[message.id] = []
            for channel_id in self.bot.global_channels:
                if channel_id == message.channel.id:
                    continue
                target_channel = self.bot.get_channel(channel_id)
                if target_channel is None:
                    self.bot.global_channels.remove(channel_id)
                    continue
                elif not target_channel.permissions_for(target_channel.guild.get_member(self.bot.user.id)).manage_webhooks:
                    self.bot.global_channels.remove(channel_id)
                    await target_channel.send(f"グローバルチャットメッセージの転送しようとしたけど、`manage_webhooks(webhookの管理)`権限が不足していて、できなかったよ(´;ω;｀)(グローバルチャットへの接続を解除しました)\n権限設定を修正してから、再度 `{self.bot.PREFIX}global join` を実行して、グローバルチャンネルに参加してね!")
                    continue
                channel_webhooks = await target_channel.webhooks()
                webhook = discord.utils.get(channel_webhooks, name="global_chat_webhook_mafu")
                if webhook is None:
                    webhook = await target_channel.create_webhook(name=f"global_chat_webhook_mafu")
                if has_attachment:
                    msg_obj = await webhook.send(message.content, embed=attachment_embed, username=str(message.author), avatar_url=message.author.avatar_url, wait=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
                else:
                    msg_obj = await webhook.send(message.content, username=str(message.author), avatar_url=message.author.avatar_url, wait=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
                self.bot.global_chat_log[str(message.id)]["webhooks"].append({
                    "guild": msg_obj.guild.id,
                    "channel": msg_obj.channel.id,
                    "message": msg_obj.id
                })
                self.global_chat_message_cache[message.id].append(msg_obj)
            del self.sending_message[message.id]
        except:
            await self.bot.get_channel(self.bot.datas["system-log-channel"]).send(traceback2.format_exc())

    async def process_new_user(self, message):
        embed = discord.Embed(title="グローバルチャットに関するお知らせ!", color=0xff0000)
        welcome_text = f"""
❔グローバルチャットとは❔他のサーバーの人と特定のチャンネルを介してお話しできちゃうサービスだよ!
__他のサーバーから届いたメッセージは、webhookという技術を使用しているため、**BOT**と表示されますが、中身は**[人間]**です!!__
(同じサーバーの人のメッセージはBOTと表示されません)
使う前に必ず[禁止事項](https://milkcoffee.cf/usage#rules_of_globalchat)を確認してね!
何かわからないことがあれば、[公式サーバー]({self.bot.datas['server']})まで！
        """
        embed.description = welcome_text
        embed.set_footer(text=f"最後まで読んでくれてありがとう！説明書読むのってめんどくさいよね💦 by 作成者({self.bot.datas['author']})")
        await message.channel.send(f"{message.author.mention}さん\nここは{self.bot.user.mention}BOTのグローバルチャットに設定されています!\n__DMに簡単な説明を送ったから必ず目を通しといてね!__")
        try:
            await message.author.send(embed=embed)
        except discord.Forbidden:
            pass
        if str(message.author.id) not in self.bot.database:
            self.bot.database[str(message.author.id)] = {
                "global": {
                    "last_word": "",
                    "last_time": 0,
                    "last_warning": 0,
                    "fast_post": 0,
                    "same_post": 0,
                    "warning": 0,
                    "history": {}
                }
            }
        elif "global" not in self.bot.database[str(message.author.id)]:
            self.bot.database[str(message.author.id)]["global"] = {
                "last_word": "",
                "last_time": 0,
                "last_warning": 0,
                "fast_post": 0,
                "same_post": 0,
                "warning": 0,
                "history": {}
            }

    async def send_log(self, message):
        files = [await attachment.to_file() for attachment in message.attachments]
        embed = discord.Embed(color=0x0000ff)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.description = message.content
        embed.timestamp = message.created_at
        embed.add_field(name="詳細情報", value=f"```メッセージID: {message.id}\n送信者情報: {str(message.author)} ({message.author.id})\n送信元サーバー: {message.guild.name} ({message.guild.id})\n送信元チャンネル: {message.channel.name} ({message.channel.id})```", inline=False)
        embed.add_field(name="日時", value=(message.created_at + datetime.timedelta(hours=9)).strftime('%Y/%m/%d %H:%M:%S'), inline=False)
        await self.global_chat_log_channel.send(embed=embed, files=files)

    async def on_global_message(self, message):
        self.sending_message[message.id] = True
        if str(message.author.id) in self.bot.BAN:
            return await message.author.send(f"あなたのアカウントはBANされています(´;ω;｀)\nBANされているユーザーはグローバルチャットもご使用になれません。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        elif str(message.author.id) in self.bot.MUTE:
            return await message.author.send(f"あなたのアカウントはグローバルチャット上でミュートされているため、グローバルチャットを現在ご使用になれません(´;ω;｀)\nミュートに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        elif str(message.author.id) in self.bot.LOCK:
            return await message.author.send(f"あなたのアカウントはグローバルチャット上でロックされているため、グローバルチャットを現在ご使用になれません(´;ω;｀)\n既にあなたにロックの解除方法をお送りしておりますので、ご確認ください。\nロックに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        elif (str(message.author.id) not in self.bot.database) or ("global" not in self.bot.database[str(message.author.id)]):
            return await self.process_new_user(message)
        await self.send_log(message)
        if self.sending_message[message.id]:
            self.sending_message[message.id] = self.bot.loop.create_task(self.process_message(message))
        else:
            del self.sending_message[message.id]

    @tasks.loop(hours=12)
    async def process_chat_log(self):
        day_head = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime('%Y%m%d')
        for day in self.bot.global_chat_day:
            if int(day) >= int(day_head):
                continue
            for msg_id in self.bot.global_chat_day[day]:
                try:
                    del self.bot.global_chat_log[str(msg_id)]
                    del self.global_chat_message_cache[msg_id]
                except KeyError:
                    pass
            del self.bot.global_chat_day[day]

    async def filter_message(self, message):
        try:
            res, reason = self.filter_obj.execute_filter(message.content, message, self.bot.invites)
            now = message.created_at.timestamp()
            punishment = {}
            warning_point = 0
            if (self.bot.database[str(message.author.id)]["global"]["last_warning"] - now) >= 60*60*24*14:
                self.bot.database[str(message.author.id)]["global"]["warning"] = 0
            if (now - self.bot.database[str(message.author.id)]["global"]["last_time"]) <= 3:
                self.bot.database[str(message.author.id)]["global"]["fast_post"] += 1
                if self.bot.database[str(message.author.id)]["global"]["fast_post"] >= 3:
                    punishment["メッセージの連投"] = 2; warning_point += 2
            elif self.bot.database[str(message.author.id)]["global"]["fast_post"] != 0:
                self.bot.database[str(message.author.id)]["global"]["fast_post"] = 0
            if self.bot.database[str(message.author.id)]["global"]["last_word"] == message.content:
                self.bot.database[str(message.author.id)]["global"]["same_post"] += 1
                if self.bot.database[str(message.author.id)]["global"]["same_post"] >= 2:
                    punishment["同一内容の連続送信"] = 2; warning_point += 2
            elif self.bot.database[str(message.author.id)]["global"]["same_post"] != 0:
                self.bot.database[str(message.author.id)]["global"]["same_post"] = 0
            self.bot.database[str(message.author.id)]["global"]["last_time"] = now
            self.bot.database[str(message.author.id)]["global"]["last_word"] = message.content
            if message.content in self.command_list:
                await message.channel.send(f"{message.author.mention}さん!\nグローバルチャットに接続しているチャンネルでは**__コマンドを使えないよ__**!\n代わりに他のチャンネルを使用してね!")
                if not punishment:
                    return 1
            if res == 1 and not punishment:
                return 0
            if reason == 0:  # 不適切なリンク
                punishment["不適切なリンク"] = 5; warning_point += 5
            elif reason == 1:  # フルでNG
                punishment["不適切な表現"] = 5; warning_point += 5
            elif reason == 2:  # 招待リンク
                punishment["招待リンクの送信"] = 5; warning_point += 5
            elif res != 1:  # 不適切な発言を含む
                punishment["不適切な内容を含む"] = 3; warning_point += 3
            # punishmentの中身をとりだしてログに送信 - historyを書く
            self.bot.database[str(message.author.id)]["global"]["history"][str(message.id)] = punishment
            warning_text = ",".join(punishment.keys())
            self.bot.database[str(message.author.id)]["global"]["warning"] += warning_point
            self.bot.database[str(message.author.id)]["global"]["last_warning"] = now
            embed = discord.Embed(title=f"{message.author.name} が警告を受けました。", color=0xffff00)
            embed.description = f"ユーザー情報: {str(message.author)} ({message.author.id})\n理由: {warning_text}\n対象メッセージ:\n {message.content}\n合計違反点数: {warning_point}\n現在の合計点数: {self.bot.database[str(message.author.id)]['global']['warning']}\n警告番号: {message.id}\n実行者: {str(self.bot.user)} ({self.bot.user.id})"
            await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
            code = await self.check_point(message, warning_text)
            if code:
                embed = discord.Embed(title="重要通知", color=0xdc143c)
                embed.description = f"{warning_text}が検出されました。これらの行為はグローバルチャット上では禁止されています。\n繰り返すとミュートなどの処置を受けることとなりますので、十分お気を付けください。\n尚、この通知が不服である場合(誤検出である等)はお手数ですが、[公式サーバー]({self.bot.datas['server']})の<#{self.bot.datas['appeal_channel']}>にて異議申し立てを行ってください。"
                await message.channel.send(message.author.mention, embed=embed)
            return 1
        except:
            await message.channel.send(traceback2.format_exc())

def setup(bot):
    bot.add_cog(GlobalChat(bot))
