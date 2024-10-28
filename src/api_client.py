# src/api_client.py
import requests
import json
from typing import Dict, Any

class AirQualityAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://airquality.googleapis.com/v1/currentConditions:lookup"
    
    def get_air_quality(self, location: Dict[str, float], city: str = "milano") -> Dict[str, Any]:
        payload = {
            "location": {
                "latitude": float(location["latitude"]),
                "longitude": float(location["longitude"])
            },
            "universalAqi": True,
            "extraComputations": [
                "LOCAL_AQI",
                "DOMINANT_POLLUTANT_CONCENTRATION",
                "POLLUTANT_CONCENTRATION"
            ],
            "customLocalAqis": [
                {
                    "aqi": "caqi",
                    "regionCode": "IT"
                }
            ],
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Pretty print the full response
            print("\nFull API Response:")
            print(json.dumps(data, indent=2))
            
            # Also specifically print pollutants
            print("\nPollutants details:")
            for pollutant in data.get("pollutants", []):
                print(f"{pollutant.get('displayName', 'Unknown')}: "
                      f"{pollutant.get('concentration', {}).get('value', 'N/A')} "
                      f"{pollutant.get('concentration', {}).get('units', 'N/A')}")
            
            caqi_index = next((idx for idx in data.get("indexes", []) 
                             if idx.get("code") == "caqi"), None)
            
            if not caqi_index:
                raise Exception("CAQI data not found in response")
            
            return {
                "caqi": caqi_index.get("aqi", 0),
                "dominantPollutant": caqi_index.get("dominantPollutant", "Unknown"),
                "category": caqi_index.get("category", "Unknown"),
                "color": caqi_index.get("color", {}),
                "pollutants": {
                    p["displayName"]: {
                        "concentration": p["concentration"]["value"],
                        "unit": p["concentration"]["units"]
                    } for p in data.get("pollutants", [])
                }
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Full error: {str(e)}")
            raise Exception(f"Failed to fetch air quality data: {str(e)}")