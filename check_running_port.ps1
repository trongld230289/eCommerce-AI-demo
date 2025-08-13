#!/usr/bin/env pwsh
# ========================================
# Port Status Checker (PowerShell)
# ========================================
# Quick port status check with colored output
# Usage: .\check_running_port.ps1

param(
    [switch]$Detailed,
    [switch]$Help
)

if ($Help) {
    Write-Host "Port Status Checker" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\check_running_port.ps1          # Quick check"
    Write-Host "  .\check_running_port.ps1 -Detailed # Detailed info"
    Write-Host "  .\check_running_port.ps1 -Help     # Show this help"
    Write-Host ""
    exit
}

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to get process info for a port
function Get-PortProcess {
    param([int]$Port)
    
    try {
        $netstat = netstat -ano | findstr ":$Port"
        if ($netstat) {
            foreach ($line in $netstat) {
                if ($line -match "LISTENING") {
                    $parts = $line -split '\s+'
                    $processId = $parts[-1]
                    
                    try {
                        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                        if ($process) {
                            return @{
                                PID = $processId
                                ProcessName = $process.ProcessName
                                Port = $Port
                            }
                        }
                    }
                    catch {
                        return @{
                            PID = $processId
                            ProcessName = "Unknown"
                            Port = $Port
                        }
                    }
                }
            }
        }
    }
    catch {
        return $null
    }
    
    return $null
}

# Service mapping
$ServiceMap = @{
    3000 = "React Frontend"
    8000 = "Backend API"
    8001 = "Recommendation System"
    5000 = "Flask (Alternative)"
    5173 = "Vite Development"
    4000 = "Development Server"
    3001 = "Alternative Frontend"
}

# Ports to check
$Ports = @(3000, 8000, 8001, 5000, 5173, 4000, 3001)

# Banner
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    🔍 Port Status Checker                   ║" -ForegroundColor Cyan
Write-Host "║                  eCommerce Development Ports                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "🎯 Port Status Check:" -ForegroundColor Cyan
Write-Host ""

$RunningPorts = @()
$FreePorts = @()

foreach ($Port in $Ports) {
    $ServiceName = $ServiceMap[$Port]
    if (-not $ServiceName) {
        $ServiceName = "Service on $Port"
    }
    
    $IsRunning = Test-Port -Port $Port
    
    if ($IsRunning) {
        $RunningPorts += $Port
        Write-Host "   🟢 Port $Port ($ServiceName): RUNNING" -ForegroundColor Red
        
        if ($Detailed) {
            $ProcessInfo = Get-PortProcess -Port $Port
            if ($ProcessInfo) {
                Write-Host "      └─ Process: $($ProcessInfo.ProcessName) (PID: $($ProcessInfo.PID))" -ForegroundColor Yellow
            }
        }
    }
    else {
        $FreePorts += $Port
        Write-Host "   ✅ Port $Port ($ServiceName): FREE" -ForegroundColor Green
    }
}

Write-Host ""

# Summary
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   • Total ports checked: $($Ports.Count)" -ForegroundColor White
if ($RunningPorts.Count -gt 0) {
    Write-Host "   • Running services: $($RunningPorts.Count)" -ForegroundColor Red
} else {
    Write-Host "   • Running services: $($RunningPorts.Count)" -ForegroundColor Green
}
Write-Host "   • Available ports: $($FreePorts.Count)" -ForegroundColor Green

if ($RunningPorts.Count -gt 0) {
    Write-Host ""
    Write-Host "🔄 To stop running services:" -ForegroundColor Yellow
    Write-Host "   • Kill all: taskkill /F /IM `"node.exe`" && taskkill /F /IM `"python.exe`"" -ForegroundColor White
    Write-Host "   • Or use: python stop_all_services.py" -ForegroundColor White
}

if ($RunningPorts.Count -eq 0) {
    Write-Host ""
    Write-Host "🚀 All development ports are now available!" -ForegroundColor Yellow
    Write-Host "   • Backend: python BE/run_BE.py" -ForegroundColor White
    Write-Host "   • Frontend: python FE/run_FE.py" -ForegroundColor White
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✨ Port check complete!" -ForegroundColor Green
