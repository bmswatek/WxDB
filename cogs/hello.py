#Import commands extension from discord.py
from discord.ext import commands 

#Define a Cog (group of events and/or commands)
class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Define a commands called "hello"
    @commands.command()
    async def hello(self, ctx): #ctx is Context of the command (who sent it, where etc.)
        await ctx.send(f"Hello {ctx.author.mention}!") #If someone executes the command, they will receive a message saying "Hello {user}!"

#Function that makes the bot load this Cog
async def setup(bot):
    await bot.add_cog(Hello(bot))
    