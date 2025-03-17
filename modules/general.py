from discord.ext import commands
import config


def checkPermission():
    def predicate(ctx):
        return ctx.guild.get_role(config.ID.admin_role) in ctx.author.roles
    return commands.check(predicate)


class autorespond(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.Cog.listener()
    async def on_ready(self):
        await self.sylvie.tree.sync()
        print (f"Sylvie v1.0.0: {self.sylvie.user} is now ready, master!")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        main = self.sylvie.get_channel(config.ID.main_channel)
        await main.send(f'Welcome {member} to our study server!')
        role = member.guild.get_role(config.ID.default_role)
        if role:
            await member.add_roles(role)
            await main.send(f"You're {role.name} now. Study hard to get better!")
        await main.send(f"I'm {self.sylvie.user}. Read <#{config.ID.rules_channel}> for details.")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{self.sylvie.user} love you")


async def setup(sylvie):
    await sylvie.add_cog(autorespond(sylvie))