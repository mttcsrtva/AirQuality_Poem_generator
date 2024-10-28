# streamlit_app.py
import streamlit as st
import os
import sys
import json
from datetime import datetime
from geopy.geocoders import Nominatim

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Now we can import from src
from src.api_client import AirQualityAPI
from src.poem_generator import PoemGenerator
from src.audio_processor import AudioProcessor
from src.utils import get_coordinates

def load_config():
    """Load configuration from config file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    if 'api_keys_set' not in st.session_state:
        st.session_state.api_keys_set = False
    if 'air_quality_data' not in st.session_state:
        st.session_state.air_quality_data = None
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = st.session_state.config['prompts']['system_prompt']
    if 'user_prompt' not in st.session_state:
        st.session_state.user_prompt = st.session_state.config['prompts']['user_prompt_template']

def set_api_keys():
    """Set API keys and update session state"""
    openai_key = st.text_input("OpenAI API Key", type="password")
    google_key = st.text_input("Google API Key", type="password")
    
    if st.button("Save API Keys"):
        if openai_key and google_key:
            st.session_state.openai_key = openai_key
            st.session_state.google_key = google_key
            st.session_state.api_keys_set = True
            st.success("API keys saved successfully!")
        else:
            st.error("Please enter both API keys")

def show_prompt_settings():
    """Show and handle prompt customization settings"""
    with st.expander("🎨 Customize Poem Generation", expanded=True):
        st.markdown("#### System Prompt")
        st.markdown("*This sets the overall style and personality of the poem generator*")
        system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.config['prompts']['system_prompt'],
            height=300,
            key="system_prompt_input"
        )
        
        st.markdown("#### User Prompt Template")
        st.markdown("*This is the template for generating each poem. Use {city}, {current_date}, {caqi}, and {dominant_pollutant} as placeholders*")
        user_prompt = st.text_area(
            "User Prompt Template",
            value=st.session_state.config['prompts']['user_prompt_template'],
            height=300,
            key="user_prompt_input"
        )
        
        if st.button("Reset to Defaults"):
            st.session_state.system_prompt = st.session_state.config['prompts']['system_prompt']
            st.session_state.user_prompt = st.session_state.config['prompts']['user_prompt_template']
            st.rerun()
            
        return system_prompt, user_prompt

def show_audio_settings():
    """Show and handle audio customization settings"""
    with st.expander("🎵 Customize Audio Effects", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Pitch and Speed")
            pitch_shift = st.slider(
                "Pitch Shift (semitones)",
                min_value=0.0,
                max_value=12.0,
                value=7.2,
                help="Higher values make the voice higher-pitched"
            )
            
            speed = st.slider(
                "Speech Speed",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                help="Adjusts how fast the text is spoken"
            )
        
        with col2:
            st.markdown("#### Voice Effects")
            vibrato_rate = st.slider(
                "Vibrato Rate (Hz)",
                min_value=0.0,
                max_value=15.0,
                value=10.0,
                help="How fast the vibrato oscillates"
            )
            
            vibrato_depth = st.slider(
                "Vibrato Depth",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                help="How pronounced the vibrato effect is"
            )
            
            distortion = st.slider(
                "Distortion Amount",
                min_value=1.0,
                max_value=2.0,
                value=1.7,
                help="Adds fuzzy distortion to the voice"
            )
        
        return {
            "pitch_shift": pitch_shift,
            "speed": speed,
            "vibrato_rate": vibrato_rate,
            "vibrato_depth": vibrato_depth,
            "distortion": distortion
        }

def get_caqi_description(caqi):
    """Get description and emoji based on CAQI value"""
    if caqi <= 25:
        return "Very low air pollution", "💚"
    elif caqi <= 50:
        return "Low air pollution", "💛"
    elif caqi <= 75:
        return "Medium air pollution", "🟧"
    elif caqi <= 100:
        return "High air pollution", "❤️"
    else:
        return "Very high air pollution", "💔"

def get_air_quality_info(caqi):
    """Get air quality description and tone based on CAQI value"""
    if caqi <= 25:
        return "OTTIMA", "molto allegro e gioioso"
    elif caqi <= 50:
        return "BUONA", "sereno e positivo"
    elif caqi <= 75:
        return "PREOCCUPANTE", "preoccupato e cauto"
    elif caqi <= 100:
        return "CATTIVA", "molto preoccupato"
    else:
        return "PESSIMA", "allarmato e pessimista"

def main():
    st.title("🌍 Air Quality Poem Generator")
    
    initialize_session_state()
    
    if not st.session_state.api_keys_set:
        set_api_keys()
        st.stop()
        
    st.markdown("### 1. Configure Generation Settings")
    system_prompt, user_prompt = show_prompt_settings()
    audio_params = show_audio_settings()
    
    st.markdown("### 2. Choose Location")
    location_type = st.radio(
        "Choose location input type:",
        ["City Name", "Coordinates"]
    )

    location = None
    if location_type == "City Name":
        city = st.text_input("Enter city name")
        if city:
            with st.spinner("Finding coordinates..."):
                location = get_coordinates(city)
                if location:
                    st.success(f"Found coordinates: {location['latitude']:.4f}, {location['longitude']:.4f}")
                else:
                    st.error("Couldn't find coordinates for this city. Try entering coordinates directly.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=45.4642)
        with col2:
            longitude = st.number_input("Longitude", value=9.1900)
        location = {"latitude": latitude, "longitude": longitude}
    
    st.markdown("### 3. Generate")
    if location and st.button("Generate Poem", type="primary"):
        try:
            api_client = AirQualityAPI(st.session_state.google_key)
            poem_generator = PoemGenerator(st.session_state.openai_key)
            audio_processor = AudioProcessor(st.session_state.openai_key)
            
            with st.spinner("Fetching air quality data..."):
                air_data = api_client.get_air_quality(location)
                st.session_state.air_quality_data = air_data
            
            geolocator = Nominatim(user_agent="air_quality_poems")
            if location_type == "City Name":
                city_name = city
            else:
                location_info = geolocator.reverse(f"{latitude}, {longitude}")
                city_name = location_info.raw.get('address', {}).get('city', 'Unknown City')
            
            caqi = air_data["caqi"]
            quality_text, quality_emoji = get_caqi_description(caqi)
            
            st.markdown("#### Air Quality Status")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("CAQI", f"{caqi:.1f}")
                st.markdown(f"Status: {quality_text} {quality_emoji}")
            with col2:
                st.markdown(f"**Location:** {city_name}")
                st.markdown(f"**Main Pollutant:** {air_data['dominantPollutant']}")
            
            current_date = datetime.now().strftime("%d %B %Y")
            with st.spinner("Generating poem..."):
                # Debug section
                with st.expander("🔍 Debug: Prompt Data", expanded=False):
                    st.json({
                        "Input Data": {
                            "city": city_name,
                            "current_date": current_date,
                            "caqi": caqi,
                            "dominant_pollutant": air_data["dominantPollutant"]
                        }
                    })
                    
                    air_quality_description, tone_description = get_air_quality_info(caqi)
                    
                    formatted_prompt = user_prompt.format(
                        city=city_name,
                        current_date=current_date,
                        caqi=caqi,
                        dominant_pollutant=air_data["dominantPollutant"],
                        air_quality_description=air_quality_description,
                        tone_description=tone_description
                    )
                    
                    st.markdown("#### System Prompt")
                    st.text(system_prompt)
                    
                    st.markdown("#### Formatted User Prompt")
                    st.text(formatted_prompt)
                
                st.session_state.current_poem = poem_generator.generate(
                    air_data,
                    system_prompt=system_prompt,
                    user_prompt_template=formatted_prompt
                )
            
            st.markdown("#### Generated Poem")
            st.text_area("Poem Text", st.session_state.current_poem, height=200)
            
            with st.spinner("Generating Animalese speech..."):
                audio = audio_processor.generate_animalese(
                    st.session_state.current_poem,
                    audio_params=audio_params
                )
                st.audio(audio, format='audio/wav')
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Regenerate Audio"):
                    with st.spinner("Regenerating audio..."):
                        new_audio = audio_processor.generate_animalese(
                            st.session_state.current_poem,
                            audio_params=audio_params
                        )
                        st.audio(new_audio, format='audio/wav')
            
            with col2:
                if st.button("🎲 New Poem"):
                    del st.session_state.current_poem
                    st.rerun()
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    st.markdown("---")
    st.markdown("""
    ### About
    This app generates poems inspired by air quality data, combining environmental awareness with poetry.
    - Data from Google Air Quality API
    - Poems generated using OpenAI GPT
    - Voice generation using OpenAI TTS with Animalese-style effects
    """)

if __name__ == "__main__":
    main()