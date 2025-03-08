from discord.ext import commands
import config



def checkPha():
    def predicate(ctx):
        return ctx.author.id in config.ID.Pha
    return commands.check(predicate)



class autorespond(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.Cog.listener()
    async def on_ready(self):
        await self.sylvie.tree.sync()
        print (f"{self.sylvie.user} is now ready, master!")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        main = self.sylvie.get_channel(config.ID.main)
        await main.send(f'Welcome {member} to the server')
        await main.send(f"I'm {self.sylvie.user}, read https://discord.com/channels/1116323597590474845/1135394985777315971 for information")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{self.sylvie.user} love you")



async def setup(sylvie):
    await sylvie.add_cog(autorespond(sylvie))