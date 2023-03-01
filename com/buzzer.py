import discord
from discord.ext import commands
import requests
import json 
import time
import univ.vars as univ
import asyncio
import re
import random



intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = commands.when_mentioned_or('!'), intents=intents, description = "Buzz", help_command=None, activity = discord.Game(name="!help"))

async def setup(bot):
	await bot.add_cog(buzzer(bot))


class buzzer(commands.Cog):
    """
    Everything you need to do you science bowl round!
    """
    def __init__(self, bot):
        self.client = bot

    @commands.command(aliases = ['a', 'ans'])
    async def answer(self,ctx, *answer):
        """
        Answer a question in the round.
        Only if you have buzzed
        """
        fullans = ""
        for item in answer:
            fullans +=item + " "
        try:
            if univ.data[ctx.guild]["channel"] == ctx.channel:
                if univ.data[ctx.guild]["Question"].answering == ctx.author.id:
                    await univ.data[ctx.guild]["Question"].validate(fullans,ctx.author.id)
                else:
                    return await ctx.reply("You didn't buzz", mention_author=False, ephermal = True)
        except:
            return await ctx.reply("There is no active round in your server", mention_author=False, ephermal = True)

    @commands.command(aliases=['start', 'begin'])
    async def startround(self, ctx):

        if ctx.guild not in univ.data:
            e = {
                "channel" : ctx.channel,
                "buzzData" : "",
                "lb": {}
            }
            univ.data[ctx.guild] = e

            for i in range(20):

                if ctx.guild not in univ.data:
                    break
                f = open("questions/questions.json")
                data = json.load(f)
                i = random.randint(0,len(data["questions"]))

                data = json.loads(json.dumps(data['questions'][i]))

                univ.data[ctx.guild]["Question"] = question(ctx,i+1, "TOSSUP",str(data['category']), str(data['tossup_format']), str(data['uri']), str(data['tossup_question']), str(data['tossup_answer']),1,ctx.author.id)
                await univ.data[ctx.guild]["Question"].run()
                try:
                    ans, CorrectMan = await univ.data[ctx.guild]["Question"].cleanup()
                except: 
                    """Do nothing"""
                if CorrectMan != False:
                    if CorrectMan in univ.data[ctx.guild]["lb"]:
                        univ.data[ctx.guild]["lb"][CorrectMan] += 4
                    else:
                        univ.data[ctx.guild]["lb"][CorrectMan] = 4

                await asyncio.sleep(1)

            scores = []
            a = []
            try:
                for key, value in univ.data[ctx.guild]["lb"].items():
                    scores.append(value)
                scores.sort(reverse=True)
                for i in range(len(scores)):
                    for key,value in univ.data[ctx.guild]["lb"].items():
                        if scores[i] == value:
                            a.append(key)
                for i in range(3):
                    a.append("No one")
                    scores.append(0)
                
                desc = f"""
                :first_place: **<@!{a[0]}>** - **{scores[0]}**
                :second_place: **<@!{a[1]}>** - **{scores[1]}**
                :third_place: **<@!{a[2]}>** - **{scores[2]}**
                """
                for i in range(3):
                    del scores[0]
                    del a[0]

                for i in range(len(scores)):
                    if a[i] != "No one":
                        desc += f":medal: **<@!{a[i]}>** - **{scores[i]}**\n"

                embed = discord.Embed(title=f"End, it's over", description=desc, color=0x00FF00)
                embed.set_author(name="Requested by: " + ctx.author.display_name,
                        icon_url=ctx.author.avatar)
                embed.set_thumbnail(
                url=
                    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Twemoji2_1f947.svg/512px-Twemoji2_1f947.svg.png?20170615234944"
                )
                await ctx.send(embed=embed)
            except :
                pass

            try:
                univ.data.pop(ctx.guild)   
            except:
                """Nothing here"""
        else:
            await ctx.send("There is already an active round in this server")
            


