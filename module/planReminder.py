import discord
from discord.ext import commands
import datetime
import pytz
import config
from module.checkpermission import checkPha



class planReminder(commands.Cog):    
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.hybrid_command(description="[Pha only] Pha's weekly plan")
    @checkPha()
    async def plan(self, ctx):
        tasks = self.sylvie.get_channel(config.ID.tasks)
        notes = self.sylvie.get_channel(config.ID.notes)

        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz = timezone)
        monday = today - datetime.timedelta(days=today.weekday())
        sunday = monday + datetime.timedelta(days = 6)
        mondate = monday.strftime("%d/%m")
        sundate = sunday.strftime("%d/%m")

        embed = discord.Embed(
            color = discord.Color.red(),
            title = ":pencil: Sylvie's planner",
        )
        embed.set_footer(text = f"-from {self.sylvie.user} with love-")
        async for message in notes.history(limit = 1):
            embed.add_field(name = "Note", value = message.content)
        async for message in tasks.history(limit = 10):
            if mondate in message.content and sundate in message.content:
                embed.insert_field_at(0, name = "This week plan", value = message.content[15:])
                await ctx.send(embed = embed)
                return



async def setup(sylvie):
    await sylvie.add_cog(planReminder(sylvie))