import discord
from discord.ext import commands, tasks
import sqlite3 as sql
import time
import config
from modules.general import checkPermission
from modules.tasksManager import TasksManager


class StudyTracker(commands.Cog):
    def __init__(self, sylvie):
        self.sylvie = sylvie
        self.start_time = {}
        self.update_time.start()
        self.create_database()

    def connect_database(self):
        database = sql.connect("./db/studytime.db")
        cursor = database.cursor()
        return database, cursor

    def disconnect_database(self, database):
        database.commit()
        database.close()

    def create_database(self):
        database, cursor = self.connect_database()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS time_database (user_id, weekly_time, all_time)")
        self.disconnect_database(database)

    def format_time(self, time):
        return f"{time // 3600} hours and {time % 3600 // 60} minutes"

    @tasks.loop(minutes=1)  # every minute
    async def update_time(self):  # Update time to database
        voice = self.sylvie.get_channel(config.ID.voice_channel)
        if not voice:
            return

        database, cursor = self.connect_database()
        for member in voice.members:
            cursor.execute(
                "SELECT * FROM time_database WHERE user_id = ?", (member.id,))
            data = cursor.fetchone()
            if data:
                updated_time = data[1] + 60
                all_time = data[2] + 60
                cursor.execute("UPDATE time_database SET weekly_time = ?, all_time = ? WHERE user_id = ?", (
                    updated_time, all_time, member.id))
            else:
                cursor.execute(
                    "INSERT INTO time_database (user_id, weekly_time, all_time) VALUES (?, ?, ?)", (member.id, 60, 60))

        self.disconnect_database(database)

    @commands.Cog.listener()  # Calculate study session
    async def on_voice_state_update(self, member, before, after):
        current_time = time.time()
        main = self.sylvie.get_channel(config.ID.main_channel)
        voice = self.sylvie.get_channel(config.ID.voice_channel)

        if not before.channel and after.channel.id == voice.id:  # join voice
            self.start_time[member.id] = current_time
            await main.send(f"{member.display_name} is diving into their study session! Join them now: {after.channel.mention}")

        if before.channel.id == voice.id and not after.channel:  # leave voice
            if member.id in self.start_time:
                session = current_time - self.start_time.pop(member.id)
                await main.send(f"{member.display_name} just grinded for {self.format_time(session)} straight")

    # Send all-time leaderboard
    @commands.hybrid_command(description="All-time leaderboard")
    async def alltime(self, ctx):
        database, cursor = self.connect_database()
        cursor.execute(
            "SELECT user_id, all_time FROM time_database ORDER BY all_time DESC")
        data = cursor.fetchall()
        await self.create_leaderboard(ctx, data, "All-time leaderboard")
        self.disconnect_database(database)

    # Send weekly leaderboard
    @commands.hybrid_command(description="Weekly leaderboard")
    async def leaderboard(self, ctx):
        database, cursor = self.connect_database()
        cursor.execute(
            "SELECT user_id, weekly_time FROM time_database WHERE weekly_time > 0 ORDER BY weekly_time DESC")
        data = cursor.fetchall()
        if not data:
            await ctx.send("No one studied this week")
            self.disconnect_database(database)
            return
        await self.create_leaderboard(ctx, data, "Weekly leaderboard")
        self.disconnect_database(database)

    # Send leaderboard: send embed
    async def create_leaderboard(self, ctx, data, title):
        embed = discord.Embed(
            color = discord.Color.yellow(),
            title = f":fire: {title} :fire:")
        user_position = "NaN"
        for user, (id, study_time) in enumerate(data, start=1):
            member = ctx.guild.get_member(id)
            name = member.display_name if member else f"Unknown User ({id})"
            embed.add_field(name=f"Top {user}: {name}", value=self.format_time(study_time), inline=False)
            if id == ctx.author.id:
                user_position = user
        user = ctx.guild.get_member(ctx.author.id)
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text=f"Your position: #{user_position}")

        await ctx.send(embed=embed)

    # Summarize (Remove weekly time and todolists)
    @commands.hybrid_command(description="[Pha only] Weekly summarize")
    @checkPermission()
    async def summarize(self, ctx):
        database, cursor = self.connect_database()
        cursor.execute(
            "SELECT user_id, weekly_time FROM time_database WHERE weekly_time > 0 ORDER BY weekly_time DESC")
        data = cursor.fetchall()
        if not data:
            await ctx.send(f"No one studied this week")
            self.disconnect_database(database)
            return

        members, highrole_list, midrole_list, lowrole_list = [], [], [], []  # place holders
        for _, (id, study_time) in enumerate(data, start=1):
            member = ctx.guild.get_member(id)
            name = member.display_name if member else f"Unknown User ({id})"
            if study_time >= 70 * 3600:
                highrole_list.append(f"- {name}: {self.format_time(study_time)}")
                members.append(member)
            elif study_time >= 10 * 3600:
                midrole_list.append(f"- {name}: {self.format_time(study_time)}")
                members.append(member)
            else:
                lowrole_list.append(f"- {name}: {self.format_time(study_time)}")

        lists = [highrole_list, midrole_list, lowrole_list]
        await self.create_summarize(ctx, data, lists)

        for member in members:
            await self.create_dm(member)

        TasksManager(self.sylvie).cleartodolist()
        cursor.execute("UPDATE time_database SET weekly_time = 0")
        self.disconnect_database(database)

    async def create_dm(self, member):  # Summarize: send dm to all users
        dm = discord.Embed(
            color=discord.Color.red(),
            title=f"Congratulations {member.display_name}!",
            description=f"I'm {self.sylvie.user}, representing Pha Cord. We really appreciate your contribution to our growth. Keep up the fire!")

        await member.send(embed=dm)

    # Summarize: send server embed
    async def create_summarize(self, ctx, data, lists):
        embed = discord.Embed(
            color=discord.Color.red(),
            title=":fire: Grinders of the week :fire:")

        top_user_id, _ = data[0]
        top_member = ctx.guild.get_member(top_user_id)
        avatar_url = top_member.avatar.url if top_member.avatar else top_member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text=f"-from {self.sylvie.user} with love-")
        if lists[0]:
            embed.add_field(name="Scholar-tier grinders", value="\n".join(lists[0]), inline=False)
        if lists[1]:
            embed.add_field(name="Student-tier grinders", value="\n".join(lists[1]), inline=False)
        if lists[2]:
            embed.add_field(name='"at least you participated"', value="\n".join(lists[2]), inline=False)

        await ctx.send(embed=embed)


async def setup(sylvie):
    await sylvie.add_cog(StudyTracker(sylvie))
