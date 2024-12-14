# Set Execution Policy to Bypass for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Navigate to the project root directory
Set-Location -Path "D:\Semester 7\ML-Ops\course-project-anas-farooq8"

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Optional: Verify activation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not available. Ensure the virtual environment is activated correctly."
    exit 1
}

# Run DVC pipeline
Write-Output "Running DVC pipeline..."
dvc repro

# Check if dvc repro was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "DVC repro failed. Check the logs for more details."
    exit 1
}

# Push changes to DVC remote storage
Write-Output "Pushing changes to DVC remote storage..."
dvc push

# Check if dvc push was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "DVC push failed. Check the logs for more details."
    exit 1
}

# Push changes to Git repository
Write-Output "Committing and pushing changes to Git..."
git add .
$commitMessage = "Automated data collection and DVC push at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m "$commitMessage"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Git commit failed. Possibly no changes to commit."
}
git push
if ($LASTEXITCODE -ne 0) {
    Write-Error "Git push failed. Check your network connection and Git remote settings."
    exit 1
}
Write-Output "Git push completed successfully."

# Deactivate the virtual environment
Deactivate

Write-Output "Data collection and pushing process completed successfully."