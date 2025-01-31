from discord.ext import commands
import config



class docsFinder(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.hybrid_command(description="Sylvie find your study docs") # Search for documents 
    async def docs(self, ctx, name: str):
        docs = self.sylvie.get_channel(config.ID.docs)
        prefix = f"# {name.lower()}"

        async for message in docs.history():
            if prefix in message.content.lower():
                await ctx.send(f"Here your docs for {name}:\n{message.content}")
                return
        await ctx.send(f"You do not have docs for {name}")



async def setup(sylvie):
    await sylvie.add_cog(docsFinder(sylvie))