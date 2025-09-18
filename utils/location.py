import requests
import json
import os

CACHE_FILE = "location_cache.json"

# Load existing cache from file
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}

def save_cache():
    """Save the current cache dictionary to disk."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def normalize_address(address: str) -> str:
    """Normalize address strings to reduce duplicate cache entries."""
    return address.strip().lower()

def get_lat_long(address: str):
    """
    Return (lat, lon) for a given address using OpenStreetMap's Nominatim API.
    Uses a persistent JSON cache to minimize API calls and prevent rate-limiting.
    """
    address_key = normalize_address(address)

    # Return cached result if it exists
    if address_key in cache:
        return cache[address_key]

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "discord-bot-collab/1.0 (your_email@example.com)"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            lat, lon = data[0]['lat'], data[0]['lon']
            cache[address_key] = (lat, lon)
        else:
            cache[address_key] = (None, None)

    except Exception:
        cache[address_key] = (None, None)

    # Save cache to disk after each new lookup
    save_cache()

    return cache[address_key]
