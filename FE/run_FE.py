#!/usr/bin/env python3
"""
Simple React Frontend Launcher
==============================

A simple script to start the React frontend development server.

Usage:
    python run_FE.py
"""

import subprocess
import sys
import os
from pathlib import Path

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message, color=Colors.WHITE):
    """Print colored message"""
    print(f"{color}{message}{Colors.END}")

def main():
    """Main function"""
    # Banner
    print_colored(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                   ⚛️  eCommerce React Frontend               ║
║                      Starting Server...                     ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
""")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print_colored(f"📁 Working directory: {script_dir}", Colors.BLUE)
    
    # Check if package.json exists
    if not Path("package.json").exists():
        print_colored("❌ package.json not found", Colors.RED)
        return
    
    # Start server
    print_colored("🚀 Starting React development server...", Colors.GREEN)
    print_colored("📍 Server will be available at: http://localhost:3000", Colors.CYAN)
    print_colored("🛑 Press Ctrl+C to stop the server", Colors.YELLOW)
    print_colored("=" * 60, Colors.CYAN)
    
    try:
        # Use shell=True on Windows to properly find npm
        subprocess.run(['npm', 'start'], cwd=script_dir, shell=True)
    except KeyboardInterrupt:
        print_colored("\n🛑 Server stopped by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", Colors.RED)
        print_colored("Make sure Node.js and npm are installed", Colors.YELLOW)

if __name__ == "__main__":
    main()
