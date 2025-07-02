"""Core business logic for Science Downloader"""

# Re-export main classes for convenience
from .extractors import BibtexExtractor, RayyanExtractor
from .downloaders import ScienceDownloader

__all__ = ["BibtexExtractor", "RayyanExtractor", "ScienceDownloader"] 