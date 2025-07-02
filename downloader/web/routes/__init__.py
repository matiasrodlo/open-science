"""Flask route blueprints for Science Downloader web interface"""

from .main import main_bp
from .api import api_bp
from .download import download_bp

__all__ = ["main_bp", "api_bp", "download_bp"]
