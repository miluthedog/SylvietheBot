from discord.ext import commands

# database structure: daily_database (user_id, task)

class planner(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie



async def setup(sylvie):
    await sylvie.add_cog(planner(sylvie))

