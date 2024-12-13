from flask import Flask, render_template, request, jsonify
import os
import time
import requests
from dotenv import load_dotenv
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import load_model
from datetime import datetime
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Define metrics
REQUEST_COUNT = Counter("app_requests_total", "Total number of requests")
PREDICTION_TIME = Histogram("prediction_time_seconds", "Time taken for predictions")

# Define metrics for data ingestion
DATA_INGESTION_COUNT = Counter('data_ingestion_total', 'Total number of data ingestion attempts')
DATA_INGESTION_TIME = Histogram('data_ingestion_time_seconds', 'Time taken for data ingestion')
DATA_INGESTION_VOLUME = Gauge('data_ingestion_volume_bytes', 'Size of data ingested in bytes')
DATA_INGESTION_LAST_SUCCESSFUL = Gauge('data_ingestion_last_successful_timestamp', 'Timestamp of the last successful data ingestion')
DATA_INGESTION_ERROR = Counter('data_ingestion_error_total', 'Total number of data ingestion errors')

# New metrics for target variables
PREDICTION_VALUE_SO2 = Gauge('prediction_value_so2', 'Predicted value for SO2')
PREDICTION_VALUE_NO2 = Gauge('prediction_value_no2', 'Predicted value for NO2')
PREDICTION_VALUE_PM10 = Gauge('prediction_value_pm10', 'Predicted value for PM10')
PREDICTION_VALUE_PM2_5 = Gauge('prediction_value_pm2_5', 'Predicted value for PM2.5')
PREDICTION_VALUE_O3 = Gauge('prediction_value_o3', 'Predicted value for O3')
PREDICTION_VALUE_CO = Gauge('prediction_value_co', 'Predicted value for CO')

# Metrics for Mean Squared Error
PREDICTION_MSE_SO2 = Gauge('prediction_mse_so2', 'MSE for SO2 predictions')
PREDICTION_MSE_NO2 = Gauge('prediction_mse_no2', 'MSE for NO2 predictions')
PREDICTION_MSE_PM10 = Gauge('prediction_mse_pm10', 'MSE for PM10 predictions')
PREDICTION_MSE_PM2_5 = Gauge('prediction_mse_pm2_5', 'MSE for PM2.5 predictions')
PREDICTION_MSE_O3 = Gauge('prediction_mse_o3', 'MSE for O3 predictions')
PREDICTION_MSE_CO = Gauge('prediction_mse_co', 'MSE for CO predictions')

# Start Prometheus metrics server (on port 8000)
start_http_server(8000)

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Environment variables
VISUAL_CROSSING_API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')
LOCATION = f"{LATITUDE},{LONGITUDE}"

