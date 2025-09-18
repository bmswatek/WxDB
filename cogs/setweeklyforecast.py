from discord.ext import commands, tasks
import discord
import aiohttp
from discord import app_commands
from datetime import datetime, time
import json, os

from utils.location import get_lat_long
from utils.dict import WEATHER_CODES
from utils.weather_icons import get_weather_icon

SETTINGS_FILE = "forecast_settings.json"
FORECAST_SETTINGS = {}  # {guild_id: {"channel": channel_id, "location": location, "message_id": last_forecast_message_id}}

# Load & Save Settings
def load_settings():
    global FORECAST_SETTINGS
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            FORECAST_SETTINGS = json.load(f)

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(FORECAST_SETTINGS, f)

# Helper Functions
def iso_convert(date_str: str):
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%a"), dt.strftime("%d/%m")

# Weather Cog
class SetWeeklyForecast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_settings()
        self.daily_forecast.start()

    async def cog_unload(self):
        self.daily_forecast.cancel()

    async def get_weather(self, lat, lon):
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,weathercode,uv_index_max,precipitation_probability_max"
            f"&timezone=auto"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        daily = data["daily"]
        forecast_list = []
        for date, t_max, t_min, code, uv, precip in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["weathercode"],
            daily["uv_index_max"],
            daily["precipitation_probability_max"],
        ):
            forecast_list.append({
                "date": date,
                "temp_max": t_max,
                "temp_min": t_min,
                "weather": WEATHER_CODES.get(code, "Unknown"),
                "uv_index": uv,
                "precipitation": precip
            })
        return forecast_list

    async def build_forecast_embeds(self, location, forecast_data):
        embeds = []
        for day in forecast_data:
            weekday, dd_mm = iso_convert(day["date"])
            icon_url = get_weather_icon(day["weather"])
            embed = discord.Embed(
                title=f"Weather Forecast: {location} — {weekday} {dd_mm}"
            )
            embed.set_thumbnail(url=icon_url)
            embed.add_field(name="Day Temp", value=f"{round(day['temp_max'])}°C", inline=True)
            embed.add_field(name="Night Temp", value=f"{round(day['temp_min'])}°C", inline=True)
            embed.add_field(name="Weather", value=day['weather'], inline=False)
            embed.add_field(name="UV Index", value=f"{round(day['uv_index'])}", inline=True)
            embed.add_field(name="Precipitation", value=f"{5 * round(day['precipitation'] / 5)}%", inline=True)
            embeds.append(embed)
        return embeds

    @app_commands.command(name="setweeklyforecast", description="Set a channel and location for daily weather updates.")
    async def set_weekly_forecast(self, interaction: discord.Interaction, channel: discord.TextChannel, location: str):
        lat, lon = get_lat_long(location)
        if lat is None or lon is None:
            await interaction.response.send_message(f"Could not find coordinates for **{location}**.", ephemeral=True)
            return

        FORECAST_SETTINGS[str(interaction.guild.id)] = {"channel": channel.id, "location": location, "message_id": None}
        save_settings()
        await interaction.response.send_message(
            f"Weekly forecast for **{location}** will now be posted daily in {channel.mention}.", ephemeral=True
        )

        forecast = await self.get_weather(lat, lon)
        embeds = await self.build_forecast_embeds(location, forecast)
        msg = await channel.send(embeds=embeds)
        FORECAST_SETTINGS[str(interaction.guild.id)]["message_id"] = msg.id
        save_settings()

    @app_commands.command(name="removeweeklyforecast", description="Remove the configured daily forecast for this server.")
    async def remove_weekly_forecast(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in FORECAST_SETTINGS:
            await interaction.response.send_message(
                "No weekly forecast is currently set up for this server.",
                ephemeral=True
            )
            return

        removed_channel = FORECAST_SETTINGS[guild_id]["channel"]
        del FORECAST_SETTINGS[guild_id]
        save_settings()

        await interaction.response.send_message(
            f"Weekly forecast updates have been **removed** for <#{removed_channel}>.",
            ephemeral=True
        )

    @tasks.loop(time=time(8, 0))
    async def daily_forecast(self):
        for guild_id, settings in FORECAST_SETTINGS.items():
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                continue
            channel = guild.get_channel(settings["channel"])
            if not channel:
                continue

            lat, lon = get_lat_long(settings["location"])
            if lat is None or lon is None:
                continue

            forecast = await self.get_weather(lat, lon)
            embeds = await self.build_forecast_embeds(settings["location"], forecast)

            try:
                # Edit existing message if exists
                if settings.get("message_id"):
                    try:
                        msg = await channel.fetch_message(settings["message_id"])
                        await msg.edit(embeds=embeds)
                        continue
                    except discord.NotFound:
                        pass  # message was deleted, send a new one

                msg = await channel.send(embeds=embeds)
                settings["message_id"] = msg.id
                save_settings()
            except discord.Forbidden:
                print(f"Permission error: Cannot post in {channel} of guild {guild.name}")

async def setup(bot):
    await bot.add_cog(SetWeeklyForecast(bot))
