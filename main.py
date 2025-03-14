import discord
from discord.ext import commands
import asyncio
import config
import os

sylvie = commands.Bot(command_prefix='Sylvie ', intents=discord.Intents.all())


async def loadModules():
    modules = config.moduleList
    for module in modules:
        await sylvie.load_extension(module)


async def SylvieOS():
    APIkey = config.token.discord
    if not os.path.isdir("./db"):
        os.mkdir("db")
    async with sylvie:
        await loadModules()
        await sylvie.start(APIkey)

if __name__ == "__main__":
    asyncio.run(SylvieOS())
