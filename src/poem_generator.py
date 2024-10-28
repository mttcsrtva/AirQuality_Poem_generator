# src/poem_generator.py
from openai import OpenAI
from typing import Dict, Any

class PoemGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate(self, air_data: Dict[str, Any], 
                system_prompt: str = None, 
                user_prompt_template: str = None) -> str:
        """
        Generate a poem based on air quality data
        """
        try:
            # Log input data without modifying anything
            print("\n=== Debug Info ===")
            print(f"CAQI: {air_data.get('caqi')}")
            print(f"Dominant Pollutant: {air_data.get('dominantPollutant')}")
            print(f"Category: {air_data.get('category')}")
            print(f"System Prompt Length: {len(system_prompt) if system_prompt else 0}")
            print(f"User Prompt Length: {len(user_prompt_template) if user_prompt_template else 0}")

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt_template}
                ],
                temperature=1.3,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in poem generation: {str(e)}")
            raise