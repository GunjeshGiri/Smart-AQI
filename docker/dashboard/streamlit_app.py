import streamlit as st
import requests
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import folium
from streamlit_folium import st_folium

# Load token
load_dotenv()
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

# --------------------------
# Helper: City -> lat/lon
# --------------------------
def get_coordinates(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}
    r = requests.get(url, params=params)

    if r.status_code != 200:
        return None

    data = r.json()
    if "results" not in data or len(data["results"]) == 0:
        return None

    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"]

# --------------------------
# Helper: Fetch AQI from WAQI
# --------------------------
def fetch_waqi(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
    r = requests.get(url)

    if r.status_code != 200:
        return None
    return r.json()

# --------------------------
# Session State Initialization
# --------------------------
if "aqi_data" not in st.session_state:
    st.session_state.aqi_data = None

if "city_name" not in st.session_state:
    st.session_state.city_name = None

if "latlon" not in st.session_state:
    st.session_state.latlon = None

# --------------------------
# STREAMLIT UI
# --------------------------
st.set_page_config(layout="wide")
st.title("🌍 Smart AQI Dashboard (Stable Version)")

city_input = st.text_input("Enter a city name:", "Delhi")

if st.button("Get AQI"):
    with st.spinner("Fetching AQI..."):

        coords = get_coordinates(city_input)
        if not coords:
            st.error("City not found. Try again.")
        else:
            lat, lon, real_name = coords

            data = fetch_waqi(lat, lon)
            if not data or data.get("status") != "ok":
                st.error("AQI API error from WAQI")
            else:
                st.session_state.city_name = real_name
                st.session_state.latlon = (lat, lon)
                st.session_state.aqi_data = data["data"]

# --------------------------
# Display AQI (Persistent)
# --------------------------
if st.session_state.aqi_data:

    aqi_data = st.session_state.aqi_data
    iaqi = aqi_data.get("iaqi", {})

    # Table Data
    table = {
        "City": st.session_state.city_name,
        "AQI": aqi_data.get("aqi"),
        "PM2.5": iaqi.get("pm25", {}).get("v"),
        "PM10": iaqi.get("pm10", {}).get("v"),
        "NO₂": iaqi.get("no2", {}).get("v"),
        "O₃": iaqi.get("o3", {}).get("v"),
        "CO": iaqi.get("co", {}).get("v"),
        "Updated": aqi_data["time"]["s"]
    }

    st.subheader(f"📡 AQI for {st.session_state.city_name}")
    st.dataframe(pd.DataFrame([table]), use_container_width=True)

    # --------------------------
    # Big Red Circle Map
    # --------------------------
    st.subheader("🗺 City AQI Area Map")

    lat, lon = st.session_state.latlon

    m = folium.Map(location=[lat, lon], zoom_start=11)

    # Big red circle for entire city
    folium.Circle(
        location=[lat, lon],
        radius=10000,  # adjust for coverage
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.35,
        popup=f"AQI: {table['AQI']}"
    ).add_to(m)

    # Optional: also show center point
    folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        color="darkred",
        fill=True,
        fill_color="darkred"
    ).add_to(m)

    st_folium(m, width=750, height=500)


else:
    st.info("Search for a city to see AQI data.")
