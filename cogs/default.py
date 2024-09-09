import discord
from discord.ext import commands
import cogs.config as config

class default(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        main = self.sylvie.get_channel(config.main_id)
        await main.send(f'Welcome {member} to the server')
        await main.send("I'm Sylvie")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("I love you, master")

async def setup(sylvie):
    await sylvie.add_cog(default(sylvie))