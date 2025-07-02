"""
Science Downloader - Professional paper downloader with web and CLI interfaces
"""

__version__ = "2.0.0"
__author__ = "Science Downloader Team"

# Main API exports
from .core.extractors import BibtexExtractor, RayyanExtractor
from .core.downloaders import ScienceDownloader

__all__ = [
    "__version__",
    "BibtexExtractor", 
    "RayyanExtractor",
    "ScienceDownloader"
] 