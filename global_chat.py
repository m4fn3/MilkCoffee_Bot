from discord.ext import commands, tasks
import discord, datetime, traceback2
import asyncio


class GlobalChat(commands.Cog):
    """他のサーバーに居る人と、設定したチャンネルでお話しできます。(現在開発中)"""

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        self.global_chat_log_channel = None
        self.sending_message = {}
        self.global_chat_message_cache = {}
        self.waiting_vertify = []

    async def delete_global_message(self, message_id: int):
        if str(message_id) in self.bot.global_chat_log:
            if message_id in self.sending_message:
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

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) in self.bot.BAN:
            await ctx.send(f"あなたのアカウントはBANされています。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
            raise commands.CommandError("Your Account Banned")

    @commands.group(name="global", usage="global [サブコマンド]", description="グローバルチャットに関するコマンドです。\nグローバルチャット設定を操作するためには、BOTが manage_webhook(webhookを管理) の権限を持ち、コマンドの実行者が manage_channel(チャンネルの管理) 権限を持っている必要があります。")
    async def global_command(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"サブコマンドが不足しています。\n`{ctx.prefix}help global`で使い方を確認できます。")

    @global_command.command(name="join", usage="global join (チャンネル)", description="グローバルチャットに接続します。チャンネルを指定しなかった場合、コマンドが実行されたチャンネルに設定します。", help="`<prefix>global join` ... コマンドを打ったチャンネルをグローバルチャットに接続します。\n`<prefix>global join #チャンネル` ... 指定したチャンネルをグローバルチャットに接続します。")
    async def global_join(self, ctx):
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if not target_channel.permissions_for(ctx.author).manage_channels:
            return await ctx.send(f"あなたは {target_channel.mention} チャンネルで設定する権限がありません。\nセキュリティ対策のため、チャンネルをグローバルチャットに接続するには、コマンドを実行するユーザーが`manage_channels(チャンネルを管理)`の権限を持っている必要があります。\n権限に関しては、サーバーの管理者に依頼してください。")
        if target_channel.id in self.bot.global_channels:
            return await ctx.send(f"{target_channel.mention} は既にグローバルチャットに参加しています。")
        if target_channel.permissions_for(ctx.guild.get_member(self.bot.user.id)).manage_webhooks:
            channel_webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(channel_webhooks, name="global_chat_webhook_mafu")
            if webhook is None:
                await target_channel.create_webhook(name=f"global_chat_webhook_mafu")
            self.bot.global_channels.append(target_channel.id)
            await ctx.send(f"{target_channel.mention} がグローバルチャットに接続されました!")
            embed = discord.Embed(title=f"{ctx.channel.name} がグローバルチャットに参加しました。", color=0x2f4f4f)
            embed.description = f"サーバー情報: {ctx.guild.name} ({ctx.guild.id})\nチャンネル情報: {ctx.channel.name} ({ctx.channel.id})\n設定したユーザー: {str(ctx.author)} ({ctx.author.id})\nメンバー数: {len(ctx.guild.members)}\nサーバー管理者: {str(ctx.guild.owner)} ({ctx.guild.owner.id})"
            await self.bot.get_channel(self.bot.datas["log_channel"]).send(embed=embed)
        else:
            await ctx.send(f"`manage_webhooks(webhookの管理)`権限が不足しています。")

    @global_command.command(name="leave", usage="global leave [チャンネル]", description="指定したチャンネルをグローバルチャットから切断します。(グローバルチャットに接続されているチャンネルではコマンドを実行できません)", help="`<prefix>global leave #チャンネル` ... 指定したチャンネルをグローバルチャットから切断します。")
    async def global_leave(self, ctx):
        if ctx.message.channel_mentions:
            target_channel = ctx.message.channel_mentions[0]
            if not target_channel.permissions_for(ctx.author).manage_channels:
                return await ctx.send(f"あなたは {target_channel.mention} チャンネルで設定する権限がありません。\nセキュリティ対策のため、チャンネルをグローバルチャットに接続するには、コマンドを実行するユーザーが`manage_channels(チャンネルを管理)`の権限を持っている必要があります。\n権限に関しては、サーバーの管理者に依頼してください。")
            if target_channel.id in self.bot.global_channels:
                self.bot.global_channels.remove(target_channel.id)
                await ctx.send(f"{target_channel.mention} をグローバルチャットから切断しました。")
            else:
                await ctx.send(f"{target_channel.mention} はフローバルチャットに接続されていません。")
        else:
            await ctx.send(f"チャンネルが指定されていません。詳しい使い方は `{ctx.prefix}help global leave` で確認してください。")

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
            #  filter text
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
                attachment_embed.set_footer(text="添付ファイルです。ファイル名をクリックして中身を確認できます。")

            attachment_links = [attachment.proxy_url for attachment in message.attachments]
            self.bot.global_chat_log[str(message.id)]["attachment"] = attachment_links
            files = []
            for attachment in message.attachments:
                attached_file = await attachment.to_file()
                files.append(attached_file)
            embed = discord.Embed(color=0x0000ff)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed.description = message.content
            embed.timestamp = message.created_at
            embed.add_field(name="詳細情報", value=f"```メッセージID: {message.id}\n送信者情報: {str(message.author)} ({message.author.id})\n送信元サーバー: {message.guild.name} ({message.guild.id})\n送信元チャンネル: {message.channel.name} ({message.channel.id})```", inline=False)
            embed.add_field(name="日時", value=(message.created_at + datetime.timedelta(hours=9)).strftime('%Y/%m/%d %H:%M:%S'), inline=False)
            await self.global_chat_log_channel.send(embed=embed, files=files)
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
                    await target_channel.send(f"グローバルチャットメッセージの転送を試みましたが、`manage_webhooks(webhookの管理)`権限が不足しているため、失敗しました。(グローバルチャットへの接続を解除しました)\n権限設定を修正してから、再度 `{self.bot.command_prefix}global join` を実行して、グローバルチャンネルに参加してください。")
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
        welcome_text = """
__最後まで必ずお読みください。__
{message.author.name}さんが先ほどメッセージを送信された {message.channel.mention} チャンネルは当BOTのグローバルチャットに設定されています。

グローバルチャットの仕組みを理解して、安全にご使用いただくために簡単な説明をさせてください。

グローバルチャットとは特定のチャンネルを介して他のサーバーに居る人とお話しできるサービスです！

グローバルチャットに設定されているチャンネルでは、他のサーバーから届いたメッセージは、BOTを介しているため__**BOT**__と表示されますが、中身は__
**人間**__です。これだけは覚えておいてくださいね！

グローバルチャットでの禁止事項:
> 1. サーバー、サービスを一方的に宣伝する行為。
> ただし、話の流れで自分が利用している便利なサービス等を他の人にも紹介するなどの場合はこれに及びません。
> discordサーバーの招待リンクに関しては、__理由を問わず__禁止されています。
> 2. R18コンテンツやグロテスクな表現を含むコンテンツの送信
> 3. その他BOT管理者が極めて不適切だと判断した行為
以上の項目を守っていただけない場合、最大でBAN(BOT使用禁止)の処置をとらせていただきます。
ルールを守って楽しんでくださいね♪

また、わからないことがあれば、公式サーバー:　{self.bot.datas['server']}　で質問してください。
        """
        try:
            await message.author.send(welcome_text)
        except discord.Forbidden:
            pass  # TODO: 何か送る
        if str(message.author.id) not in self.bot.database:
            self.bot.database[str(message.author.id)] = {
                "global": {
                    "last_word": "",
                    "last_time": "",
                    "warning": {}
                }
            }
        elif "global" not in self.bot.database[str(message.author.id)]:
            self.bot.database[str(message.author.id)]["global"] = {
                "last_word": "",
                "last_time": "",
                "warning": {}
            }


    async def on_global_message(self, message):
        if str(message.author.id) in self.bot.BAN:
            return await message.author.send(f"あなたのアカウントはBANされています。\nBANされているユーザーはグローバルチャットもご使用になれません。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        elif str(message.author.id) in self.bot.MUTE:
            return await message.author.send(f"あなたのアカウントはグローバルチャット上でミュートされているため、グローバルチャットを現在ご使用になれません。\nミュートに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        elif (str(message.author.id) not in self.bot.database) or ("global" not in self.bot.database[str(message.author.id)]):
            await self.process_new_user(message)
        self.sending_message[message.id] = self.bot.loop.create_task(self.process_message(message))

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


# TODO: filterの追加
# TODO: 初回送信時 user-global-chat
# TODO: レベリング(?)


def setup(bot):
    bot.add_cog(GlobalChat(bot))
