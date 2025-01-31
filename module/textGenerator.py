from discord.ext import commands
from huggingface_hub import InferenceClient
import config

client = InferenceClient(
    provider="together",
    api_key=config.token.together
)

class textGenerator(commands.Cog):
    def __init__(self, sylvie):
        self.sylvie = sylvie

    @commands.Cog.listener()
    async def on_message(self, message):
        main = self.sylvie.get_channel(config.ID.main)
        if message.author == self.sylvie.user or message.channel.id is not main.id:
            return

        if "hey sylvie" in message.content.lower():
            print("Sylvie suddenly became DeepSeek")
            input = [{"role": "user", "content": message.content}]
            output = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=input,
                max_tokens=250
                )
            await message.channel.send(output.choices[0].message.content)

async def setup(sylvie):
    await sylvie.add_cog(textGenerator(sylvie))
