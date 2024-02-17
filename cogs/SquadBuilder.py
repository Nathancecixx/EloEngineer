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
from discord.ext import commands
import asyncio


class SquadBuilder(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.squad = {}
        self.squad_lock = asyncio.Lock()

    async def create_voice_channel(self, message, name, squad_num):
        category_name = "Squads"
        category = discord.utils.get(message.guild.categories, name=category_name)

        if category is None:
            category = await message.guild.create_category(category_name)
            print(f"Created new category: {category_name}")

        voice_channel = await message.guild.create_voice_channel(name=f"Squad #{squad_num}", category=category)
        self.squad[message.id] = {"members": [], "voice_channel_id": voice_channel.id}
        print(f"Created voice channel {voice_channel.name} in category {category_name} with ID {voice_channel.id}")

    async def delete_voice_channel(self, guild, channel_id):
        voice_channel = guild.get_channel(channel_id)
        if voice_channel is not None:
            await voice_channel.delete()
            print(f"Deleted voice channel with ID {channel_id}")

    async def create_squad(self, game, channel, num_of_spots, color):
        squad_num = len(self.squad) + 1
        embed = discord.Embed(title=game, description="React with ✅ to join the squad! \n\nOpen Positions:",
                              color=color)
        for i in range(num_of_spots):
            embed.add_field(name=f"Position {i + 1}", value="Open", inline=False)
        msg = await channel.send(embed=embed)
        await msg.add_reaction('✅')
        self.squad[msg.id] = {"members": [], "voice_channel_id": None, "size": num_of_spots}
        # await self.create_voice_channel(msg, game, squad_num)

    async def delete_squad(self, message, prompt):
        await message.delete()
        await message.channel.send(prompt)
        if "voice_channel_id" in self.squad[message.id]:
            await self.delete_voice_channel(message.guild, self.squad[message.id]["voice_channel_id"])
        del self.squad[message.id]

    @commands.command(name='squad', help='Initializes a squad builder embed')
    async def squad(self, ctx, size: int = 0, game='Default'):

        if size == 0:
            await ctx.channel.send("Invalid arguments")
        else:
            print(size)
            print(ctx.channel)
            game_title = f'{game}, {size} Stack'
            await self.create_squad(game_title, ctx.channel, size, discord.Color.blurple())
    """
    
    # Optional functionality built specifically for my server
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.content.startswith('<@&1206000439653306409>'):
            await self.create_squad("Rainbow Six Siege", message.channel, 5, discord.Color.yellow())
        elif message.content.startswith('<@&1206000241053138964>'):
            await self.create_squad("League Of Legends", message.channel, 5, discord.Color.green())
    """
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        async with self.squad_lock:
            message_id = reaction.message.id
            if user != self.client.user and message_id in self.squad:
                if reaction.emoji == '✅' and len(self.squad[message_id].get("members", [])) < 5:
                    if user.id not in self.squad[message_id]["members"]:
                        self.squad[message_id]["members"].append(user.id)
                        embed = reaction.message.embeds[0]
                        for i, field in enumerate(embed.fields):
                            if field.value == "Open":
                                embed.set_field_at(i, name=f"Position {i + 1}", value=f"Filled by {user.display_name}",
                                                   inline=False)
                                await reaction.message.edit(embed=embed)
                                break
                        if len(self.squad[message_id]["members"]) == self.squad[message_id]["size"]:
                            await self.delete_squad(reaction.message, "The squad is now full!")


async def setup(client):
    await client.add_cog(SquadBuilder(client))
