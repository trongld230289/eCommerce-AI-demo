#!/usr/bin/env python3
"""
Port Status Checker
==================

This script checks the status of all development ports used by the eCommerce application.
It provides a quick overview of which services are running and which ports are available.

Usage:
    python check_running_port.py

Features:
    - Checks all development ports (3000, 8000, 8001, 5000, 5173)
    - Colored console output
    - Service identification
    - Process information
    - Quick status overview
"""

import socket
import subprocess
import sys
import os
from typing import Dict, List, Optional

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
    """Print status check banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    🔍 Port Status Checker                   ║
║                  eCommerce Development Ports                ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)

def check_port(port: int, timeout: float = 1.0) -> bool:
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except Exception:
        return False

def get_process_info_windows(port: int) -> Optional[Dict]:
    """Get process information for Windows"""
    try:
        cmd = f'netstat -ano | findstr :{port}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        process_name = get_process_name_windows(pid)
                        return {'pid': pid, 'process': process_name, 'port': port}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return None

def get_process_name_windows(pid: str) -> str:
    """Get process name from PID on Windows"""
    try:
        cmd_name = f'tasklist /fi "PID eq {pid}" /fo csv /nh'
        name_result = subprocess.run(cmd_name, shell=True, capture_output=True, text=True)
        if name_result.stdout:
            return name_result.stdout.split(',')[0].strip('"')
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return 'Unknown'

def get_process_info_unix(port: int) -> Optional[Dict]:
    """Get process information for Unix/Linux/macOS"""
    try:
        cmd = f'lsof -i :{port} -t'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            pid = result.stdout.strip().split('\n')[0]
            process_name = get_process_name_unix(pid)
            return {'pid': pid, 'process': process_name, 'port': port}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return None

def get_process_name_unix(pid: str) -> str:
    """Get process name from PID on Unix"""
    try:
        cmd_name = f'ps -p {pid} -o comm='
        name_result = subprocess.run(cmd_name, shell=True, capture_output=True, text=True)
        if name_result.stdout:
            return name_result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return 'Unknown'

def get_process_info(port: int) -> Optional[Dict]:
    """Get process information for a port"""
    if os.name == 'nt':  # Windows
        return get_process_info_windows(port)
    else:  # Unix/Linux/macOS
        return get_process_info_unix(port)

def get_service_name(port: int) -> str:
    """Get service name based on port"""
    service_map = {
        3000: "React Frontend",
        8000: "Backend API",
        8001: "Recommendation System",
        5000: "Flask (Alternative)",
        5173: "Vite Development",
        4000: "Development Server",
        3001: "Alternative Frontend"
    }
    return service_map.get(port, f"Service on {port}")

def check_all_ports() -> Dict[int, Dict]:
    """Check status of all development ports"""
    ports_to_check = [3000, 8000, 8001, 5000, 5173, 4000, 3001]
    results = {}
    
    for port in ports_to_check:
        is_running = check_port(port)
        service_name = get_service_name(port)
        process_info = get_process_info(port) if is_running else None
        
        results[port] = {
            'running': is_running,
            'service': service_name,
            'process_info': process_info
        }
    
    return results

def display_results(results: Dict[int, Dict]):
    """Display port check results"""
    print_colored("🎯 Port Status Check:", Colors.CYAN)
    print()
    
    running_ports = []
    free_ports = []
    
    # Sort ports for consistent display
    sorted_ports = sorted(results.keys())
    
    for port in sorted_ports:
        data = results[port]
        service = data['service']
        is_running = data['running']
        process_info = data['process_info']
        
        if is_running:
            running_ports.append(port)
            status_icon = "🟢"
            status_text = "RUNNING"
            color = Colors.RED
            
            if process_info:
                print_colored(f"   {status_icon} Port {port} ({service}): {status_text}", color)
                print_colored(f"      └─ Process: {process_info['process']} (PID: {process_info['pid']})", Colors.YELLOW)
            else:
                print_colored(f"   {status_icon} Port {port} ({service}): {status_text}", color)
        else:
            free_ports.append(port)
            status_icon = "✅"
            status_text = "FREE"
            color = Colors.GREEN
            print_colored(f"   {status_icon} Port {port} ({service}): {status_text}", color)
    
    print()
    
    # Summary
    total_ports = len(results)
    running_count = len(running_ports)
    free_count = len(free_ports)
    
    print_colored("📊 Summary:", Colors.CYAN)
    print_colored(f"   • Total ports checked: {total_ports}", Colors.WHITE)
    print_colored(f"   • Running services: {running_count}", Colors.RED if running_count > 0 else Colors.GREEN)
    print_colored(f"   • Available ports: {free_count}", Colors.GREEN)
    
    if running_ports:
        print()
        print_colored("🔄 To stop running services:", Colors.YELLOW)
        print_colored("   • Kill all: taskkill /F /IM \"node.exe\" && taskkill /F /IM \"python.exe\"", Colors.WHITE)
        print_colored("   • Or use: python stop_all_services.py", Colors.WHITE)
    
    if not running_ports:
        print()
        print_colored("🚀 All ports are available! Ready to start services:", Colors.GREEN)
        print_colored("   • Backend: python BE/run_BE.py", Colors.WHITE)
        print_colored("   • Frontend: python FE/run_FE.py", Colors.WHITE)

def get_system_info():
    """Get system information"""
    print_colored("💻 System Information:", Colors.BLUE)
    print_colored(f"   • OS: {os.name}", Colors.WHITE)
    print_colored(f"   • Platform: {sys.platform}", Colors.WHITE)
    
    # Check if common tools are available
    tools = ['node', 'npm', 'python', 'uvicorn']
    available_tools = []
    
    for tool in tools:
        try:
            result = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                available_tools.append(f"{tool} ({version})")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    if available_tools:
        print_colored("   • Available tools:", Colors.WHITE)
        for tool in available_tools:
            print_colored(f"     └─ {tool}", Colors.YELLOW)
    
    print()

def main():
    """Main function"""
    print_banner()
    
    # Get system info
    get_system_info()
    
    # Check all ports
    print_colored("🔍 Checking development ports...", Colors.BLUE)
    results = check_all_ports()
    
    # Display results
    display_results(results)
    
    print()
    print_colored("=" * 60, Colors.CYAN)
    print_colored("✨ Port check complete!", Colors.GREEN)

if __name__ == "__main__":
    main()
