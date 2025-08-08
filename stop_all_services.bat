@echo off
echo ======================================
echo  eCommerce-AI Service Stopper
echo ======================================
echo Stopping all services on known ports...
echo.

REM Stop processes on specific ports
echo Stopping Frontend (Port 3000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /F /PID %%a 2>nul

echo Stopping Backend (Port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a 2>nul

echo Stopping Recommendation System (Port 8001)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do taskkill /F /PID %%a 2>nul

echo Stopping AI Service (Port 8002)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do taskkill /F /PID %%a 2>nul

echo Stopping Alternative ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /F /PID %%a 2>nul

echo.
echo Stopping Node.js processes...
taskkill /F /IM node.exe 2>nul

echo.
echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul

echo.
echo ======================================
echo All services stopped!
echo You can now restart them fresh.
echo ======================================
pause
