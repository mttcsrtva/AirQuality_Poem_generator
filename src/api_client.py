# src/api_client.py
import requests
from typing import Dict, Any

class AirQualityAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://airquality.googleapis.com/v1"
    
    def get_air_quality(self, location: Dict[str, float]) -> Dict[str, Any]:
        """
        Get air quality data for a specific location
        
        Args:
            location (dict): Dictionary containing latitude and longitude
            
        Returns:
            dict: Processed air quality data
        """
        endpoint = f"{self.base_url}/currentConditions:lookup"
        
        payload = {
            "location": {
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            },
            "universalAqi": False,
            "extraComputations": [
                "LOCAL_AQI",
                "DOMINANT_POLLUTANT_CONCENTRATION",
                "POLLUTANT_CONCENTRATION"
            ]
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                params={"key": self.api_key}
            )
            response.raise_for_status()
            data = response.json()
            
            # Process and structure the response
            return {
                "aqi": data["indexes"][0]["aqi"],
                "dominantPollutant": data["indexes"][0].get("dominantPollutant", "Unknown"),
                "pollutants": {
                    p["displayName"]: {
                        "concentration": p["concentration"]["value"],
                        "unit": p["concentration"]["units"]
                    } for p in data["pollutants"]
                }
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch air quality data: {str(e)}")