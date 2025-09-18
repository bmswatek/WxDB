# Weather Discord Bot (WxDB) 🌦️

**Greetings and citations!** <br>
This is a simple Discord bot that provides real-time weather forecasts on command.

## Features ✨
* Fetches current weather, hourly, six-hourly and 7-day forecasts for multiple locations;
* Supports slash commands e.g: `/weather`;
* Showing weather variables such as minimum and maximum temperatures, precipitaion, cloud cover and more;
* Easy to deploy on any server!

## Technical Side 🛠️

* Language coded in Python
* Libraries including:
    * `python-dotenv`
    * `discord.py`
    * `aiohttp`
    * `requests`
    * Weather API (e.g. [Open-Meteo](https://open-meteo.com/))

## Installation

### 1. Clone the repository

```
git clone https://github.com/bmswatek/discord-bot-collab.git

cd ~/discord-bot-collab
```

### 2. Install the dependancies and libraries

```
py -m pip install python-dotenv
py -m pip install discord.py
py -m pip install aiohttp
py -m pip install requests
```
(or replace `py` with `python3`) 

### 3. Set up your own `.env` within the root of the directory

Set up your own Discord token: 
```
DISCORD_TOKEN=<own-private-token>
```
Do **NOT** share your own private token. <br>
Ensure that the `.env` file **is** ignored within the `.gitignore` file.

## Citations 📚

This bot is the collaborative effort made by [bmswatek](https://github.com/bmswatek) 
and [liamhall64](https://github.com/liamhall64).

With thanks to:
* [Open-Meteo](https://open-meteo.com/) for their open-source weather data<sup>[1](https://github.com/open-meteo/open-meteo)</sup>;
* [Nominatim](https://nominatim.openstreetmap.org/search) for latitude and longitudes for locations<sup>[2](https://github.com/osm-search/nominatim-ui)</sup>;
* [NOAA](https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM) for their weather codes.
* [OpenWeather](https://openweathermap.org/) for their weather icons. 
