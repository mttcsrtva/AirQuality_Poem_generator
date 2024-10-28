# src/audio_processor.py
from openai import OpenAI
import numpy as np
from scipy import signal
import io
import soundfile as sf
from typing import Tuple, Dict

class AudioProcessor:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def generate_animalese(self, text: str, audio_params: Dict = None) -> bytes:
        """
        Generate Animalese-style audio from text with customizable parameters
        
        Args:
            text (str): Text to convert to speech
            audio_params (dict): Dictionary of audio parameters
                - pitch_shift (float): Semitones to shift pitch
                - vibrato_rate (float): Vibrato frequency in Hz
                - vibrato_depth (float): Vibrato intensity
                - distortion (float): Distortion amount
                - speed (float): Speech speed
            
        Returns:
            bytes: Processed audio data
        """
        # Default parameters
        default_params = {
            "pitch_shift": 7.2,
            "vibrato_rate": 10.0,
            "vibrato_depth": 0.5,
            "distortion": 1.7,
            "speed": 0.85
        }
        
        # Use provided parameters or defaults
        params = {**default_params, **(audio_params or {})}
        
        try:
            # Generate base audio using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text,
                speed=params["speed"]
            )
            
            # Load the audio data
            audio_data, sample_rate = sf.read(io.BytesIO(response.content))
            
            # Apply Animalese-style effects with custom parameters
            processed_audio = self._apply_effects(audio_data, sample_rate, params)
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            sf.write(output_buffer, processed_audio, sample_rate, format='WAV')
            return output_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to generate audio: {str(e)}")
    
    def _apply_effects(self, audio: np.ndarray, sample_rate: int, params: Dict) -> np.ndarray:
        """Apply Animalese-style effects to the audio with custom parameters"""
        
        # 1. Pitch shifting
        pitched = signal.resample(
            audio,
            int(len(audio) * 2**(-params["pitch_shift"]/12))
        )
        
        # 2. Add vibrato
        t = np.arange(len(pitched)) / sample_rate
        vibrato = params["vibrato_depth"] * np.sin(2 * np.pi * params["vibrato_rate"] * t)
        pitched_vibrato = pitched * (1 + vibrato[:len(pitched)])
        
        # 3. Add distortion
        distortion = np.clip(pitched_vibrato * params["distortion"], -0.8, 0.8)
        
        # 4. Normalize
        normalized = distortion / np.max(np.abs(distortion))
        
        return normalized