#!/usr/bin/env python3
"""
FastAPI Backend Server Launcher
===============================

This script provides an easy way to start the eCommerce FastAPI backend server.
It includes automatic dependency installation and server startup.

Usage:
    python run_BE.py

Features:
    - Automatic dependency check and installation
    - Firebase initialization verification
    - Server startup with hot reload
    - Colored console output
    - Error handling and recovery

Server Details:
    - URL: http://localhost:8000
    - API Docs: http://localhost:8000/docs (Swagger UI)
    - ReDoc: http://localhost:8000/redoc
    - Health Check: http://localhost:8000/health
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# ANSI color codes for console output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(message, color=Colors.WHITE):
    """Print colored message to console"""
    print(f"{color}{message}{Colors.END}")

def print_banner():
    """Print startup banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                   🚀 eCommerce FastAPI Backend               ║
║                      Starting Server...                     ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print_colored("❌ Error: Python 3.8 or higher is required", Colors.RED)
        print_colored(f"Current version: {sys.version}", Colors.YELLOW)
        return False
    
    print_colored(f"✅ Python version: {sys.version.split()[0]}", Colors.GREEN)
    return True

def install_dependencies():
    """Install required dependencies"""
    print_colored("📦 Checking and installing dependencies...", Colors.BLUE)
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print_colored("⚠️  requirements.txt not found, installing basic FastAPI dependencies", Colors.YELLOW)
        basic_deps = [
            "fastapi==0.85.0",
            "uvicorn[standard]==0.20.0",
            "firebase-admin==6.2.0",
            "pydantic==1.10.12",
            "python-dotenv==1.0.0",
            "httpx==0.25.2",
            "python-multipart==0.0.6"
        ]
        
        for dep in basic_deps:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print_colored(f"⚠️  Failed to install {dep}", Colors.YELLOW)
    else:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print_colored("✅ Dependencies installed successfully", Colors.GREEN)
        except subprocess.CalledProcessError as e:
            print_colored(f"⚠️  Warning: Some dependencies might not be installed properly", Colors.YELLOW)
            print_colored("You can manually run: pip install -r requirements.txt", Colors.YELLOW)

def check_firebase_config():
    """Check if Firebase configuration exists"""
    firebase_files = [
        "serviceAccountKey.json",
        "firebase_config.py"
    ]
    
    missing_files = []
    for file in firebase_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print_colored("⚠️  Firebase configuration files missing:", Colors.YELLOW)
        for file in missing_files:
            print_colored(f"   - {file}", Colors.YELLOW)
        print_colored("Firebase features may not work properly", Colors.YELLOW)
    else:
        print_colored("✅ Firebase configuration found", Colors.GREEN)

def start_server():
    """Start the FastAPI server"""
    print_colored("🌟 Starting FastAPI server...", Colors.MAGENTA)
    print_colored("📍 Server URLs:", Colors.CYAN)
    print_colored("   • Main API: http://localhost:8000", Colors.WHITE)
    print_colored("   • API Docs: http://localhost:8000/docs", Colors.WHITE)
    print_colored("   • ReDoc: http://localhost:8000/redoc", Colors.WHITE)
    print_colored("   • Health Check: http://localhost:8000/health", Colors.WHITE)
    print()
    print_colored("🛑 Press Ctrl+C to stop the server", Colors.YELLOW)
    print_colored("=" * 60, Colors.CYAN)
    
    try:
        # Start uvicorn with the FastAPI app (try main.py first, then fastapi_server.py)
        if os.path.exists("main.py"):
            print_colored("🎯 Using main.py FastAPI server", Colors.CYAN)
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload",
                "--reload-dir", ".",
                "--log-level", "info"
            ])
        elif os.path.exists("fastapi_server.py"):
            print_colored("🎯 Using fastapi_server.py", Colors.CYAN)
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "fastapi_server:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload",
                "--reload-dir", ".",
                "--log-level", "info"
            ])
        else:
            raise FileNotFoundError("No FastAPI server file found")
    except KeyboardInterrupt:
        print_colored("\n🛑 Server stopped by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Error starting server: {e}", Colors.RED)
        print_colored("Trying alternative startup methods...", Colors.YELLOW)
        
        # Fallback: try different server files
        fallback_files = ["main.py", "fastapi_server.py", "start_simple.py"]
        for server_file in fallback_files:
            if os.path.exists(server_file):
                try:
                    print_colored(f"🔄 Trying {server_file}...", Colors.BLUE)
                    subprocess.run([sys.executable, server_file])
                    break
                except Exception as e2:
                    print_colored(f"❌ {server_file} failed: {e2}", Colors.RED)
                    continue
        else:
            print_colored("❌ All startup methods failed", Colors.RED)
            print_colored("Please check the error messages above and try again", Colors.RED)

def main():
    """Main function"""
    print_banner()
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print_colored(f"📁 Working directory: {script_dir}", Colors.BLUE)
    
    # Check system requirements
    if not check_python_version():
        return
    
    # Install dependencies
    install_dependencies()
    
    # Check Firebase configuration
    check_firebase_config()
    
    # Wait a moment for better UX
    time.sleep(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
