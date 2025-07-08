# AMA Backend Server Startup Script
Write-Host "=== Starting AMA Backend Server ===" -ForegroundColor Green
Write-Host "Location: backend directory" -ForegroundColor Yellow

# Navigate to backend directory
Set-Location "c:\Users\t-lucahadife\Documents\luca-ama-app\backend"

# Check if virtual environment exists and activate it
if (Test-Path ".venv/Scripts/Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    try {
        & ".venv/Scripts/Activate.ps1"
    } catch {
        Write-Host "Could not activate virtual environment, using system Python" -ForegroundColor Yellow
    }
} elseif (Test-Path "../.venv/Scripts/Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    try {
        & "../.venv/Scripts/Activate.ps1"
    } catch {
        Write-Host "Could not activate virtual environment, using system Python" -ForegroundColor Yellow
    }
} else {
    Write-Host "No virtual environment found, using system Python" -ForegroundColor Yellow
}

# Run migrations first
Write-Host "Running database migrations..." -ForegroundColor Cyan
python manage.py migrate

# Start Django server
Write-Host "Starting Django server on http://127.0.0.1:8000..." -ForegroundColor Green
Write-Host "API endpoints available at http://127.0.0.1:8000/api/" -ForegroundColor Yellow
Write-Host "Admin interface at http://127.0.0.1:8000/admin/" -ForegroundColor Yellow
Write-Host "" 
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

python manage.py runserver 127.0.0.1:8000
