# src/poem_generator.py
from openai import OpenAI
from typing import Dict, Any
import json
import os

class PoemGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration from config file"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate(self, air_data: Dict[str, Any], 
                system_prompt: str = None, 
                user_prompt_template: str = None) -> str:
        """
        Generate a poem based on air quality data and context
        
        Args:
            air_data (dict): Processed air quality data
            system_prompt (str): Custom system prompt
            user_prompt_template (str): Custom user prompt template
            
        Returns:
            str: Generated poem
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": system_prompt or self.config['prompts']['system_prompt']},
                    {"role": "user", "content": user_prompt_template or self.config['prompts']['user_prompt_template']}
                ],
                temperature=self.config['openai']['temperature'],
                max_tokens=self.config['openai']['max_tokens']
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate poem: {str(e)}")