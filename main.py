import discord
from discord.ext import commands
import logging 
from dotenv import load_dotenv
import os

#Loading environemnt Variables
load_dotenv()

#Retrieving the Discord Token
token = os.getenv('DISCORD_TOKEN')

#Logging within a file called 'discord.log'
#Handling all permissions with intents, manually setting them up within code 
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Set custom prefix for commands here
bot = commands.Bot(command_prefix='/', intents=intents)

#Bot message in terminal when bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} has come online!")

# /hello triggers this command 
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

#Calls for token and runs bot 
bot.run(token, log_handler=handler, log_level=logging.DEBUG)