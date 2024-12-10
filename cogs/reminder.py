import discord
from discord.ext import commands
import datetime
import pytz
import cogs.config as config
from typing import Literal

class reminder(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie
    
    def is_allowed():
        async def predicate(ctx):
            return ctx.author.id in config.allowed_users
        return commands.check(predicate)

    @commands.hybrid_command(description="[Pha only] Sylvie remind your classes")
    @is_allowed()
    async def classes(self, ctx, day: Literal["tomorrow", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] = None):
        schedule = self.sylvie.get_channel(config.schedule_id)

        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = tz)
        tomorrow = today + datetime.timedelta(days = 1)
        to_weekday = today.weekday()
        to_morweekday = tomorrow.weekday()
        to_day = config.day_names[to_weekday]
        to_morrow = config.day_names[to_morweekday]

        if day is None:
            async for message in schedule.history(limit = 7):
                if to_day in message.content:
                    await ctx.send(f"These are your classes for today, master:\n{message.content[2:]}")
                    return
        else:
            if day == "tomorrow":
                async for message in schedule.history(limit = 7):
                    if to_morrow in message.content:
                        await ctx.send(f"These are your classes for {day}, master:\n{message.content[2:]}")
                        return
            else:
                async for message in schedule.history(limit = 7):
                    if day in message.content:
                        await ctx.send(f"These are your classes for {day}, master:\n{message.content[2:]}")
                        return

    @commands.hybrid_command(description="[Pha only] Sylvie remind your weekly plan")
    @is_allowed()
    async def plan(self, ctx):
        weekly = self.sylvie.get_channel(config.weekly_id)

        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = tz)
        monday = today - datetime.timedelta(days=today.weekday())
        sunday = monday + datetime.timedelta(days = 6)
        nextmonday = sunday + datetime.timedelta(days = 1)
        nextsunday = nextmonday + datetime.timedelta(days = 6)

        embed = discord.Embed(
            color = discord.Color.red(),
            title = ":pencil: Sylvie's planner",
        )
        embed.set_footer(text = "-from Sylvie with love-")

        mon_day = monday.strftime("%d/%m")
        sun_day = sunday.strftime("%d/%m")
        next_mon_day = nextmonday.strftime("%d/%m")
        next_sun_day = nextsunday.strftime("%d/%m")

        async for message in weekly.history(limit = 5):
            if next_mon_day in message.content and next_sun_day in message.content:
                embed.add_field(name = "Next week plan", value = message.content[15:])
            elif mon_day in message.content and sun_day in message.content:
                embed.insert_field_at(0, name = "This week plan", value = message.content[15:])
                await ctx.send(embed = embed)
                return

async def setup(sylvie):
    await sylvie.add_cog(reminder(sylvie))