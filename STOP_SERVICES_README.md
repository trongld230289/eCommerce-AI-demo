# Stop All Services - eCommerce-AI

This directory contains scripts to stop all running services for the eCommerce-AI project with **one command**.

## 🚀 Quick Usage

### Option 1: Python Script (Recommended - Cross-platform)
```bash
python stop_all_services.py
```

### Option 2: Windows Batch File (Simple)
```cmd
stop_all_services.bat
```

### Option 3: PowerShell Script (Advanced Windows)
```powershell
./stop_all_services.ps1
```

## 📋 What Gets Stopped

The scripts will stop all processes running on these ports:

| Port | Service | Description |
|------|---------|-------------|
| 3000 | Frontend | React development server |
| 8000 | Backend | Flask API server |
| 8001 | Recommendation System | Flask recommendation service |
| 8002 | AI Service | AI/ML service (if running) |
| 5000 | Flask Default | Default Flask port |
| 5173 | Vite Dev Server | Alternative frontend server |

Additionally stops:
- **All Node.js processes** (for React/Vite servers)
- **All Python Flask processes** (for backend services)

## 🔧 Scripts Details

### `stop_all_services.py`
- **Cross-platform**: Works on Windows, macOS, Linux
- **Smart detection**: Finds processes by port and name
- **Detailed output**: Shows what was stopped
- **Safe**: Asks for confirmation before stopping
- **Comprehensive**: Handles edge cases and multiple processes

### `stop_all_services.bat`
- **Windows only**: Simple batch file
- **Fast**: Quick execution
- **No dependencies**: Uses built-in Windows commands
- **Silent**: Minimal output

### `stop_all_services.ps1`
- **Windows PowerShell**: Advanced Windows script
- **Colorful output**: Nice formatting and colors
- **Smart detection**: Uses PowerShell cmdlets
- **User-friendly**: Clear status messages

## 🎯 Use Cases

### Development Workflow
```bash
# Stop all services
python stop_all_services.py

# Make changes to your code

# Restart services fresh
cd FE && npm start          # Frontend
cd BE && python app.py     # Backend
cd Recommendation_System && python flask_recommendation_server.py  # Recommendations
```

### Troubleshooting
When services are stuck or ports are busy:
```bash
python stop_all_services.py
# All ports are now free for fresh restart
```

### Clean Shutdown
Before system restart or when done developing:
```bash
python stop_all_services.py
# All eCommerce-AI services cleanly stopped
```

## ⚠️ Notes

- **PowerShell Execution Policy**: On Windows, you might need to run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **Admin Rights**: Scripts may require administrator privileges on some systems

- **Confirmation**: All scripts ask for confirmation before stopping services

- **Process Detection**: Scripts are designed to be safe and only stop eCommerce-AI related processes

## 🔍 Verification

After running the script, you can verify all services are stopped:

```bash
# Check if ports are free
netstat -ano | findstr "3000 8000 8001"  # Windows
lsof -i :3000,8000,8001                  # macOS/Linux
```

Should return no results if all services are stopped.

## 🛠️ Customization

To add more ports or services, edit the `KNOWN_PORTS` dictionary in `stop_all_services.py`:

```python
KNOWN_PORTS = {
    3000: "Frontend (React)",
    8000: "Backend (Flask)",
    8001: "Recommendation System (Flask)",
    8002: "AI Service",
    # Add your custom ports here
    9000: "Your Custom Service"
}
```
