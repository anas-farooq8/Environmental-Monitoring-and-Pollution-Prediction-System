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
