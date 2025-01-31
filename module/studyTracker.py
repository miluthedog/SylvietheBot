import discord
from discord.ext import commands
import sqlite3 as sql
import time
import config
from module.checkpermission import checkPha
from module.tasksManager import cleartodolist



database = sql.connect("./module/studytime.db")
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS time_database (user_id, weekly_time, all_time)")

start_time = {} # place holder for session start time

class studyTracker(commands.Cog):
    def __init__(self, sylvie):
        self.sylvie = sylvie

    def update_time(self, user_id, session): # update time to database
        database = sql.connect("./module/studytime.db")
        cursor = database.cursor()
        cursor.execute("SELECT * from time_database WHERE user_id = ?", (user_id,))

        data = cursor.fetchone()
        if data:
            updated_time = data[1] + session
            all_time = data[2] + session
            cursor.execute("UPDATE time_database SET weekly_time = ?, all_time = ? WHERE user_id = ?", (updated_time, all_time, user_id))
        else: 
            cursor.execute("INSERT INTO time_database (user_id, weekly_time, all_time) VALUES (?, ?, ?)", (user_id, session, session))

        database.commit()
        database.close()

    @commands.Cog.listener() # calculate study session time
    async def on_voice_state_update(self, member, before, after):
        current_time = time.time()
        main = self.sylvie.get_channel(config.ID.main)
        voice = self.sylvie.get_channel(config.ID.voice)

        if not before.channel and after.channel.id == voice.id: # join voice
            start_time[member.id] = current_time
            await main.send(f"{member.display_name} is diving into their study session! Join them now: {after.channel.mention}")

        if before.channel.id == voice.id and not after.channel: # leave voice
            if member.id in start_time:
                session = current_time - start_time.pop(member.id)
                self.update_time(member.id, session)
                await main.send(f"{member.display_name} just grinded for {session // 60} minutes straight")


    @commands.hybrid_command(description="All-time leaderboard") # see all-time leaderboard
    async def leaderboard(self, ctx):
        database = sql.connect("./module/studytime.db")
        cursor = database.cursor()
        cursor.execute("SELECT user_id, all_time FROM time_database ORDER BY all_time DESC")

        embed = discord.Embed(
            color = discord.Color.yellow(),
            title = ":fire: __All-time leaderboard__ :fire:"
        )

        data = cursor.fetchall()
        for i, (user_id, all_time) in enumerate(data, start=1): # add users to embed
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"Top {i}: {name}", value=f"{all_time//3600} hours and {all_time%3600//60} minutes", inline=False)            
            if user_id == ctx.author.id:
                user_position = i

        user = ctx.guild.get_member(ctx.author.id)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text = f"Your position: #{user_position}")

        await ctx.send(embed = embed)
        database.close()


    @commands.hybrid_command(description="Weekly leaderboard")  # see weekly leaderboard
    async def time(self, ctx):
        database = sql.connect("./module/studytime.db")
        cursor = database.cursor()
        cursor.execute("SELECT user_id, weekly_time FROM time_database WHERE weekly_time > 0 ORDER BY weekly_time DESC")
        
        embed = discord.Embed(
            color=discord.Color.yellow(),
            title=":fire: __Weekly leaderboard__ :fire:"
        )

        data = cursor.fetchall()
        if not data:
            await ctx.send(f"No one studied this week")
            return
        for i, (user_id, weekly_time) in enumerate(data, start=1): # add users to embed
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"Top {i}: {name}", value=f"{weekly_time//3600} hours and {weekly_time%3600//60} minutes", inline=False)            
            if user_id == ctx.author.id:
                user_position = i

        user = ctx.guild.get_member(ctx.author.id)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text = f"Your position: #{user_position}")

        await ctx.send(embed = embed)
        database.close()


    @commands.hybrid_command(description="[Pha only] Weekly summarize")
    @checkPha()
    async def summarize(self, ctx):
        database = sql.connect("./module/studytime.db")
        cursor = database.cursor()
        cursor.execute("SELECT user_id, weekly_time FROM time_database WHERE weekly_time > 0 ORDER BY weekly_time DESC")

        embed = discord.Embed(
            color=discord.Color.red(),
            title=":fire: __Weekly leaderboard__ :fire:"
        )

        data = cursor.fetchall()
        if not data:
            await ctx.send(f"No one studied this week")
            return
        for i, (user_id, weekly_time) in enumerate(data, start=1): # add users to embed
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"Top {i}: {name}", value=f"{weekly_time // 60} minutes", inline=False)

        top_user_id, top_weekly_time = data[0] # add 1's avatar to embed
        top_member = ctx.guild.get_member(top_user_id)
        embed.set_thumbnail(url=top_member.avatar.url)
        embed.set_footer(text = f"-from {self.sylvie.user} with love-")

        cleartodolist()
        cursor.execute("UPDATE time_database SET weekly_time = 0")
        await ctx.send(embed = embed)
        database.commit()
        database.close()



async def setup(sylvie):
    await sylvie.add_cog(studyTracker(sylvie))
