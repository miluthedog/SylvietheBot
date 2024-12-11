from discord.ext import commands
import sqlite3 as sql
import random
import cogs.config as config

# database structure: todolist (user_id, task)

class planner(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.hybrid_command(description="Add task to your list") # add task to database
    async def add(self, ctx, task: str):
        connection = sql.connect("./cogs/planner.db")
        cursor = connection.cursor()
    
        cursor.execute("INSERT INTO todolist (user_id, task) VALUES (?, ?)", (ctx.author.id, task))

        await ctx.send(f"{ctx.author.display_name} added `{task}` to their todolist")

        connection.commit()
        connection.close()
    
    @commands.hybrid_command(description="Remove tasks you completed") # remove task from database
    async def remove(self, ctx, task: str):
        connection = sql.connect("./cogs/planner.db")
        cursor = connection.cursor()

        cursor.execute("SELECT task FROM todolist WHERE user_id = ? AND task LIKE ?", (ctx.author.id, f"%{task}%"))
        data = cursor.fetchone()

        if not data:
            await ctx.send(f"You have no '{task}' in your list, {ctx.author.display_name}")
            return
        
        full_task = data[0]

        cursor.execute("DELETE FROM todolist WHERE user_id = ? AND task = ?", (ctx.author.id, full_task))

        random_compliment = random.choice(config.compliments)
        await ctx.send(f"{ctx.author.display_name} completed `{full_task}`. {random_compliment}!")

        connection.commit()
        connection.close()
    
    @commands.hybrid_command(description="See all your tasks") # show remaining task in database
    async def todolist(self, ctx):
        connection = sql.connect("./cogs/planner.db")
        cursor = connection.cursor()

        cursor.execute("SELECT task FROM todolist WHERE user_id = ?", (ctx.author.id,))
        data = cursor.fetchall()

        if not data:
            random_compliment = random.choice(config.compliments)
            await ctx.send(f"You have no tasks left, {ctx.author.display_name}. {random_compliment}!")
            return
        
        task_list = "\n".join([task[0] for task in data])
        await ctx.send(f"Your remaining tasks:\n{task_list}")

        connection.close()

async def setup(sylvie):
    await sylvie.add_cog(planner(sylvie))

