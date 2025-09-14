import requests

def get_lat_long(address):
    """This function takes an address as input and return the lat long 
       coordinates using OpenStreetMap's Nominatim API."""
    
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
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        else:
            print("No results found for address.")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None

# An example
address = "Exeter, UK"
lat, lon = get_lat_long(address)
print(f"Latitude: {lat}, Longitude: {lon}")