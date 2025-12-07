# src/ingest.py
# WAQI AQI downloader using city name -> lat/lon auto-detection

import argparse
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

if not WAQI_TOKEN:
    raise ValueError("ERROR: WAQI_TOKEN not found in .env!")

# 1. Convert city name → latitude/longitude
def get_coordinates(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"City '{city_name}' not found!")

    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"]

# 2. Fetch AQI from WAQI using coordinates
def fetch_waqi(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

# 3. Save AQI data
def save_data(json_data, output="data/raw/waqi_latest.parquet"):
    Path(os.path.dirname(output)).mkdir(parents=True, exist_ok=True)

    if json_data["status"] != "ok":
        print("API Error:", json_data.get("data"))
        return

    data = json_data["data"]
    iaqi = data.get("iaqi", {})

    df = pd.DataFrame([{
        "aqi": data.get("aqi"),
        "pm25": iaqi.get("pm25", {}).get("v"),
        "pm10": iaqi.get("pm10", {}).get("v"),
        "no2": iaqi.get("no2", {}).get("v"),
        "o3": iaqi.get("o3", {}).get("v"),
        "co": iaqi.get("co", {}).get("v"),
        "time": data["time"]["s"]
    }])

    df.to_parquet(output, index=False)
    print("✔ Saved AQI:", output)
    print(df)

# 4. Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True)
    parser.add_argument("--output", default="data/raw/waqi_latest.parquet")
    args = parser.parse_args()

    city = args.city
    lat, lon, found_name = get_coordinates(city)
    print(f"✔ Found city '{found_name}': lat={lat}, lon={lon}")

    json_data = fetch_waqi(lat, lon)
    save_data(json_data, args.output)
