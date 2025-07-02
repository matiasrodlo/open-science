"""
Modern logging configuration for Science Downloader
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from ..config import get_config


def get_logger(name: str = "downloader") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        config = get_config()
        
        # Set log level
        if config.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        if config.debug:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        
        # File handler (with rotation)
        try:
            file_handler = RotatingFileHandler(
                config.log_file,
                maxBytes=config.log_max_bytes,
                backupCount=config.log_backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)  # File gets all messages
            logger.addHandler(file_handler)
        except (PermissionError, OSError) as e:
            # If we can't write to log file, just use console
            logger.warning(f"Could not create log file {config.log_file}: {e}")
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger


def setup_logging(debug: bool = False, log_file: Optional[Path] = None):
    """
    Set up application-wide logging configuration.
    
    Args:
        debug: Enable debug logging
        log_file: Custom log file path (optional)
    """
    config = get_config()
    
    if debug:
        config.debug = True
    
    if log_file:
        # Override the log file path
        config.logs_dir = log_file.parent
        config.logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the root application logger to ensure it's configured
    get_logger() 