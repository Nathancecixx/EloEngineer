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
from youtube_dl import YoutubeDL
import os


class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # Initializes the queue dictionary

    def check_queue(self, ctx):
        if self.queues[ctx.guild.id]:
            voice_client = ctx.guild.voice_client
            source, filename = self.queues[ctx.guild.id].pop(0)
            voice_client.play(source, after=lambda e: self.cleanup(ctx, filename))

    def cleanup(self, ctx, filename):
        """Remove the downloaded files after playback."""
        try:
            os.remove(filename)
            self.check_queue(ctx)
        except Exception as e:
            print(f"Failed to delete {filename}: {e}")

    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel.")
            return

        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name='play', help='Provide a youtube.com URL to play a song')
    async def play(self, ctx, url):
        server = ctx.message.guild
        voice_channel = server.voice_client

        if not voice_channel:
            await ctx.send("The bot is not connected to a voice channel.")
            return

        async with ctx.typing():
            try:
                # Setup youtube_dl options
                ytdl_options = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                    'restrictfilenames': True,
                    'noplaylist': True,
                }

                # Download the song
                with YoutubeDL(ytdl_options) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    filename = os.path.splitext(filename)[0] + '.mp3'

                source = discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
                if not voice_channel.is_playing():
                    voice_channel.play(source, after=lambda e: self.cleanup(ctx, filename))
                    await ctx.send(f'**Now playing:** {info["title"]}')
                    if ctx.guild.id not in self.queues:
                        self.queues[ctx.guild.id] = []
                else:
                    self.queues[ctx.guild.id].append((source, filename))
                    await ctx.send(f'**Added to queue:** {info["title"]}')
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
                print(f"Error playing {url}: {e}")

    @commands.command(name='skip', help='Skips the current song and plays the next one in the queue')
    async def skip(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Skipped the current song.")
            self.check_queue(ctx)
        else:
            await ctx.send("No song is currently playing.")

    @commands.command(name='que', help='Displays the next 3 songs in queue')
    async def que(self, ctx):
        if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
            # Initialize the embed with dynamic content
            embed = discord.Embed(
                title=f"{ctx.guild.name} Current Song Queue:",
                description='Here are the next three songs in the queue:',
                color=discord.Color.blue()
            )

            # Optional: Add guild icon to embed
            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            # Fetch up to the next three songs from the queue
            next_songs = self.queues[ctx.guild.id][:3]
            for index, (_source, filename) in enumerate(next_songs, start=1):
                # Extract the title from the filename and replace underscores with spaces
                song_title = os.path.basename(filename).split('-', 2)[-1].rsplit('.', 1)[0].replace('_', ' ')
                embed.add_field(name=f"Song {index}", value=song_title, inline=False)

            # If fewer than three songs are in the queue, inform the user
            if not next_songs:
                embed.add_field(name="Queue is empty", value="No more songs are queued.", inline=False)
        else:
            # Prepare an embed for an empty queue
            embed = discord.Embed(
                title=f"{ctx.guild.name} Current Song Queue:",
                description="The queue is currently empty.",
                color=discord.Color.blue()
            )
            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed)

        @commands.command(name='pause', help='This command pauses the song')
        async def pause(self, ctx):
            voice_client = ctx.message.guild.voice_client
            if voice_client and voice_client.is_playing():
                voice_client.pause()
                await ctx.send("Music paused.")
            else:
                await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Music resumed.")
        else:
            await ctx.send("There is no music to resume.")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Music stopped.")
        else:
            await ctx.send("The bot is not playing anything at the moment.")


async def setup(client):
    await client.add_cog(MusicBot(client))
