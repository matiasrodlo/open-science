"""
Modern configuration management for Science Downloader.
Handles platform-specific user directories and prevents permission issues.
"""

import os
import sys
import platform
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    """Application configuration with smart defaults and platform-aware paths"""
    
    # App metadata
    version: str = "2.0.0"
    name: str = "Science Downloader"
    debug: bool = False
    
    # Directory paths (will be set automatically)
    data_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None
    uploads_dir: Optional[Path] = None
    
    # Science settings
    science_urls: List[str] = field(default_factory=lambda: [
        "https://arxiv.org",
        "https://pubmed.ncbi.nlm.nih.gov",
        "https://www.ncbi.nlm.nih.gov/pmc",
        "https://biorxiv.org",
        "https://medrxiv.org",
        "https://www.researchsquare.com",
        "https://www.preprints.org",
    ])
    
    # CORE API settings
    core_api_key: str = "G3mnZJNEbDUPpz1weydfqv8uCOhIaxHt"
    core_base_url: str = "https://api.core.ac.uk/v3"
    core_rate_limit: int = 10  # requests per minute (free tier)
    core_timeout: int = 30  # seconds
    core_max_results: int = 1  # results per DOI search
    
    # arXiv API settings
    arxiv_base_url: str = "https://export.arxiv.org/api/query"
    arxiv_timeout: int = 30  # seconds
    arxiv_max_results: int = 1  # results per DOI search
    arxiv_rate_limit: int = 30  # requests per minute (arXiv is more generous)
    
    # NCBI E-utilities settings
    ncbi_base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    ncbi_api_key: str = "163202f0d5070cd1ba9f5a7cd87c4dfa7309"
    ncbi_tool: str = "science-downloader"
    ncbi_email: str = "science-downloader@example.com"  # Should be updated by user
    ncbi_timeout: int = 30  # seconds
    ncbi_max_results: int = 5  # results per DOI search
    ncbi_rate_limit: int = 10  # requests per second with API key (600/minute)
    ncbi_databases: List[str] = field(default_factory=lambda: ["pubmed", "pmc"])
    
    # Europe PMC API settings
    europepmc_base_url: str = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    europepmc_timeout: int = 30  # seconds
    europepmc_max_results: int = 5  # results per search
    europepmc_rate_limit: int = 20  # requests per minute (conservative estimate)
    europepmc_format: str = "json"  # json, xml, or dc
    
    download_timeout: int = 10
    delay_between_downloads: int = 8  # 8 seconds = ~7.5 requests/minute (safe for 10/min limit)
    max_workers: int = 5
    
    # Web interface settings
    flask_host: str = "localhost"
    flask_port: int = 5000
    max_upload_size: int = 16 * 1024 * 1024  # 16MB
    
    # File settings
    doi_regex: str = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
    
    # Logging settings
    log_max_bytes: int = 1_000_000
    log_backup_count: int = 5
    
    def __post_init__(self):
        """Initialize paths after object creation"""
        if self.data_dir is None:
            self.data_dir = self._get_user_data_dir()
        if self.logs_dir is None:
            self.logs_dir = self.data_dir / "logs"
        if self.uploads_dir is None:
            self.uploads_dir = self.data_dir / "uploads"
            
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _get_user_data_dir(self) -> Path:
        """
        Get appropriate user data directory for the platform.
        This prevents permission issues by using user-writable locations.
        """
        # Check if running from a packaged app
        if self._is_packaged_app():
            return self._get_packaged_app_data_dir()
        
        # Development mode - use project directory
        if self._is_development_mode():
            return Path(__file__).parent.parent.parent / "data"
        
        # Default platform-specific user directories
        system = platform.system()
        if system == "Windows":
            return Path.home() / "AppData" / "Local" / "Science Downloader"
        elif system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Science Downloader"
        else:  # Linux and other Unix-like systems
            return Path.home() / ".local" / "share" / "science-downloader"
    
    def _is_packaged_app(self) -> bool:
        """Check if running from a packaged application"""
        return (
            getattr(sys, 'frozen', False) or  # PyInstaller
            ("/Applications/" in str(Path(__file__)) and ".app" in str(Path(__file__)))  # macOS app bundle
        )
    
    def _is_development_mode(self) -> bool:
        """Check if running in development mode"""
        # Look for development indicators
        current_path = Path(__file__).resolve()
        
        # Check if we're in a git repository
        git_dir = current_path
        while git_dir.parent != git_dir:
            if (git_dir / ".git").exists():
                return True
            git_dir = git_dir.parent
        
        # Check if requirements.txt exists in parent directories
        req_file = current_path
        while req_file.parent != req_file:
            if (req_file / "requirements.txt").exists():
                return True
            req_file = req_file.parent
            
        return False
    
    def _get_packaged_app_data_dir(self) -> Path:
        """Get data directory for packaged applications"""
        system = platform.system()
        if system == "Windows":
            return Path.home() / "AppData" / "Roaming" / "Science Downloader"
        elif system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Science Downloader"
        else:  # Linux
            return Path.home() / ".science-downloader"
    
    def _ensure_directories(self):
        """Create necessary directories with proper error handling"""
        directories = [self.data_dir, self.logs_dir, self.uploads_dir]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                # Test write permissions
                test_file = directory / ".write_test"
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError) as e:
                # If we can't write to the preferred location, fall back to temp
                import tempfile
                fallback_dir = Path(tempfile.gettempdir()) / "science-downloader"
                fallback_dir.mkdir(parents=True, exist_ok=True)
                
                if directory == self.data_dir:
                    self.data_dir = fallback_dir
                    self.logs_dir = fallback_dir / "logs"
                    self.uploads_dir = fallback_dir / "uploads"
                    self.logs_dir.mkdir(exist_ok=True)
                    self.uploads_dir.mkdir(exist_ok=True)
                    print(f"Warning: Using fallback directory {fallback_dir} due to permissions")
                    break
    
    @property
    def bibtex_file(self) -> Path:
        """Default BibTeX file path"""
        return self.data_dir / "meta-data-sample.bib"
    
    @property
    def rayyan_csv_file(self) -> Path:
        """Default Rayyan CSV file path"""
        return self.data_dir / "articles.csv"
    
    @property
    def extracted_dois_file(self) -> Path:
        """Default extracted DOIs file path"""
        return self.data_dir / "extracted_dois.txt"
    
    @property
    def failed_dois_file(self) -> Path:
        """Default failed DOIs file path"""
        return self.data_dir / "failed_dois.txt"
    
    @property
    def log_file(self) -> Path:
        """Default log file path"""
        return self.logs_dir / "downloader.log"
    
    @property
    def extraction_summary_file(self) -> Path:
        """Default extraction summary file path"""
        return self.data_dir / "extraction_summary.json"


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance (singleton pattern)"""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def set_config(config: AppConfig):
    """Set the global configuration instance"""
    global _config
    _config = config


def reset_config():
    """Reset the global configuration (useful for testing)"""
    global _config
    _config = None 