#!/usr/bin/env python3
"""
macOS Build Script for Science Downloader
Creates a complete .app bundle with all dependencies in the portable directory
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running: {cmd}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running {cmd}: {e}")
        return False


def create_spec_file(project_root, builder_dir):
    """Create a proper spec file with correct paths"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(r"{project_root}")
sys.path.insert(0, str(project_root))

a = Analysis(
    [str(project_root / 'app.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / 'downloader/web/templates'), 'downloader/web/templates'),
        (str(project_root / 'downloader/web/static'), 'downloader/web/static'),
    ],
    hiddenimports=[
        'flask',
        'requests', 
        'bs4',
        'werkzeug',
        'werkzeug.security',
        'werkzeug.serving',
        'jinja2',
        'click',
        'lxml',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'threading',
        'json',
        'pathlib',
        'webbrowser',
        'socket',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'PIL',
        'pandas',
        'scipy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Science Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Science Downloader',
)

app = BUNDLE(
    coll,
    name='Science Downloader.app',
    icon=str(Path(r"{builder_dir}") / 'science-ico.icns'),
    bundle_identifier='com.science.downloader',
    version='2.0.0',
    info_plist={{
        'CFBundleDisplayName': 'Science Downloader',
        'CFBundleName': 'Science Downloader',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleIdentifier': 'com.science.downloader',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'SHDD',
        'CFBundleExecutable': 'Science Downloader',
        'CFBundleIconFile': 'science-ico.icns',
        'NSHumanReadableCopyright': 'Copyright © 2025 Science Downloader',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'NSAppTransportSecurity': {{
            'NSAllowsArbitraryLoads': True,
        }},
    }}
)
'''
    
    spec_file = builder_dir / "science-downloader-fixed.spec"
    spec_file.write_text(spec_content)
    return spec_file


def main():
    """Main build process"""
    print("🚀 Building Science Downloader for macOS...")
    print("=" * 50)
    
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    portable_dir = script_dir.parent / "portable"
    
    print(f"📁 Project root: {project_root}")
    print(f"📁 Builder dir: {script_dir}")
    print(f"📁 Portable dir: {portable_dir}")
    
    # Change to project root
    os.chdir(project_root)
    
    # Install PyInstaller if not available
    print("📦 Checking PyInstaller...")
    if not run_command("python -c 'import PyInstaller'"):
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("❌ Failed to install PyInstaller")
            return False
    
    # Create proper spec file
    print("📝 Creating spec file...")
    spec_file = create_spec_file(project_root, script_dir)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for dir_name in ["build", "dist"]:
        if (project_root / dir_name).exists():
            shutil.rmtree(project_root / dir_name)
    
    # Run PyInstaller
    print("⚙️ Running PyInstaller...")
    cmd = f"pyinstaller --clean --noconfirm {spec_file}"
    if not run_command(cmd):
        print("❌ Build failed!")
        return False
    
    # Check if app was created
    app_bundle = project_root / "dist" / "Science Downloader.app"
    if not app_bundle.exists():
        print("❌ App bundle not found!")
        return False
    
    # Create portable package
    print("📦 Creating portable package...")
    
    # Clear portable directory
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True)
    
    # Copy app bundle
    target_app = portable_dir / "Science Downloader.app"
    shutil.copytree(app_bundle, target_app)
    
    # Create launcher script
    launcher_script = portable_dir / "launch.sh"
    launcher_content = '''#!/bin/bash
# Science Downloader Launcher

echo "🚀 Starting Science Downloader..."
echo "📱 Your browser will open automatically"
echo "⏹️  Press Ctrl+C to stop the application"
echo ""

# Launch the app
open "./Science Downloader.app"
'''
    launcher_script.write_text(launcher_content)
    launcher_script.chmod(0o755)
    
    # Create README
    readme_file = portable_dir / "README.txt"
    readme_content = '''# Science Downloader for macOS

Download research papers with ease on macOS.

## Installation

1. Copy "Science Downloader.app" to your Applications folder
2. Double-click to launch, or use Terminal: ./launch.sh

## First Launch

macOS may show a security warning for apps from unidentified developers.

To allow the app:
1. Go to System Preferences > Security & Privacy
2. Click "Allow" for Science Downloader
3. Or right-click the app and select "Open"

## How to Use

1. Double-click "Science Downloader.app"
2. Your web browser will open automatically
3. Follow the 2-step process:
   - Step 1: Extract DOIs from your research files
   - Step 2: Download papers

## Data Storage

All data is stored in:
~/Library/Application Support/Science Downloader/

## System Requirements

- macOS 10.13 (High Sierra) or later
- Internet connection

## Legal Notice

For research and educational purposes only.
Users are responsible for compliance with applicable laws.

## Support

Visit: https://github.com/your-repo/science-downloader
'''
    readme_file.write_text(readme_content)
    
    # Create DMG creation script
    dmg_script = portable_dir / "create_dmg.sh"
    dmg_content = '''#!/bin/bash
    # Create DMG installer for Science Downloader

    APP_NAME="Science Downloader"
DMG_NAME="Science-Downloader-macOS"
SOURCE_DIR="."

echo "📦 Creating DMG installer..."

# Create temporary DMG
hdiutil create -srcfolder "$SOURCE_DIR" -volname "$APP_NAME" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW -size 100m temp.dmg

# Mount the DMG
device=$(hdiutil attach -readwrite -noverify -noautoopen "temp.dmg" | egrep '^/dev/' | sed 1q | awk '{print $1}')

# Copy files and create symlink to Applications
sleep 2
ln -s /Applications "/Volumes/$APP_NAME/Applications" 2>/dev/null || true

# Unmount and convert to final DMG
hdiutil detach $device
hdiutil convert "temp.dmg" -format UDZO -imagekey zlib-level=9 -o "$DMG_NAME.dmg"
rm temp.dmg

echo "✅ DMG created: $DMG_NAME.dmg"
'''
    dmg_script.write_text(dmg_content)
    dmg_script.chmod(0o755)
    
    # Get sizes
    app_size = sum(f.stat().st_size for f in target_app.rglob('*') if f.is_file())
    total_size = sum(f.stat().st_size for f in portable_dir.rglob('*') if f.is_file())
    
    print("\n" + "=" * 50)
    print("✅ BUILD COMPLETE!")
    print(f"📦 Portable package: {portable_dir}")
    print(f"🚀 App bundle: {target_app}")
    print(f"📊 App size: {app_size / 1024 / 1024:.1f} MB")
    print(f"📊 Total size: {total_size / 1024 / 1024:.1f} MB")
    print("\n📄 Files created:")
    for item in sorted(portable_dir.rglob("*")):
        if item.is_file() and not item.name.startswith('.'):
            size = item.stat().st_size
            print(f"   {item.relative_to(portable_dir)} ({size:,} bytes)")
    
    print("\n🎯 Next steps:")
    print("1. Test the app: open 'Science Downloader.app'")
    print("2. Create DMG: cd portable && ./create_dmg.sh")
    print("3. Distribute the portable folder or DMG")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 