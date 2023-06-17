import discord
from discord.ext import commands

async def setup(bot):
	await bot.add_cog(Misc(bot))
	bot.add_command(hello)
class buttons(discord.ui.View):
		def __init__(self, oninteraction,timeout=180):
			super().__init__(timeout=timeout)
			global result
			result = oninteraction

		@discord.ui.button(label="MORE",style=discord.ButtonStyle.gray)
		async def blurple_button(self,interaction:discord.Interaction,button):

			await interaction.message.edit(embed= result,view=self)
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
		"""
		Pong! What else
		Usage: {}ping
		"""
		t = await ctx.send('Pong!')
		ms = (t.created_at-ctx.message.created_at).total_seconds() * 1000
		embed = discord.Embed(title = "Pong", description = f"Pong, what else? \nOur client delay time was about {round(self.client.latency * 1000)} ms\nMy lag should be about {ms - round(self.client.latency * 1000)} ms\nTotal time taken was {ms}\n")
		embed.set_thumbnail(url="https://www.publicdomainpictures.net/pictures/350000/nahled/paddle-bat-ping-pong.png")
		embed.set_footer(text=f"Running on version {self.version}.\nDiscord py version: {discord.__version__}\nResponded in {round(self.client.latency * 1000)} ms\nPS:	press MORE for more info")
		embed.set_author(name= "Requested by: " +ctx.author.display_name, icon_url=ctx.author.avatar)
		embed2 = embed.copy()
		embed2.add_field(name = "For Nerds", value = f"Your message was created at {ctx.message.created_at} \nOur message was created at the time {t.created_at}, with the gap being {ms} ms \nOur internet delay time is {round(self.client.latency * 1000)} ms\nMy lag should be about {ms - round(self.client.latency * 1000)} ms")

		await t.edit(content = "", embed=embed, view = buttons(embed2))
        
	@commands.hybrid_command(name="help")
	async def _help(self, ctx, *, module):
		"""
		Shows this message
		Usage: {}help (command)
		"""
		prefix = "sci!"
		owner = 754532384984137772

		async def predicate(cmd):
			try:
				return await cmd.can_run(ctx)
			except commands.CommandError:
				return False

		if not module:
			try:
				owner = ctx.guild.get_member(owner).mention

			except:
				owner = 712426753238237274

			embed = discord.Embed(
				title="Help",
				description=
				f'Use `{prefix}help <module>` to gain more information about that module '
			)
			cogs_desc = ''
			for module in ctx.bot.cogs:
				if str(module) != "Jishaku":
					cogs_desc += f'`{module}` {ctx.bot.cogs[module].__doc__}\n'

			# adding 'list' of cogs to embed
			embed.add_field(name='Modules', value=cogs_desc, inline=False)

			commands_desc = ''
			for command in ctx.bot.walk_commands():
				# if cog not in a cog
				# listing command if cog name is None and command isn't hidden
				if not command.cog_name and not command.hidden:
					commands_desc += f'`{command.name}` - {command.help}\n'.format(prefix)

			# adding those commands to embed
			if commands_desc:
				embed.add_field(name='Not belonging to a module',
								value=commands_desc,
								inline=False)

			embed.add_field(
				name='About',
				value=
				f"{ctx.bot.get_user(ctx.bot.user.id)} is devoloped by {owner}",
				inline=False)
		else:

			# iterating trough cogs
			for cog in ctx.bot.cogs:
				# check if cog is the matching one
				if cog.lower() == module.lower():

					# making title - getting description from doc-string below class
					embed = discord.Embed(title=f'{cog} - Commands',
										description=ctx.bot.cogs[cog].__doc__,
										color=discord.Color.green())

					# getting commands from cog
					for command in ctx.bot.get_cog(cog).get_commands():
						# if cog is not hidden
						if not command.hidden:
							valid = await predicate(command)
							if valid:
								if command.help != None:
									embed.add_field(name=f"`{prefix}{command.name}`",
												value=command.help.split("\n")[0],
												inline=False)
								else:
									embed.add_field(name=f"`{prefix}{command.name}`",
												value="No help info for this command",
												inline=False)
					# found cog - breaking loop
					break

			# if module not found
			# yes, for-loops have an else statement, it's called when no 'break' was issued
			else:
				for command in ctx.bot.commands:
					if command.name.lower() == str(module).lower():
						command_help = str(command.help)
						command_help = command_help.format(prefix)
						command_help = command_help.replace("Usage:","Usage:`")
						command_help += "`"
						# making title - getting description from doc-string below class
						embed = discord.Embed(title=f'{command} - Commands',
											description=command_help,
											color=discord.Color.green())
						# found command - breaking loop
						break

				else:
					embed = discord.Embed(
						title="Hmmmm",
						description=
						f"No module or command found of the instance `{module}`",
					)

		embed.set_footer(
			text=
			f"Discord py version: {discord.__version__}\nResponded in {round(ctx.bot.latency * 1000)} ms"
		)
		embed.set_author(name="Requested by: " + ctx.author.display_name,
						icon_url=ctx.author.avatar)

		await ctx.send(embed=embed)

	@_help.autocomplete('module')
	async def q_autocomplete(self, interaction, current):
		choices = []
		for command in self.bot.commands:
			choices.append(str(command))
		for cog in self.bot.cogs:
			if str(cog) != "Jishaku":
				choices.append(str(cog))
		return [
			discord.app_commands.Choice(name=thing, value=thing)
			for thing in choices
			if current.lower() in thing.lower()
		]

@commands.hybrid_command(name = "hello")
async def hello(ctx):
	"""
	Hello, Just a random fun command
	Usage: {}help
	"""
	await ctx.send("Hello to you my good sir.")