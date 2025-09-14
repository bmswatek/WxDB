import discord
from discord.ext import commands
import logging 
from dotenv import load_dotenv
import os
import asyncio

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

#Loading COGS to setup all the commands
#Define commandsetup() to load every file within the cogs folder without having to add every new command into the main.py 
async def commandsetup():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    #Sync (/) commnds 
    await bot.tree.sync()
    print("Slash commands synced!")
    #Bot message in terminal when bot is ready
    print(f"{bot.user.name} has come online!")
    

#Start the bot with cog loading 
async def main():
    await commandsetup()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())