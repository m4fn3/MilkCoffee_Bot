import nextcord as discord

async def error_embed(sendable, text: str, title: str = None):
    embed = discord.Embed(
        description=f"<:xx:773568207222210650> {text}",
        color=discord.Color.red()
    )
    if title:
        embed.title = title
    return await sendable.send(embed=embed)


async def success_embed(sendable, text: str, title: str = None):
    embed = discord.Embed(
        description=f"<:oo:773568207231123476> {text}",
        color=discord.Color.green()
    )
    if title:
        embed.title = title
    return await sendable.send(embed=embed)


async def warning_embed(sendable, text: str, title: str = None):
    embed = discord.Embed(
        description=f"<:warn:773569061442289674> {text}",
        color=0xf7b51c
    )
    if title:
        embed.title = title
    return await sendable.send(embed=embed)


async def normal_embed(sendable, text: str, title: str = None):
    embed = discord.Embed(
        description=f"{text}",
        color=discord.Color.blue()
    )
    if title:
        embed.title = title
    return await sendable.send(embed=embed)
