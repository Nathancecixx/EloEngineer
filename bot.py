"""
Old version
"""

import discord
import asyncio
from ApiKeys import *

# setup discord bot
intents = discord.Intents.default()  # sets all intents to false by default
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

squad_message_id = None
squad = {}

# lock to prevent dirty reads
squad_Lock = asyncio.Lock()


async def Create_Voice_Channel(message, name, squad_num):
    # Find the category by name (or ID)
    category_name = "Squads"  # Replace with your actual category name
    category = discord.utils.get(message.guild.categories, name=category_name)

    # Check if the category exists

    if category is None:
        category = await message.guild.create_category(category_name)
        print(f"Created new category: {category_name}")

    # Create a voice channel for the squad within the found category
    voice_channel = await message.guild.create_voice_channel(name=f"Squad #{squad_num}", category=category)
    # Store the voice channel ID if needed for later reference
    squad[message.id] = {"members": [], "voice_channel_id": voice_channel.id}
    print(f"Created voice channel {voice_channel.name} in category {category_name} with ID {voice_channel.id}")


async def delete_voice_channel(guild, channel_id):
    voice_channel = guild.get_channel(channel_id)
    if voice_channel is not None:
        await voice_channel.delete()
        print(f"Deleted voice channel with ID {channel_id}")


async def Create_Squad(Game, Message, Num_Of_Spots, Color):
    squad_num = len(squad) + 1

    embed = discord.Embed(title=Game,
                          description="React with ✅ to join the 5 stack! \n\nOpen Positions:",
                          color=Color)
    for i in range(Num_Of_Spots):
        embed.add_field(name=f"Position {i + 1}", value="Open", inline=False)
    msg = await Message.channel.send(embed=embed)
    await msg.add_reaction('✅')
    squad[msg.id] = []

    await Create_Voice_Channel(msg, Game, squad_num)


async def Delete_Squad(Message, user, Prompt):
    await Message.delete()
    await Message.channel.send(Prompt)
    await delete_voice_channel(user.guild, squad[Message.id]["voice_channel_id"])
    del squad[Message.id]


# On start print in console what user is signed in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# on message event check if it is bot sending it, if not check if it is command
@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

    # RAINBOW SIX SIEGE
    if message.content.startswith('<@&1206000439653306409>'):
        await Create_Squad("Rainbow Six Siege", message, 5, discord.Color.yellow())

    # League Of Legends
    if message.content.startswith('<@&1206000241053138964>'):
        await Create_Squad("League Of Legends", message, 5, discord.Color.green())


@client.event
async def on_reaction_add(reaction, user):
    # Lock Squad to prevent dirty reads
    async with squad_Lock:
        # Store the id the reaction was on
        message_ID = reaction.message.id

        # Reaction was not done by bot
        if user != client.user:
            # Reaction is on a squad builder embed
            if message_ID in squad:
                if reaction.emoji == '❌':
                    await Delete_Squad(reaction.message, user, "The squad has been cancelled :(")
                    return

                # Check if the squad is full
                if len(squad[message_ID]["members"]) < 5:  # Ensure this references a list of members
                    print(f'{user.name} has added {reaction.emoji} to the message: {reaction.message.id}')

                    # Check if user id is in current squad
                    if user.id not in squad[message_ID]["members"]:  # Directly check for user ID
                        # Add the user's ID to the squad list
                        squad[message_ID]["members"].append(user.id)  # Store user IDs

                        # Update the embed with the new user's information
                        embed = reaction.message.embeds[0]
                        for i, field in enumerate(embed.fields):
                            if field.value == "Open":
                                embed.set_field_at(i, name=f"Position {i + 1}", value=f"Filled by {user.display_name}", inline=False)
                                await reaction.message.edit(embed=embed)
                                break  # Break after updating the first open position

                        # Send a message if the squad is now full
                        if len(squad[message_ID]["members"]) == 5:  # Ensure this references the list of members
                            await Delete_Squad(reaction.message, user, "The squad is now full!")


client.run(BotKey)
