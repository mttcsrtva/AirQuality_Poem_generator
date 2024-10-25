# streamlit_app.py
import streamlit as st
import os
import sys

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Now we can import from src
from src.api_client import AirQualityAPI
from src.poem_generator import PoemGenerator
from src.audio_processor import AudioProcessor
from src.utils import get_coordinates

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'api_keys_set' not in st.session_state:
        st.session_state.api_keys_set = False
    if 'air_quality_data' not in st.session_state:
        st.session_state.air_quality_data = None

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

def main():
    st.title("🌍 Air Quality Poem Generator")
    
    initialize_session_state()
    
    if not st.session_state.api_keys_set:
        set_api_keys()
        st.stop()
    
    # Location input
    location_type = st.radio(
        "Choose location input type:",
        ["City Name", "Coordinates"]
    )

    location = None
    if location_type == "City Name":
        city = st.text_input("Enter city name")
        if city:
            with st.spinner("Finding city coordinates..."):
                location = get_coordinates(city)
                if location:
                    st.success(f"Found coordinates: {location['latitude']:.4f}, {location['longitude']:.4f}")
                else:
                    st.error("Couldn't find coordinates for this city. Try entering coordinates directly.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=45.4642)  # Default to Milan
        with col2:
            longitude = st.number_input("Longitude", value=9.1900)
        location = {"latitude": latitude, "longitude": longitude}
    
    if location and st.button("Generate Poem"):
        try:
            # Initialize clients with API keys
            api_client = AirQualityAPI(st.session_state.google_key)
            poem_generator = PoemGenerator(st.session_state.openai_key)
            audio_processor = AudioProcessor(st.session_state.openai_key)
            
            # Get air quality data
            with st.spinner("Fetching air quality data..."):
                air_data = api_client.get_air_quality(location)
            
            # Generate poem
            with st.spinner("Generating poem..."):
                poem = poem_generator.generate(air_data)
                st.text_area("Generated Poem", poem, height=200)
            
            # Generate and process audio
            with st.spinner("Generating Animalese speech..."):
                audio = audio_processor.generate_animalese(poem)
                st.audio(audio, format='audio/wav')
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()