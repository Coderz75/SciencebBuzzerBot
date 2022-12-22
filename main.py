import discord
import os
from discord.ext import commands
import univ.vars as univ
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix = commands.when_mentioned_or('!'), intents=intents, description = "Buzz", help_command=None, activity = discord.Game(name="!help"))


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await setup_hook(client)
    univ.init()

async def setup_hook(self):
    await self.load_extension('jishaku')
    try:
        await self.load_extension('com.buzzer')
    except Exception as e:
            raise e


class NewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page)
            await destination.send(embed=embed)

client.help_command = NewHelp()


client.run(os.getenv("TOKEN"))

