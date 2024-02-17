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
from Downloader import YTDLSource
import asyncio


class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name='play', help='Provide a youtube.com url to play a song')
    async def play(self, ctx, url):
        server = ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel:
            await ctx.send("The bot is not connected to a voice channel.")
            return

        try:
            async with ctx.typing():
                ytdl_source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                if not ytdl_source:
                    await ctx.send("Couldn't download the audio from the provided URL.")
                    return
                voice_channel.play(ytdl_source)
            await ctx.send('**Now playing:** {}'.format(ytdl_source.title))
        except Exception as e:
            await ctx.send("An error occurred: {}".format(str(e)))

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")


async def setup(client):
    await client.add_cog(MusicBot(client))
    