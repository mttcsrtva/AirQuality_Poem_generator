# src/utils.py
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from typing import Dict, Optional

def get_coordinates(city_name: str) -> Optional[Dict[str, float]]:
    """
    Get coordinates for a city name using GeoPy
    
    Args:
        city_name (str): Name of the city
        
    Returns:
        dict: Dictionary containing latitude and longitude, or None if not found
    """
    try:
        geolocator = Nominatim(user_agent="air_quality_poems")
        location = geolocator.geocode(city_name)
        
        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        return None
        
    except GeocoderTimedOut:
        return None