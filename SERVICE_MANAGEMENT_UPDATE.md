# eCommerce-AI Service Management Update

## Overview
Updated all service management scripts to include the new Whisper API service for voice chat transcription.

## Services Configuration

### All Services (4 total):
1. **Backend (Flask)** - Port 8000
   - File: `BE/flask_server.py`
   - Main API server

2. **Whisper API (Transcription)** - Port 5005
   - File: `BE/whisper_api.py`
   - Voice transcription using OpenAI Whisper large-v2 API

3. **Frontend (React)** - Port 3000
   - Directory: `FE/`
   - Command: `npm start`

4. **Recommendation System (Flask)** - Port 8001
   - File: `Recommendation_System/flask_recommendation_server.py`
   - Product recommendations and semantic search

## Updated Files

### ✅ Start Service Files

#### 1. `start_all_services.py` (Cross-platform Python)
- ✅ Already included Whisper API service
- ✅ Fixed duplicate backend starting code
- ✅ Updated service descriptions and URLs
- **Usage**: `python start_all_services.py`

#### 2. `start_all_services.ps1` (PowerShell)
- ✅ Added Whisper API service startup
- ✅ Updated service URLs display
- ✅ Fixed backend file reference (flask_server.py)
- **Usage**: `.\start_all_services.ps1`

#### 3. `start_all_services.bat` (Windows Batch)
- ✅ Already included Whisper API service
- ✅ Updated URLs display to include Whisper API
- **Usage**: `start_all_services.bat`

### ✅ Stop Service Files

#### 1. `stop_all_services.py` (Cross-platform Python)
- ✅ Already included port 5005 for Whisper API
- **Usage**: `python stop_all_services.py`

#### 2. `stop_all_services.ps1` (PowerShell)
- ✅ Added port 5005 for Whisper API service
- **Usage**: `.\stop_all_services.ps1`

#### 3. `stop_all_services.bat` (Windows Batch)
- ✅ Should be checked and updated if needed

## How to Start All Services

### Option 1: PowerShell (Recommended for Windows)
```powershell
.\start_all_services.ps1
```

### Option 2: Python (Cross-platform)
```bash
python start_all_services.py
```

### Option 3: Batch File (Windows)
```cmd
start_all_services.bat
```

## How to Stop All Services

### Option 1: PowerShell
```powershell
.\stop_all_services.ps1
```

### Option 2: Python
```bash
python stop_all_services.py
```

### Option 3: Batch File
```cmd
stop_all_services.bat
```

## Service URLs (When Running)

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Whisper API**: http://localhost:5005/transcribe
- **Recommendations**: http://localhost:8001

## Dependencies

Ensure all dependencies are installed:

### Backend & Whisper API
```bash
cd BE
pip install -r requirements.txt
```

### Frontend
```bash
cd FE
npm install
```

### Recommendation System
```bash
cd Recommendation_System
pip install -r requirements.txt
```

## Environment Variables

Make sure the `.env` file in the `BE` directory contains:
```
OPENAI_API_KEY=your_openai_api_key_here
FIREBASE_PROJECT_ID=your_firebase_project_id
```

## Testing the Configuration

Run the configuration test:
```bash
python test_service_configuration.py
```

This will verify all necessary files and directories exist.

## Notes

- Each service runs in its own terminal/console window
- All services start automatically with proper dependencies
- The Whisper API now uses OpenAI's cloud API instead of local models
- Services can be stopped individually or all at once
- Windows users can use any of the three methods (PowerShell recommended)
- macOS/Linux users should use the Python scripts
