"""
+------------------------------------------------------------+
| * Squad Builder is a discord bot written in python which * |
| * adds easy squad formation features to a server.        * |
|                                                            |
| * Squad_Builder                                          * |
| * fall 23 - Nathan Ceci                                  * |
+------------------------------------------------------------+
"""

import discord
from discord.utils import get
from discord.ext import commands
import asyncio


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Hey {member.mention}, Welcome to {member.guild.name}.')
        else:
            channel = await member.guild.create_text_channel("Welcome!")
            await channel.send(f'Hey {member.mention}, Welcome to {member.guild.name}.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = get(member.guild.text_channels, name="losers-list")
        if channel is None:
            channel = await member.guild.create_text_channel('losers-list')

        await channel.send(f"{member.name} has become a loser...")

    # TODO
    @commands.command(name='info', help='Prints details about the server')
    async def info(self, ctx):
        owner = str(ctx.guild.owner)
        guild_id = str(ctx.guild.id)
        member_count = str(ctx.guild.member_count)
        desc = ctx.guild.description

        embed = discord.Embed(
            title=ctx.guild.name + " Server Information",
            description=desc,
            color=discord.Color.blue()
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Server ID", value=guild_id, inline=True)
        embed.add_field(name="Member Count", value=member_count, inline=True)

        guild = ctx.guild
        roles = [role for role in guild.roles if role != ctx.guild.default_role]
        embed2 = discord.Embed(title="Server Roles", description=f" ".join([role.mention for role in roles]))

        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)

    @commands.command(name='coinflip', help='Generates 50/50 coin flip in chat')
    async def coinflip(self, ctx):
        import random
        result = random.randint(0, 1)
        if result:
            await ctx.send('Heads')
        else:
            await ctx.send('Tails')


async def setup(client):
    await client.add_cog(General(client))
