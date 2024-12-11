import discord
from discord.ext import commands
import sqlite3 as sql
import random
import cogs.config as config

class summarizer(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    def is_allowed():
        async def predicate(ctx):
            return ctx.author.id in config.allowed_users
        return commands.check(predicate)

    @commands.hybrid_command(description="[Pha only] Weekly summarize")
    @is_allowed()
    async def summarize(self, ctx):
        connection1 = sql.connect("./cogs/planner.db") # todolist
        cursor1 = connection1.cursor()

        cursor1.execute("DELETE FROM todolist")
        connection1.commit()

        connection2 = sql.connect("./cogs/tracker.db") # time_database
        cursor2 = connection2.cursor()

        cursor2.execute("SELECT user_id, weekly_time FROM time_database WHERE weekly_time > 0 ORDER BY weekly_time DESC")
        
        data = cursor2.fetchall()

        if not data:
            random_compliment = random.choice(config.compliments)
            await ctx.send(f"No one studied this week. {random_compliment}!")
            return
        
        embed = discord.Embed(
            title=":fire: __Weekly leaderboard__ :fire:",
            color=discord.Color.red()
        )

        for i, (user_id, weekly_time) in enumerate(data, start=1): # players
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"Top {i}: {name}", value=f"{weekly_time // 60} minutes", inline=False)

        top_user_id, top_weekly_time = data[0] # top 1 server
        top_member = ctx.guild.get_member(top_user_id)

        embed.set_thumbnail(url=top_member.avatar.url)
        embed.set_footer(text = "-from Sylvie with love-")

        cursor2.execute("UPDATE time_database SET weekly_time = 0")

        await ctx.send(embed=embed)

        connection2.commit()
        connection1.close()
        connection2.close()

async def setup(sylvie):
    await sylvie.add_cog(summarizer(sylvie))