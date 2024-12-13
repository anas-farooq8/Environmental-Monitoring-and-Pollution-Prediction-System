# app/app.py

from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime

app = Flask(__name__)

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

# Load scalers
if not os.path.exists(FEATURE_SCALER_PATH) or not os.path.exists(TARGET_SCALER_PATH):
    raise FileNotFoundError("Scaler files not found. Ensure they are present in the 'models' directory.")

feature_scaler = joblib.load(FEATURE_SCALER_PATH)
target_scaler = joblib.load(TARGET_SCALER_PATH)

# Load the local model
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model directory not found. Ensure the model is saved in the 'MLModel' directory.")

try:
    model = load_model(MODEL_PATH)
except Exception as e:
    print(f"Error loading model from {MODEL_PATH}: {e}")
    model = None

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
    
    # Scale features
    X_scaled = feature_scaler.transform(X)  # Shape: (24, 8)
    
    # Reshape to (1, 24, 8)
    X_scaled = X_scaled.reshape(1, 24, 8)
    
    return X_scaled

def determine_aqi(pollutant_values):
    """
    Determine AQI level based on pollutant values.
    Assigns AQI based on the highest pollutant concentration.
    """
    max_aqi_level = "Good"
    highest_aqi_index = -1  # Initialize to lowest AQI level
    
    # Iterate over each pollutant and determine its AQI level
    for pollutant, value in pollutant_values.items():
        for idx, aqi in enumerate(AQI_RANGES):
            lower, upper = aqi[pollutant]
            if lower <= value < upper:
                if idx > highest_aqi_index:
                    highest_aqi_index = idx
                    max_aqi_level = aqi["level"]
                break
            elif value >= aqi[pollutant][1]:
                continue
    
    return max_aqi_level

@app.route('/', methods=['GET', 'POST'])
def index():
    current_date = datetime.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        target_date = request.form.get('date')
        target_hour = request.form.get('hour')
        
        # Validate and convert hour to integer
        try:
            target_hour = int(target_hour)
        except ValueError:
            return render_template('index.html', error="Invalid hour value. Please enter an integer between 0 and 23.", current_date=current_date)
        
        # Validate date format
        try:
            prediction_datetime = pd.to_datetime(target_date)
        except ValueError:
            return render_template('index.html', error="Invalid date format. Use 'YYYY-MM-DD'.", current_date=current_date)
        
        # Validate hour
        if not (0 <= target_hour <= 23):
            return render_template('index.html', error="Hour must be between 0 and 23.", current_date=current_date)
        
        # Ensure the requested datetime is not in the future
        #now = pd.Timestamp.now()
        #target_datetime = prediction_datetime.replace(hour=target_hour)
        #if target_datetime > now:
        #    return render_template('index.html', error="Requested datetime is in the future.", current_date=current_date)
        
        # Fetch weather data for the target date and the previous date
        end_date = target_date
        start_date = (prediction_datetime - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        
        data = fetch_weather_data(start_date, end_date)
        if data is None:
            return render_template('index.html', error="Error fetching weather data.", current_date=current_date)
        
        # Extract past 24 hours
        past_24_hours = extract_past_24_hours(data, target_date, target_hour)
        if past_24_hours is None:
            return render_template('index.html', error="Error extracting past 24 hours data.", current_date=current_date)
        
        # Preprocess data
        X_scaled = preprocess_data(past_24_hours)
        if X_scaled is None:
            return render_template('index.html', error="Error preprocessing data.", current_date=current_date)
        
        # Make prediction
        try:
            y_pred_scaled = model.predict(X_scaled)
        except Exception as e:
            print(f"Error during prediction: {e}")
            return render_template('index.html', error="Error during prediction.", current_date=current_date)
        
        # Inverse transform predictions
        try:
            y_pred = target_scaler.inverse_transform(y_pred_scaled)
        except Exception as e:
            print(f"Error during inverse scaling: {e}")
            return render_template('index.html', error="Error processing prediction results.", current_date=current_date)
        
        # Prepare pollutant values
        pollutant_values = {
            TARGETS[i].split('.')[1]: round(y_pred[0][i], 2) for i in range(len(TARGETS))
        }
        
        # Determine AQI
        aqi_level = determine_aqi(pollutant_values)
        
        return render_template(
            'index.html',
            pollutants=pollutant_values,
            aqi=aqi_level,
            current_date=current_date
        )
    
    return render_template('index.html', current_date=current_date)

if __name__ == '__main__':
    if model is None:
        print("Model is not loaded. Please check the model path.")
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
