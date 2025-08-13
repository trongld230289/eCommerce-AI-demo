@echo off
REM ========================================
REM React Frontend Startup Script (Batch)
REM ========================================
REM Simple batch script to start the React frontend
REM Usage: run_FE.bat

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                   ⚛️  eCommerce React Frontend               ║
echo ║                      Starting Server...                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Change to the FE directory
cd /d "%~dp0"
echo 📁 Working directory: %CD%

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js is installed
node --version

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found
    pause
    exit /b 1
)

echo ✅ npm is installed
npm --version

REM Check if package.json exists
if not exist "package.json" (
    echo ❌ package.json not found
    pause
    exit /b 1
)

echo ✅ package.json found

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ Dependencies already installed
)

REM Kill any existing node processes (optional)
taskkill /F /IM "node.exe" >nul 2>&1

echo.
echo 🌟 Starting React development server...
echo 📍 Server will be available at: http://localhost:3000
echo 🛑 Press Ctrl+C to stop the server
echo ═══════════════════════════════════════════════════════════════
echo.

REM Start the React development server
npm start

echo.
echo 🛑 Server stopped
pause
