from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
import requests
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
ACTIVE_LOCATION_FILE = "active_location.json"

class LocationSelectRequest(BaseModel):
    name: str
    place_id: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

@router.get("/locations/search")
def search_locations(q: str):
    if not q:
        return []
    
    api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")
    if not api_key:
        print("Places API error: GOOGLE_GEOCODING_API_KEY not found")
        return []

    try:
        url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json"
        response = requests.get(
            url,
            params={
                "input": q,
                "types": "(cities)",
                "key": api_key
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("predictions", []):
            results.append({
                "name": item.get("description"),
                "place_id": item.get("place_id")
            })
        return results
        
    except requests.RequestException as e:
        print(f"Places API error: {e}")
        return []

@router.post("/locations/select")
def select_location(req: LocationSelectRequest):
    lat = req.lat
    lon = req.lon

    if req.place_id:
        api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")
        if not api_key:
            if lat is not None and lon is not None:
                print("Geocoding API key not found, using provided coordinates")
            else:
                raise HTTPException(status_code=500, detail="Geocoding API key not found and no coordinates provided")
        else:
            try:
                url = f"https://maps.googleapis.com/maps/api/geocode/json"
                response = requests.get(
                    url,
                    params={
                        "place_id": req.place_id,
                        "key": api_key
                    },
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "OK" and len(data.get("results", [])) > 0:
                    gc_loc = data["results"][0]["geometry"]["location"]
                    lat = gc_loc["lat"]
                    lon = gc_loc["lng"]
                elif lat is None or lon is None:
                    raise HTTPException(status_code=400, detail="Could not resolve coordinates for place and none provided")
                    
            except Exception as e:
                if lat is None or lon is None:
                    raise HTTPException(status_code=500, detail=f"Failed to resolve location: {e}")
                print(f"Failed to resolve location from place_id, using provided coordinates: {e}")

    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Either place_id or lat/lon must be provided")

    location_data = {
        "name": req.name,
        "lat": lat,
        "lon": lon
    }
        
    try:
        # Save to file
        with open(ACTIVE_LOCATION_FILE, "w") as f:
            json.dump(location_data, f)
            
        return {"message": "Location selected", "active_location": location_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save location: {e}")

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
