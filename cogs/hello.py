import discord
from discord import app_commands
from discord.ext import commands

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Define a slash command instead of a prefix command
    @app_commands.command(name="hello", description="Say hello to the bot!")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")

async def setup(bot):
    await bot.add_cog(Hello(bot))
