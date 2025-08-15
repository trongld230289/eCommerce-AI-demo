# eCommerce-AI Service Starter PowerShell Script
# =============================================

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " eCommerce-AI Service Starter" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if directory exists
function Test-ServiceDirectory {
    param([string]$Path, [string]$ServiceName)
    
    if (-not (Test-Path $Path)) {
        Write-Host "❌ $ServiceName directory '$Path' not found!" -ForegroundColor Red
        return $false
    }
    return $true
}

# Function to start a service in a new window
function Start-ServiceWindow {
    param([string]$Path, [string]$Command, [string]$ServiceName, [int]$Port)
    
    Write-Host "🚀 Starting $ServiceName on port $Port..." -ForegroundColor Green
    
    try {
        $fullCommand = "cd '$Path'; $Command; Read-Host 'Press Enter to close'"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $fullCommand -WindowStyle Normal
        Write-Host "  ✅ $ServiceName started successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "  ❌ Failed to start $ServiceName" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Check all required directories
$allDirsExist = $true

if (-not (Test-ServiceDirectory "BE" "Backend")) { $allDirsExist = $false }
if (-not (Test-ServiceDirectory "FE" "Frontend")) { $allDirsExist = $false }
if (-not (Test-ServiceDirectory "Recommendation_System" "Recommendation System")) { $allDirsExist = $false }

if (-not $allDirsExist) {
    Write-Host ""
    Write-Host "❌ Cannot start services - missing directories!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "All directories found! Starting services..." -ForegroundColor Green
Write-Host ""

# Start services
$services = @()

# Backend
if (Start-ServiceWindow "BE" "python flask_server.py" "Backend (Flask)" 8000) {
    $services += "Backend"
    Start-Sleep 2
}

# Whisper API Service
if (Start-ServiceWindow "BE" "python whisper_api.py" "Whisper API (Transcription)" 5005) {
    $services += "Whisper API"
    Start-Sleep 2
}

# Frontend  
if (Start-ServiceWindow "FE" "npm start" "Frontend (React)" 3000) {
    $services += "Frontend"
    Start-Sleep 2
}

# Recommendation System
if (Start-ServiceWindow "Recommendation_System" "python flask_recommendation_server.py" "Recommendation System" 8001) {
    $services += "Recommendation System"
    Start-Sleep 2
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ Started $($services.Count) service(s)!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

if ($services.Count -gt 0) {
    Write-Host "🌐 Access URLs:" -ForegroundColor Yellow
    Write-Host "  Frontend:        http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:         http://localhost:8000" -ForegroundColor White
    Write-Host "  Recommendations: http://localhost:8001" -ForegroundColor White
    Write-Host "  Whisper API:     http://localhost:5005" -ForegroundColor White
    if ($services -contains "AI Service") {
        Write-Host "  AI Service:      http://localhost:8002" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "💡 Each service runs in its own window" -ForegroundColor Gray
    Write-Host "💡 Close the windows to stop services" -ForegroundColor Gray
    Write-Host "💡 Or use stop_all_services.py to stop all at once" -ForegroundColor Gray
} else {
    Write-Host "❌ No services started successfully!" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
