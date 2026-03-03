# Static list of cities for the prototype
# In a real app, this would be a database or external API

CITIES = [
    {"id": "loc_1", "name": "Kochi, Kerala", "lat": 9.9312, "lon": 76.2673},
    {"id": "loc_2", "name": "Kozhikode, Kerala", "lat": 11.2588, "lon": 75.7804},
    {"id": "loc_3", "name": "Thiruvananthapuram, Kerala", "lat": 8.5241, "lon": 76.9366},
    {"id": "loc_4", "name": "Thrissur, Kerala", "lat": 10.5276, "lon": 76.2144},
    {"id": "loc_5", "name": "Kottayam, Kerala", "lat": 9.5916, "lon": 76.5222},
    {"id": "loc_6", "name": "Alappuzha, Kerala", "lat": 9.4981, "lon": 76.3388},
    {"id": "loc_7", "name": "Palakkad, Kerala", "lat": 10.7867, "lon": 76.6548},
    {"id": "loc_8", "name": "Malappuram, Kerala", "lat": 11.0510, "lon": 76.0711},
    {"id": "loc_9", "name": "Kannur, Kerala", "lat": 11.8745, "lon": 75.3704},
    {"id": "loc_10", "name": "Kollam, Kerala", "lat": 8.8932, "lon": 76.6141},
    {"id": "loc_11", "name": "Munnar, Kerala", "lat": 10.0889, "lon": 77.0595},
    {"id": "loc_12", "name": "Waynad, Kerala", "lat": 11.6854, "lon": 76.1320},
    {"id": "loc_13", "name": "Idukki, Kerala", "lat": 9.8494, "lon": 76.9082},
    {"id": "loc_14", "name": "Kasargod, Kerala", "lat": 12.5102, "lon": 74.9852},
    {"id": "loc_15", "name": "Pathanamthitta, Kerala", "lat": 9.2648, "lon": 76.7870}
]

def search_cities(query: str):
    query = query.lower()
    return [city for city in CITIES if query in city["name"].lower()]

def get_city_by_id(city_id: str):
    for city in CITIES:
        if city["id"] == city_id:
            return city
    return None
