import discord
from discord.ext import commands
import datetime
import pytz
import cogs.config as config
from typing import Literal

class reminder(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.hybrid_command(description="Sylvie remind your daily plan")
    async def remind(self, ctx):
        daily = self.sylvie.get_channel(config.daily_id)
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz=tz)
        to_day = today.strftime("%d/%m")

        found = False
        messages = ""

        async for message in daily.history(limit = 10):
            message_date = message.created_at.astimezone(tz)
            if today.date() == message_date.date() and "~~" not in message.content: # sent today, not crossed
                messages = f"{messages}\n- {message.content}"
                found = True
        if found:
            await ctx.send(f"Master, this is your plan for today ({to_day}):{messages}")
        else:
            await ctx.send("Congrats, master! There are no plan left for today.")

    @commands.hybrid_command(description="Sylvie remind your classes")
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
            async for message in schedule.history(limit = 8):
                if to_day in message.content:
                    await ctx.send(f"These are your classes for today, master:\n{message.content[2:]}")
                    return
        else:
            if day == "tomorrow":
                async for message in schedule.history(limit = 8):
                    if to_morrow in message.content:
                        await ctx.send(f"These are your classes for {day}, master:\n{message.content[2:]}")
                        return
            else:
                async for message in schedule.history(limit = 8):
                    if day in message.content:
                        await ctx.send(f"These are your classes for {day}, master:\n{message.content[2:]}")
                        return

    @commands.hybrid_command(description="Sylvie remind your weekly plan")
    async def plan(self, ctx):
        schedule = self.sylvie.get_channel(config.schedule_id)
        weekly = self.sylvie.get_channel(config.weekly_id)

        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = tz)
        monday = today - datetime.timedelta(days=today.weekday())
        sunday = monday + datetime.timedelta(days = 6)

        embed = discord.Embed(
            color = discord.Color.red(),
            title = ":pencil: Sylvie's planner",
        )
        embed.set_footer(text = "-from Sylvie with love-")

        async for message in schedule.history(limit = 1):
            if "Routine" in message.content:
                modified_message = message.content[9:]
                if modified_message:
                    embed.add_field(name = "Daily Routine", value = modified_message)
                elif not modified_message:
                    embed.add_field(name = "Daily Routine", value = "none")

        async for message in weekly.history(limit = 5):
            mon_day = monday.strftime("%d/%m")
            sun_day = sunday.strftime("%d/%m")

            if mon_day in message.content and sun_day in message.content:
                embed.insert_field_at(0, name = "Weekly plan", value = message.content[15:])
                await ctx.send(embed = embed)
                return

async def setup(sylvie):
    await sylvie.add_cog(reminder(sylvie))