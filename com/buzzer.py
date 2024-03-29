import discord
from discord.ext import commands
import json, requests
import time
import univ.vars as univ
import asyncio
import re
import random
import collections

type_of_questions = ["astro","bio","chem","cs","eas","energy","es","gen","math","phy"]

def similarity(string1, string2):
    string1 = string1.upper()
    string2 = string2.upper()
    intersection = collections.Counter(string1) & collections.Counter(string2)
    union = collections.Counter(string1) | collections.Counter(string2)
    return sum(intersection.values()) / sum(union.values())
    
class GetResponse(discord.ui.Modal, title="Short Response"):
    answer = discord.ui.TextInput(label='Answer',
                                  style=discord.TextStyle.short,
                                  placeholder="Quick! Your answer")

    def __init__(self, view, timeout, author):
        super().__init__()
        self.view = view
        self.a = author
        self.timeouted = False

    async def on_submit(self, interaction: discord.Interaction):
        # Do something with user's response
        fullans = self.answer.value
        try:
            if univ.data[interaction.guild]["channel"] == interaction.channel:
                if univ.data[interaction.guild]["Question"].answering == interaction.user.id:
                    await univ.data[interaction.guild]["Question"].validate(fullans,interaction.user.id)
                    await interaction.response.defer()
                else:
                    return await interaction.channel.send("You didn't buzz", mention_author=False, ephermal = True)
        except:
            return await interaction.channel.send("There is no active round in your server", mention_author=False, ephemeral = True)


async def setup(bot):
	await bot.add_cog(buzzer(bot))

def get_lb(guild):
                    scores = []
                    a = []

                    for key, value in univ.data[guild]["lb"].items():
                        scores.append(value)
                    scores.sort(reverse=True)
                    for i in range(len(scores)):
                        for key,value in univ.data[guild]["lb"].items():
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
                    
                    embed.set_thumbnail(
                    url=
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Twemoji2_1f947.svg/512px-Twemoji2_1f947.svg.png?20170615234944"
                    )
                    return embed

