#!/usr/bin/env python3
"""
Port Destroyer - Kill All Running Development Services
=====================================================

This script forcefully terminates all processes running on development ports.
Use with caution as it will kill all Node.js and Python processes.

Usage:
    python destroy_running_port.py

Features:
    - Kills processes on specific ports
    - Terminates all Node.js and Python processes
    - Multiple termination methods
    - Colored console output
    - Safety confirmations
    - Cross-platform support
"""

import subprocess
import sys
import os
import time
import socket
from typing import List, Dict, Optional

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
    """Print destruction banner"""
    banner = f"""
{Colors.RED}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    💥 Port Destroyer                        ║
║              Kill All Development Services                  ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)

def check_port(port: int) -> bool:
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except Exception:
        return False

def get_process_pid_by_port_windows(port: int) -> List[str]:
    """Get PIDs using a port on Windows"""
    pids = []
    try:
        cmd = f'netstat -ano | findstr :{port}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            pids = extract_pids_from_netstat(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    
    return pids

def extract_pids_from_netstat(netstat_output: str) -> List[str]:
    """Extract PIDs from netstat output"""
    pids = []
    lines = netstat_output.strip().split('\n')
    for line in lines:
        if 'LISTENING' in line:
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid not in pids and pid.isdigit():
                    pids.append(pid)
    return pids

def get_process_pid_by_port_unix(port: int) -> List[str]:
    """Get PIDs using a port on Unix/Linux/macOS"""
    pids = []
    try:
        cmd = f'lsof -ti :{port}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            pids = [pid for pid in pids if pid.isdigit()]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    
    return pids

def get_process_pids_by_port(port: int) -> List[str]:
    """Get PIDs using a port"""
    if os.name == 'nt':  # Windows
        return get_process_pid_by_port_windows(port)
    else:  # Unix/Linux/macOS
        return get_process_pid_by_port_unix(port)

def kill_process_by_pid_windows(pid: str) -> bool:
    """Kill process by PID on Windows"""
    try:
        subprocess.run(['taskkill', '/F', '/PID', pid], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def kill_process_by_pid_unix(pid: str) -> bool:
    """Kill process by PID on Unix/Linux/macOS"""
    try:
        subprocess.run(['kill', '-9', pid], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def kill_process_by_pid(pid: str) -> bool:
    """Kill process by PID"""
    if os.name == 'nt':  # Windows
        return kill_process_by_pid_windows(pid)
    else:  # Unix/Linux/macOS
        return kill_process_by_pid_unix(pid)

def kill_processes_by_name_windows(process_names: List[str]) -> Dict[str, bool]:
    """Kill processes by name on Windows"""
    results = {}
    for process_name in process_names:
        try:
            subprocess.run(['taskkill', '/F', '/IM', process_name], 
                          capture_output=True, stderr=subprocess.DEVNULL)
            results[process_name] = True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            results[process_name] = False
    
    return results

def kill_processes_by_name_unix(process_names: List[str]) -> Dict[str, bool]:
    """Kill processes by name on Unix/Linux/macOS"""
    results = {}
    for process_name in process_names:
        try:
            subprocess.run(['pkill', '-f', process_name], 
                          capture_output=True, stderr=subprocess.DEVNULL)
            results[process_name] = True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            results[process_name] = False
    
    return results

def kill_processes_by_name(process_names: List[str]) -> Dict[str, bool]:
    """Kill processes by name"""
    if os.name == 'nt':  # Windows
        return kill_processes_by_name_windows(process_names)
    else:  # Unix/Linux/macOS
        return kill_processes_by_name_unix(process_names)

def scan_running_ports() -> Dict[int, List[str]]:
    """Scan for running processes on development ports"""
    ports_to_check = [3000, 8000, 8001, 5000, 5173, 4000, 3001]
    running_ports = {}
    
    print_colored("🔍 Scanning for running processes...", Colors.BLUE)
    
    for port in ports_to_check:
        if check_port(port):
            pids = get_process_pids_by_port(port)
            if pids:
                running_ports[port] = pids
                service_name = {
                    3000: "React Frontend",
                    8000: "Backend API",
                    8001: "Recommendation System",
                    5000: "Flask Alternative",
                    5173: "Vite Development",
                    4000: "Development Server",
                    3001: "Alternative Frontend"
                }.get(port, f"Service on {port}")
                
                print_colored(f"   🎯 Found {service_name} on port {port} (PIDs: {', '.join(pids)})", Colors.YELLOW)
    
    return running_ports

def kill_by_ports(running_ports: Dict[int, List[str]]) -> int:
    """Kill processes by specific ports"""
    killed_count = 0
    
    if not running_ports:
        print_colored("✅ No processes found on development ports", Colors.GREEN)
        return 0
    
    print_colored("🎯 Killing processes by port...", Colors.MAGENTA)
    
    for port, pids in running_ports.items():
        service_name = {
            3000: "React Frontend",
            8000: "Backend API", 
            8001: "Recommendation System",
            5000: "Flask Alternative",
            5173: "Vite Development",
            4000: "Development Server",
            3001: "Alternative Frontend"
        }.get(port, f"Service on {port}")
        
        print_colored(f"   💥 Killing {service_name} (port {port})...", Colors.RED)
        
        for pid in pids:
            if kill_process_by_pid(pid):
                print_colored(f"      ✅ Killed PID {pid}", Colors.GREEN)
                killed_count += 1
            else:
                print_colored(f"      ❌ Failed to kill PID {pid}", Colors.RED)
    
    return killed_count

def kill_by_process_names() -> Dict[str, bool]:
    """Kill processes by common development process names"""
    print_colored("🔥 Killing processes by name...", Colors.MAGENTA)
    
    process_names = []
    if os.name == 'nt':  # Windows
        process_names = ['node.exe', 'python.exe', 'uvicorn.exe']
    else:  # Unix/Linux/macOS
        process_names = ['node', 'python', 'python3', 'uvicorn']
    
    results = kill_processes_by_name(process_names)
    
    for process_name, success in results.items():
        if success:
            print_colored(f"   💥 Terminated all {process_name} processes", Colors.RED)
        else:
            print_colored(f"   ⚠️  No {process_name} processes found or failed to kill", Colors.YELLOW)
    
    return results

def verify_cleanup() -> bool:
    """Verify that ports are now free"""
    print_colored("🔍 Verifying cleanup...", Colors.BLUE)
    time.sleep(2)  # Wait for processes to fully terminate
    
    ports_to_check = [3000, 8000, 8001, 5000, 5173, 4000, 3001]
    still_running = []
    
    for port in ports_to_check:
        if check_port(port):
            still_running.append(port)
    
    if still_running:
        print_colored(f"⚠️  Some ports are still in use: {', '.join(map(str, still_running))}", Colors.YELLOW)
        return False
    else:
        print_colored("✅ All development ports are now free!", Colors.GREEN)
        return True

def show_confirmation() -> bool:
    """Show confirmation dialog"""
    print_colored("⚠️  WARNING: This will kill ALL Node.js and Python processes!", Colors.YELLOW)
    print_colored("This includes:", Colors.WHITE)
    print_colored("   • React development servers", Colors.WHITE)
    print_colored("   • FastAPI/Flask backends", Colors.WHITE)
    print_colored("   • Any other Node.js/Python applications", Colors.WHITE)
    print()
    
    response = input("Are you sure you want to continue? (y/N): ").strip().lower()
    return response in ['y', 'yes']

def main():
    """Main function"""
    print_banner()
    
    # Show warning and get confirmation
    if not show_confirmation():
        print_colored("🛑 Operation cancelled by user", Colors.YELLOW)
        return
    
    print()
    print_colored("🚀 Starting port destruction sequence...", Colors.RED)
    print()
    
    # Scan for running processes
    running_ports = scan_running_ports()
    
    total_killed = 0
    
    # Method 1: Kill by specific ports
    if running_ports:
        print()
        killed_by_port = kill_by_ports(running_ports)
        total_killed += killed_by_port
    
    # Method 2: Kill by process names (more aggressive)
    print()
    kill_by_process_names()
    
    # Verify cleanup
    print()
    cleanup_successful = verify_cleanup()
    
    # Summary
    print()
    print_colored("=" * 60, Colors.CYAN)
    
    if cleanup_successful:
        print_colored("✅ Port destruction completed successfully!", Colors.GREEN)
        print_colored("🚀 All development ports are now available", Colors.GREEN)
        print_colored("💡 You can now start fresh services:", Colors.BLUE)
        print_colored("   • Backend: python BE/run_BE.py", Colors.WHITE)
        print_colored("   • Frontend: python FE/run_FE.py", Colors.WHITE)
    else:
        print_colored("⚠️  Some processes may still be running", Colors.YELLOW)
        print_colored("💡 Try running the script again or manually check processes", Colors.BLUE)
    
    print_colored("=" * 60, Colors.CYAN)

if __name__ == "__main__":
    main()
