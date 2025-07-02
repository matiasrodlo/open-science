#!/usr/bin/env python3
"""
Windows Portable App Builder for Science Downloader
Creates a standalone executable that can run on any Windows machine.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_portable_app():
    """Build portable Windows executable"""
    
    print("Building Science Downloader Portable for Windows...")
    
    # Clean previous builds
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name", "Science-Downloader",  # Executable name
        "--icon", "portable/science-icon.ico",      # App icon (if exists)
        
        # Include Flask templates and static files
        "--add-data", "downloader/web/templates;downloader/web/templates",
        "--add-data", "downloader/web/static;downloader/web/static",
        
        # Include rich module data
        "--collect-data", "rich",
        
        # Hidden imports for Flask
        "--hidden-import", "flask",
        "--hidden-import", "requests",
        "--hidden-import", "bs4",
        "--hidden-import", "werkzeug",
        "--hidden-import", "rich",
        "--hidden-import", "rich.console",
        "--hidden-import", "rich.panel",
        "--hidden-import", "click",
        
        # Exclude unnecessary modules to reduce size
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "PIL",
        
        # Main script
        "app.py"
    ]
    
    print("Running PyInstaller...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        
        # Create portable package
        create_portable_package()
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def create_portable_package():
    """Create a complete portable package"""
    
    print("Creating portable package...")
    
    # Create portable directory
    portable_dir = Path("Science-Downloader-Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir()
    
    # Copy executable
    exe_path = Path("dist/Science-Downloader.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, portable_dir / "Science-Downloader.exe")
    
    # Create launcher script
    create_launcher(portable_dir)
    
    # Create README for portable version
    create_portable_readme(portable_dir)
    
    print(f"Portable app created in: {portable_dir}")
    print("Ready to distribute!")

def create_launcher(portable_dir):
    """Create a launcher script for better user experience"""
    
    launcher_content = '''@echo off
title Science Downloader
echo Starting Science Downloader...
echo.
echo Web interface will open automatically in your browser
echo Press Ctrl+C to stop the application
echo.
start "" "Science-Downloader.exe"
'''
    
    with open(portable_dir / "Launch.bat", "w") as f:
        f.write(launcher_content)

def create_portable_readme(portable_dir):
    """Create README for portable version"""
    
    readme_content = '''# Science Downloader Portable

Download research papers with ease.

## How to Use

1. Double-click "Launch.bat" to start the application
2. Your web browser will open automatically
3. Follow the 2-step process:
   - Step 1: Extract DOIs from your research files
   - Step 2: Download papers

## Data Storage

All data is stored in:
%USERPROFILE%\\AppData\\Local\\Science Downloader\\

## System Requirements

- Windows 7 or later
- Internet connection

## Legal Notice

For research and educational purposes only.
Users are responsible for compliance with applicable laws.

## Support

Visit: https://github.com/your-repo/science-downloader
'''
    
    with open(portable_dir / "README.txt", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    build_portable_app() 