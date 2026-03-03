from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.weather_service import get_realtime_weather, get_forecast_rainfall
from typing import Optional
import json
import os

router = APIRouter()
ACTIVE_LOCATION_FILE = "active_location.json"

class WeatherRequest(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None

@router.post("/weather/current")
async def get_current_weather(request: WeatherRequest):
    lat = request.lat
    lon = request.lon

    # If coords not provided, load from active location file
    if lat is None or lon is None:
        if os.path.exists(ACTIVE_LOCATION_FILE):
             try:
                with open(ACTIVE_LOCATION_FILE, "r") as f:
                    data = json.load(f)
                    lat = data["lat"]
                    lon = data["lon"]
             except:
                 pass
    
    # Fallback to default (Kochi) if still None
    if lat is None or lon is None:
        lat = 9.9312
        lon = 76.2673

    # Fetch real-time weather
    data = get_realtime_weather(lat, lon)
    if not data:
        raise HTTPException(status_code=503, detail="Weather service unavailable or invalid API key")
    
    # Enrich with forecast
    forecast_rain = get_forecast_rainfall(lat, lon)
    data["rainfall_forecast_24h"] = forecast_rain
    
    return data
