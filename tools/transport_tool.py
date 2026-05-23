import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTE_API_KEY")


def get_transport_info(origin, destination):

    if not API_KEY:
        return {
            "error": "MISSING_API_KEY"
        }

    # Geocoding function
    def get_coordinates(place):

        url = "https://api.openrouteservice.org/geocode/search"

        params = {
            "api_key": API_KEY,
            "text": place,
            "size": 1
        }

        response = requests.get(url, params=params)

        data = response.json()

        features = data.get("features")

        if not features:
            return None

        coords = features[0]["geometry"]["coordinates"]

        return coords

    origin_coords = get_coordinates(origin)
    destination_coords = get_coordinates(destination)

    if not origin_coords or not destination_coords:
        return {
            "error": "LOCATION_NOT_FOUND"
        }

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            origin_coords,
            destination_coords
        ]
    }

    response = requests.post(
        url,
        json=body,
        headers=headers
    )

    data = response.json()

    if "routes" not in data:
        return {
            "error": "NO_ROUTE_FOUND",
            "response": data
        }

    summary = data["routes"][0]["summary"]

    distance_km = round(summary["distance"] / 1000, 2)

    duration_min = round(summary["duration"] / 60, 2)

    return {
        "origin": origin,
        "destination": destination,
        "distance_km": distance_km,
        "duration_minutes": duration_min
    }