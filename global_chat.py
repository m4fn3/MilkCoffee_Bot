from discord.ext import commands, tasks
import discord, datetime, traceback2, time
from filter.filter import *


class GlobalChat(commands.Cog):
    """他のサーバーに居る人と、設定したチャンネルでお話しできるよ!"""

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        self.global_chat_log_channel = None
        self.sending_message = {}
        self.filter_obj = Filter(self.bot)
        self.global_chat_message_cache = {}

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
        self.global_chat_log_channel = self.bot.get_channel(self.bot.datas["global_chat_log_channel"])
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
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(f"あなたのアカウントはBANされています。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
            raise commands.CommandError("Your Account Banned")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"引数が足りません。\nエラー詳細:\n{error}")
        else:
            await ctx.send(f"エラーが発生しました:\n{error}")

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

    @global_command.command()
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
        embed = discord.Embed(title=f"{user.name} がミュートされました。", color=0xdc143c)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @global_command.command()
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
            await ctx.send("このユーザーはミュートされていません。")
        del self.bot.MUTE[str(user.id)]
        await ctx.send(f"該当ユーザーをミュート解除しました。(ユーザー情報: {str(user)} ({user.id}))")
        embed = discord.Embed(title=f"{user.name} がミュート解除されました。", color=0x4169e1)
        embed.description = f"ユーザー情報: {str(user)} ({user.id})\n理由: {reason}\n実行者: {str(ctx.author)} ({ctx.author.id})"
        await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)

    @global_command.command(name="muted")
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
                    await target_channel.send(f"グローバルチャットメッセージの転送しようとしたけど、`manage_webhooks(webhookの管理)`権限が不足していて、できなかったよ(´;ω;｀)(グローバルチャットへの接続を解除しました)\n権限設定を修正してから、再度 `{self.bot.command_prefix}global join` を実行して、グローバルチャンネルに参加してね!")
                    continue
                channel_webhooks = await target_channel.webhooks()
                webhook = discord.utils.get(channel_webhooks, name="global_chat_webhook_mafu")
                if webhook is None:
                    webhook = await target_channel.create_webhook(name=f"global_chat_webhook_mafu")
                if has_attachment:
                    msg_obj = await webhook.send(message.content, embed=attachment_embed, username=message.author.name, avatar_url=message.author.avatar_url, wait=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
                else:
                    msg_obj = await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar_url, wait=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
                self.bot.global_chat_log[str(message.id)]["webhooks"].append({
                    "guild": msg_obj.guild.id,
                    "channel": msg_obj.channel.id,
                    "message": msg_obj.id
                })
                self.global_chat_message_cache[message.id].append(msg_obj)
            del self.sending_message[message.id]
        except:
            await message.channel.send(traceback2.format_exc())

    async def process_new_user(self, message):
        embed = discord.Embed(title="グローバルチャットに関するお知らせ!", color=0xff0000)
        welcome_text = f"""
❔グローバルチャットとは❔他のサーバーの人と特定のチャンネルを介してお話しできちゃうサービスだよ!
__他のサーバーから届いたメッセージは、webhookという技術を使用しているため、**BOT**と表示されますが、中身は**[人間]**です!!__
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
            #  連投検知 - 最後に送った時間から2秒たっていない場合
            now = message.created_at.timestamp()
            punishment = {}
            warning_point = 0
            if (now - self.bot.database[str(message.author.id)]["global"]["last_time"]) <= 3:
                self.bot.database[str(message.author.id)]["global"]["fast_post"] += 1
                if self.bot.database[str(message.author.id)]["global"]["fast_post"] >= 2:
                    self.bot.database[str(message.author.id)]["global"]["warning"] += 2
                    punishment["メッセージの連投"] = 2; warning_point += 2
            elif self.bot.database[str(message.author.id)]["global"]["fast_post"] != 0:
                self.bot.database[str(message.author.id)]["global"]["fast_post"] = 0
            #  同じメッセージの連続投稿検知
            if self.bot.database[str(message.author.id)]["global"]["last_word"] == message.content:
                self.bot.database[str(message.author.id)]["global"]["same_post"] += 1
                if self.bot.database[str(message.author.id)]["global"]["same_post"] >= 2:
                    self.bot.database[str(message.author.id)]["global"]["warning"] += 2
                    punishment["同一内容の連続送信"] = 2; warning_point += 2
                    pass  # 同じメッセージ投稿の警告
            elif self.bot.database[str(message.author.id)]["global"]["same_post"] != 0:
                self.bot.database[str(message.author.id)]["global"]["same_post"] = 0
            self.bot.database[str(message.author.id)]["global"]["last_time"] = now
            self.bot.database[str(message.author.id)]["global"]["last_word"] = message.content
            # TODO: history書き込み - 5,10を超えているか検知 - -管理者によるhistory&ポイント取り消しコマンド
            if res == 1 and not punishment:
                return 0
            if reason == 0:
                #  不適切なリンク
                punishment["不適切なリンク"] = 5; warning_point += 5
                self.bot.database[str(message.author.id)]["global"]["warning"] += 5
            elif reason == 1:
                # フルでNG
                punishment["不適切な表現"] = 5; warning_point += 5
                self.bot.database[str(message.author.id)]["global"]["warning"] += 5
            elif reason == 2:
                #  招待リンク
                punishment["招待リンクの送信"] = 5; warning_point += 5
                self.bot.database[str(message.author.id)]["global"]["warning"] += 5
            elif res != 1:
                #  不適切な発言を含む
                punishment["不適切な内容を含む"] = 3; warning_point += 3
                self.bot.database[str(message.author.id)]["global"]["warning"] += 3
            # punishmentの中身をとりだしてログに送信 - historyを書く
            self.bot.database[str(message.author.id)]["global"]["history"][str(message.id)] = punishment
            warning_text = ",".join(punishment.keys())
            await message.channel.send(f"{message.author.mention}さん\n{warning_text}が検出されました。これらの行為はグローバルチャットでは禁止されています。\n繰り返すとミュート等の処置を受けることになりますので十分注意してください。\n尚、この通知が不服である場合(誤検出である等)は、公式サーバー( {self.bot.datas['server']} )の{self.bot.datas['appeal_channel']}にて異議申し立てを行ってください。")
            embed = discord.Embed(title=f"{message.author.name} が警告を受けました。", color=0xffff00)
            embed.description = f"ユーザー情報: {str(message.author)} ({message.author.id})\n理由: {warning_text}\n合計違反点数: {warning_point}\n実行者: {str(self.bot.user)} ({self.bot.user.id})"
            await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
            if self.bot.database[str(message.author.id)]["global"]["warning"] >= 10:
                reason = f"自動ミュート({message.id}) " + warning_text
                self.bot.MUTE[str(message.author.id)] = reason
                embed = discord.Embed(title=f"{message.author.name} がミュートされました。", color=0xdc143c)
                embed.description = f"ユーザー情報: {str(message.author)} ({message.author.id})\n理由: {reason}\n実行者: {str(self.bot.user)} ({self.bot.user.id})"
                await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
                self.bot.database[str(message.author.id)]["global"]["warning"] = 0
            elif self.bot.database[str(message.author.id)]["global"]["warning"] >= 5:
                pass  # lock
            return 1
        except:
            await message.channel.send(traceback2.format_exc())

#TODO: レベリング?名前の横に絵文字追加

def setup(bot):
    bot.add_cog(GlobalChat(bot))
