import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')

sylvie = commands.Bot(command_prefix = 'Sylvie ', intents = discord.Intents.all())

@sylvie.event
async def on_ready():
    await sylvie.tree.sync()
    print (f'{sylvie.user} is now ready, master!')

extension_list = [
"cogs.default",
"cogs.finder",
#"cogs.planner",
"cogs.reminder",
"cogs.tracker"
]

async def load():
    for extension in extension_list:
        await sylvie.load_extension(extension)

async def main():
    async with sylvie:
        await load()
        await sylvie.start(token)

asyncio.run(main())