[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/h2zn46__)

# fall24_mlops_project

### Step 1: Setup a Virtual Environment

Create virtual environment using
`python -m venv .venv`

Source this environment
`Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`
`.\.venv\Scripts\Activate.ps1`

Install all the dependencies
`pip install -r requirements.txt`

Verify the Install Packages
`pip freeze`

### Step 2: Initialize DVC in the Repository

`dvc init`
`dvc list --dvc-only .`
`dvc remote add -d gdrive_remote gdrive://<folder_id>`
`dvc remote modify gdrive_remote gdrive_use_service_account true`
`dvc remote modify gdrive_remote gdrive_service_account_json_file_path "D:/Semester 7/ML-Ops/course-project-anas-farooq8/dvc-key.json"`
`dvc remote default gdrive_remote`
`dvc repro`
`dvc push`

### Step 3: Create the PowerShell Script

`New-Item -Path . -Name "collect_and_push.ps1" -ItemType "File" -Force`
`.\collect_and_push.ps1`

### Step 4: Schedule the Script with Task Scheduler (Windows)

1. Open Task Scheduler:

- Press Win + R, type taskschd.msc, and press Enter.

2. Create a New Task:

- Action: Click on Action > Create Task....
  Name: Enter a descriptive name, e.g., Environmental Data Collection and Push.
  Description: (Optional) Automates data collection and versioning using DVC every hour.
  Security Options:
  User Account: Choose an account with the necessary permissions.
  Run whether user is logged on or not: Select this to ensure the task runs in the background.
  Run with highest privileges: Check this if required by your scripts.

3. Set Triggers:

- Navigate to the "Triggers" Tab:
  Click New....
  Begin the task: On a schedule.
  Settings: Select Daily.
  Start: Set the date and time you want the scheduling to begin.
  Advanced Settings:
  Repeat task every: 1 hour.
  For a duration of: Indefinitely.
  Enabled: Ensure this is checked.
  Click OK.

4. Set Actions:

Navigate to the "Actions" Tab:
Click New....

Action: Start a program.

Program/script: powershell.exe

Add arguments:
-File "D:\Semester 7\ML-Ops\course-project-anas-farooq8\scripts\collect_and_push.ps1"

5. Finalize the Task:

Click OK.
Authentication: If prompted, enter the password for the user account under which the task will run.

### Step 5: Script Writing for Model Training & Setting up ML-Flow

### Step 6: Deploying an API

### Step 7: Building Flask App

### Step 8: Dockerizing the App

- docker build -t pollution-prediction-app .
- ```bash
  docker run -d -p 5000:5000 --env-file .env --name pollution-app pollution-prediction-app
  ```

- docker ps
- docker logs -f pollution-app
- docker stop pollution-app

### Step 9: Monitoring and Live Testing

- Grafana:
  Grafana is an open-source visualization and monitoring tool.
  It provides interactive dashboards for visualizing metrics, logs, and alerts collected from various data sources.
  We will use it for Application-specific metrics (API response times, errors, etc.).

- Prometheus:
  Prometheus is an open-source monitoring and alerting toolkit.
  It collects and stores metrics as time-series data (numerical data over time).

- Relationship Between Grafana, Prometheus, and Docker
  Prometheus collects metrics from applications running in Docker containers.
  Grafana visualizes those metrics by connecting to Prometheus as a data source.
  Using Docker, you can containerize Grafana, Prometheus, and your application for a streamlined and consistent deployment.

* Start Prometheus

- docker-compose up -d
- http://localhost:9090

* Flow of Metrics with Prometheus:
  We define metrics in app (like REQUEST_COUNT, PREDICTION_TIME, DATA_INGESTION_TIME).
  Prometheus scrapes these metrics from your app's /metrics endpoint. This scraping happens at intervals you configure in Prometheus.
  Prometheus stores these metrics and makes them available for querying.
  Grafana visualizes these metrics using dashboards.

- docker-compose up --build -d
- docker-compose down
- http://localhost:9090
- http://localhost:3000
