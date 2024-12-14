import discord
from discord.ext import commands
import sqlite3 as sql
import time
import random
import cogs.config as config

# database structure: time_database (user_id, weekly_time, all_time)

start_time = {}

class tracker(commands.Cog):
    def __init__(self, sylvie):
        self.sylvie = sylvie
    
    def is_allowed(): # permission: Pha
        async def predicate(ctx):
            return ctx.author.id in config.allowed_users
        return commands.check(predicate)

    def update_time(self, user_id, session): # update time to database
        connection = sql.connect("./cogs/tracker.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * from time_database WHERE user_id = ?", (user_id,))

        data = cursor.fetchone()

        if data:
            updated_time = data[1] + session
            all_time = data[2] + session
            cursor.execute("UPDATE time_database SET weekly_time = ?, all_time = ? WHERE user_id = ?", (updated_time, all_time, user_id))
        
        else: 
            cursor.execute("INSERT INTO time_database (user_id, weekly_time, all_time) VALUES (?, ?, ?)", (user_id, session, session))

        connection.commit()
        connection.close()

    @commands.Cog.listener() # calculate study session time
    async def on_voice_state_update(self, member, before, after):
        current_time = time.time()
        main = self.sylvie.get_channel(config.main_id)
        voice = self.sylvie.get_channel(config.voice_id)

        if before.channel and before.channel.id == voice.id: # leave voice
            if member.id in start_time:
                session = current_time - start_time.pop(member.id)
                self.update_time(member.id, session)

                random_compliment = random.choice(config.compliments)
                await main.send(f"{member.display_name} just grinded for {session // 60} minutes straight. {random_compliment}!")

        if after.channel and after.channel.id == voice.id: # join voice
            start_time[member.id] = current_time

            await main.send(f"{member.display_name} is diving into their study session! Join them now: {after.channel.mention}")

    @commands.hybrid_command(description="All-time leaderboard") # see all-time leaderboard
    async def leaderboard(self, ctx):
        connection = sql.connect("./cogs/tracker.db")
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, all_time FROM time_database ORDER BY all_time DESC")

        data = cursor.fetchall()

        embed = discord.Embed(
            title=":fire: __All-time leaderboard__ :fire:",
            color=discord.Color.yellow()
        )

        for i, (user_id, all_time) in enumerate(data, start=1): # players
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"Top {i}: {name}", value=f"{all_time//3600} hours and {all_time%3600//60} minutes", inline=False)
            
            if user_id == ctx.author.id:
                user_position = i

        top_user_id, top_weekly_time = data[0] # top 1 server
        top_member = ctx.guild.get_member(top_user_id)

        embed.set_thumbnail(url=top_member.avatar.url)
        embed.set_footer(text = f"Your position: #{user_position}")

        await ctx.send(embed=embed)

        connection.close()

    @commands.hybrid_command(description="Weekly leaderboard")  # see weekly leaderboard
    async def time(self, ctx):
        connection = sql.connect("./cogs/tracker.db")
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, weekly_time FROM time_database WHERE weekly_time > 0 ORDER BY weekly_time DESC")
        
        data = cursor.fetchall()

        if not data:
            random_compliment = random.choice(config.compliments)
            await ctx.send(f"No one studied this week. {random_compliment}!")
            return
        
        embed = discord.Embed(
            title=":fire: __Weekly leaderboard__ :fire:",
            color=discord.Color.yellow()
        )

        for i, (user_id, weekly_time) in enumerate(data, start=1): # players
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"Top {i}: {name}", value=f"{weekly_time // 60} minutes", inline=False)

            if user_id == ctx.author.id:
                user_position = i

        top_user_id, top_weekly_time = data[0] # top 1 server
        top_member = ctx.guild.get_member(top_user_id)

        embed.set_thumbnail(url=top_member.avatar.url)
        embed.set_footer(text = f"Your position: #{user_position}")

        await ctx.send(embed=embed)

        connection.close()

async def setup(sylvie):
    await sylvie.add_cog(tracker(sylvie))
