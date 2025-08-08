@echo off
echo ======================================
echo  eCommerce-AI Service Starter
echo ======================================
echo Starting all services...
echo.

REM Check if directories exist
if not exist "BE" (
    echo ❌ Backend directory 'BE' not found!
    pause
    exit /b 1
)

if not exist "FE" (
    echo ❌ Frontend directory 'FE' not found!
    pause
    exit /b 1
)

if not exist "Recommendation_System" (
    echo ❌ Recommendation System directory not found!
    pause
    exit /b 1
)

echo 🚀 Starting Backend (Flask) on port 8000...
start "Backend Server" cmd /k "cd BE ; python flask_server.py"

echo 🚀 Starting Frontend (React) on port 3000...
start "Frontend Server" cmd /k "cd FE ; npm start"

echo 🚀 Starting Recommendation System on port 8001...
start "Recommendation Server" cmd /k "cd Recommendation_System && python flask_recommendation_server.py"

echo.
echo ======================================
echo ✅ All services are starting!
echo ======================================
echo.
echo 🌐 Access URLs:
echo   Frontend:     http://localhost:3000
echo   Backend:      http://localhost:8000
echo   Recommendations: http://localhost:8001
echo.
echo 💡 Each service runs in its own window
echo 💡 Close the windows to stop services
echo ======================================
pause
