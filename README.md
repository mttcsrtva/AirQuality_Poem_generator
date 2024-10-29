# Air Quality Poetry Generator

An R&D project by mttcsr that automatically generates and vocalizes poetry based on air quality data, using GPT models and text-to-speech with Animalese-style effects.

## Overview

This experimental system takes air quality data and transforms it into emotional, context-aware poetry. It demonstrates how environmental data can be made more engaging through creative AI applications.

Key features:
- Generates poetry based on CAQI (Common Air Quality Index)
- Creates Animalese-style voice readings
- Real-time air quality data integration
- Location-aware content generation

## System Architecture

```
Air Quality Data → Poetry Generation → Voice Synthesis
[Google AQ API] → [GPT-4o-mini] → [OpenAI TTS + Effects]
```

### API Flow
1. **Air Quality Data Retrieval**
   - Endpoint: `airquality.googleapis.com/v1/currentConditions:lookup`
   - Returns: CAQI value, dominant pollutant, detailed pollutant data

2. **Poetry Generation**
   - Model: GPT-4o-mini
   - Input: Structured prompt with air quality data, location, and tone guidance
   - Output: 4-line poem

3. **Voice Synthesis**
   - OpenAI TTS with custom audio processing
   - Configurable parameters: pitch, speed, vibrato, distortion

## Integration Points

The system is designed for future integration into larger applications:
```python
# Core data flow
air_data = get_air_quality(location)
poem = generate_poem(air_data)
voice = generate_voice(poem)
```

Key configuration files:
- `config.json`: Prompt templates and model parameters
- `api.json`: API endpoints and regional settings

## Future Development

This R&D prototype demonstrates the potential for:
- Integration with existing air quality monitoring systems
- Multilingual support
- Custom voice effect profiles
- Real-time poetry generation based on sensor data

## Technical Requirements
- Python 3.8+
- OpenAI API key
- Google Air Quality API key
- Streamlit (for demo interface)

## Notes
This is a research prototype focused on demonstrating the concept of automated creative content generation from environmental data. The system is designed to be modular for easy integration into production environments.