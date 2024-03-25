"""
+------------------------------------------------------------+
| * Squad Builder is a discord bot written in python which * |
| * adds easy squad formation features to a server.        * |
|                                                            |
| * Squad_Builder                                          * |
| * fall 23 - Nathan Ceci                                  * |
+------------------------------------------------------------+
"""
import datetime

import discord
from discord.utils import get
from discord.ext import commands
import asyncio
from ApiKeys import *

from siegeapi import Auth

from riotwatcher import LolWatcher, ApiError


class Tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auth = None

    # function used for sorting operators by time played
    def mins_played(self, operator):
        return operator.minutes_played

    async def CreateOperatorEmbed(self, ctx, operator, color, player):
        Embed = discord.Embed(
            title=operator.name,
            description=str(operator.roles[0]),
            color=color,
            timestamp=datetime.datetime.now()
        )
        kd = round(float(operator.kills) / float(operator.death), 2)
        wl = str(round(operator.win_loss_ratio, 2))

        Embed.set_thumbnail(url=operator.icon_url)
        Embed.add_field(name='', value='\u200B', inline=True)
        Embed.add_field(name='Matches Played', value=operator.matches_played, inline=False)
        Embed.add_field(name='K/D', value=kd, inline=False)
        Embed.add_field(name='W/L', value=wl, inline=False)
        Embed.add_field(name='', value='\u200B', inline=True)

        Embed.set_footer(text=player.name, icon_url=player.profile_pic_url)

        await ctx.send(embed=Embed)

    @commands.group(name='r6')
    async def r6(self, ctx):
        pass

    @r6.command(name='ops', help='Prints details about the server')
    async def ops(self, ctx, PlayerName=''):
        if PlayerName == '':
            await ctx.send("Invalid Arguments")
            return

        self.auth = Auth(Ubi_Email, Ubi_Pass)
        player = await self.auth.get_player(name=PlayerName)

        playername = str(player.name)

        # Create a embed for attacker display
        attackersembed = discord.Embed(
            title=playername + "'s Attackers",
            description="Top 3 Attackers",
            color=discord.Color.red()
        )
        # Add player pfp if they have one
        if player.profile_pic_url:
            attackersembed.set_thumbnail(url=player.profile_pic_url)
        # Collect attack op data and sort it
        await player.load_operators(True)
        attackers = player.operators.all.attacker
        attackers.sort(reverse=True, key=self.mins_played)
        # Send the display embed and create op embeds
        await ctx.send(embed=attackersembed)
        await self.CreateOperatorEmbed(ctx, attackers[0], discord.Color.red(), player)
        await self.CreateOperatorEmbed(ctx, attackers[1], discord.Color.red(), player)
        await self.CreateOperatorEmbed(ctx, attackers[2], discord.Color.red(), player)

        # Create a embed for defender display
        defendersembed = discord.Embed(
            title=playername + "'s Defenders",
            description="Top 3 Defenders",
            color=discord.Color.blue()
        )
        # Add player pfp if they have one
        if player.profile_pic_url:
            defendersembed.set_thumbnail(url=player.profile_pic_url)
        # Collect attack op data and sort it
        await player.load_operators(True)
        defenders = player.operators.all.defender
        defenders.sort(reverse=True, key=self.mins_played)
        # Send the display embed and create op embeds
        await ctx.send(embed=defendersembed)
        await self.CreateOperatorEmbed(ctx, defenders[0], discord.Color.blue(), player)
        await self.CreateOperatorEmbed(ctx, defenders[1], discord.Color.blue(), player)
        await self.CreateOperatorEmbed(ctx, defenders[2], discord.Color.blue(), player)

        await self.auth.close()
    # TODO: Change stats to focus on statistics
    # TODO: Add Rank command which focuses on the persons rank
    # TODO: Add a 'General Stats' command that highlights only quick and important info mid game

    @r6.command(name='stats', help='Prints details about the server')
    async def stats(self, ctx, PlayerName=''):
        if PlayerName == '':
            await ctx.send("Invalid Arguments")
            return
        try:
            self.auth = Auth(Ubi_Email, Ubi_Pass)
            player = await self.auth.get_player(name=PlayerName)

            # TODO: Handle exceptions with finding player
            if player is None:
                await ctx.send("Player Not found...")
                return

            await player.load_playtime()
            hoursplayed = str(player.total_time_played_hours)
            playername = str(player.name)
            currentlvl = str(player.level)
            pfp = player.profile_pic_url

            await player.load_ranked_v2()
            currentrank = str(player.ranked_profile.rank) + " \n(" + str(player.ranked_profile.rank_points) + ")"
            maxrank = str(player.ranked_profile.max_rank) + " \n(" + str(player.ranked_profile.max_rank_points) + ")"

            await player.load_summaries(gamemodes=["ranked"], team_roles=["all"])
            if player.ranked_summary:
                latest_season_id = max(player.ranked_summary.keys())
                summary_for_season = player.ranked_summary[latest_season_id]

                all_stats = summary_for_season['all']
                matchesplayed = str(all_stats.matches_played)
                # print(all_stats)
            else:
                matchesplayed = "0"

            # Calculate kd
            if player.ranked_profile.deaths > 0:
                kd = round(float(player.ranked_profile.kills/player.ranked_profile.deaths), 2)
            else:
                kd = player.ranked_profile.kills
            # Calculate wl
            if player.ranked_profile.losses > 0:
                wl = round(float(player.ranked_profile.wins/player.ranked_profile.losses), 2)
            else:
                wl = player.ranked_profile.wins
            # Get season code
            season_code = player.ranked_profile.season_code
            if player.ranked_profile.season_code is None:
                season_code = "Unknown Season"

            embed = discord.Embed(
                title=playername + "'s",
                description=f"{season_code} stats:",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )

            if player.profile_pic_url:
                embed.set_thumbnail(url=pfp)

            embed.add_field(name='', value='\u200B', inline=False)

            embed.add_field(name="K/D", value=kd, inline=False)
            embed.add_field(name='', value='\u200B', inline=True)

            embed.add_field(name="W/L", value=wl, inline=False)
            embed.add_field(name='', value='\u200B', inline=False)

            embed.add_field(name="LvL", value=currentlvl, inline=True)
            embed.add_field(name="Matches", value=matchesplayed, inline=True)

            embed.add_field(name='\u200B', value='\u200B', inline=False)
            embed.add_field(name='Rank info:', value='', inline=False)
            embed.add_field(name="Current", value=currentrank, inline=True)
            embed.add_field(name='', value='\u200B', inline=True)
            embed.add_field(name="Peak", value=maxrank, inline=True)
            embed.add_field(name='', value='\u200B', inline=False)

            embed.set_footer(text=str("Hours Played: " + hoursplayed + " "), icon_url=pfp)

            await ctx.send(embed=embed)

            await self.auth.close()

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            return


    @r6.command(name='test', help='Prints details about the server')
    async def test(self, ctx, PlayerName=''):
        if PlayerName == '':
            await ctx.send("Invalid Arguments")
            return
        try:
            self.auth = Auth(Ubi_Email, Ubi_Pass)
            player = await self.auth.get_player(name=PlayerName)

            # TODO: Handle exceptions with finding player
            if player is None:
                await ctx.send("Player Not found...")
                return

            await player.load_playtime()
            hoursplayed = str(player.total_time_played_hours)
            playername = str(player.name)
            currentlvl = str(player.level)
            pfp = player.profile_pic_url

            await player.load_ranked_v2()
            currentrank = str(player.ranked_profile.rank) + " \n(" + str(player.ranked_profile.rank_points) + ")"
            maxrank = str(player.ranked_profile.max_rank) + " \n(" + str(player.ranked_profile.max_rank_points) + ")"

            await player.load_summaries(gamemodes=["ranked"], team_roles=["all"])
            if player.ranked_summary:
                latest_season_id = max(player.ranked_summary.keys())
                summary_for_season = player.ranked_summary[latest_season_id]

                all_stats = summary_for_season['all']
                matchesplayed = str(all_stats.matches_played)
                # print(all_stats)
            else:
                matchesplayed = "0"

            # Calculate kd
            if player.ranked_profile.deaths > 0:
                kd = round(float(player.ranked_profile.kills/player.ranked_profile.deaths), 2)
            else:
                kd = player.ranked_profile.kills
            # Calculate wl
            if player.ranked_profile.losses > 0:
                wl = round(float(player.ranked_profile.wins/player.ranked_profile.losses), 2)
            else:
                wl = player.ranked_profile.wins
            # Get season code
            season_code = player.ranked_profile.season_code
            if player.ranked_profile.season_code is None:
                season_code = "Unknown Season"

            embed = discord.Embed(
                title=playername + "'s",
                description=f"{season_code} stats:",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )

            if player.profile_pic_url:
                embed.set_thumbnail(url=pfp)

            embed.add_field(name='', value='\u200B', inline=False)

            embed.add_field(name="K/D", value=kd, inline=True)
            embed.add_field(name='', value='\u200B', inline=True)
            embed.add_field(name="LvL", value=currentlvl, inline=True)
            embed.add_field(name='', value='\u200B', inline=True)

            embed.add_field(name="W/L", value=wl, inline=False)
            embed.add_field(name='', value='\u200B', inline=False)

            embed.add_field(name="Matches", value=matchesplayed, inline=True)

            embed.add_field(name='\u200B', value='\u200B', inline=False)
            embed.add_field(name='Rank info:', value='', inline=False)
            embed.add_field(name="Current", value=currentrank, inline=True)
            embed.add_field(name='', value='\u200B', inline=True)
            embed.add_field(name="Peak", value=maxrank, inline=True)
            embed.add_field(name='', value='\u200B', inline=False)

            embed.set_footer(text=str("Hours Played: " + hoursplayed + " "), icon_url=pfp)

            await ctx.send(embed=embed)

            await self.auth.close()

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            return

    @commands.group(name='lol')
    async def lol(self, ctx):
        pass

    @lol.command(name='stat')
    async def stat(self, ctx, PlayerName=''):
        if PlayerName == '':
            await ctx.send("Please provide a player name.")
            return

        try:
            riot = LolWatcher(RiotKey)
            region = 'na1'

            player = riot.summoner.by_name(region, PlayerName)
            ranked_stats = riot.league.by_summoner(region, player['id'])

            # Initialize variables to store ranked stats
            solo_duo_rank = "Unranked"
            win_rate = 0
            league_points = 0
            wins = 0
            losses = 0

            # Search for Solo/Duo queue stats
            for queue in ranked_stats:
                if queue['queueType'] == 'RANKED_SOLO_5x5':
                    solo_duo_rank = f"{queue['tier']} {queue['rank']}"
                    league_points = queue['leaguePoints']
                    wins = queue['wins']
                    losses = queue['losses']
                    total_games = wins + losses
                    win_rate = round((wins / total_games) * 100, 1) if total_games > 0 else 0
                    break

            # Create the embed message
            embed = discord.Embed(
                title=f"{PlayerName}'s",
                description=f"League Of Legends Stats:",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(
                url=f"http://ddragon.leagueoflegends.com/cdn/11.24.1/img/profileicon/{player['profileIconId']}.png")
            embed.add_field(name="Solo/Duo Rank", value=solo_duo_rank, inline=False)
            embed.add_field(name="League Points", value=str(league_points), inline=True)
            embed.add_field(name="Wins", value=str(wins), inline=True)
            embed.add_field(name="Losses", value=str(losses), inline=True)
            embed.add_field(name="Win Rate", value=f"{win_rate}%", inline=True)
            embed.set_footer(text="Stats provided by Riot's API")

            await ctx.send(embed=embed)

        except ApiError as e:
            if e.response.status_code in (400, 401, 403, 404):
                await ctx.send(f"Client error: {e.response.status_code}")
            elif e.response.status_code in (500, 502, 503, 504):
                await ctx.send("Riot API server error. Please try again later.")
            else:
                await ctx.send(f"An error occurred: {e.response.status_code}")


async def setup(client):
    await client.add_cog(Tracker(client))
