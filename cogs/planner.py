from discord.ext import commands

# database structure: daily_database (user_id, task)

class planner(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.hybrid_command(description="Add tasks")
    async def add(self, task):



async def setup(sylvie):
    await sylvie.add_cog(planner(sylvie))

