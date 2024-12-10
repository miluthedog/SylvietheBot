from discord.ext import commands

class planner(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie



async def setup(sylvie):
    await sylvie.add_cog(planner(sylvie))

