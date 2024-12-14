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
- [Acknowledgments](#acknowledgments)

## Overview

The **Environmental Data Management with DVC** project aims to efficiently collect, version, and manage real-time environmental data streams using [Data Version Control (DVC)](https://dvc.org/). By integrating live data streams from reputable APIs, this project ensures that environmental data such as weather conditions and air quality metrics are consistently tracked and accessible for analysis and prediction models.

## Features

- **Real-Time Data Collection**: Fetches current, forecasted, and historical air quality and weather data.
- **Data Versioning with DVC**: Ensures reproducibility and trackability of data changes over time.
- **Remote Storage Integration**: Utilizes Google Drive for storing large data files.
- **Automated Data Fetching**: Scheduled scripts to regularly update data repositories.
- **Comprehensive Documentation**: Detailed guides for setup, usage, and contribution.

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

## Acknowledgments

- [DVC Documentation](https://dvc.org/doc)
- [OpenWeatherMap API](https://openweathermap.org/api/air-pollution)
- [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api)
