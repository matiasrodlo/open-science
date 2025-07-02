# Makefile for Science Downloader macOS build

.PHONY: build clean run package dmg

# Build the macOS app
build:
	@echo "🚀 Building Science Downloader for macOS..."
	@./build.sh

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf ../../build ../../dist
	@rm -rf Science-Downloader-macOS
	@rm -rf science-downloader.dmg

# Run the built app
run: build
	@if [ -d "dist/Science Downloader.app" ]; then \
		echo "🚀 Launching Science Downloader..."; \
		open "dist/Science Downloader.app"; \
	else \
		echo "❌ App not found. Run 'make build' first."; \
	fi

# Create portable package
package: build
	@echo "📦 Creating portable package..."
	@if [ -d "Science-Downloader-macOS" ]; then \
		rm -rf Science-Downloader-macOS; \
	fi
	@mkdir Science-Downloader-macOS
	@cp -r "dist/Science Downloader.app" Science-Downloader-macOS/
	@cp ../portable/launch.sh Science-Downloader-macOS/
	@cp ../portable/README.txt Science-Downloader-macOS/
	@chmod +x Science-Downloader-macOS/launch.sh
	@echo "✅ Portable package created: Science-Downloader-macOS/"

# Create DMG installer
dmg: package
	@echo "📦 Creating DMG installer..."
	@if [ -d "Science-Downloader-macOS" ]; then \
		cd Science-Downloader-macOS && ./create_dmg.sh; \
	else \
		echo "❌ Package not found. Run 'make package' first."; \
	fi

# Help
help:
	@echo "Available targets:"
	@echo "  build   - Build the macOS app"
	@echo "  clean   - Clean build artifacts"
	@echo "  run     - Build and run the app"
	@echo "  package - Create portable package"
	@echo "  dmg     - Create DMG installer"
	@echo "  help    - Show this help" 