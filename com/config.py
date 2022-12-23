import discord
from discord.ext import commands

async def setup(bot):
	
	await bot.add_cog(Misc(bot))

class Misc(commands.Cog):
	"""
	Miscilaneaous
	"""

	def __init__(self, bot):
		self.client = bot
		self.bot = bot
		self.version = 1
		
	@commands.hybrid_command()
	async def ping(self, ctx):
		t = await ctx.channel.send('Pong!')
		ms = (t.created_at-ctx.message.created_at).total_seconds() * 1000
		embed = discord.Embed(title = "Pong", description = f"Pong, what else? \nOur client delay time was about {round(self.client.latency * 1000)} ms\nYour lag should be about {ms - round(self.client.latency * 1000)} ms\nTotal time taken was {ms}\n")
		embed.set_thumbnail(url="https://www.publicdomainpictures.net/pictures/350000/nahled/paddle-bat-ping-pong.png")
		embed.set_footer(text=f"Running on version {self.version}.\nDiscord py version: {discord.__version__}\nResponded in {round(self.client.latency * 1000)} ms\nPS:	press MORE for more info")
		embed.set_author(name= "Requested by: " +ctx.author.display_name, icon_url=ctx.author.avatar)
		embed2 = embed.copy()
		embed2.add_field(name = "For Nerds", value = f"Your message was created at {ctx.message.created_at} \nOur message was created at the time {t.created_at}, with the gap being {ms} ms \nOur internet delay time is {round(self.client.latency * 1000)} ms\nYour lag should be about {ms - round(self.client.latency * 1000)} ms")

		await t.edit(content = "", embed=embed, view = univ.buttons(embed2))
        

	@commands.command()
	async def help(self, ctx, *args):
		"""Sends this message"""
		prefix = "!"
		owner = 754532384984137772
		async def predicate(cmd):
				try:
					return await cmd.can_run(ctx)
				except commands.CommandError:
					return False
		if not args:
			try:
				owner = ctx.guild.get_member(owner).mention

			except AttributeError as e:
				owner = "pulsar|not|black_hole#5039"

			embed = discord.Embed(title = "Help", description = f'Use `{prefix}help <module>` to gain more information about that module ')
			cogs_desc = ''
			for module in self.client.cogs:
				if str(module) != "Jishaku":
					cogs_desc += f'`{module}` {self.bot.cogs[module].__doc__}\n'

            # adding 'list' of cogs to embed
			embed.add_field(name='Modules', value=cogs_desc, inline=False)

			commands_desc = ''
			for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
				if not command.cog_name and not command.hidden:
					commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
			if commands_desc:
				embed.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

			embed.add_field(name='About', value=f"{self.client.get_user(self.client.user.id)} is devoloped by {owner}", inline=False)
		elif len(args) == 1:

            # iterating trough cogs
			for cog in self.bot.cogs:
                # check if cog is the matching one
				if cog.lower() == args[0].lower():

                    # making title - getting description from doc-string below class
					embed = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.green())

                    # getting commands from cog
					for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
						if not command.hidden:
							valid = await predicate(command)
							if valid:
								embed.add_field(name=f"`{prefix}{command.name}`", value=command.help, inline=False)
                    # found cog - breaking loop
					break

            # if args not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
			else:
				embed = discord.Embed(title="Hmmmm",description=f"No module found of the instance `{args[0]}`",)

		elif len(args) > 1:
			embed = discord.Embed(title = "Chill", description = "Im not a search engine dude, one module at a time")

		embed.set_footer(text=f"Running on version {self.version}.\nDiscord py version: {discord.__version__}\nResponded in {round(self.client.latency * 1000)} ms")
		embed.set_author(name= "Requested by: " +ctx.author.display_name, icon_url=ctx.author.avatar)

		await ctx.channel.send(embed=embed)
