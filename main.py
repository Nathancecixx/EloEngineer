"""
+------------------------------------------------------------+
| * Squad Builder is a discord bot written in python which * |
| * adds easy squad formation features to a server.        * |
|                                                            |
|                                                            |
| * Squad_Builder                                          * |
| * fall 23 - Nathan Ceci                                  * |
+------------------------------------------------------------+
"""

import discord
import os
import asyncio
from discord.ext import commands
from ApiKeys import *

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix='*', intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with client:
        await load_extensions()
        await client.start(BotKey)

asyncio.run(main())
