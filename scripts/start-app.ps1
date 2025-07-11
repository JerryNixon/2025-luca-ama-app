# AMA Application Startup Script
# Starts both Django backend and Next.js frontend simultaneously

Write-Host "🚀 Starting AMA Application Stack" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Kill any existing processes on target ports
Write-Host "🔄 Checking for existing processes..." -ForegroundColor Yellow
try {
    $backend_process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($backend_process) {
        Write-Host "   Stopping existing backend process on port 8000..." -ForegroundColor Yellow
        $backend_pid = (Get-Process -Id $backend_process.OwningProcess -ErrorAction SilentlyContinue).Id
        Stop-Process -Id $backend_pid -Force -ErrorAction SilentlyContinue
    }
    
    $frontend_process = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
    if ($frontend_process) {
        Write-Host "   Stopping existing frontend process on port 3000..." -ForegroundColor Yellow
        $frontend_pid = (Get-Process -Id $frontend_process.OwningProcess -ErrorAction SilentlyContinue).Id
        Stop-Process -Id $frontend_pid -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "   No existing processes found" -ForegroundColor Gray
}

# Start Backend
Write-Host "🔧 Starting Django Backend..." -ForegroundColor Cyan
$projectRoot = Split-Path $PSScriptRoot -Parent
$backendPath = Join-Path $projectRoot "backend"
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python manage.py runserver 127.0.0.1:8000" -WindowStyle Normal

# Wait for backend to initialize
Write-Host "   Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "🎨 Starting Next.js Frontend..." -ForegroundColor Cyan
$frontendPath = Join-Path $projectRoot "frontend"
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal

# Wait for frontend to initialize
Write-Host "   Waiting for frontend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Application URLs
Write-Host "" 
Write-Host "✅ Application Started Successfully!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "🌐 Frontend:     http://localhost:3000" -ForegroundColor Yellow
Write-Host "🔧 Backend API:  http://127.0.0.1:8000/api/" -ForegroundColor Yellow
Write-Host "👤 Django Admin: http://127.0.0.1:8000/admin/" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎯 Test Users:" -ForegroundColor Cyan
Write-Host "   Moderator: moderator@test.com / test123" -ForegroundColor Gray
Write-Host "   User:      user@test.com / test123" -ForegroundColor Gray
Write-Host ""
Write-Host "💾 Database: Microsoft Fabric SQL" -ForegroundColor Cyan
Write-Host "🔐 Authentication: Automatic (ActiveDirectoryIntegrated)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
