import discord
from discord.ext import commands
import sqlite3 as sql
from modules.general import checkPermission


class TasksManager(commands.Cog):
    def __init__(self, sylvie):
        self.sylvie = sylvie
        self.create_database()

    def connect_database(self):
        database = sql.connect("./db/tasks.db")
        cursor = database.cursor()
        return database, cursor

    def disconnect_database(self, database):
        database.commit()
        database.close()

    def create_database(self):
        database, cursor = self.connect_database()
        cursor.execute("CREATE TABLE IF NOT EXISTS todolist (user_id, task)")
        self.disconnect_database(database)

    def cleartodolist(self):
        database, cursor = self.connect_database()
        cursor.execute("DELETE FROM todolist")
        self.disconnect_database(database)

    @commands.hybrid_command(description="Add task to your list")  # Add task
    async def add(self, ctx, task: str):
        database, cursor = self.connect_database()
        cursor.execute(
            "INSERT INTO todolist (user_id, task) VALUES (?, ?)", (ctx.author.id, task))
        self.disconnect_database(database)

        await ctx.send(f"{ctx.author.display_name} added `{task}` to their todolist")

    # Remove tasks
    @commands.hybrid_command(description="Remove your todolist")
    async def remove(self, ctx):
        database, cursor = self.connect_database()
        cursor.execute("DELETE FROM todolist WHERE user_id = ?",
                       (ctx.author.id,))
        self.disconnect_database(database)

        await ctx.send(f"Cleared {ctx.author.display_name}'s todolist")

    # Check todolist
    @commands.hybrid_command(description="See all your tasks")
    async def todolist(self, ctx):
        database, cursor = self.connect_database()
        cursor.execute(
            "SELECT task FROM todolist WHERE user_id = ?", (ctx.author.id,))

        data = cursor.fetchall()
        if not data:
            await ctx.send(f"You have no tasks left, {ctx.author.display_name}")
            return
        await self.create_todolist(ctx, data)

        self.disconnect_database(database)

    async def create_todolist(self, ctx, data):  # Check todolist: create embed
        number_of_tasks = len(data)
        task_list = "\n".join(f"- {task[0]}" for task in data)

        embed = discord.Embed(
            color=discord.Color.yellow(),
            title=f":pencil: {ctx.author.display_name}'s todolist",
            description=task_list
        )
        user = ctx.guild.get_member(ctx.author.id)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"Tasks left: {number_of_tasks}")

        await ctx.send(embed=embed)

    # Clear database
    @commands.hybrid_command(description="[Pha only] Remove all tasks in database")
    @checkPermission()
    async def clear(self, ctx):
        self.cleartodolist()
        await ctx.send(f"Removed all tasks in database")


async def setup(sylvie):
    await sylvie.add_cog(TasksManager(sylvie))
