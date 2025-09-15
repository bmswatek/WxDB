from discord.ext import commands
import discord
import aiohttp
from discord import app_commands
from datetime import datetime
from utils.location import get_lat_long
from utils.dict import WEATHER_CODES

# Function to convert ISO date string to weekday and DD/MM format
def iso_convert(date_str: str):
    """Converts the ISO standard date formate and splits it into two strings to
       shows the weekday and DD/MM."""
    dt = datetime.fromisoformat(date_str)
    weekday = dt.strftime("%a")  # Returns Mon, Tues etc...
    dd_mm = dt.strftime("%d/%m") # Returns 22/04 etc...
    return weekday, dd_mm

# Open Meteo Weather Codes Reference, utilising the World Meteorological Organization (WMO) system
# https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM

# Define the Weather Cog
class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Use slash command decorator
    @app_commands.command(name="weather", description="Get a 7-day weather forecast")
    async def weather(self, interaction: discord.Interaction, location: str):

        # Defer the response to allow for processing before sending the embeds
        await interaction.response.defer()

        # Get latitude and longitude from location.py and grabs forecast for said location
        lat, long = get_lat_long(location)
        if lat is None or long is None:
            # Sending error message as a followup (ephemeral)
            await interaction.followup.send(
                f"Could not find coordinates for **{location}**.", ephemeral=True
            )
            return

        # Fetch forecast data from Open-Meteo API
        forecast_data = await self.get_weather(lat, long)

        # Prepare a list to hold all embeds for 7 days
        embeds = []

        # Create a separate embed for each day
        for day in forecast_data:
            weekday, dd_mm = iso_convert(day["date"])
            # Build embed for the forecast data 
            embed = discord.Embed(
                title=f"Weather Forecast: {location} — {weekday} {dd_mm}",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Day Temp", 
                value=f"{round(day['temp_max'])}°C", 
                inline=True
            )
            embed.add_field(
                name="Night Temp", 
                value=f"{round(day['temp_min'])}°C", 
                inline=True
            )
            embed.add_field(
                name="Weather", 
                value=day['weather'], 
                inline=False
            )
            # Add UV Index 
            embed.add_field(
                name="UV Index", 
                value=f"{round(day['uv_index'])}", 
                inline=True
            )
            # Add Precipitation %
            embed.add_field(
                name="Precipitation", 
                value=f"{5 * round(day['precipitation'] / 5)}%", # Round to the nearest 5% 
                inline=True
            )

            # You can add more fields here later, e.g., humidity, wind, sunrise, sunset

            embeds.append(embed)

        # Send all 7 embeds in a single message
        await interaction.followup.send(embeds=embeds)

    # Fetch weather data from Open-Meteo API
    async def get_weather(self, lat, lon):
        # Added uv_index_max and precipitation_probability_max to API call
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,weathercode,uv_index_max,precipitation_probability_max"
            f"&timezone=auto"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        # Parse the relevant data
        daily = data["daily"]
        forecast_list = []
        for date, t_max, t_min, code, uv, precip in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["weathercode"],
            daily["uv_index_max"],
            daily["precipitation_probability_max"]
        ):
            weather_text = WEATHER_CODES.get(code, "Unknown")
            forecast_list.append({
                "date": date,
                "temp_max": t_max,
                "temp_min": t_min,
                "weather": weather_text,
                "uv_index": uv,
                "precipitation": precip
            })

        return forecast_list

# Setup function to load the Cog
async def setup(bot):
    await bot.add_cog(Weather(bot))
