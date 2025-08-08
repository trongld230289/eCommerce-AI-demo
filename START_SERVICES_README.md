# Start All Services - eCommerce-AI

Start all your eCommerce-AI services (Backend, Frontend, Recommendation System) with **one command**!

## 🚀 Quick Start

### Option 1: Windows Batch File (Recommended for Windows)
```cmd
start_all_services.bat
```

### Option 2: PowerShell Script (Advanced Windows)
```powershell
./start_all_services.ps1
```

### Option 3: Python Script (Cross-platform)
```bash
python start_all_services.py
```

## 📋 What Gets Started

| Service | Port | Command | URL |
|---------|------|---------|-----|
| **Backend** | 8000 | `python app.py` | http://localhost:8000 |
| **Frontend** | 3000 | `npm start` | http://localhost:3000 |
| **Recommendation System** | 8001 | `python flask_recommendation_server.py` | http://localhost:8001 |
| **AI Service** (optional) | 8002 | `python main.py` | http://localhost:8002 |

## 🔧 Script Details

### `start_all_services.bat` ⭐ Recommended
- **Windows only**: Simple and fast
- **Separate windows**: Each service runs in its own console window
- **Easy to monitor**: See logs for each service separately
- **Easy to stop**: Close individual windows or use Ctrl+C

### `start_all_services.ps1`
- **Windows PowerShell**: Advanced with error checking
- **Colorful output**: Nice formatting and status messages
- **Automatic detection**: Finds main files automatically
- **Optional services**: Gracefully handles missing AI Service

### `start_all_services.py`
- **Cross-platform**: Works on Windows, macOS, Linux
- **Smart detection**: Automatically finds main files
- **Integrated monitoring**: Keeps all services in one terminal
- **Signal handling**: Ctrl+C stops all services cleanly

## 🎯 Development Workflow

### Quick Start for Development
```bash
# Start all services
start_all_services.bat

# Wait for services to start (30-60 seconds)
# Then access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - Recommendations: http://localhost:8001
```

### Making Changes
```bash
# Services auto-reload on file changes:
# - Frontend: React hot reload ✅
# - Backend: Manual restart needed 🔄
# - Recommendation: Manual restart needed 🔄

# To restart backend only:
# Close backend window, then:
cd BE && python app.py
```

### Complete Restart
```bash
# Stop all services
python stop_all_services.py

# Start all services fresh
start_all_services.bat
```

## 📁 Directory Structure Expected

```
eCommerce-AI/
├── BE/                     # Backend Flask application
│   ├── app.py             # Main backend file
│   └── ...
├── FE/                     # Frontend React application  
│   ├── package.json       # Required for npm start
│   └── ...
├── Recommendation_System/ # Recommendation service
│   ├── flask_recommendation_server.py
│   └── ...
├── AI_Service/            # Optional AI service
│   ├── main.py
│   └── ...
└── start_all_services.*   # Startup scripts
```

## ⚠️ Prerequisites

### For Backend & Recommendation System
- **Python 3.7+** installed
- **Dependencies installed**:
  ```bash
  cd BE && pip install -r requirements.txt
  cd Recommendation_System && pip install -r requirements.txt
  ```

### For Frontend
- **Node.js & npm** installed
- **Dependencies installed**:
  ```bash
  cd FE && npm install
  ```

## 🔍 Troubleshooting

### Service Won't Start
```
❌ Backend directory 'BE' not found!
```
**Solution**: Make sure you're running from the eCommerce-AI root directory

### Port Already in Use
```
Error: Port 3000 is already in use
```
**Solution**: Stop existing services first
```bash
python stop_all_services.py
```

### Missing Dependencies
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Install dependencies
```bash
cd BE && pip install -r requirements.txt
cd Recommendation_System && pip install -r requirements.txt
cd FE && npm install
```

### Permission Issues (PowerShell)
```
Execution policy error
```
**Solution**: Allow script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🌐 Service URLs & Testing

### Frontend (React)
- **URL**: http://localhost:3000
- **Test**: Should show the eCommerce homepage
- **Features**: Product browsing, search, cart, recommendations

### Backend (Flask API)
- **URL**: http://localhost:8000
- **Test**: http://localhost:8000/health (should return status)
- **API Docs**: Check BE/README.md for endpoints

### Recommendation System
- **URL**: http://localhost:8001  
- **Test**: http://localhost:8001/health
- **Features**: User events, recommendations, semantic search


## 💡 Pro Tips

### Development Mode
```bash
# Start all services in development mode
start_all_services.bat

# Keep terminals open to see logs
# Frontend auto-reloads on changes
# Backend/Rec need manual restart for changes
```

### Production Testing
```bash
# Use Python script for integrated logging
python start_all_services.py

# All logs in one terminal
# Ctrl+C stops all services cleanly
```

### Service Dependencies
1. **Start Backend first** (other services depend on it)
2. **Wait 10-20 seconds** between starting services
3. **Check logs** for "Running on port..." messages
4. **Test APIs** before using frontend

## 🔄 Related Commands

- **Stop all services**: `python stop_all_services.py`
- **Clear all data**: `python clear_all_data.py` (BE and Recommendation)
- **Individual start**: `cd SERVICE_DIR && python main_file.py`

---

**🎉 Happy Development!** All your eCommerce-AI services are now just one command away!
