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

    async def create_permissions_role(self, guild, squad_num):
        role = await guild.create_role(name=f"Squad {squad_num}")
        return role

    async def create_voice_channel(self, guild, name, role):
        category_name = "Squads"
        category = discord.utils.get(guild.categories, name=category_name)

        if category is None:
            category = await guild.create_category(category_name)
            print(f"Created new category: {category_name} in server {guild.id}")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True)
        }

        voice_channel = await guild.create_voice_channel(name=name, category=category, overwrites=overwrites)

        print(f"Created voice channel {voice_channel.name} in category {category_name} with ID {voice_channel.id}")
        return voice_channel

    async def delete_voice_channel(self, guild, voice_channel):
        voice_channel = guild.get_channel(voice_channel.id)
        if voice_channel is not None:
            await voice_channel.delete()
            print(f"Deleted voice channel with ID {voice_channel.id}")

    async def create_squad(self, game, channel, num_of_spots, color):
        squad_num = len(self.squad) + 1
        embed = discord.Embed(title=game, description="React with ✅ to join the squad! \n\nOpen Positions:",
                              color=color)
        for i in range(num_of_spots):
            embed.add_field(name=f"Position {i + 1}", value="Open", inline=False)
        msg = await channel.send(embed=embed)
        await msg.add_reaction('✅')
        role = await self.create_permissions_role(msg.guild, squad_num)
        voice_channel = await self.create_voice_channel(msg.guild, f"{game} Squad #{squad_num}", role)
        self.squad[msg.id] = {"members": [], "voice_channel_id": voice_channel.id, "message_channel_id": msg.channel.id, "size": num_of_spots, "role": role}

    async def edit_squad_message(self, channel_id, message_id, prompt):
        channel = self.client.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
                embed = discord.Embed(description=prompt, color=discord.Color.red())
                await message.edit(content=None, embed=embed)

            except discord.NotFound:
                print(f"Message with ID {message_id} could not be found in channel {channel_id}.")
            except discord.Forbidden:
                print(f"Lack permissions to fetch/delete message in channel {channel_id}.")
            except discord.HTTPException as e:
                print(f"Failed to fetch/delete message due to an HTTP error: {e}.")
        else:
            print(f"Channel with ID {channel_id} not found.")

    async def delete_squad(self, channel_id, message_id, prompt):
        # Fetch the channel where the squad message is located
        channel = self.client.get_channel(channel_id)
        if not channel:
            print(f"Channel with ID {channel_id} not found.")
            return

        # Fetch and update the squad message
        try:
            message = await channel.fetch_message(message_id)
            embed = discord.Embed(description=prompt, color=discord.Color.red())
            await message.edit(content=None, embed=embed)
        except discord.NotFound:
            print(f"Message with ID {message_id} could not be found in channel {channel_id}.")
            return
        except Exception as e:
            print(f"Failed to edit message due to: {e}")
            return

        # Perform cleanup for voice channel and role
        if message_id in self.squad:
            squad_info = self.squad[message_id]
            guild = channel.guild

            # Delete the voice channel if it exists
            voice_channel_id = squad_info.get("voice_channel_id")
            if voice_channel_id:
                voice_channel = guild.get_channel(voice_channel_id)
                if voice_channel:
                    await voice_channel.delete()
                    print(f"Deleted voice channel with ID {voice_channel_id}")

            # Delete the role if it exists
            role = squad_info.get("role")
            if role:
                await role.delete()
                print(f"Deleted role {role}")

            # Remove the squad from tracking
            del self.squad[message_id]

    @commands.command(name='squad', help='Initializes a squad builder embed')
    async def squad(self, ctx, size: int = 0, game='Default'):
        # Argument check
        if size < 1 or size > 11:
            await ctx.channel.send("Invalid arguments")
        else:
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
        async with (self.squad_lock):
            message_id = reaction.message.id
            # Checks if reaction was from the bot and is on a logged squad builder embed message
            if user != self.client.user and message_id in self.squad:
                # Checks if reaction is an emoji and if the squad is full already
                if reaction.emoji == '✅' and len(self.squad[message_id].get("members", [])) < 5:
                    # Checks if the user is already in the squad they are reacting too
                    if user.id not in self.squad[message_id]["members"]:
                        # Person is not in list therefore:
                        # Add them to the list of members
                        self.squad[message_id]["members"].append(user.id)
                        # Add them to squad role
                        role = self.squad[message_id]["role"]

                        await user.add_roles(role)

                        # Creating updated embed
                        embed = reaction.message.embeds[0]
                        for i, field in enumerate(embed.fields):
                            if field.value == "Open":
                                embed.set_field_at(i, name=f"Position {i + 1}", value=f"Filled by {user.display_name}",
                                                   inline=False)
                                await reaction.message.edit(embed=embed)
                                break
                        if len(self.squad[message_id]["members"]) == self.squad[message_id]["size"]:
                            await self.edit_squad_message(reaction.message.channel.id,
                                                          reaction.message.id,
                                                          "The squad is now full!")

    # watches voice channels to disband squads when their calls become empty
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async with self.squad_lock:
            # Check if the member leaves a voice channel (before.channel is not None)
            # and the after.channel is None (they left or disconnected from a channel)
            if before.channel is not None and after.channel is None:
                # Get the voice channel ID the user left from
                voice_channel_id = before.channel.id

                # Check if this voice channel is one of the squad channels
                for message_id, info in self.squad.items():
                    if info.get("voice_channel_id") == voice_channel_id:
                        # Check if the voice channel is now empty
                        if len(before.channel.members) == 0:
                            # Delete the squad
                            await self.delete_squad(info.get("message_channel_id"), message_id, "Squad Disbanded...")
                            break


async def setup(client):
    await client.add_cog(SquadBuilder(client))
