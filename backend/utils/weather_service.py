import requests
import os

# Using the key provided from env var
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_realtime_weather(lat: float, lon: float):
    """
    Fetches current weather data for given coordinates.
    Returns: { "temperature": 25.0, "humidity": 60, "rainfall": 0.0 }
    """
    try:
        url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
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
    try:
        url = f"{BASE_URL}/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
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
