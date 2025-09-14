from discord.ext import commands
import discord
import aiohttp
from discord import app_commands

# Predefined list of cities with their latitude and longitude
# You can expand this list as needed
CITIES = {
    "Aberdeen": {"lat": 57.1437, "lon": -2.0981},
    "Aberystwyth": {"lat": 52.4155, "lon": -4.0829},
    "Belfast": {"lat": 54.5968, "lon": -5.9254},
    "Birmingham": {"lat": 52.4814, "lon": -1.8998},
    "Bristol": {"lat": 51.4552, "lon": -2.5966},
    "Cambridge": {"lat": 52.2, "lon": 0.1167},
    "Cardiff": {"lat": 51.48, "lon": -3.18},
    "Edinburgh": {"lat": 55.9521, "lon": -3.1965},
    "Exeter": {"lat": 50.7236, "lon": -3.5275},
    "Glasgow": {"lat": 55.8651, "lon": -4.2576},
    "Ipswich": {"lat": 52.0592, "lon": 1.1555},
    "Leeds": {"lat": 53.7965, "lon": -1.5478},
    "Liverpool": {"lat": 53.4106, "lon": -2.9779},
    "London": {"lat": 51.5085, "lon": -0.1257},
    "Maidstone": {"lat": 51.2667, "lon": 0.5167},
    "Manchester": {"lat": 53.4809, "lon": -2.2374},
    "Newcastle": {"lat": 54.218, "lon": -5.8898},
    "Newquay": {"lat": 50.4156, "lon": -5.0732},
    "Norwich": {"lat": 52.6278, "lon": 1.2983},
    "Nottingham": {"lat": 52.9536, "lon": -1.1505},
    "Oxford": {"lat": 51.7522, "lon": -1.256},
    "Penzance": {"lat": 50.1186, "lon": -5.5371},
    "Southampton": {"lat": 50.904, "lon": -1.4043},
    "Swansea": {"lat": 51.6208, "lon": -3.9432},
    "York": {"lat": 53.9576, "lon": -1.0827},
}


# Open Meteo Weather Codes Reference, utilising the World Meteorological Organization (WMO) system
# https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM

WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Freezing Fog ❄️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow 🌨️",
    73: "Moderate snow 🌨️",
    75: "Heavy snow ❄️",
    80: "Rain showers 🌦️",
    81: "Moderate showers 🌧️",
    82: "Violent showers ⛈️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with hail ⛈️"
}
# Define the Weather Cog
class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Use slash command decorator
    @app_commands.command(name="weather", description="Get a 7-day weather forecast")
    async def weather(self, interaction: discord.Interaction):
        # Create dropdown menu for city selection
        options = [discord.SelectOption(label=city) for city in CITIES.keys()]
        select = discord.ui.Select(placeholder="Choose a city", options=options)

        # Define the callback for when a city is selected
        async def select_callback(select_interaction: discord.Interaction):
            city = select.values[0]
            coords = CITIES[city]
            forecast_data = await self.get_weather(coords["lat"], coords["lon"])

            # Build embed for the forecast data 
            embed = discord.Embed(title=f"7-Day Weather Forecast: {city}", color=discord.Color.blue())
            for day in forecast_data:
                embed.add_field(
                    name=day["date"],
                    value=f"{day['temp_min']}°C - {day['temp_max']}°C\n{day['weather']}",
                    inline=False
                )
            
            await select_interaction.response.send_message(embed=embed)

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)

        # Send dropdown menu as ephemeral
        await interaction.response.send_message("Please select the city to get the weather forecast:", view=view, ephemeral=True)
    
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
