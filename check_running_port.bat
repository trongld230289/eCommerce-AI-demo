@echo off
REM ========================================
REM Port Status Checker (Batch)
REM ========================================
REM Quick port status check for Windows
REM Usage: check_running_port.bat

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🔍 Port Status Checker                   ║
echo ║                  eCommerce Development Ports                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🎯 Port Status Check:
echo.

set running_count=0
set free_count=0

REM Check Port 3000 (React Frontend)
netstat -an | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo    ✅ Port 3000 ^(React Frontend^): FREE
    set /a free_count+=1
) else (
    echo    🟢 Port 3000 ^(React Frontend^): RUNNING
    set /a running_count+=1
)

REM Check Port 8000 (Backend API)
netstat -an | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo    ✅ Port 8000 ^(Backend API^): FREE
    set /a free_count+=1
) else (
    echo    🟢 Port 8000 ^(Backend API^): RUNNING
    set /a running_count+=1
)

REM Check Port 8001 (Recommendation System)
netstat -an | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo    ✅ Port 8001 ^(Recommendation System^): FREE
    set /a free_count+=1
) else (
    echo    🟢 Port 8001 ^(Recommendation System^): RUNNING
    set /a running_count+=1
)

REM Check Port 5000 (Flask Alternative)
netstat -an | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo    ✅ Port 5000 ^(Flask Alternative^): FREE
    set /a free_count+=1
) else (
    echo    🟢 Port 5000 ^(Flask Alternative^): RUNNING
    set /a running_count+=1
)

REM Check Port 5173 (Vite Development)
netstat -an | findstr ":5173" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo    ✅ Port 5173 ^(Vite Development^): FREE
    set /a free_count+=1
) else (
    echo    🟢 Port 5173 ^(Vite Development^): RUNNING
    set /a running_count+=1
)

echo.
echo 📊 Summary:
echo    • Total ports checked: 5
echo    • Running services: %running_count%
echo    • Available ports: %free_count%

if %running_count% gtr 0 (
    echo.
    echo 🔄 To stop running services:
    echo    • Kill all: taskkill /F /IM "node.exe" ^&^& taskkill /F /IM "python.exe"
    echo    • Or use: python stop_all_services.py
)

if %running_count% equ 0 (
    echo.
    echo 🚀 All development ports are now available!
    echo    • Backend: python BE/run_BE.py
    echo    • Frontend: python FE/run_FE.py
)

echo.
echo ════════════════════════════════════════════════════════════════
echo ✨ Port check complete!

REM Pause if run directly (not from another script)
if "%1"=="" pause
