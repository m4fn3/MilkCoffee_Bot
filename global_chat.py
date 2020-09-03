from discord.ext import commands
import discord


class GlobalChat(commands.Cog):
    """他のサーバーに居る人と、設定したチャンネルでお話しできます。(現在開発中)"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    async def cog_before_invoke(self, ctx):
        if ctx.author.id in self.bot.BAN:
            await ctx.send(f"あなたのアカウントはブロックされています。あなたの電話番号は {ctx.author.id} です。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
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

    async def on_global_message(self, message):
        if message.author.id in self.bot.BAN:
            return await message.author.send(f"あなたのアカウントはBANされています。\nBANされているユーザーはグローバルチャットもご使用になれません。\nBANに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        elif message.author.id in self.bot.MUTE:
            return await message.author.send(f"あなたのアカウントはグローバルチャット上でミュートされているため、グローバルチャットを現在ご使用になれません。\nミュートに対する異議申し立ては、公式サーバーの <#{self.bot.datas['appeal_channel']}> にてご対応させていただきます。")
        #  filter text
        #  save message data to log
        files = []
        for attachment in message.attachments:
            attached_file = await attachment.to_file()
            files.append(attached_file)
        for channel_id in self.bot.global_channels:
            if channel_id == message.channel.id:
                continue
            target_channel = self.bot.get_channel(channel_id)
            if target_channel is None:
                self.bot.global_channels.remove(channel_id)
            elif not target_channel.permissions_for(target_channel.guild.get_member(self.bot.user.id)).manage_webhooks:
                self.bot.global_channels.remove(channel_id)
                return await target_channel.send(f"グローバルチャットメッセージの転送を試みましたが、`manage_webhooks(webhookの管理)`権限が不足しているため、失敗しました。(グローバルチャットへの接続を解除しました)\n権限設定を修正してから、再度 `{self.bot.command_prefix}global join` を実行して、グローバルチャンネルに参加してください。")
            channel_webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(channel_webhooks, name="global_chat_webhook_mafu")
            if webhook is None:
                webhook = await target_channel.create_webhook(name=f"global_chat_webhook_mafu")
            msg_obj = await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar_url, files=files, wait=True)
            #  save webhooked mesage log

# TODO: めっセージ削除
# TODO: log保存
# TODO: filterの追加


def setup(bot):
    bot.add_cog(GlobalChat(bot))