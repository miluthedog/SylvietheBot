import discord
from discord.ext import commands
import asyncio
import config

sylvie = commands.Bot(command_prefix = 'Sylvie ', intents = discord.Intents.all())

async def loadModules():
    modules = config.moduleList
    for module in modules:
        await sylvie.load_extension(module)

async def SylvieOS():
    APIkey = config.token.discord
    async with sylvie:
        await loadModules()
        await sylvie.start(APIkey)

if __name__ == "__main__":
    asyncio.run(SylvieOS())