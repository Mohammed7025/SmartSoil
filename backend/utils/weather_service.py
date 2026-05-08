import requests
import os

# Using the key provided from env var
BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_realtime_weather(lat: float, lon: float):
    """
    Fetches current weather data for given coordinates.
    Returns: { "temperature": 25.0, "humidity": 60, "rainfall": 0.0 }
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Weather API Error: OPENWEATHER_API_KEY not found in environment")
        return None

    try:
        url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            main = data.get("main", {})
            rain = data.get("rain", {})
            
            return {
                "temperature": main.get("temp", 0.0),
                "humidity": main.get("humidity", 0.0),
                "rainfall": rain.get("1h", 0.0), # Rainfall in last 1 hour
                "description": data.get("weather", [{}])[0].get("description", "")
            }
        else:
            print(f"Weather API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Weather Fetch Exception: {e}")
        return None

def get_forecast_rainfall(lat: float, lon: float):
    """
    Fetches 5-day forecast to estimate upcoming rainfall.
    Useful for Irrigation prediction.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return 0.0

    try:
        url = f"{BASE_URL}/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            list_data = data.get("list", [])
            
            # Sum rainfall for next 24 hours (8 * 3-hour blocks)
            total_rain_24h = 0.0
            for item in list_data[:8]:
                rain = item.get("rain", {})
                total_rain_24h += rain.get("3h", 0.0)
                
            return total_rain_24h
        else:
            return 0.0
            
    except Exception as e:
        print(f"Forecast Fetch Exception: {e}")
        return 0.0

import time

# Basic memory cache for weather requests
_weather_cache = {}
CACHE_TTL = 86400  # 24 hours

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4, 
    "may": 5, "june": 6, "july": 7, "august": 8, 
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, 
    "jun": 6, "jul": 7, "aug": 8, 
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def get_coordinates(location: str):
    api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")
    if not api_key:
        print("Geocoding Error: GOOGLE_GEOCODING_API_KEY not found in env")
        return None, None
        
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "OK" and len(data.get("results", [])) > 0:
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except Exception as e:
        print(f"Geocoding exception: {e}")
    return None, None

def get_monthly_weather(location: str, month_str: str):
    """
    Fetches climatology data (averages) for a specific location and month.
    """
    cache_key = f"{location.lower()}_{month_str.lower()}"
    current_time = time.time()
    
    # Check cache
    if cache_key in _weather_cache:
        cached_data, timestamp = _weather_cache[cache_key]
        if current_time - timestamp < CACHE_TTL:
            return cached_data
            
    lat, lon = get_coordinates(location)
    if lat is None or lon is None:
        print(f"Could not get coordinates for location: {location}")
        return None

    month_number = MONTH_MAP.get(month_str.lower(), 1)
    
    try:
        # NASA Climatology API
        # Using PRECTOTCORR as it's the corrected version of PRECTOT in newer NASA POWER versions
        nasa_url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,RH2M,PRECTOTCORR&community=RE&longitude={lon}&latitude={lat}&format=JSON"
        response = requests.get(nasa_url)
        data = response.json()
        
        if "properties" in data and "parameter" in data["properties"]:
            params = data["properties"]["parameter"]
            # Climatology endpoint typically returns months by index '1', '2', ..., '12' for monthly averages
            month_key = str(month_number)
            
            # Fallback if properties use two-digit strings
            if month_key not in params.get("T2M", {}):
                month_key = str(month_number).zfill(2)
                
            # Fallback if properties use JAN, FEB strings
            if month_key not in params.get("T2M", {}) and month_number <= 12:
                month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
                month_key = month_names[month_number - 1]
                
            temp = params.get("T2M", {}).get(month_key, 25.0)
            hum = params.get("RH2M", {}).get(month_key, 60.0)
            rain_daily = params.get("PRECTOTCORR", {}).get(month_key, 0.0)
            
            # NASA PRECTOTCORR in climatology is usually mm/day. 
            # Multiply by days in month to get total monthly rainfall.
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            total_rain = rain_daily * days_in_month[month_number - 1]
            
            result = {
                "temperature": float(temp),
                "humidity": float(hum),
                "rainfall": float(total_rain)
            }
            
            # Cache the result
            _weather_cache[cache_key] = (result, current_time)
            return result
            
    except Exception as e:
        print(f"NASA POWER exception: {e}")
        
    return None
