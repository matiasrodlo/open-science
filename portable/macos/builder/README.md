# Science Downloader - macOS Portable Version

This directory contains the build system for creating a portable macOS application.

## Quick Build

```bash
# Build the app
make build

# Create portable package
make package

# Create DMG installer
make dmg
```

## Build Process

### 1. PyInstaller Build
```bash
pyinstaller --windowed --onedir --name "Science Downloader" ../../app.py
```

### 2. Package Structure
```
Science-Downloader-macOS/
├── Science Downloader.app    # Main macOS app bundle
├── launch.sh                 # Launcher script
└── README.txt               # User instructions
```

### 3. Distribution
- **Portable Package**: Zip the `Science-Downloader-macOS` folder
- **DMG Installer**: Professional installer with drag-and-drop

## Build Commands

### Using Makefile
```bash
make build      # Build app bundle
make clean      # Clean build artifacts
make run        # Build and run app
make package    # Create portable package
make dmg        # Create DMG installer
```

### Using Scripts
```bash
./build.sh                    # Build app bundle
./create_installer_dmg.sh     # Create DMG installer
python build_macos_portable.py # Python-based build
```

## Requirements

- macOS 10.13+
- Python 3.8+
- PyInstaller
- create-dmg (for DMG creation)

## Installation

### Install Dependencies
```bash
# Install PyInstaller
pip install pyinstaller

# Install create-dmg (optional)
brew install create-dmg
```

### Build Dependencies
```bash
# Install build tools
make install-deps
```

## Code Signing

### Developer Certificate
```bash
# Sign the app bundle
codesign --force --sign "Developer ID Application: Your Name" "Science Downloader.app"

# Verify signature
codesign --verify --verbose "Science Downloader.app"
```

### Notarization (for distribution)
```bash
# Create notarization package
ditto -c -k --keepParent "Science Downloader.app" "Science-Downloader.zip"

# Submit for notarization
xcrun altool --notarize-app --primary-bundle-id "com.yourcompany.sciencedownloader" \
    --username "your-apple-id@example.com" --password "@keychain:AC_PASSWORD" \
    --file "Science-Downloader.zip"
```

## Troubleshooting

### Build Issues
```bash
# Clean and rebuild
make clean
make build

# Check PyInstaller version
pyinstaller --version

# Verify Python environment
python --version
pip list | grep pyinstaller
```

### Permission Issues
```bash
# Fix file permissions
chmod +x build.sh
chmod +x create_installer_dmg.sh
chmod +x launch.sh
```

### Code Signing Issues
```bash
# Check certificate
security find-identity -v -p codesigning

# Remove existing signature
codesign --remove-signature "Science Downloader.app"
```

## Distribution

### Portable Package
1. Run `make package`
2. Zip the `Science-Downloader-macOS` folder
3. Distribute the zip file

### DMG Installer
1. Run `make dmg`
2. The DMG file will be created in the current directory
3. Distribute the DMG file

### App Store (Future)
- Requires Apple Developer account
- Code signing and notarization required
- App Store review process

## Version Management

### Update Version
```bash
# Update version in app.py
# Update version in Info.plist
# Update version in README files
```

### Build Different Versions
```bash
# Development build
make build

# Release build
make clean && make build

# Beta build
make clean && make build
```

## Support

For build issues or questions:
1. Check the troubleshooting section
2. Review the build logs
3. Verify system requirements
4. Check PyInstaller documentation 