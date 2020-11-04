import discord


async def error(sendable, text: str, title: str = None):
    embed = discord.Embed(description=f"<:xx:773568207222210650> {text}", color=discord.Color.red())
    if title:
        embed.title = title
    await sendable.send(embed=embed)


async def success(sendable, text: str, title: str = None):
    embed = discord.Embed(description=f"<:oo:773568207231123476> {text}", color=discord.Color.green())
    if title:
        embed.title = title
    await sendable.send(embed=embed)


async def warning(sendable, text: str, title: str = None):
    embed = discord.Embed(description=f"<:warn:773569061442289674> {text}", color=0xf7b51c)
    if title:
        embed.title = title
    await sendable.send(embed=embed)


async def normal(sendable, text: str, title: str = None):
    embed = discord.Embed(description=f"{text}", color=discord.Color.blue())
    if title:
        embed.title = title
    await sendable.send(embed=embed)
