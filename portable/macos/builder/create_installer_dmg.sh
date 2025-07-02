#!/bin/bash
# Create Professional DMG Installer for Science Downloader
set -e  # Exit on any error

echo "📦 Creating DMG installer for Science Downloader..."

APP_NAME="Science Downloader"
DMG_NAME="science-downloader.dmg"
TEMP_DIR="installer_temp"
APP_FILE="../portable/Science Downloader.app"

echo "🚀 Creating Professional DMG Installer..."
echo "=========================================="

# Check if app exists
if [ ! -d "$APP_FILE" ]; then
    echo "❌ Error: $APP_FILE not found!"
    echo "💡 Make sure to run the build script first: python build_macos_portable.py"
    exit 1
fi

# Clean up any previous builds
echo "🧹 Cleaning up previous builds..."
rm -rf "$TEMP_DIR" 2>/dev/null || true
rm -f temp.dmg "$DMG_NAME.dmg" 2>/dev/null || true

# Create clean temporary directory
echo "📁 Creating clean temporary directory..."
mkdir "$TEMP_DIR"
cp -R "$APP_FILE" "$TEMP_DIR/"

echo "✅ App copied to temp directory"
echo "📦 App size: $(du -sh "$TEMP_DIR/$APP_FILE" | cut -f1)"

# Create initial DMG
echo "💿 Creating initial DMG..."
hdiutil create -srcfolder "$TEMP_DIR" -volname "$APP_NAME" -fs HFS+ -format UDRW -size 120m temp.dmg

if [ $? -ne 0 ]; then
    echo "❌ Failed to create initial DMG"
    exit 1
fi

echo "✅ Initial DMG created"

# Mount the DMG with write access
echo "🔧 Mounting DMG for modifications..."
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen temp.dmg)
DEVICE=$(echo "$MOUNT_OUTPUT" | egrep '^/dev/' | sed 1q | awk '{print $1}')
MOUNT_POINT="/Volumes/$APP_NAME"

echo "📍 Mounted at: $MOUNT_POINT"
echo "🔌 Device: $DEVICE"

# Wait for mount to complete
sleep 2

# Verify mount
if [ ! -d "$MOUNT_POINT" ]; then
    echo "❌ Failed to mount DMG at $MOUNT_POINT"
    exit 1
fi

echo "📂 Current DMG contents:"
ls -la "$MOUNT_POINT/"

# Create Applications symlink
echo "🔗 Creating Applications folder shortcut..."
if ln -s /Applications "$MOUNT_POINT/Applications"; then
    echo "✅ Applications shortcut created successfully"
else
    echo "❌ Failed to create Applications shortcut"
    hdiutil detach "$DEVICE"
    exit 1
fi

# Verify the symlink was created
echo "🔍 Verifying DMG contents after adding Applications shortcut:"
ls -la "$MOUNT_POINT/"

# Unmount the DMG
echo "📤 Unmounting DMG..."
if hdiutil detach "$DEVICE"; then
    echo "✅ DMG unmounted successfully"
else
    echo "❌ Failed to unmount DMG"
    exit 1
fi

# Convert to compressed final DMG
echo "🗜️  Converting to compressed DMG..."
if hdiutil convert temp.dmg -format UDZO -imagekey zlib-level=9 -o "$DMG_NAME.dmg"; then
    echo "✅ DMG compression completed"
else
    echo "❌ Failed to compress DMG"
    exit 1
fi

# Clean up
echo "🧹 Cleaning up temporary files..."
rm -f temp.dmg
rm -rf "$TEMP_DIR"

# Get final size
FINAL_SIZE=$(du -sh "$DMG_NAME.dmg" | cut -f1)

echo ""
echo "🎉 SUCCESS! Professional DMG installer created!"
echo "=========================================="
echo "📦 File: $DMG_NAME.dmg"
echo "📊 Size: $FINAL_SIZE"
echo ""
echo "📱 The DMG contains:"
echo "   • Science Downloader.app"
echo "   • Applications folder shortcut"
echo ""
echo "👥 User installation process:"
echo "   1. Double-click $DMG_NAME.dmg"
echo "   2. Drag 'Science Downloader.app' to 'Applications'"
echo "   3. Launch from Applications or Launchpad"
echo ""
echo "✅ Ready for distribution!" 