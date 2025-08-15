#!/usr/bin/env python3
"""
Stop All Services Script
========================
This script stops all running services for the eCommerce-AI project:
- Frontend (React) - Port 3000
- Backend (Flask) - Port 8000  
- Recommendation System (Flask) - Port 8001
- AI Service - Port 8002 (if running)

Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import platform
import time
from typing import List, Dict, Tuple

# Known ports used by the eCommerce-AI project
KNOWN_PORTS = {
    3000: "Frontend (React)",
    8000: "Backend (Flask)",
    8001: "Recommendation System (Flask)",
    8002: "AI Service",
    5005: "Transcribing Service (Whisper API)",
    5000: "Flask (default)",
    5173: "Vite Dev Server",
    4000: "Alternative Frontend"
}

class ServiceStopper:
    """Cross-platform service stopper for eCommerce-AI project"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.stopped_services = []
        
    def get_processes_on_port(self, port: int) -> List[Dict]:
        """Get processes running on a specific port"""
        processes = []
        
        try:
            if self.os_type == "windows":
                # Windows: Use netstat and tasklist
                cmd = f'netstat -ano | findstr :{port}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 5 and f':{port}' in parts[1]:
                            pid = parts[-1]
                            if pid.isdigit():
                                # Get process name
                                name_cmd = f'tasklist /FI "PID eq {pid}" /FO CSV /NH'
                                name_result = subprocess.run(name_cmd, shell=True, capture_output=True, text=True)
                                process_name = "Unknown"
                                if name_result.stdout:
                                    csv_line = name_result.stdout.strip().strip('"')
                                    if csv_line:
                                        process_name = csv_line.split('","')[0].strip('"')
                                
                                processes.append({
                                    'pid': int(pid),
                                    'name': process_name,
                                    'port': port
                                })
            else:
                # macOS/Linux: Use lsof
                cmd = f'lsof -i :{port} -t'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.stdout:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.isdigit():
                            # Get process name
                            name_cmd = f'ps -p {pid} -o comm='
                            name_result = subprocess.run(name_cmd, shell=True, capture_output=True, text=True)
                            process_name = name_result.stdout.strip() if name_result.stdout else "Unknown"
                            
                            processes.append({
                                'pid': int(pid),
                                'name': process_name,
                                'port': port
                            })
                            
        except Exception as e:
            print(f"⚠️  Error checking port {port}: {e}")
            
        return processes
    
    def kill_process(self, pid: int, name: str = "Unknown") -> bool:
        """Kill a process by PID"""
        try:
            if self.os_type == "windows":
                cmd = f'taskkill /F /PID {pid}'
            else:
                cmd = f'kill -9 {pid}'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Stopped process: {name} (PID: {pid})")
                return True
            else:
                print(f"❌ Failed to stop process: {name} (PID: {pid})")
                return False
                
        except Exception as e:
            print(f"❌ Error killing process {pid}: {e}")
            return False
    
    def stop_port(self, port: int) -> bool:
        """Stop all processes on a specific port"""
        service_name = KNOWN_PORTS.get(port, f"Port {port}")
        print(f"🔍 Checking {service_name}...")
        
        processes = self.get_processes_on_port(port)
        
        if not processes:
            print(f"✅ No processes running on port {port}")
            return True
        
        print(f"📋 Found {len(processes)} process(es) on port {port}")
        success = True
        
        for process in processes:
            if self.kill_process(process['pid'], process['name']):
                self.stopped_services.append({
                    'port': port,
                    'service': service_name,
                    'pid': process['pid'],
                    'name': process['name']
                })
            else:
                success = False
        
        return success
    
    def stop_all_known_ports(self) -> bool:
        """Stop all processes on known eCommerce-AI ports"""
        print("🛑 Stopping all eCommerce-AI services...")
        print("=" * 50)
        
        overall_success = True
        
        for port, service_name in KNOWN_PORTS.items():
            if not self.stop_port(port):
                overall_success = False
            print()  # Add spacing between ports
        
        return overall_success
    
    def stop_nodejs_processes(self) -> bool:
        """Stop all Node.js processes (for React/Vite servers)"""
        print("🔍 Stopping Node.js processes...")
        
        try:
            if self.os_type == "windows":
                # Stop all node.exe processes
                cmd = 'taskkill /F /IM node.exe'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if "SUCCESS" in result.stdout:
                    print("✅ Stopped Node.js processes")
                    return True
                else:
                    print("✅ No Node.js processes found")
                    return True
            else:
                # Stop all node processes
                cmd = 'pkill -f node'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                print("✅ Stopped Node.js processes")
                return True
                
        except Exception as e:
            print(f"⚠️  Error stopping Node.js processes: {e}")
            return False
    
    def stop_python_flask_processes(self) -> bool:
        """Stop Python Flask processes"""
        print("🔍 Stopping Python Flask processes...")
        
        try:
            if self.os_type == "windows":
                # Find and kill Python processes running Flask
                cmd = 'wmic process where "name=\'python.exe\' and commandline like \'%flask%\'" get processid /value'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                pids = []
                for line in result.stdout.split('\n'):
                    if 'ProcessId=' in line:
                        pid = line.split('=')[1].strip()
                        if pid.isdigit():
                            pids.append(int(pid))
                
                if pids:
                    for pid in pids:
                        self.kill_process(pid, "Python Flask")
                    return True
                else:
                    print("✅ No Python Flask processes found")
                    return True
            else:
                # Stop Python processes with flask in command line
                cmd = "pkill -f 'python.*flask'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                print("✅ Stopped Python Flask processes")
                return True
                
        except Exception as e:
            print(f"⚠️  Error stopping Python Flask processes: {e}")
            return False
    
    def print_summary(self):
        """Print summary of stopped services"""
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        
        if self.stopped_services:
            print(f"🛑 Stopped {len(self.stopped_services)} service(s):")
            for service in self.stopped_services:
                print(f"  • {service['service']} (Port {service['port']}) - PID {service['pid']}")
        else:
            print("✅ No services were running (or all were already stopped)")
        
        print("\n💡 All eCommerce-AI services have been stopped")
        print("🚀 You can now restart them fresh when needed")


def main():
    """Main function to stop all services"""
    print("🛑 eCommerce-AI Service Stopper")
    print("=" * 35)
    print("This will stop all running services:")
    print("• Frontend (React/Vite)")
    print("• Backend (Flask)")  
    print("• Recommendation System")
    print("• AI Service")
    print("• Any Node.js/Python processes")
    
    # Ask for confirmation
    confirm = input("\nDo you want to stop all services? (type 'yes' to confirm): ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled")
        return
    
    stopper = ServiceStopper()
    
    # Stop services on known ports
    stopper.stop_all_known_ports()
    
    # Stop Node.js processes (for frontend)
    stopper.stop_nodejs_processes()
    
    # Stop Python Flask processes
    stopper.stop_python_flask_processes()
    
    # Wait a moment for processes to fully stop
    print("\n⏳ Waiting for processes to fully stop...")
    time.sleep(2)
    
    # Print summary
    stopper.print_summary()


if __name__ == "__main__":
    main()
