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
    weekday = dt.strftime("%a")
    dd_mm = dt.strftime("%d/%m")
    return weekday, dd_mm

# Open Meteo Weather Codes Reference, utilising the World Meteorological Organization (WMO) system
# https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM

def get_weather_icon(weather_text: str) -> str:
    """
    Maps detailed weather descriptions to specific OpenWeatherMap icons.
    Reference: https://openweathermap.org/weather-conditions
    """
    w = weather_text.lower()

    # Thunderstorms
    if "thunder" in w or "storm" in w:
        return "https://openweathermap.org/img/wn/11d@2x.png"  

    # Snow & Ice
    elif "snow" in w or "sleet" in w or "ice" in w:
        return "https://openweathermap.org/img/wn/13d@2x.png"  

    # Heavy Rain
    elif "heavy rain" in w or "torrential" in w:
        return "https://openweathermap.org/img/wn/10d@2x.png" 

    # Showers
    elif "shower" in w or "rain shower" in w:
        return "https://openweathermap.org/img/wn/09d@2x.png"

    # Light/Slight Rain 
    elif "slight rain" in w or "light rain" in w or "rain" in w:
        return "https://openweathermap.org/img/wn/10d@2x.png"

    # Drizzle
    elif "drizzle" in w or "misty rain" in w:
        return "https://openweathermap.org/img/wn/09d@2x.png"

    # Fog, Haze, Mist
    elif "fog" in w or "mist" in w or "haze" in w:
        return "https://openweathermap.org/img/wn/50d@2x.png"

    # Clouds
    elif "overcast" in w or "cloud" in w or "mostly cloudy" in w:
        return "https://openweathermap.org/img/wn/03d@2x.png"

    # Clear / Sunny
    elif "clear" in w or "sun" in w:
        return "https://openweathermap.org/img/wn/01d@2x.png"

    # Default Fallback 
    else:
        return "https://openweathermap.org/img/wn/02d@2x.png"

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
        lat, lon = get_lat_long(location)
        if lat is None or lon is None:
            # Sending error message as a followup (ephemeral)
            await interaction.followup.send(
                f"Could not find coordinates for **{location}**.", ephemeral=True
            )
            return

        # Fetch forecast data from Open-Meteo API
        forecast_data = await self.get_weather(lat, lon)

        # Prepare a list to hold all embeds for 7 days
        embeds = []

        # Create a separate embed for each day
        for day in forecast_data:
            weekday, dd_mm = iso_convert(day["date"])
            icon_url = get_weather_icon(day["weather"])  # Get the weather icon URL
            # Build embed for the forecast data 
            embed = discord.Embed(
                title=f"Weather Forecast: {location} — {weekday} {dd_mm}"
            )
            embed.set_thumbnail(url=icon_url)  # Use weather icon
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
                value=f"{5 * round(day['precipitation'] / 5)}%",  # Round to the nearest 5% 
                inline=True
            )

            # You can add more fields here later, e.g., humidity, wind, sunrise, sunset

            embeds.append(embed)

        # Send all 7 embeds in a single message
        await interaction.followup.send(embeds=embeds)

    # Fetch weather data from Open-Meteo API
    async def get_weather(self, lat, lon):
        """Fetch daily weather data from Open-Meteo API."""
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
