# Environmental-Monitoring-and-Pollution-Prediction-System

## Demo
![1](https://github.com/user-attachments/assets/d874c112-9a43-4805-9a2b-90792880d61d)
![2](https://github.com/user-attachments/assets/b1b0dd39-4cbb-459a-8333-b44542360c46)
![Screenshot (6)](https://github.com/user-attachments/assets/6e617260-0638-4c6c-9782-11fb438d1b5c)
![grafana](https://github.com/user-attachments/assets/77a0a6e6-8872-40ed-b9d7-57530315264f)


## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Data Collection](#data-collection)
  - [Air Quality Data](#air-quality-data)
  - [Weather Data](#weather-data)
- [DVC Integration](#dvc-integration)
  - [Initializing DVC](#initializing-dvc)
  - [Remote Storage Configuration](#remote-storage-configuration)
  - [Data Versioning](#data-versioning)
- [Automation](#automation)
  - [PowerShell Script](#powershell-script)
  - [Scheduling with Task Scheduler](#scheduling-with-task-scheduler)
- [Manual Usage](#usage)
- [Data Preparation](#data-preparation)
- [Model Development](#model-development)
- [MLflow Integration](#mlflow-integration)
  - [Experiment Tracking](#experiment-tracking)
  - [Hyperparameter Tuning](#hyperparameter-tuning)
  - [Model Evaluation](#model-evaluation)
- [Deployment](#deployment)
  - [Flask API Setup](#flask-api-setup)
  - [Integrating MLflow](#integrating-mlflow)
  - [Prometheus and Grafana Integration](#prometheus-and-grafana-integration)
  - [Grafana Dashboards](#grafana-dashboards)
  - [Docker Compose Setup](#docker-compose-setup)
  - [Docker Compose Commands](#docker-compose-commands)
- [Monitoring](#monitoring)

  - [Prometheus Metrics](#prometheus-metrics)
  - [Grafana Dashboards](#grafana-dashboards)

- [Acknowledgments](#acknowledgments)

## Overview

The project aims to efficiently collect, version, and manage real-time environmental data streams using [Data Version Control (DVC)](https://dvc.org/). By integrating live data streams from reputable APIs, this project ensures that environmental data such as weather conditions and air quality metrics are consistently tracked and accessible for analysis and prediction models.
Then developing machine learning models to predict pollution trends and alert high-risk days. By leveraging time-series models and integrating MLflow for experiment tracking, this project ensures robust model development, evaluation, and deployment processes.

## Features

- **Real-Time Data Collection**: Fetches current, forecasted, and historical air quality and weather data.
- **Data Versioning with DVC**: Ensures reproducibility and trackability of data changes over time.
- **Remote Storage Integration**: Utilizes Google Drive for storing large data files.
- **Automated Data Fetching**: Scheduled scripts to regularly update data repositories.
- **Data Preprocessing**: Cleans and prepares environmental data for modeling.
- **Time-Series Modeling**: Utilizes LSTM networks for accurate pollution trend predictions.
- **MLflow Integration**: Tracks experiments, logs metrics, and manages model versions.
- **Hyperparameter Tuning**: Optimizes model performance using grid search techniques.
- **Model Deployment**: Deploys the best-performing model as an API for real-time predictions.
- **Monitoring**: Integrates Prometheus for monitoring API requests and data ingestion processes.
- **Visualization**: Generates correlation heatmaps and prediction vs. actual plots.

## Technologies Used

- **Python**: Primary programming language for data collection scripts.
- **DVC (Data Version Control)**: For data versioning and management.
- **Git**: Version control system.
- **Visual Crossing Weather API**: Source for weather data.
- **OpenWeatherMap Air Pollution API**: Source for air quality data.
- **PowerShell**: Scripting for automation on Windows.
- **Task Scheduler (Windows)**: Scheduling automated tasks.
- **Google Drive**: Remote storage for DVC.
- **Dotenv**: Managing environment variables.
- **Pandas & NumPy**: Data manipulation and numerical operations.
- **Scikit-learn**: Data preprocessing and evaluation metrics.
- **TensorFlow & Keras**: Building and training LSTM models.
- **MLflow**: Experiment tracking and model management.
- **Flask**: Deploying the prediction API.
- **Matplotlib & Seaborn**: Data visualization.
- **Prometheus**: Monitoring application metrics.

## Getting Started

### Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **Git**: Version control system.
- **DVC**: Install DVC for data management.
- **Google Drive Account**: For remote storage.
- **API Keys**:
  - [OpenWeatherMap API Key](https://openweathermap.org/api/air-pollution)
  - [Visual Crossing Weather API Key](https://www.visualcrossing.com/resources/documentation/weather-api/timeline-weather-api/)

### Installation

1. **Set Up a Virtual Environment**

   ```bash
   python -m venv .venv
   ```

2. **Activate the Virtual Environment**

   **Windows:**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **Unix/Linux:**

   ```bash
   source .venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the root directory and add the following:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
VISUAL_CROSSING_API_KEY=your_visual_crossing_api_key
LATITUDE=your_latitude
LONGITUDE=your_longitude
```

Replace `your_openweather_api_key`, `your_visual_crossing_api_key`, `your_latitude`, and `your_longitude` with your actual API keys and coordinates.

### MLflow Setup

Ensure MLflow is installed and accessible. Start an MLflow server:

```bash
mlflow ui
```

### Prometheus Setup

Install and configure Prometheus to scrape metrics from the Flask application. Add the following job to your `prometheus.yml` configuration file:

```bash
scrape_configs:
  - job_name: 'flask_app'
    static_configs:
      - targets: ['localhost:8000']
```

### DVC Remote Storage Setup

Ensure you have a `dvc-key.json` file for Google Drive service account authentication and place it in the project directory.

## Data Collection

### Air Quality Data

- **Script**: `scripts/air_collector.py`
- **Description**: Fetches current, forecasted, and historical air quality data from OpenWeatherMap API.

### Weather Data

- **Script**: `scripts/weather_collector.py`
- **Description**: Fetches current, forecasted, and historical weather data from Visual Crossing Weather API.

## DVC Integration

### Initializing DVC

```bash
dvc init
```

### Remote Storage Configuration

1. **Add Remote Storage**
   ```bash
   dvc remote add -d gdrive_remote gdrive://<folder_id>
   ```
2. **Modify Remote for Service Account**
   ```bash
   dvc remote modify gdrive_remote gdrive_use_service_account true
   dvc remote modify gdrive_remote gdrive_service_account_json_file_path "path/to/dvc-key.json"
   dvc remote default gdrive_remote
   ```

### Data Versioning

#### Create `dvc.yaml`

```yaml
stages:
  air_quality:
    cmd: python scripts/air_collector.py
    outs:
      - data/air_quality/current/air_quality_current.json
      - data/air_quality/forecast/air_quality_forecast.json
      - data/air_quality/historical/air_quality_historical.json
  weather:
    cmd: python scripts/weather_collector.py
    outs:
      - data/weather/current/weather_current.json
      - data/weather/forecast/weather_forecast.json
      - data/weather/historical/weather_historical.json
```

#### Commit Changes

```bash
git add .
git commit -m "Initialize DVC and add data collection stages"
```

## Automation

### PowerShell Script

- **Script**: `collect_and_push.ps1`
- **Description**: Automates data fetching, DVC pipeline execution, and pushing changes to remote storage and Git repository.

### Scheduling with Task Scheduler (Windows)

1. **Open Task Scheduler**
2. **Create a New Task**
   - **Name**: Environmental Data Collection
   - **Trigger**: Set the desired schedule (e.g., daily at midnight).
   - **Action**:
     - **Program/script**: `powershell.exe`
     - **Add arguments**: `-ExecutionPolicy Bypass -File "path\to\collect_and_push.ps1"`
3. **Save the Task**

## Manual Usage

### Run Data Collection Manually

```bash
python scripts/air_collector.py
python scripts/weather_collector.py
```

### Run DVC Pipeline

```bash
dvc repro
```

### Push Data to Remote Storage

```bash
dvc push
git push
```

## Data Preparation

Data preparation is crucial for building effective machine learning models. The following steps outline how environmental data is loaded, merged, and preprocessed for model training.

### Loading and Merging Data

- **Air Quality Data**: Loaded from historical JSON files.
- **Weather Data**: Loaded from historical JSON files.
- **Merging**: DataFrames are merged on the `datetime` column to combine air quality and weather metrics.

### Cleaning and Feature Engineering

- **Missing Values**: Checked and handled to ensure data integrity.
- **Outlier Removal**: Removed using Z-score thresholding to eliminate anomalous data points.
- **Feature Scaling**: Applied `StandardScaler` to normalize features and targets.

### Creating Sequences for LSTM

- **Sequence Length**: 24 hours (past 24 data points) used to predict current pollution levels.
- **Input Features**: Selected weather-related metrics.
- **Target Variables**: Pollutant concentrations (SO₂, NO₂, PM₁₀, PM₂.₅, O₃, CO).

## Model Development

Leveraging time-series models, particularly LSTM networks, to predict pollution trends.

### Model Architecture

- **Input Layer**: Accepts sequences of past 24 hours of weather data.
- **LSTM Layers**: Three stacked LSTM layers with dropout for regularization.
- **Dense Layer**: Outputs predictions for each pollutant.
- **Activation**: `tanh` for LSTM layers and `linear` for the output layer.

### Compilation

- **Optimizer**: Adam with varying learning rates.
- **Loss Function**: Mean Squared Error (MSE).
- **Metrics**: Mean Absolute Error (MAE).

## MLflow Integration

MLflow is integrated to track experiments, log metrics, and manage model versions.

### Experiment Tracking

- **Experiment Name**: `Pollution_Trend_Prediction_LSTM`
- **Parameters Logged**: Hyperparameters such as units, dropout rates, learning rates, batch sizes, epochs, etc.
- **Metrics Logged**: MSE and MAE for each pollutant and average metrics.

### Hyperparameter Tuning

Utilized grid search to explore combinations of hyperparameters:

- **Units**: [128]
- **Dropout**: [0.2, 0.3]
- **Learning Rate**: [0.001, 0.0001]
- **Batch Size**: [16, 32]
- **Epochs**: [50]

### Model Evaluation

- **Metrics**: Calculated MSE, MAE, and R² scores for each pollutant.
- **Visualization**: Plotted actual vs. predicted pollutant concentrations.
- **Best Model Selection**: Based on lowest average MSE and MAE.

## Deployment

Deploying the best-performing model as an API ensures real-time accessibility for predictions. This section outlines the steps to set up the Flask API, integrate MLflow, incorporate Prometheus for monitoring, and run the application.

### Flask API Setup

The Flask application serves as the interface for making real-time pollution predictions based on input weather data. It integrates MLflow for model management and Prometheus for monitoring.

Key Components:

- Endpoints:
  - **/:** Main page with a form to input date and hour for prediction.
  - **/predict**: Processes prediction requests and returns results.
- **Data Ingestion**: Fetches historical weather data and actual pollution data for validation.
- **Model Inference**: Utilizes the trained LSTM model to make predictions.
- **AQI Determination**: Categorizes pollution levels into AQI ratings.
- **Prometheus Metrics**: Tracks API requests, prediction times, data ingestion metrics, and prediction accuracy.

### Integrating MLflow

The Flask app leverages MLflow's Model Registry to load and manage the best-performing model.

Steps:

1. **Load Scalers and Model**:

- Feature Scaler: Standardizes input features.
- Target Scaler: Standardizes target pollutant concentrations.
- Model: Loaded from the MLflow Model Registry.

2. **Model Loading Code Snippet**:

```bash
# Load the scalers
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
```

### Prometheus and Grafana Integration

Prometheus and Grafana are integrated to monitor various aspects of the application, including API requests, prediction times, data ingestion processes, and prediction accuracy.

Prometheus Metrics Defined:

- **API Metrics**:

  - app_requests_total: Total number of API requests.
  - prediction_time_seconds: Time taken to process predictions.

- **Data Ingestion Metrics**:

  - data_ingestion_total: Total number of data ingestion attempts.
  - data_ingestion_time_seconds: Time taken for data ingestion.
  - data_ingestion_volume_bytes: Size of data ingested in bytes.
  - data_ingestion_last_successful_timestamp: Timestamp of the last successful data ingestion.
  - data_ingestion_error_total: Total number of data ingestion errors.

- **Prediction Metrics**:

  - prediction*value*<pollutant>: Predicted values for each pollutant.
  - prediction*mse*<pollutant>: Mean Squared Error for predictions of each pollutant.

### Grafana Dashboards:

Grafana is configured to connect to Prometheus as a data source. Dashboards are created to visualize the defined metrics, providing real-time insights into the application's performance and health.

### Docker Compose Setup

To streamline the deployment process, Docker Compose is used to orchestrate the Flask API, Prometheus, and Grafana services.

Docker Compose Configuration:

```bash
services:
  flask-api:
    build:
      context: . # Build using the Dockerfile in the current directory
    container_name: flask-api
    ports:
      - "5000:5000" # Exposes Flask app on port 5000
      - "8000:8000" # Exposes Prometheus metrics endpoint on port 8000
    env_file:
      - .env # Passes the .env file to the container
    environment:
      - FLASK_APP=app.py
    networks:
      - monitoring
    depends_on:
      - prometheus # Ensures Prometheus starts before Flask app

  prometheus:
    image: prom/prometheus
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml # Mounts Prometheus config
    ports:
      - "9090:9090" # Exposes Prometheus on port 9090
    command:
      - "--config.file=/etc/prometheus/prometheus.yml" # Specifies config file
    networks:
      - monitoring

  grafana:
    image: grafana/grafana
    container_name: grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin # Sets Grafana admin password
    ports:
      - "3000:3000" # Exposes Grafana on port 3000
    volumes:
      - grafana-storage:/var/lib/grafana # Persists Grafana data
    networks:
      - monitoring
    depends_on:
      - prometheus # Ensures Prometheus starts before Grafana

volumes:
  grafana-storage: # Defines a named volume for Grafana data

networks:
  monitoring:
    driver: bridge
```

Explanation of Services:

- **flask-api**:

  - Build Context: Uses the current directory's Dockerfile.
  - Ports: Exposes the Flask application on port 5000 and Prometheus metrics on port 8000.
  - Environment Variables: Loads variables from the .env file.
  - Dependencies: Waits for Prometheus to start before launching.

- **prometheus**:

  - Image: Uses the official Prometheus image.
  - Configuration: Mounts a custom prometheus.yml for scraping metrics.
  - Ports: Accessible on port 9090.

- **grafana**:

  - Image: Uses the official Grafana image.
  - Configuration: Sets the admin password and persists data using Docker volumes.
  - Ports: Accessible on port 3000.
  - Dependencies: Waits for Prometheus to start before launching.

### Docker Compose Commands:

- Start Services

```bash
docker-compose up -d
```

- Stop Services

```bash
docker-compose down
```

## Monitoring

Monitoring is essential to ensure the reliability and performance of the data collection and model deployment processes.

- **MLflow UI**: Monitors experiment runs, metrics, and model versions.
- **Prometheus Metrics**: Tracks API requests, prediction times, data ingestion metrics, and prediction accuracy.
- **Visualization Tools**: Using Grafana to visualize Prometheus metrics for better insights.

### Prometheus Metrics:

- **API Metrics**:

  - app_requests_total: Indicates the total number of prediction requests made to the API.
  - prediction_time_seconds: Measures the time taken to process each prediction request.

- **Data Ingestion Metrics**:

  - data_ingestion_total: Tracks the number of data ingestion attempts.
  - data_ingestion_time_seconds: Logs the duration of each data ingestion process.
  - data_ingestion_volume_bytes: Monitors the size of data ingested.
  - data_ingestion_last_successful_timestamp: Records the timestamp of the last successful data ingestion.
  - data_ingestion_error_total: Counts the number of errors encountered during data ingestion.

- **Prediction Metrics**:

  - prediction_value_so2, prediction_value_no2, etc.: Gauge the predicted pollutant concentrations.
  - prediction_mse_so2, prediction_mse_no2, etc.: Gauge the Mean Squared Error for each pollutant's predictions.

### Grafana Dashboards

Grafana visualizes the metrics collected by Prometheus, providing real-time insights into the application's performance and health.

Setting Up Dashboards:

1. **Create a New Dashboard**:

- Click on Create > Dashboard.
- Add new panels for each metric you wish to visualize.

2. **Sample Panels**:

- API Requests Total: Visualize app_requests_total over time.
- Prediction Time: Monitor prediction_time_seconds to assess response times.
- Data Ingestion Volume: Track data_ingestion_volume_bytes to understand data flow.
- Pollutant Predictions: Display gauges for prediction_value_so2, prediction_value_no2, etc.
- Prediction Accuracy: Plot prediction_mse_so2, prediction_mse_no2, etc., to monitor model performance.

3. **Alerts**:

- Configure alerts for critical metrics, such as unusually high prediction times or data ingestion errors.

## Acknowledgments

- [DVC Documentation](https://dvc.org/doc)
- [OpenWeatherMap API](https://openweathermap.org/api/air-pollution)
- [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api)
