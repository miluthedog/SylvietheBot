from discord.ext import commands
import config



def checkPha():
    def predicate(ctx):
        return ctx.author.id in config.ID.Pha
    return commands.check(predicate)