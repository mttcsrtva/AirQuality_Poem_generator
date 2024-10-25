# src/poem_generator.py
from openai import OpenAI
from typing import Dict, Any

class PoemGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def generate(self, air_data: Dict[str, Any]) -> str:
        """
        Generate a poem based on air quality data
        
        Args:
            air_data (dict): Processed air quality data
            
        Returns:
            str: Generated poem
        """
        # Create a prompt that includes the air quality data in a structured way
        aqi = air_data["aqi"]
        dominant_pollutant = air_data["dominantPollutant"]
        
        prompt = f"""Create a short, playful poem about the current air quality.
        The AQI is {aqi} and the dominant pollutant is {dominant_pollutant}.
        
        Make the poem:
        1. Whimsical and light-hearted like Animal Crossing
        2. 4-6 lines long
        3. Include a simple rhyme scheme
        4. Mention the air quality in a creative way
        
        If the AQI is good (0-50), make it very cheerful.
        If the AQI is moderate (51-100), make it optimistic but cautious.
        If the AQI is unhealthy (>100), make it concerned but still playful."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cheerful poet in the style of Animal Crossing characters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate poem: {str(e)}")