# Model and scaler paths
FEATURE_SCALER_PATH = "models/feature_scaler.joblib"
TARGET_SCALER_PATH = "models/target_scaler.joblib"
MODEL_PATH = "models/model.keras"

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
    """
    DATA_INGESTION_COUNT.inc()  # Increment data ingestion attempts
    start_time = time.time()     # Start timing data ingestion

    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/{start_date}/{end_date}?unitGroup=metric&key={VISUAL_CROSSING_API_KEY}&include=hours&elements=datetime,temp,dew,humidity,windspeed,windgust,winddir,pressure,solarenergy,cloudcover,solarradiation,uvindex'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        ingestion_time = time.time() - start_time  # Time taken for data ingestion
        DATA_INGESTION_TIME.observe(ingestion_time)  # Record ingestion time

        # Calculate data volume
        data_volume = len(response.content)  # Size in bytes
        DATA_INGESTION_VOLUME.set(data_volume)  # Record data volume

        # Record the timestamp of successful ingestion
        DATA_INGESTION_LAST_SUCCESSFUL.set(time.time())

        return data
    except Exception as e:
        DATA_INGESTION_ERROR.inc()  # Increment error count
        print(f'Error fetching weather data: {e}')
        return None

def fetch_actual_pollution_data():
    """
    Fetch actual air pollution data from the OpenWeatherMap API.
    """
    api_url = "http://api.openweathermap.org/data/2.5/air_pollution/forecast"
    params = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "appid": OPENWEATHER_API_KEY
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        return data
    except Exception as e:
        print(f'Error fetching actual pollution data: {e}')
        return None

def extract_actual_pollutants(actual_data, target_timestamp):
    """
    Extract actual pollutant values for the target timestamp from the API data.
    """
    list_data = actual_data.get('list', [])
    for entry in list_data:
        entry_timestamp = datetime.utcfromtimestamp(entry['dt'])
        if entry_timestamp == target_timestamp:
            pollutants = {
                'so2': entry['components'].get('so2', 0.0),
                'no2': entry['components'].get('no2', 0.0),
                'pm10': entry['components'].get('pm10', 0.0),
                'pm2_5': entry['components'].get('pm2_5', 0.0),
                'o3': entry['components'].get('o3', 0.0),
                'co': entry['components'].get('co', 0.0)
            }
            return pollutants
    print("Specified timestamp not found in actual data.")
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

def calculate_mse(predicted_scaled, actual_scaled):
    """
    Calculate Mean Squared Error between predicted and actual pollutant values.
    """
    mse = {}
    pollutants = ['so2', 'no2', 'pm10', 'pm2_5', 'o3', 'co']
    
    for i, pollutant in enumerate(pollutants):
        mse_value = mean_squared_error([actual_scaled[0][i]], [predicted_scaled[0][i]])
        mse[pollutant] = mse_value
    
    return mse

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
        
        # Start time before making the prediction
        start_time = time.time()  # Track the time when prediction starts
        
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
        
        # Track the prediction time
        prediction_time = time.time() - start_time  # Calculate time taken for prediction
        PREDICTION_TIME.observe(prediction_time)  # Log this time in the histogram

        # Increment api call count
        REQUEST_COUNT.inc()
        
        # Prepare pollutant values
        pollutant_values = {
            TARGETS[i].split('.')[1]: round(y_pred[0][i], 2) for i in range(len(TARGETS))
        }

        # Record prediction values
        PREDICTION_VALUE_SO2.set(pollutant_values['so2'])
        PREDICTION_VALUE_NO2.set(pollutant_values['no2'])
        PREDICTION_VALUE_PM10.set(pollutant_values['pm10'])
        PREDICTION_VALUE_PM2_5.set(pollutant_values['pm2_5'])
        PREDICTION_VALUE_O3.set(pollutant_values['o3'])
        PREDICTION_VALUE_CO.set(pollutant_values['co'])
        
        # Determine AQI
        aqi_level = determine_aqi(pollutant_values)
        
        # Fetch actual pollution data
        actual_data = fetch_actual_pollution_data()
        if actual_data is None:
            return render_template('index.html', error="Error fetching actual pollution data for validation.", current_date=current_date)
        
        # Define the target timestamp
        target_datetime_str = f"{target_date}T{target_hour:02d}:00:00"
        target_timestamp = pd.to_datetime(target_datetime_str)
        
        # Extract actual pollutants
        actual_pollutants = extract_actual_pollutants(actual_data, target_timestamp)
        if actual_pollutants is None:
            return render_template('index.html', error="Error extracting actual pollutants data for validation.", current_date=current_date)
        
        # Prepare actual pollutants for scaling
        actual_values = [
            actual_pollutants['so2'],
            actual_pollutants['no2'],
            actual_pollutants['pm10'],
            actual_pollutants['pm2_5'],
            actual_pollutants['o3'],
            actual_pollutants['co']
        ]

        # Scale actual pollutants
        y_actual_scaled = target_scaler.transform([actual_values])  # Shape: (1, 6)
        
        # Calculate MSE on scaled data
        mse_values = calculate_mse(y_pred_scaled, y_actual_scaled)
        # Round the MSE values
        mse_values = {k: round(v, 3) for k, v in mse_values.items()}
        
        # Record MSE as Prometheus metrics
        PREDICTION_MSE_SO2.set(mse_values.get('so2', 0))
        PREDICTION_MSE_NO2.set(mse_values.get('no2', 0))
        PREDICTION_MSE_PM10.set(mse_values.get('pm10', 0))
        PREDICTION_MSE_PM2_5.set(mse_values.get('pm2_5', 0))
        PREDICTION_MSE_O3.set(mse_values.get('o3', 0))
        PREDICTION_MSE_CO.set(mse_values.get('co', 0))

        # Inverse transform actual pollutants for display
        try:
            y_actual = target_scaler.inverse_transform(y_actual_scaled)
        except Exception as e:
            print(f"Error during inverse scaling of actual pollutants: {e}")
            return render_template('index.html', error="Error processing actual pollution results.", current_date=current_date)
        
        # Prepare actual pollutant values after inverse scaling
        actual_pollutants_display = {
            'so2': round(y_actual[0][0], 2),
            'no2': round(y_actual[0][1], 2),
            'pm10': round(y_actual[0][2], 2),
            'pm2_5': round(y_actual[0][3], 2),
            'o3': round(y_actual[0][4], 2),
            'co': round(y_actual[0][5], 2)
        }

        return render_template(
            'index.html',
            pollutants=pollutant_values,
            actual_pollutants=actual_pollutants_display,
            mse=mse_values,
            aqi=aqi_level,
            current_date=current_date
        )
    
    return render_template('index.html', current_date=current_date)

if __name__ == '__main__':
    if model is None:
        print("Model is not loaded. Please check the model path.")
    else:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
