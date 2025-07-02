"""
Modern Flask application factory for Science Downloader
"""

import os
from flask import Flask
from pathlib import Path

from ..config import get_config, AppConfig
from ..utils import setup_logging


def create_app(config: AppConfig = None) -> Flask:
    """
    Flask application factory.
    
    Args:
        config: Optional AppConfig instance. If None, uses default config.
        
    Returns:
        Configured Flask application
    """
    # Initialize configuration
    if config is None:
        config = get_config()
    
    # Set up logging
    setup_logging(debug=config.debug)
    
    # Create Flask app
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static")
    )
    
    # Configure Flask
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        UPLOAD_FOLDER=str(config.uploads_dir),
        MAX_CONTENT_LENGTH=config.max_upload_size,
        DEBUG=config.debug,
        
        # Custom config
        SCIENCE_CONFIG=config
    )
    
    # Ensure upload directory exists
    config.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    from .routes.main import main_bp
    from .routes.api import api_bp
    from .routes.download import download_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(download_bp, url_prefix='/download')
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register template filters
    _register_template_filters(app)
    
    return app


def _register_error_handlers(app: Flask):
    """Register error handlers"""
    
    @app.errorhandler(413)
    def file_too_large(error):
        return {
            'error': 'File too large. Maximum size is 16MB.'
        }, 413
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Endpoint not found'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': 'Internal server error'
        }, 500


def _register_template_filters(app: Flask):
    """Register custom template filters"""
    
    @app.template_filter('humanize_size')
    def humanize_size(size_bytes):
        """Convert bytes to human readable format"""
        if not size_bytes:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    @app.template_filter('format_percent')
    def format_percent(value):
        """Format percentage with 1 decimal place"""
        return f"{value:.1f}%" 