class buzzer(commands.Cog):
    """
    Everything you need to do you science bowl round!
    """
    def __init__(self, bot):
        self.client = bot

    @commands.hybrid_command()
    async def q(self,ctx, type: str):
        """
        Get a single question, of a subject of your choosing
        Available types are:
        astro
        bio
        chem
        cs
        eas
        energy
        es
        gen
        math
        phy
        Usage: {}q [type]
        """
        if type not in type_of_questions:
            return await ctx.send("That is not a valid question type. See `sci!help q` for valid question types",ephemeral = True)
        d = requests.get(f"https://raw.githubusercontent.com/DevNotHackerCorporations/scibowlbot/main/questions/{type}.json")
        if ctx.guild not in univ.data:
                await ctx.send(f"Loading question of type: {type}")
                univ.data[ctx.guild] = {"channel": ctx.channel}
                data = d.json()
                i = random.randint(0,len(data))

                data = json.loads(json.dumps(data[i]))
                univ.data[ctx.guild]["Question"] = question(ctx,1, "TOSSUP",str(type.upper()), str(data.get('tossup_format')), str(data.get('uri')), str(data.get('tossup_question')), str(data.get('tossup_answer')),1,ctx.author.id)
                await univ.data[ctx.guild]["Question"].run()
                await univ.data[ctx.guild]["Question"].cleanup()
                try:
                    univ.data.pop(ctx.guild)   
                except:
                    """Nothing here"""
        else:
            await ctx.send("There is still another question, or round in your server")
    @q.autocomplete('type')
    async def q_autocomplete(self, interaction, current):
        return [
			discord.app_commands.Choice(name=thing, value=thing)
			for thing in type_of_questions
			if current.lower() in thing.lower()
		]

    @commands.hybrid_command()
    async def reset(self, ctx):
        """
        Use this in case it says there is an active round even though there is not
        Usage: {}reset
        """
        try:
            embed = get_lb(ctx.guild)
            embed.set_author(name="Stopped by: " + ctx.author.display_name,
                                icon_url=ctx.author.avatar)
        except:
            pass
        try:
            univ.data.pop(ctx.guild)
        except:
            pass
        await ctx.send("Round stopped!! (Please note that the final question did not count)", )
        try:
            await ctx.channel.send(embed=embed)
        except:
            pass
    @commands.hybrid_command()
    async def startround(self, ctx, num_questions: int = 20):
        """
        Start a science bowl round!
        Usage: {}startround (number of questions)
        """
        
        if ctx.guild not in univ.data:
            e = {
                "channel" : ctx.channel,
                "buzzData" : "",
                "lb": {}
            }
            if num_questions >= 100:
                await ctx.send("WAYYYYY TOO MANY QUESTIONS MAN")
                return
            univ.data[ctx.guild] = e
            await ctx.send(f"Ok, starting a round of {num_questions} questions")
            for i in range(num_questions):

                if not (ctx.guild in univ.data):
                    break
                type = random.choice(type_of_questions)
                d = requests.get(f"https://raw.githubusercontent.com/DevNotHackerCorporations/scibowlbot/main/questions/{type}.json")
                data = d.json()
                i = random.randint(0,len(data))

                data = json.loads(json.dumps(data[i]))

                univ.data[ctx.guild]["Question"] = question(ctx,i+1, "TOSSUP",str(data['category']), str(data['tossup_format']), str(data['uri']), str(data['tossup_question']), str(data['tossup_answer']),1,ctx.author.id)
                await univ.data[ctx.guild]["Question"].run()
                await asyncio.sleep(0.05)
                try:
                    ans, CorrectMan = await univ.data[ctx.guild]["Question"].cleanup()
                    if CorrectMan != False:
                        if CorrectMan in univ.data[ctx.guild]["lb"]:
                            univ.data[ctx.guild]["lb"][CorrectMan] += 4
                        else:
                            univ.data[ctx.guild]["lb"][CorrectMan] = 4
                except:
                    break

                await asyncio.sleep(1)
            else:
                    embed = get_lb(ctx.guild)
                    embed.set_author(name="Requested by: " + ctx.author.display_name,
                            icon_url=ctx.author.avatar)
                    await ctx.send(embed=embed)


                    try:
                        univ.data.pop(ctx.guild)   
                    except:
                        """Nothing here"""
        else:
            await ctx.send("There is already an active round in this server", ephemeral = True)
            


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
        self.embed = discord.Embed(title="Loading", description="Loading", color=0xFF5733)
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
        self.embed.add_field(name="Question", value=f"{self.typed_question}" if not showans else f"{self.question}", inline=False)
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
        else:
            self.BuzzData += "**Incorrect**\n"
            self.progress = True
            self.answering = False

        for item in self.children:
            if item.label.lower() == "w" or item.label.lower() == "x" or item.label.lower() == "y" or item.label.lower() == "z":

                self.remove_item(item)

        if self.answered:
            """yay?"""
        else:
            await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>",beRed= True)
        
    async def validate(self,ans,author):
        self.BuzzData += ans+ " - "
        correct = False
        for e in self.answer_list:
            if similarity(e,ans) > 0.5:
                correct = True
                break
        if correct:
            self.BuzzData += "**Correct!**"
            self.answered = True 
            self.CorrectMan = author
        else:
            self.BuzzData += "**Incorrect**\n"
            self.progress = True
            self.answering = False
            
        if self.answered:
            """"""
        else:
            await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>",beRed=True)

    async def sendquestion(self, ctx,type, choice_type, source, question, answer,speed):
        self.message = await self.ctx.channel.send(embed = self.embed)
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
            await asyncio.sleep(0.01)
        
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
        stuff = f"**<@{interaction.user.id}>** - "
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
                await interaction.response.send_modal(
                GetResponse(self, 4,
                            self.author))
                self.timeleftUNIX += int(len(self.answer)) + 4
                await self.updateEmbed(f"<t:{self.timeleftUNIX}:R>")

                oldBuzzData = self.BuzzData
                await asyncio.sleep(int(len(self.answer)) + 4.1)

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