import discord
from discord.ext import commands
import datetime
import pytz
import cogs.config as config

class tracker(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.hybrid_command(description="Sylvie remind your daily plan")
    async def remind(self, ctx):
        daily = self.sylvie.get_channel(config.daily_id)
        found = False
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz=tz)

        to_day = today.strftime("%d/%m")
        await ctx.send(f'Master, this is your plan for today ({to_day}):')

        async for message in daily.history(limit = 10):
            message_date = message.created_at.astimezone(tz)

            if today.date() == message_date.date() and "~~" not in message.content: # sent today, not crossed
                await ctx.send(message.content)
                found = True

        if not found:
            await ctx.send("...")
            await ctx.send("Congrats, master! There are no plan left for today.")
    
    @commands.hybrid_command(description="Sylvie remind your classes today")
    async def classes(self, ctx):
        schedule = self.sylvie.get_channel(config.schedule_id)

        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = tz)
        weekday = today.weekday()
        to_day = config.day_names[weekday]

        async for message in schedule.history(limit = 10):
            if to_day in message.content:
                modified_message = message.content[2:]
                await ctx.send("This is your classes for today, master")
                await ctx.send(modified_message)
                return
    
    @commands.hybrid_command(description="Sylvie remind your classes tomorrow")
    async def classestmr(self, ctx):
        schedule = self.sylvie.get_channel(config.schedule_id)

        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = tz)
        tomorrow = today + datetime.timedelta(days = 1)
        weekday = tomorrow.weekday()
        to_morrow = config.day_names[weekday]

        async for message in schedule.history(limit = 10):
            if to_morrow in message.content:
                modified_message = message.content[2:]
                await ctx.send("This is your classes for tomorrow, master")
                await ctx.send(modified_message)
                return
    
    @commands.hybrid_command(description="Sylvie remind your weekly plan")
    async def plan(self, ctx):
        schedule = self.sylvie.get_channel(config.schedule_id)
        weekly = self.sylvie.get_channel(config.weekly_id)
        daily = self.sylvie.get_channel(config.daily_id)

        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = tz)
        yesterday = today - datetime.timedelta(days = 1)
        monday = today - datetime.timedelta(days=today.weekday())
        sunday = monday + datetime.timedelta(days = 6)

        async for message in schedule.history(limit = 1):
            if "Routine" in message.content:
                modified_message = message.content[15:]
                if modified_message:
                    await ctx.send("This's your daily routine, master")
                    await ctx.send(modified_message)
                elif not modified_message:
                    await ctx.send("There's no routine today, master")
        
        async for message in daily.history(limit=20):
            message_date = message.created_at.astimezone(tz)

            if yesterday.date() == message_date.date() and "-" not in message.content and "~~" not in message.content: # sent yesterday, not routine/class, not crossed
                await ctx.send(message.content)

        async for message in weekly.history(limit = 5):
            mon_day = monday.strftime("%d/%m")
            sun_day = sunday.strftime("%d/%m")

            if mon_day in message.content and sun_day in message.content:
                await ctx.send("Here's your plan for this week:")
                await ctx.send(message.content)
                return

async def setup(sylvie):
    await sylvie.add_cog(tracker(sylvie))