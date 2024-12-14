[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/h2zn46__)

# fall24_mlops_project

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
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

#### MLflow Setup

Ensure MLflow is installed and accessible. Start an MLflow server:

```bash
mlflow ui
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

The best-performing model is deployed as an API using Flask, enabling real-time pollution trend predictions.

### API Features

- **Endpoint**: `/predict`
- **Input**: JSON payload with current weather metrics.
- **Output**: Predicted pollutant concentrations.

### Deployment Steps

1. **Load Trained Model**: Retrieved from MLflow's Model Registry.
2. **Set Up Flask Server**: Created endpoints to handle prediction requests.
3. **Model Inference**: Processes input data, applies scaling, and generates predictions.
4. **Response**: Returns predictions in JSON format.

## Acknowledgments

- [DVC Documentation](https://dvc.org/doc)
- [OpenWeatherMap API](https://openweathermap.org/api/air-pollution)
- [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api)
