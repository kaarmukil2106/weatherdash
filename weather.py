import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import pytz
import json

def get_ip_location():
    """Fallback method to get location from IP address"""
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            return data.get('latitude'), data.get('longitude')
    except:
        return None, None

def get_weather(lat, lon):
    api_key = "06c921750b9a82d8f5d1294e1586276f"
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    
    try:
        response = requests.get(api_url).json()
        
        if response.get('cod') != 200:
            return None
        
        timezone_offset = response.get('timezone', 0)
        
        sunrise_utc = datetime.utcfromtimestamp(response['sys']['sunrise'])
        sunset_utc = datetime.utcfromtimestamp(response['sys']['sunset'])
        
        sunrise_local = sunrise_utc + timedelta(seconds=timezone_offset)
        sunset_local = sunset_utc + timedelta(seconds=timezone_offset)
        
        return {
            "condition": response['weather'][0]['main'],
            "description": response['weather'][0]['description'].capitalize(),
            "temp": int(response['main']['temp'] - 273.15),
            "feels_like": int(response['main']['feels_like'] - 273.15),
            "min_temp": int(response['main']['temp_min'] - 273.15),
            "max_temp": int(response['main']['temp_max'] - 273.15),
            "pressure": response['main']['pressure'],
            "humidity": response['main']['humidity'],
            "wind": response['wind']['speed'],
            "sunrise": sunrise_local.strftime('%I:%M %p'),
            "sunset": sunset_local.strftime('%I:%M %p'),
            "location": response['name'],
            "country": response['sys']['country']
        }
    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Weather App",
        page_icon="🌤️",
        layout="centered"
    )
    
    st.markdown("""
        <style>
        .stApp {
            max-width: 800px;
            margin: 0 auto;
        }
        .weather-card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🌤️ Real-Time Weather App")
    st.markdown("### Get current weather information for your location")
    
    # Initialize session state
    if 'coordinates' not in st.session_state:
        st.session_state.coordinates = None
        st.session_state.location_method = None

    # Manual location input option
    location_method = st.radio(
        "Choose location method:",
        ["Automatic Detection", "Manual Input"],
        key="location_choice"
    )

    if location_method == "Manual Input":
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=0.0, min_value=-90.0, max_value=90.0, step=0.000001)
        with col2:
            lon = st.number_input("Longitude", value=0.0, min_value=-180.0, max_value=180.0, step=0.000001)
        if st.button("Use These Coordinates"):
            st.session_state.coordinates = (lat, lon)
            st.session_state.location_method = "manual"

    elif location_method == "Automatic Detection":
        # Try browser geolocation
        loc = st.components.v1.html(
            """
            <div id="location"></div>
            <script>
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        document.getElementById('location').innerHTML = 
                            position.coords.latitude + ',' + position.coords.longitude;
                    },
                    function(error) {
                        document.getElementById('location').innerHTML = 'error';
                        console.error("Geolocation error:", error);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0
                    }
                );
            } else {
                document.getElementById('location').innerHTML = 'error';
            }
            </script>
            """,
            height=0,
        )

        if loc and loc != 'error':
            try:
                lat, lon = map(float, loc.split(','))
                st.session_state.coordinates = (lat, lon)
                st.session_state.location_method = "browser"
            except:
                # Fallback to IP-based location
                if st.session_state.location_method != "ip":
                    lat, lon = get_ip_location()
                    if lat and lon:
                        st.session_state.coordinates = (lat, lon)
                        st.session_state.location_method = "ip"
                        st.info("Using IP-based location as fallback.")
                    else:
                        st.error("Unable to detect location automatically. Please try manual input.")

    # Display weather information if coordinates are available
    if st.session_state.coordinates:
        lat, lon = st.session_state.coordinates
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.map(data=[{"lat": lat, "lon": lon}], zoom=12)
        
        weather_info = get_weather(lat, lon)
        
        if weather_info:
            with col2:
                st.markdown(f"### 📍 {weather_info['location']}, {weather_info['country']}")
                st.markdown(f"### 🌡️ {weather_info['temp']}°C")
                st.markdown(f"_{weather_info['description']}_")
                st.markdown(f"Feels like: {weather_info['feels_like']}°C")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Temperature")
                st.write(f"Current: {weather_info['temp']}°C")
                st.write(f"Min: {weather_info['min_temp']}°C")
                st.write(f"Max: {weather_info['max_temp']}°C")
            
            with col2:
                st.markdown("### Conditions")
                st.write(f"Pressure: {weather_info['pressure']} hPa")
                st.write(f"Humidity: {weather_info['humidity']}%")
                st.write(f"Wind: {weather_info['wind']} m/s")
            
            with col3:
                st.markdown("### Sun Times")
                st.write(f"Sunrise: {weather_info['sunrise']}")
                st.write(f"Sunset: {weather_info['sunset']}")
            
            if st.button("🔄 Refresh Weather"):
                st.experimental_rerun()
        else:
            st.error("Unable to fetch weather data. Please try again later.")
    
    st.markdown("---")
    st.markdown("Made with ❤️ by lav")

if __name__ == "__main__":
    main()