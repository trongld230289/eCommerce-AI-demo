#!/usr/bin/env python3
"""
Startup script for the eCommerce Backend API

This script will:
1. Install dependencies
2. Set up Firebase configuration
3. Migrate data to Firebase
4. Start the API server
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        sys.exit(1)

def main():
    print("🎯 Starting eCommerce Backend Setup")
    print("=" * 50)
    
    # Change to BE directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠️  No .env file found. Please create one using .env.example as template")
        print("   You need to configure Firebase credentials before running the server")
        sys.exit(1)
    
    # Run data migration
    print("\n🔄 Running data migration...")
    try:
        subprocess.run([sys.executable, "migrate_data.py"], check=True)
        print("✅ Data migration completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Data migration failed: {e}")
        print("   The server will still start, but the database might be empty")
    
    # Start the server
    print("\n🚀 Starting the API server...")
    print("   Server will be available at: http://localhost:8000")
    print("   API documentation at: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
