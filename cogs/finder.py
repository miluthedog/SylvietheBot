import discord
from discord.ext import commands
import cogs.config as config

class finder(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie
    
    @commands.hybrid_command(description="Sylvie find your study docs")
    async def docs(self, ctx, name: str):
        docs = self.sylvie.get_channel(config.docs)

        async for message in docs.history():
            if name.lower() in message.content.lower():
                await ctx.send(f'Here your docs for {name}, master')
                await ctx.send(message.content)
                
                return
        await ctx.send(f'You do not have docs for {name}, master')



    @commands.hybrid_command(description="Sylvie find your HUST docs")
    async def docshust(self, ctx, name: str):
        docs = self.sylvie.get_channel(config.hustdocs)

        async for message in docs.history():
            if name.lower() in message.content.lower():
                await ctx.send(f'Here your docs for {name}, master')
                await ctx.send(message.content)
                
                return
        await ctx.send(f'You do not have docs for {name}, master')

async def setup(sylvie):
    await sylvie.add_cog(finder(sylvie))