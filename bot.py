import discord
import asyncio

#setup discord bot
intents = discord.Intents.default() #sets all intetns to false by default
intents.messages = True
intents.guilds = True
intents.reactions = True 
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

squad_message_id = None
squad = []

#lock to prevetn dirty reads
squad_Lock = asyncio.Lock()




#On start print in console what user is signed in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))



#on message event check if it is bot sending it, if not check if it is command
@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

#RAINBOW SIX SIEGE
    if message.content.startswith('<@&1206000439653306409>'):
        embed = discord.Embed(title="Rainbow Six Siege",
                              description="React with ✅ to join the 5 stack! \n\nOpen Positions:",
                              color=discord.Color.yellow())
        for i in range(5):
            embed.add_field(name=f"Position {i+1}", value="Open", inline=False)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction('✅')
        global squad_message_id
        squad_message_id = msg.id


#TODO: Implement this

#League Of Legends
#    if message.content.startswith('<@&1206000241053138964>'):
#        embed = discord.Embed(title="Leagge Of Legends",
#                              description="React with ✅ to join the 5 stack! \n\nOpen Positions:",
#                              color=discord.Color.green())
#        for i in range(5):
#            embed.add_field(name=f"Position {i+1}", value="Open", inline=False)
#        msg = await message.channel.send(embed=embed)
#        await msg.add_reaction('✅')
#        global squad_message_id
#        squad_message_id = msg.id






@client.event
async def on_reaction_add(reaction, user):
    #Lock Squad to prevent dirty reads
    async with squad_Lock:
        # Check if the reaction is valid
        if user != client.user and reaction.message.id == squad_message_id and len(squad) < 5:
            print(f'{user.name} has added {reaction.emoji} to the embed: {reaction.message.content}')

            # Check by user ID instead of user object
            if user.id not in [member.id for member in squad]:
                print(user.display_name)
                squad.append(user)  # Add the user to the squad list

                # Update embed
                embed = reaction.message.embeds[0]
                updated = False
                for i, field in enumerate(embed.fields):
                    if field.value == "Open":
                        embed.set_field_at(i, name=f"Position {i+1}", value=f"Filled by {user.display_name}", inline=False)
                        updated = True
                        break  # Break after the first update

                if updated:
                    await reaction.message.edit(embed=embed)

                if len(squad) == 5:
                    await reaction.message.channel.send("The squad is now full!")


client.run('MTAyMTQ2NzMwMDQ3NTQ0MTIyMw.GVULYH.kUCw5hOyfNFIaVBerRZptwr45C3HQ-3TC33HT4')
