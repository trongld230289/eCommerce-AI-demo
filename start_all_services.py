#!/usr/bin/env python3
"""
Start All Services Script
=========================
This script starts all eCommerce-AI services with one command:
- Backend (Flask) - Port 8000
- Whisper API (Transcription) - Port 5005
- Frontend (React) - Port 3000  
- Recommendation System (Flask) - Port 8001

Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import platform
import time
import os
import threading
from typing import List, Dict
import signal

class ServiceStarter:
    """Cross-platform service starter for eCommerce-AI project"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.processes = []
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
    def check_directory_exists(self, path: str) -> bool:
        """Check if a directory exists"""
        return os.path.exists(path) and os.path.isdir(path)
    
    def check_file_exists(self, path: str) -> bool:
        """Check if a file exists"""
        return os.path.exists(path) and os.path.isfile(path)
    
    def start_backend(self) -> bool:
        """Start the Backend Flask service"""
        print("🚀 Starting Backend (Flask) on port 8000...")

        be_path = os.path.join(self.project_root, "BE")
        if not self.check_directory_exists(be_path):
            print(f"❌ Backend directory not found: {be_path}")
            return False

        # Check for main files
        main_files = ["flask_server.py"]
        main_file = None
        for file in main_files:
            file_path = os.path.join(be_path, file)
            if self.check_file_exists(file_path):
                main_file = file
                break
        if not main_file:
            print(f"❌ No main file found in {be_path}")
            print(f"   Looking for: {', '.join(main_files)}")
            return False
        try:
            if self.os_type == "windows":
                cmd = f'cd /d "{be_path}" && python {main_file}'
                process = subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                process = subprocess.Popen([
                    "python", main_file
                ], cwd=be_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append({
                'name': 'Backend',
                'process': process,
                'port': 8000,
                'path': be_path,
                'file': main_file
            })
            print(f"✅ Backend started with {main_file}")
            # Start transcribing service (Whisper API)
            whisper_file = "whisper_api.py"
            whisper_path = os.path.join(be_path, whisper_file)
            if self.check_file_exists(whisper_path):
                print("🚀 Starting Transcribing Service (Whisper API) on port 5005...")
                if self.os_type == "windows":
                    cmd = f'cd /d "{be_path}" && python {whisper_file}'
                    whisper_proc = subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    whisper_proc = subprocess.Popen([
                        "python", whisper_file
                    ], cwd=be_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append({
                    'name': 'Transcribing Service',
                    'process': whisper_proc,
                    'port': 5005,
                    'path': be_path,
                    'file': whisper_file
                })
                print(f"✅ Transcribing Service started with {whisper_file}")
            else:
                print(f"❌ whisper_api.py not found in {be_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to start Backend or Transcribing Service: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """Start the Frontend React service"""
        print("🚀 Starting Frontend (React) on port 3000...")
        
        fe_path = os.path.join(self.project_root, "FE")
        
        if not self.check_directory_exists(fe_path):
            print(f"❌ Frontend directory not found: {fe_path}")
            return False
        
        # Check for package.json
        package_json = os.path.join(fe_path, "package.json")
        if not self.check_file_exists(package_json):
            print(f"❌ package.json not found in {fe_path}")
            return False
        
        try:
            if self.os_type == "windows":
                cmd = f'cd /d "{fe_path}" && npm start'
                process = subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                process = subprocess.Popen(
                    ["npm", "start"],
                    cwd=fe_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.processes.append({
                'name': 'Frontend',
                'process': process,
                'port': 3000,
                'path': fe_path,
                'file': 'npm start'
            })
            
            print("✅ Frontend started with npm start")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Frontend: {e}")
            return False
    
    def start_recommendation_system(self) -> bool:
        """Start the Recommendation System Flask service"""
        print("🚀 Starting Recommendation System (Flask) on port 8001...")
        
        rec_path = os.path.join(self.project_root, "Recommendation_System")
        
        if not self.check_directory_exists(rec_path):
            print(f"❌ Recommendation System directory not found: {rec_path}")
            return False
        
        # Check for main files
        main_files = ["flask_recommendation_server.py"]
        main_file = None
        
        for file in main_files:
            file_path = os.path.join(rec_path, file)
            if self.check_file_exists(file_path):
                main_file = file
                break
        
        if not main_file:
            print(f"❌ No main file found in {rec_path}")
            print(f"   Looking for: {', '.join(main_files)}")
            return False
        
        try:
            if self.os_type == "windows":
                cmd = f'cd /d "{rec_path}" && python {main_file}'
                process = subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                process = subprocess.Popen(
                    ["python", main_file],
                    cwd=rec_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.processes.append({
                'name': 'Recommendation System',
                'process': process,
                'port': 8001,
                'path': rec_path,
                'file': main_file
            })
            
            print(f"✅ Recommendation System started with {main_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Recommendation System: {e}")
            return False
    
    def wait_for_services(self):
        """Wait for services to start and provide status"""
        print("\n⏳ Waiting for services to start...")
        time.sleep(3)
        
        print("\n🔍 Service Status Check:")
        print("=" * 50)
        
        for service in self.processes:
            # Check if process is still running
            if service['process'].poll() is None:
                print(f"✅ {service['name']}: Running (Port {service['port']})")
            else:
                print(f"❌ {service['name']}: Failed to start")
        
        print("\n🌐 Access URLs:")
        print("=" * 30)
        print("🖥️  Frontend:     http://localhost:3000")
        print("🔧 Backend:      http://localhost:8000")
        print("🎤 Whisper API:  http://localhost:5005")
        print("🤖 Recommendations: http://localhost:8001")
        if any(s['name'] == 'AI Service' for s in self.processes):
            print("🧠 AI Service:   http://localhost:8002")
    
    def start_all_services(self) -> bool:
        """Start all eCommerce-AI services"""
        print("🚀 eCommerce-AI Service Starter")
        print("=" * 35)
        print("Starting all services...")
        print()
        
        success_count = 0
        
        # Start Backend
        if self.start_backend():
            success_count += 1
            time.sleep(1)
        
        # Start Frontend
        if self.start_frontend():
            success_count += 1
            time.sleep(1)
        
        # Start Recommendation System
        if self.start_recommendation_system():
            success_count += 1
            time.sleep(1)
        
        
        # Wait and check status
        self.wait_for_services()
        
        if success_count >= 3:  # BE, FE, Rec are required
            print(f"\n🎉 Successfully started {success_count} core services!")
            print("💡 Press Ctrl+C to stop all services")
            return True
        else:
            print(f"\n⚠️  Only {success_count}/3 core services started successfully")
            return False
    
    def stop_all_services(self):
        """Stop all started services"""
        print("\n🛑 Stopping all services...")
        
        for service in self.processes:
            try:
                if service['process'].poll() is None:
                    service['process'].terminate()
                    print(f"✅ Stopped {service['name']}")
                else:
                    print(f"⚠️  {service['name']} was already stopped")
            except Exception as e:
                print(f"❌ Error stopping {service['name']}: {e}")
        
        print("🎉 All services stopped!")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C signal"""
        print("\n\n🛑 Received interrupt signal...")
        self.stop_all_services()
        sys.exit(0)


def main():
    """Main function to start all services"""
    starter = ServiceStarter()
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, starter.signal_handler)
    
    print("🚀 eCommerce-AI Complete Startup")
    print("=" * 40)
    print("This will start:")
    print("• Backend (Flask) - Port 8000")
    print("• Whisper API (Transcription) - Port 5005")
    print("• Frontend (React) - Port 3000")
    print("• Recommendation System - Port 8001")
    
    # Ask for confirmation
    confirm = input("\nDo you want to start all services? (type 'yes' to confirm): ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled")
        return
    
    success = starter.start_all_services()
    
    if success:
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            starter.stop_all_services()
    else:
        print("\n⚠️  Some services failed to start. Check the errors above.")
        starter.stop_all_services()


if __name__ == "__main__":
    main()
