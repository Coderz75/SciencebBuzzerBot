import discord
from discord.ext import commands

async def setup(bot):
	
	await bot.add_cog(cf(bot))

class cf(commands.Cog):
	"""Configuration + Info"""

	def __init__(self, bot):
		self.client = bot
		self.bot = bot
		self.version = 1

	@commands.hybrid_command()
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

			embed.add_field(name='About', value=f"{self.client.get_user(self.client.user.id)} is devoloped by {owner} \nFind out private policy at ```{prefix}policy```", inline=False)
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
