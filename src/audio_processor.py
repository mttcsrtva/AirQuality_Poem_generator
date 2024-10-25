# src/audio_processor.py
from openai import OpenAI
import numpy as np
from scipy import signal
import io
import soundfile as sf
from typing import Tuple

class AudioProcessor:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def generate_animalese(self, text: str) -> bytes:
        """
        Generate Animalese-style audio from text
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            bytes: Processed audio data
        """
        try:
            # Generate base audio using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text,
                speed=1.2  # Slightly faster than normal
            )
            
            # Load the audio data
            audio_data, sample_rate = sf.read(io.BytesIO(response.content))
            
            # Apply Animalese-style effects
            processed_audio = self._apply_effects(audio_data, sample_rate)
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            sf.write(output_buffer, processed_audio, sample_rate, format='WAV')
            return output_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to generate audio: {str(e)}")
    
    def _apply_effects(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply Animalese-style effects to the audio
        
        Args:
            audio (np.ndarray): Input audio data
            sample_rate (int): Sample rate of the audio
            
        Returns:
            np.ndarray: Processed audio data
        """
        # 1. Pitch shifting (up by 6 semitones)
        pitch_shift = 6
        pitched = signal.resample(
            audio,
            int(len(audio) * 2**(-pitch_shift/12))
        )
        
        # 2. Add slight vibrato
        t = np.arange(len(pitched)) / sample_rate
        vibrato_rate = 8.0  # Hz
        vibrato_depth = 0.3
        vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        pitched_vibrato = pitched * (1 + vibrato[:len(pitched)])
        
        # 3. Add subtle distortion
        distortion = np.clip(pitched_vibrato * 1.2, -0.8, 0.8)
        
        # 4. Normalize
        normalized = distortion / np.max(np.abs(distortion))
        
        return normalized