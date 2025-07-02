#!/bin/bash
# Build script for Science Downloader macOS app

echo "🚀 Building Science Downloader for macOS..."
echo "========================================"

# Install PyInstaller if needed
echo "📦 Installing PyInstaller..."
pip install pyinstaller

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf ../../build ../../dist

# Build app
echo "⚙️ Building .app bundle..."
cd ../..
pyinstaller portable/macos/science-downloader-macos.spec

# Check if build was successful
if [ ! -d "dist/Science Downloader.app" ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo "📦 App bundle created: dist/Science Downloader.app"
echo ""
echo "To create portable package, run:"
echo "  python portable/macos/build_macos.py" 