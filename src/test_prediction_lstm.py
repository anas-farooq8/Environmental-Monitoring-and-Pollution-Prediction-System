# scripts/test_prediction.py

import os
import requests
import json
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Load environment variables from .env file
load_dotenv()

# Environment variables
VISUAL_CROSSING_API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')
LOCATION = f"{LATITUDE},{LONGITUDE}"

# Model and scaler paths
FEATURE_SCALER_PATH = "../models/feature_scaler.joblib"
TARGET_SCALER_PATH = "../models/target_scaler.joblib"
MODEL_PATH = "../models/model.keras"

# AQI Classification Ranges
AQI_RANGES = [
    {"level": "Good", "so2": (0, 20), "no2": (0, 40), "pm10": (0, 20), "pm2_5": (0, 10), "o3": (0, 60), "co": (0, 4400)},
    {"level": "Fair", "so2": (20, 80), "no2": (40, 70), "pm10": (20, 50), "pm2_5": (10, 25), "o3": (60, 100), "co": (4400, 9400)},
    {"level": "Moderate", "so2": (80, 250), "no2": (70, 150), "pm10": (50, 100), "pm2_5": (25, 50), "o3": (100, 140), "co": (9400, 12400)},
    {"level": "Poor", "so2": (250, 350), "no2": (150, 200), "pm10": (100, 200), "pm2_5": (50, 75), "o3": (140, 180), "co": (12400, 15400)},
    {"level": "Very Poor", "so2": (350, float('inf')), "no2": (200, float('inf')), "pm10": (200, float('inf')), "pm2_5": (75, float('inf')), "o3": (180, float('inf')), "co": (15400, float('inf'))},
]

# Define targets
TARGETS = ['components.so2', 'components.no2', 'components.pm10', 'components.pm2_5', 'components.o3', 'components.co']

def fetch_weather_data(start_date, end_date):
    """
    Fetch historical weather data between start_date and end_date.
    Dates should be in 'YYYY-MM-DD' format.
    """
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/{start_date}/{end_date}?unitGroup=metric&key={VISUAL_CROSSING_API_KEY}&include=hours&elements=datetime,temp,dew,humidity,windspeed,windgust,winddir,pressure,solarenergy,cloudcover,solarradiation,uvindex'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f'Error fetching weather data: {e}')
        return None

def extract_past_24_hours(data, target_date, target_hour):
    """
    Extract the past 24 hours of data up to the target_date and target_hour.
    """
    # Combine hours from both days
    all_hours = []
    for day in data.get('days', []):
        for hour_data in day.get('hours', []):
            # Combine date and time
            datetime_str = f"{day['datetime']}T{hour_data['datetime']}"
            timestamp = pd.to_datetime(datetime_str)
            all_hours.append({**hour_data, 'timestamp': timestamp})
    
    # Sort all_hours by timestamp
    all_hours = sorted(all_hours, key=lambda x: x['timestamp'])
    
    # Convert to DataFrame
    df = pd.DataFrame(all_hours)
    
    # Convert target_date and target_hour to timestamp
    target_datetime_str = f"{target_date}T{target_hour:02d}:00:00"
    target_timestamp = pd.to_datetime(target_datetime_str)
    
    # Find the index where timestamp == target_timestamp
    target_index = df.index[df['timestamp'] == target_timestamp].tolist()
    if not target_index:
        print("Specified datetime not found in the fetched data.")
        return None
    target_index = target_index[0]
    
    # Extract the past 24 hours
    start_index = target_index - 23  # inclusive of target_index
    if start_index < 0:
        print("Not enough historical data to extract past 24 hours.")
        return None
    past_24_hours = df.iloc[start_index:target_index + 1]
    
    return past_24_hours

def preprocess_data(past_24_hours):
    """
    Preprocess the past 24 hours data:
    - Select required features
    - Scale features
    - Reshape for model input
    """
    required_features = ['temp', 'dew', 'humidity', 'windspeed', 'windgust', 'winddir', 'pressure', 'solarenergy']
    if not all(feature in past_24_hours.columns for feature in required_features):
        print("Missing required features in the data.")
        return None
    
    X = past_24_hours[required_features].values  # Shape: (24, 8)
    
    # Load scalers
    feature_scaler = joblib.load(FEATURE_SCALER_PATH)
    
    # Scale features
    X_scaled = feature_scaler.transform(X)  # Shape: (24, 8)
    
    # Reshape to (1, 24, 8)
    X_scaled = X_scaled.reshape(1, 24, 8)
    
    return X_scaled

def determine_aqi(pollutant_values):
    """
    Determine AQI level based on pollutant values.
    """
    for aqi in AQI_RANGES:
        if (aqi["so2"][0] <= pollutant_values["so2"] < aqi["so2"][1] and
            aqi["no2"][0] <= pollutant_values["no2"] < aqi["no2"][1] and
            aqi["pm10"][0] <= pollutant_values["pm10"] < aqi["pm10"][1] and
            aqi["pm2_5"][0] <= pollutant_values["pm2_5"] < aqi["pm2_5"][1] and
            aqi["o3"][0] <= pollutant_values["o3"] < aqi["o3"][1] and
            aqi["co"][0] <= pollutant_values["co"] < aqi["co"][1]):
            return aqi["level"]
    return "Very Poor"

def main():
    # User-specified date and hour
    # Example: Predict for December 13, 2024 at 15:00
    target_date = "2024-12-13"
    target_hour = 15  # 0-23
    
    # Fetch weather data for the target date and the previous date
    end_date = target_date
    start_date = pd.to_datetime(end_date) - pd.Timedelta(days=1)
    start_date = start_date.strftime("%Y-%m-%d")
    
    data = fetch_weather_data(start_date, end_date)
    if data is None:
        return
    
    # Extract past 24 hours
    past_24_hours = extract_past_24_hours(data, target_date, target_hour)
    if past_24_hours is None:
        return
    
    print("Past 24 Hours Data:")
    print(past_24_hours[['timestamp', 'temp', 'dew', 'humidity', 'windspeed', 'windgust', 'winddir', 'pressure', 'solarenergy']])
    
    # Preprocess data
    X_scaled = preprocess_data(past_24_hours)
    if X_scaled is None:
        return
    
    # Load the local model
    try:
        best_model = load_model(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model from {MODEL_PATH}: {e}")
        return
    
    # Make prediction
    y_pred_scaled = best_model.predict(X_scaled)
    
    # Inverse transform predictions
    target_scaler = joblib.load(TARGET_SCALER_PATH)
    y_pred = target_scaler.inverse_transform(y_pred_scaled)
    
    # Print predicted pollutant values
    pollutant_values = {
        TARGETS[i].split('.')[1]: y_pred[0][i] for i in range(len(TARGETS))
    }
    
    print("\nPredicted Pollutant Values:")
    for pollutant, value in pollutant_values.items():
        print(f"{pollutant.upper()}: {value:.2f} μg/m³")
    
    # Determine AQI
    aqi_level = determine_aqi(pollutant_values)
    print(f"\nAir Quality Index (AQI): {aqi_level}")

if __name__ == "__main__":
    main()
