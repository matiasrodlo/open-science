"""
Entry point for the Science Downloader web interface
"""

import sys
import socket
import webbrowser
import threading
import time
from pathlib import Path

# Add current directory to path for development
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from downloader.web import create_app
from downloader.config import get_config
from downloader.utils import setup_logging, get_logger


def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    # If no port found, raise an error
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts starting from {start_port}")


def open_browser(port):
    """Open web browser after a short delay"""
    time.sleep(1.5)  # Wait for server to start
    webbrowser.open(f'http://localhost:{port}')


def main():
    """
    Start the Science Downloader web interface
    """
    print("🚀 Starting Science Downloader Web Interface")
    print("=" * 50)
    
    # Initialize configuration
    config = get_config()
    
    # Find available port
    try:
        available_port = find_available_port(config.flask_port)
        if available_port != config.flask_port:
            print(f"⚠️  Port {config.flask_port} is busy, using port {available_port}")
    except RuntimeError as e:
        print(f"❌ {e}")
        print("💡 Try closing other applications or restart your computer")
        sys.exit(1)
    
    # Set up logging
    setup_logging(debug=config.debug)
    logger = get_logger(__name__)
    
    print(f"📁 Data directory: {config.data_dir}")
    print(f"📝 Logs directory: {config.logs_dir}")
    print(f"🌐 Web server: http://localhost:{available_port}")
    print("📱 Your browser will open automatically")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    logger.info("Starting Science Downloader web interface")
    logger.info(f"Data directory: {config.data_dir}")
    logger.info(f"Version: {config.version}")
    logger.info(f"Using port: {available_port}")
    
    # Create Flask app
    app = create_app(config)
    
    # Open browser after delay with correct port
    browser_thread = threading.Timer(1.5, lambda: open_browser(available_port))
    browser_thread.start()
    
    # Run the application
    try:
        app.run(
            host=config.flask_host,
            port=available_port,
            debug=config.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Science Downloader stopped. Goodbye!")
        logger.info("Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 