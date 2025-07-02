"""
Validation utilities for Science Downloader
"""

import re
from pathlib import Path
from typing import Union

from ..config import get_config


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit length to reasonable size
    if len(sanitized) > 200:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        name = name[:200-len(ext)-1]
        sanitized = f"{name}.{ext}" if ext else name
    
    return sanitized


def validate_doi(doi: str) -> bool:
    """
    Validate a DOI string format.
    
    Args:
        doi: DOI string to validate
        
    Returns:
        True if DOI is valid, False otherwise
    """
    if not doi or not isinstance(doi, str):
        return False
    
    config = get_config()
    doi_pattern = re.compile(config.doi_regex, re.IGNORECASE)
    return bool(doi_pattern.match(doi.strip()))


def validate_file_path(file_path: Union[str, Path], must_exist: bool = True) -> bool:
    """
    Validate a file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether the file must exist
        
    Returns:
        True if path is valid, False otherwise
    """
    try:
        path = Path(file_path)
        
        if must_exist:
            return path.exists() and path.is_file()
        else:
            # Check if parent directory exists and is writable
            parent = path.parent
            return parent.exists() and parent.is_dir()
            
    except (TypeError, ValueError, OSError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit length to reasonable size
    if len(sanitized) > 200:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        name = name[:200-len(ext)-1]
        sanitized = f"{name}.{ext}" if ext else name
    
    return sanitized


def normalize_doi(doi: str) -> str:
    """
    Normalize a DOI string by removing extra formatting.
    
    Args:
        doi: DOI string to normalize
        
    Returns:
        Normalized DOI string
    """
    if not doi:
        return ""
    
    # Remove common prefixes
    doi = doi.strip()
    prefixes = ["doi:", "DOI:", "https://doi.org/", "http://dx.doi.org/"]
    for prefix in prefixes:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
            break
    
    # Remove quotes and extra whitespace
    doi = doi.strip('\'"')
    
    return doi 