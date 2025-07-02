"""Download managers for papers from various sources"""

from .openaccess import OpenAccessDownloader as ScienceDownloader

__all__ = ["ScienceDownloader"] 