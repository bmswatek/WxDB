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
