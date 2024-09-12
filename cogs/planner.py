import discord
from discord.ext import commands
import datetime
import pytz
import asyncio
import cogs.config as config

class planner(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    def is_allowed():
        async def predicate(ctx):
            return ctx.author.id in config.allowed_users
        return commands.check(predicate)

    @commands.hybrid_command(description="Sylvie make daily plan with you")
    @is_allowed()
    async def add(self, ctx, task: str):
        daily = self.sylvie.get_channel(config.daily_id)
        
        await daily.send(task)
        await ctx.send("Yes, master")

    @commands.hybrid_command(description="Sylvie cross completed plans") 
    @is_allowed()
    async def cross(self, ctx, task: str):
        daily = self.sylvie.get_channel(config.daily_id)
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = tz)

        async for message in daily.history(limit = 10):
            message_date = message.created_at.astimezone(tz)

            if today.date() == message_date.date() and task.lower() in message.content.lower() and "~~" not in message.content: # sent today, contain keyword, not crossed
                await ctx.send("Let summarize what we learned, master")

                def check(respond):
                    return respond.author == ctx.author and respond.channel == ctx.channel

                try:
                    context = await self.sylvie.wait_for('message', check = check, timeout = 300.0)
                    await message.edit(content = f'~~{message.content}~~: {context.content}')
                    await ctx.send(f'Congrats on completing {task}, master')
                except asyncio.TimeoutError:
                    await message.edit(content = f'~~{message.content}~~')
                    await ctx.send("Yes, congrats master for doing good work")
                
                return
        await ctx.send(f'You do not have plan for {task} today, master')

async def setup(sylvie):
    await sylvie.add_cog(planner(sylvie))

