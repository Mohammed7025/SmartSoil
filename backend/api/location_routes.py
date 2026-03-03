from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
import requests
from typing import List

router = APIRouter()
ACTIVE_LOCATION_FILE = "active_location.json"

# Use the key provided from env
API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"

class LocationSelectRequest(BaseModel):
    name: str
    lat: float
    lon: float

@router.get("/locations/search")
def search_locations(q: str):
    if not q:
        return []
    
    try:
        response = requests.get(
            GEO_URL,
            params={
                "q": q,
                "limit": 10,
                "appid": API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data:
            # Format: City, State, Country
            parts = [item.get("name")]
            if "state" in item:
                parts.append(item["state"])
            if "country" in item:
                parts.append(item["country"])
            
            display_name = ", ".join(parts)
            
            results.append({
                "name": display_name,
                "lat": item["lat"],
                "lon": item["lon"]
            })
        return results
        
    except requests.RequestException as e:
        print(f"Geocoding API error: {e}")
        return []

@router.post("/locations/select")
def select_location(req: LocationSelectRequest):
    data = {
        "name": req.name,
        "lat": req.lat,
        "lon": req.lon
    }
    
    # Save to file
    try:
        with open(ACTIVE_LOCATION_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save location: {e}")
    
    return {"message": "Location selected", "active_location": data}

@router.get("/locations/active")
def get_active_location():
    if os.path.exists(ACTIVE_LOCATION_FILE):
        try:
            with open(ACTIVE_LOCATION_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    # Default fallback
    return {"name": "Kochi, Kerala (Default)", "lat": 9.9312, "lon": 76.2673}