class question(discord.ui.View):
    def __init__(self,ctx,number,type,category,choice_type,source,question,answer,speed, owner,bonus = False):
        super().__init__(timeout = None)
        self.bonus = bonus
        self.ctx = ctx
        self.number = number
        self.category = category
        self.type = type
        self.choice_type = choice_type
        self.source = source
        self.question = question
        self.answer = answer
        self.speed = speed
        self.view = self
        self.embed = discord.Embed(title=f"Loading", description=f"Loading", color=0xFF5733)
        self.BeingRead = True
        self.answered = False
        self.BuzzData = "Nobody Buzzed Yet!"
        self.progress = True
        self.mc = choice_type == "Multiple Choice"
        self.answering = False
        self.author = owner
    
    async def getAns(self):
        answers = [self.answer.upper()]
        if self.mc:
            return answers

        x = self.answer.upper()
        #Remove parenthesis
        answers.append(re.sub("[\(\[].*?[\)\]]", "", x))

        #get accepted answer
        x = self.answer.upper()
        try:
            x = x.split("(ACCEPT: ",1)[1]
            try:
                x = x.split(")",1)[0]
            except:
                """Do nothing"""
            try:
                x=x.split("DO NOT ACCEPT:")[0]
            except:
                """Do nothing"""
        except:
            """Do nothing"""

        #remove spaces
        x = self.answer.upper()
        answers.append(x.strip())

        return answers

    async def run(self):
        self.answer_list = await self.getAns()
        await self.sendquestion(self.ctx,self.type,self.choice_type,self.source,self.question,self.answer,self.speed)

    async def cleanup(self):
        for item in self.children:
            self.remove_item(item)
        await self.updateEmbed("THis question is expired",True, not self.answered)
        

        if self.answered:
            return self.answered, self.CorrectMan
        else:
            return self.answered, False
        

    async def updateEmbed(self,Timeleft, showans = False, beRed = False):
        if self.answered:
            self.embed = discord.Embed(title=f"{self.number}) {self.category} {self.type} {self.choice_type}", description=f"(SOURCE: {self.source} \nPress buzz to buzz)", color=0x00FF00)
        elif beRed:
            self.embed = discord.Embed(title=f"{self.number}) {self.category} {self.type} {self.choice_type}", description=f"(SOURCE: {self.source} \nPress buzz to buzz)", color=0xFF0000)
        else:
            self.embed = discord.Embed(title=f"{self.number}) {self.category} {self.type} {self.choice_type}", description=f"(SOURCE: {self.source} \nPress buzz to buzz)", color=0xFF5733)
        self.embed.add_field(name="Question", value=f"{self.typed_question}", inline=False)
        self.embed.add_field(name="Buzz's:", value=f"{self.BuzzData}", inline=False)
        self.embed.add_field(name="TimeLeft", value=f"{Timeleft}.", inline=True)
        if showans:
            self.embed.add_field(name = "Answer", value = f"It was: \n{self.answer}", inline = False)
        await self.message.edit(embed=self.embed, view = self.view)

    async def validateMC(self,ans):

        self.BuzzData += ans.label[0] + " - "
        if ans.label[0].lower() == self.answer[0].lower():
            self.BuzzData += "**Correct!**"
            self.answered = True 
            self.CorrectMan = ans.author
            await self.updateEmbed("Question has expired")
        else:
            self.BuzzData += "**Incorrect**\n"
            self.progress = True
            self.answering = False

        for item in self.children:
            if item.label.lower() == "w" or item.label.lower() == "x" or item.label.lower() == "y" or item.label.lower() == "z":

                self.remove_item(item)

        if self.answered:
            await self.updateEmbed("Question has expired")
        else:
            await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>",beRed= True)
        
    async def validate(self,ans,author):
        self.BuzzData += ans+ " - "
        if ans.upper() in self.answer_list:
            self.BuzzData += "**Correct!**"
            self.answered = True 
            self.CorrectMan = author
        else:
            self.BuzzData += "**Incorrect**\n"
            self.progress = True
            self.answering = False
            
        if self.answered:
            await self.updateEmbed("Question has expired")
        else:
            await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>",beRed=True)

    async def sendquestion(self, ctx,type, choice_type, source, question, answer,speed):
        self.message = await self.ctx.send(embed = self.embed)
        self.typed_question = ""

        self.full_question = question.split("\n")
        

        if type == "TOSSUP":
            self.timeleftUNIX = int(time.time() + 5)
        else:
            self.timeleftUNIX = int(time.time() +20)

        self.timeleftUNIX += (len(self.full_question)+1) * speed
        
        i = 0
        run = True
        while i < len(self.full_question) and run:

            while not self.progress:
                if self.answered:
                    run = False
                    break
                await asyncio.sleep(0.5)
            
            await asyncio.sleep(speed)

            self.typed_question += self.full_question[i] + "\n" 

            await self.updateEmbed("Question is being read")
            i+=1

        self.BeingRead = False
        
        
        await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>")

        while self.timeleftUNIX > time.time() and not self.answered:
            await asyncio.sleep(0.1)

        await self.updateEmbed("Time over")
        self.embed.add_field(name = "Answer", value = f"It was: \n{answer}", inline = False)
        await self.message.edit(embed=self.embed)


    @discord.ui.button(label="Buzz!", style=discord.ButtonStyle.green)
    async def buzz(self, interaction, button):
        if self.answering != False:
            return await interaction.response.send_message(
                "Somebody else is currently buzzing",
                ephemeral=True)
        if self.BuzzData == "Nobody Buzzed Yet!":
            self.BuzzData = ""
        stuff = f"**{interaction.user.name}** - "
        if self.BeingRead:
            stuff += "Interupt - "
            self.progress = False
        self.BuzzData += stuff
        self.answering = interaction.user.id
        if self.timeleftUNIX <= time.time():
            return await interaction.response.send_message(
                "Time over",
                ephemeral=True) 

        if self.type == "TOSSUP":
            if self.mc:
                await interaction.response.defer()
                self.timeleftUNIX += 5
                

                self.add_item(McButton("W",interaction.user.id))
                self.add_item(McButton("X",interaction.user.id))
                self.add_item(McButton("Y",interaction.user.id))
                self.add_item(McButton("Z",interaction.user.id))

                
                await self.updateEmbed(f"<t:{int(time.time() + 5)}:R>")
                
                oldBuzzData = self.BuzzData
                await asyncio.sleep(5.1)


                if str(self.BuzzData) == str(oldBuzzData):
                    self.BuzzData += "**Stall**"
                    self.progress = True
                    self.answering = False
                    for item in self.children:
                        if item.label.lower() == "w" or item.label.lower() == "x" or item.label.lower() == "y" or item.label.lower() == "z":

                            self.remove_item(item)
                    if self.BeingRead:
                        await self.updateEmbed("Question is being read")
                    else:
                        await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>")



                button.disabled = False
                

            else:
                await interaction.response.defer()
                await interaction.response.send_message(f"Quick! Send `sci!a [answer]` to provide your answer", ephemeral=True)
                self.timeleftUNIX += int(len(self.answer) * 0.2) + 4
                await self.updateEmbed(f"<t:{int(time.time() + len(self.answer) * 0.2) + 4}:R>")

                oldBuzzData = self.BuzzData
                await asyncio.sleep(int(len(self.answer) * 0.2) + 4.1)

                if str(self.BuzzData) == str(oldBuzzData):
                    self.BuzzData += "**Stall**"
                    self.progress = True
                    self.answering = False
                    if self.BeingRead:
                        await self.updateEmbed("Question is being read")
                    else:
                        await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>")

        else:
            self.timeleftUNIX + 20
            await self.updateEmbed(f"{int(time.time() + 20)}")
        




    @discord.ui.button(label = "stop", style = discord.ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.button):
        try:
            if interaction.author.id == self.author:
                univ.data.pop(interaction.guild)
                self.embed.add_field(name="Stopped", value=f"The round has been stopped. Please wait for the question to finish", inline=False)
                await self.message.edit(embed = self.embed)
            else:
                await interaction.response.send_message("You are not the owner >:(")   
        except:
            """Do nothing"""
        await interaction.response.defer()

class McButton(discord.ui.Button):
    def __init__(self, lable,author):
        self.author = author
        self.lable = lable
        self.mc = True
        super().__init__(label=f"{self.lable}",style=discord.ButtonStyle.blurple,row = 2)

    
    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "You didn't buzz. Somebody else did.",
                ephemeral=True)
        if self.view.timeleftUNIX <= time.time():
            return await interaction.response.send_message(
                "Time over",
                ephemeral=True) 
        await interaction.response.defer()
        await self.view.validateMC(self)