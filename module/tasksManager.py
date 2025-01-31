import discord
from discord.ext import commands
import sqlite3 as sql
from module.checkpermission import checkPha



database = sql.connect("./module/tasks.db")
cursor = database.cursor()
database.execute("CREATE TABLE IF NOT EXISTS todolist (user_id, task)")

def cleartodolist():
    database = sql.connect("./module/tasks.db")
    cursor = database.cursor()
    cursor.execute("DELETE FROM todolist")
    database.commit()
    database.close()

class tasksManager(commands.Cog):
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.hybrid_command(description="Add task to your list") # add task to database
    async def add(self, ctx, task: str):
        database = sql.connect("./module/tasks.db")
        cursor = database.cursor()
        cursor.execute("INSERT INTO todolist (user_id, task) VALUES (?, ?)", (ctx.author.id, task))
        database.commit()
        database.close()

        await ctx.send(f"{ctx.author.display_name} added `{task}` to their todolist")


    @commands.hybrid_command(description="Remove task from your list") # remove task from database
    async def remove(self, ctx, task: str):
        database = sql.connect("./module/tasks.db")
        cursor = database.cursor()
        cursor.execute("SELECT task FROM todolist WHERE user_id = ? AND task LIKE ?", (ctx.author.id, f"%{task}%"))
        
        data = cursor.fetchone()
        if not data:
            await ctx.send(f"You have no '{task}' in your list, {ctx.author.display_name}")
            return
        
        full_task = data[0]
        cursor.execute("DELETE FROM todolist WHERE user_id = ? AND task = ?", (ctx.author.id, full_task))
        database.commit()
        database.close()

        await ctx.send(f"{ctx.author.display_name} removed `{full_task}` from their todolist")


    @commands.hybrid_command(description="See all your tasks") # show users' remaining tasks in database
    async def todolist(self, ctx):
        database = sql.connect("./module/tasks.db")
        cursor = database.cursor()
        cursor.execute("SELECT task FROM todolist WHERE user_id = ?", (ctx.author.id,))
        
        data = cursor.fetchall()
        if not data:
            await ctx.send(f"You have no tasks left, {ctx.author.display_name}")
            return
        number_of_tasks = len(data)
        task_list = "\n".join(f"- {task[0]}" for task in data)    

        embed = discord.Embed(
            color = discord.Color.yellow(),
            title = f":pencil: {ctx.author.display_name}'s todolist",
            description = task_list
        )
        user = ctx.guild.get_member(ctx.author.id)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text = f"Tasks left: {number_of_tasks}")

        await ctx.send(embed = embed)
        database.close()


    @commands.hybrid_command(description="[Pha only] Remove all tasks in database") # clear database
    @checkPha()
    async def clear(self, ctx):
        cleartodolist()
        await ctx.send(f"Removed all tasks in database")



async def setup(sylvie):
    await sylvie.add_cog(tasksManager(sylvie))

