import discord
from discord.ext import commands

import datetime
import pytz
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix = 'Sylvie ', intents=intents)


# Section 0: IDs


server_id = 1116323597590474845

documents_id = 1116329448535506944

main_id = 1242439205406244954
daily_id = 1135773874135502989
weekly_id = 1148614907701514300
schedule_id = 1269607407751925826

allowed_users = [
  discord.Object(id=754703228003942522), # Pha 1
  discord.Object(id=754703510360162425)  # Pha 2
]

day_names = {
  0: "Monday's",
  1: "Tuesday's",
  2: "Wednesday's",
  3: "Thursday's",
  4: "Friday's",
  5: "Saturday's",
  6: "Sunday's"
}

def is_allowed():
  async def predicate(ctx):
    return ctx.author.id in [user.id for user in allowed_users]
  return commands.check(predicate)


# Section 1: Default features


@client.event
async def on_ready():
  await client.tree.sync()
  print (f'{client.user} is now ready, master!')

@client.event
async def on_member_join(member):
  main = client.get_channel(main_id)
  await main.send(f'Welcome {member} to the server')
  await main.send("I'm Sylvie")

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send("I love you, master")

@client.tree.command(description="Checks Sylvie's latency")
async def ping(interaction: discord.Interaction):
  await interaction.response.send_message(f"Master, Sylvie's latency: {round(client.latency * 1000)}ms")


# Section 2: Study tracker


@client.hybrid_command(description="Sylvie remind your daily plan") # sent today, not crossed
async def remind(ctx):
  daily = client.get_channel(daily_id)
  found = False
  tz = pytz.timezone('Asia/Ho_Chi_Minh')
  today = datetime.datetime.now(tz=tz)

  to_day = today.strftime("%d/%m")
  await ctx.send(f'Master, this is your plan for today ({to_day}):')

  async for message in daily.history(limit=7):
    message_date = message.created_at.astimezone(tz)

    if today.date() == message_date.date() and "~~" not in message.content:
      await ctx.send(message.content)
      found = True

  if not found:
    await ctx.send("You didn't make a plan for today, master")
    await ctx.send("Let's make one together")

@client.hybrid_command(description="Sylvie cross completed plans") # sent today, contain keyword, not crossed
@is_allowed()
async def cross(ctx, keyword: str):
  daily = client.get_channel(daily_id)
  tz = pytz.timezone('Asia/Ho_Chi_Minh')
  today = datetime.datetime.now(tz=tz)

  async for message in daily.history(limit=7):
    message_date = message.created_at.astimezone(tz)

    if today.date() == message_date.date() and keyword.lower() in message.content.lower() and "~~" not in message.content:
      await message.edit(content = f'~~{message.content}~~')
      await ctx.send(f'Congrats on completing {keyword}, master')
      return

  await ctx.send(f'You do not have plan for {keyword} today, master')


# Section 3: Study planner (access restricted)


@client.hybrid_command(description="Sylvie remind your weekly plan") # contain this week
@is_allowed()
async def plan(ctx):
  weekly = client.get_channel(weekly_id)
  schedule = client.get_channel(schedule_id)
  daily = client.get_channel(daily_id)

  tz = pytz.timezone('Asia/Ho_Chi_Minh')
  today = datetime.datetime.now(tz=tz)
  weekday = today.weekday()
  monday = today - datetime.timedelta(days=today.weekday())
  sunday = monday + datetime.timedelta(days=6)
  to_day = day_names[weekday]

  async for message in schedule.history(limit=8):
    if to_day in message.content:
      modified_message = message.content[2:]
      await daily.send(modified_message)
    elif "Routine" in message.content:
      modified_message = message.content[2:]
      await daily.send(modified_message)

  async for message in weekly.history(limit=5):
    mon_day = monday.strftime("%d/%m")
    sun_day = sunday.strftime("%d/%m")

    if mon_day in message.content and sun_day in message.content:
      await ctx.send("Here's your plan for this week:")
      await ctx.send(message.content) 
      await ctx.send("What should we do today, master?")

      return

@client.hybrid_command(description="Sylvie extend due for uncompleted plans") # sent yesterday, not routine/class, not crossed
@is_allowed()
async def extend(ctx):
  daily = client.get_channel(daily_id)
  tz = pytz.timezone('Asia/Ho_Chi_Minh')
  today = datetime.datetime.now(tz=tz)
  yesterday = today - datetime.timedelta(days=1)

  async for message in daily.history(limit=14):
    message_date = message.created_at.astimezone(tz)

    if yesterday.date() == message_date.date() and "-" not in message.content and "~~" not in message.content:
      await daily.send(message.content)
      await ctx.send("Yes, master")

@client.hybrid_command(description="Sylvie make daily plan with you") # same user, same channel
@is_allowed()
async def add(ctx):
  daily = client.get_channel(daily_id)
  
  await ctx.send("What else should we do today, master?")

  def check(respond):
    return respond.author == ctx.author and respond.channel == ctx.channel
      
  try:
    plan = await client.wait_for('message', check=check, timeout=60.0)
    await daily.send(plan.content)
    await ctx.send("Yes, master")
  except asyncio.TimeoutError:
    await ctx.send("Maybe later, master")


# Section 4: Study documents finder


@client.hybrid_command(description="Sylvie find your study docs") # contain keyword (and start with #)
async def docs(ctx,keyword: str):
  docs = client.get_channel(documents_id)

  for channel in docs.text_channels:
    async for message in channel.history():
      if message.content.startswith('#') and keyword.lower() in message.content.lower():
        await ctx.send(f'Here your docs for {keyword}, master')
        await ctx.send(message.content)
        return

  await ctx.send(f'You do not have docs for {keyword}, master')


# PRIVATE KEY BELOW


client.run('MTI2NTM2MzEzMjU0MTQ0MDEwMA.GalPSE._dHOdKaGNMHH29KR51ALrzf6VV0UXXBTg5rd3I')