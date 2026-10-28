#!/usr/bin/env python3
"""
Build script to create executables for Windows, Mac, and Linux
"""

import os
import sys
import platform
import subprocess

def build_executable():
    """Build executable using PyInstaller"""
    
    system = platform.system()
    
    # Install PyInstaller if not present
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "WhatsAppConnector",
        "--icon", "icon.ico" if system == "Windows" else "icon.icns",
        "--add-data", "icon.png:.",
        "whatsapp_connector.py"
    ]
    
    print(f"Building for {system}...")
    subprocess.run(cmd)
    
    print(f"\n✅ Build complete!")
    print(f"Executable location: dist/WhatsAppConnector")

if __name__ == "__main__":
    build_executable()
