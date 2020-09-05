from discord.ext import commands, tasks
import discord, datetime, traceback2


class GlobalChat(commands.Cog):
    """他のサーバーに居る人と、設定したチャンネルでお話しできます。(現在開発中)"""

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        self.global_chat_log_channel = None
        self.sending_message = {}
        self.global_chat_message_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.global_chat_log_channel = self.bot.get_channel(self.bot.datas["global_chat_log_channel"])
        if not self.process_chat_log.is_running():
            self.process_chat_log.start()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.channel_id in self.bot.global_channels:
            if str(payload.message_id) in self.bot.global_chat_log:
                if payload.message_id in self.sending_message:
                    task = self.sending_message[payload.message_id]
                    task.cancel()
                    del self.sending_message[payload.message_id]
                if payload.message_id in self.global_chat_message_cache:
                    for msg_obj in self.global_chat_message_cache[payload.message_id]:
                        try:
                            await msg_obj.delete()
                        except:
                            pass
                    del self.global_chat_message_cache[payload.message_id]
                else:
                    for msg_data in self.bot.global_chat_log[str(payload.message_id)]["webhooks"]:
                        try:
                            channel = self.bot.get_channel(msg_data["channel"])
                            message = await channel.fetch_message(msg_data["message"])
                            await message.delete()
                        except:
                            pass
                msg_data = self.bot.global_chat_log[str(payload.message_id)]
                embed = discord.Embed(color=0xff0000)
                embed.set_author(name=msg_data["sender"]["name"], icon_url=msg_data["sender"]["avatar"])
                embed.description = msg_data["content"]
                timestamp = msg_data["timestamp"]
                embed.timestamp = datetime.datetime.fromtimestamp(timestamp)
                guild = self.bot.get_guild(msg_data['guild'])
                embed.add_field(name="詳細情報", value=f"```メッセージID: {payload.message_id}\n送信者情報: {msg_data['sender']['name']} ({msg_data['sender']['id']})\n送信元サーバー: {guild.name} ({guild.id})\n送信元チャンネル: {guild.get_channel(msg_data['channel'])} ({msg_data['channel']})```", inline=False)
                embed.add_field(name="日時", value=(datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(hours=9)).strftime('%Y/%m/%d %H:%M:%S'), inline=False)
                links = [link for link in msg_data['attachment']]
                await self.global_chat_log_channel.send(content="\n".join(links), embed=embed)

    async def cog_before_invoke(self, ctx):
        if ctx.author.id in self.bot.BAN:
            await ctx.send(f"あなたのアカウントはBANされています。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
            raise commands.CommandError("Your Account Banned")

    @commands.group(name="global", usage="global [サブコマンド]", description="グローバルチャットに関するコマンドです。")
    async def global_command(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("サブコマンドを指定してください。例: `{0}global join`\n詳しくは `{0}help global`".format(ctx.prefix))

    @global_command.command(name="join", usage="global join (チャンネル)", description="グローバルチャットに接続します。チャンネルを指定しなかった場合、コマンドが実行されたチャンネルに設定します。")
    async def global_join(self, ctx):
        channel_id: int
        if ctx.message.channel_mentions:  # チャンネルのメンションがあった場合
            target_channel = ctx.message.channel_mentions[0]
        else:
            target_channel = ctx.channel
        if target_channel.id in self.bot.global_channels:
            return await ctx.send(f"{target_channel.mention} は既にグローバルチャットに参加しています。")
        if target_channel.permissions_for(ctx.guild.get_member(self.bot.user.id)).manage_webhooks:
            channel_webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(channel_webhooks, name="global_chat_webhook_mafu")
            if webhook is None:
                await target_channel.create_webhook(name=f"global_chat_webhook_mafu")
            self.bot.global_channels.append(target_channel.id)
            await ctx.send(f"{target_channel.mention} がグローバルチャットに接続されました!")
        else:
            await ctx.send(f"`manage_webhooks(webhookの管理)`権限が不足しています。")

    async def process_message(self, message):
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
        files = []
        for attachment in message.attachments:
            attached_file = await attachment.to_file()
            files.append(attached_file)
            self.bot.global_chat_log[str(message.id)]["attachment"].append(attachment.proxy_url)
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
            files = []
            for attachment in message.attachments:
                attached_file = await attachment.to_file()
                files.append(attached_file)
            msg_obj = await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar_url, files=files, wait=True, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
            self.bot.global_chat_log[str(message.id)]["webhooks"].append({
                "guild": msg_obj.guild.id,
                "channel": msg_obj.channel.id,
                "message": msg_obj.id
            })
            self.global_chat_message_cache[message.id].append(msg_obj)
        del self.sending_message[message.id]

    async def on_global_message(self, message):
        if message.author.id in self.bot.BAN:
            return await message.author.send(f"あなたのアカウントはBANされています。\nBANされているユーザーはグローバルチャットもご使用になれません。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        elif message.author.id in self.bot.MUTE:
            return await message.author.send(f"あなたのアカウントはグローバルチャット上でミュートされているため、グローバルチャットを現在ご使用になれません。\nミュートに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
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
