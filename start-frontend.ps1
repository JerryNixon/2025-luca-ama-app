# AMA Frontend Server Startup Script
Write-Host "=== Starting AMA Frontend Server ===" -ForegroundColor Green
Write-Host "Location: frontend directory" -ForegroundColor Yellow

# Navigate to frontend directory
Set-Location "c:\Users\t-lucahadife\Documents\luca-ama-app\frontend"

# Install/update dependencies
Write-Host "Checking Node dependencies..." -ForegroundColor Cyan
npm install

# Start Next.js development server
Write-Host "Starting Next.js server on http://localhost:3000..." -ForegroundColor Green
Write-Host "Connected to backend API at http://127.0.0.1:8000/api/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

npm run dev
