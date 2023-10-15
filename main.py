import discord, logging, jishaku
import os
from discord.ext import commands
import univ.vars as univ
from discord.ext.commands import CommandNotFound
import traceback

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix = commands.when_mentioned_or('sci!'), intents=intents, description = "Buzz", help_command=None, activity = discord.Game(name="sci!help"))


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await setup_hook(client)
    univ.init()

async def setup_hook(self):
    await self.load_extension('jishaku')
    try:
        await self.load_extension('com.buzzer')
        await self.load_extension('com.config')
    except Exception as e:
            raise e

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error,discord.ext.commands.errors.TooManyArguments):
        await ctx.send("Too many arguments")
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument")
        return
    if isinstance(error, discord.errors.Forbidden):
        await ctx.send("I don't have permissions to run this command")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument: One or more arguments were entered incorrectly")
        return
    user = await client.fetch_user("754532384984137772")
    embed = discord.Embed(title="ERROR", description= f"```{''.join(traceback.format_exception(type(error), error, error.__traceback__))}```",color=0xFF0000)

    await user.send(embed = embed)
    raise error


from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return "online"


def run():
    if __name__ == '__main__':
        app.run(host="0.0.0.0", debug=False)


def keep_alive():
    t = Thread(target=run)
    t.start()


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

keep_alive()
client.run(os.getenv("TOKEN"))

