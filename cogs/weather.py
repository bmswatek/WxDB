from discord.ext import commands
import discord
import aiohttp
from discord import app_commands
from utils.location import get_lat_long
from utils.dict import WEATHER_CODES

# Open Meteo Weather Codes Reference, utilising the World Meteorological Organization (WMO) system
# https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM

# Define the Weather Cog
class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Use slash command decorator
    @app_commands.command(name="weather", description="Get a 7-day weather forecast")
    async def weather(self, interaction: discord.Interaction, location: str):

        # Get latitude and longitude from location.py and grabs forecast for said location
        lat, long = get_lat_long(location)
        if lat is None or long is None:
            await interaction.response.send_message(embed=f"Could not find coordinates for **{location}**.", ephemeral=True)
            return

        forecast_data = await self.get_weather(lat, long)

        # Build embed for the forecast data 
        embed = discord.Embed(title=f"7-Day Weather Forecast: {location}", color=discord.Color.blue())
        for day in forecast_data:
            embed.add_field(
                name=day["date"],
                value=f"{day['temp_min']}°C - {day['temp_max']}°C\n{day['weather']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    # Fetch weather data from Open-Meteo API
    async def get_weather(self, lat, lon):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        # Parse the relevant data
        daily = data["daily"]
        forecast_list = []
        for date, t_max, t_min, code in zip(daily["time"], daily["temperature_2m_max"], daily["temperature_2m_min"], daily["weathercode"]):
            weather_text = WEATHER_CODES.get(code, "Unknown")
            forecast_list.append({
                "date": date,
                "temp_max": t_max,
                "temp_min": t_min,
                "weather": weather_text
            })

        return forecast_list

async def setup(bot):
    await bot.add_cog(Weather(bot))
