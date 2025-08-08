# eCommerce-AI Service Stopper PowerShell Script
# =============================================

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " eCommerce-AI Service Stopper" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Function to stop processes on a specific port
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    
    Write-Host "Checking $ServiceName (Port $Port)..." -ForegroundColor Green
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
        
        if ($processes) {
            foreach ($pid in $processes) {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "  Stopping: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                }
            }
            Write-Host "  ✅ Stopped processes on port $Port" -ForegroundColor Green
        } else {
            Write-Host "  ✅ No processes running on port $Port" -ForegroundColor Green
        }
    }
    catch {
        # Fallback method using netstat
        $netstat = netstat -ano | Select-String ":$Port "
        if ($netstat) {
            foreach ($line in $netstat) {
                $parts = $line.ToString().Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
                if ($parts.Length -ge 5) {
                    $pid = $parts[-1]
                    if ($pid -match '^\d+$') {
                        Write-Host "  Stopping PID: $pid" -ForegroundColor Yellow
                        taskkill /F /PID $pid 2>$null
                    }
                }
            }
        }
        Write-Host "  ✅ Checked port $Port" -ForegroundColor Green
    }
    Write-Host ""
}

# Stop services on known ports
Stop-ProcessOnPort -Port 3000 -ServiceName "Frontend (React)"
Stop-ProcessOnPort -Port 8000 -ServiceName "Backend (Flask)"
Stop-ProcessOnPort -Port 8001 -ServiceName "Recommendation System"
Stop-ProcessOnPort -Port 8002 -ServiceName "AI Service"
Stop-ProcessOnPort -Port 5000 -ServiceName "Flask Default"
Stop-ProcessOnPort -Port 5173 -ServiceName "Vite Dev Server"

# Stop Node.js processes
Write-Host "Stopping all Node.js processes..." -ForegroundColor Green
try {
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        $nodeProcesses | Stop-Process -Force
        Write-Host "  ✅ Stopped $($nodeProcesses.Count) Node.js process(es)" -ForegroundColor Green
    } else {
        Write-Host "  ✅ No Node.js processes found" -ForegroundColor Green
    }
}
catch {
    Write-Host "  ⚠️  Error stopping Node.js processes" -ForegroundColor Yellow
}
Write-Host ""

# Stop Python Flask processes
Write-Host "Stopping Python Flask processes..." -ForegroundColor Green
try {
    $pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*flask*" -or $_.CommandLine -like "*app.py*" -or $_.CommandLine -like "*main.py*" }
    if ($pythonProcesses) {
        $pythonProcesses | Stop-Process -Force
        Write-Host "  ✅ Stopped $($pythonProcesses.Count) Python process(es)" -ForegroundColor Green
    } else {
        Write-Host "  ✅ No Python Flask processes found" -ForegroundColor Green
    }
}
catch {
    Write-Host "  ⚠️  Error stopping Python processes" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "🎉 All eCommerce-AI services stopped!" -ForegroundColor Green
Write-Host "💡 You can now restart them fresh" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan

# Optional: Wait for user input
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
