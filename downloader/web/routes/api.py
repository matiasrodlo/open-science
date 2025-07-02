"""
API routes for programmatic access to Science Downloader
"""

from flask import Blueprint, request, jsonify, current_app
from pathlib import Path

from ...core.extractors import BibtexExtractor, RayyanExtractor
from ...core.downloaders import ScienceDownloader
from ...utils import get_logger, validate_doi

api_bp = Blueprint('api', __name__)
logger = get_logger(__name__)


@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': current_app.config['SCIENCE_CONFIG'].version,
        'service': 'Science Downloader'
    })


@api_bp.route('/config')
def get_config():
    """Get current configuration"""
    config = current_app.config['SCIENCE_CONFIG']
    
    return jsonify({
        'version': config.version,
        'debug': config.debug,
        'data_dir': str(config.data_dir),
        'science_urls': config.science_urls,
        'download_timeout': config.download_timeout,
        'delay_between_downloads': config.delay_between_downloads
    })


@api_bp.route('/validate-doi', methods=['POST'])
def validate_doi_endpoint():
    """Validate a DOI string"""
    data = request.get_json()
    
    if not data or 'doi' not in data:
        return jsonify({'error': 'Missing DOI in request body'}), 400
    
    doi = data['doi']
    is_valid = validate_doi(doi)
    
    return jsonify({
        'doi': doi,
        'valid': is_valid
    })


@api_bp.route('/extract/bibtex', methods=['POST'])
def extract_bibtex_api():
    """Extract DOIs from BibTeX content via API"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing BibTeX content in request body'}), 400
        
        bibtex_content = data['content']
        
        # Save content to temporary file
        config = current_app.config['SCIENCE_CONFIG']
        temp_input = config.uploads_dir / "temp_bibtex.bib"
        temp_output = config.uploads_dir / "temp_dois.txt"
        
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)
        
        # Extract DOIs
        extractor = BibtexExtractor()
        result = extractor.extract(temp_input, temp_output)
        
        # Read extracted DOIs
        dois = []
        if temp_output.exists():
            with open(temp_output, 'r', encoding='utf-8') as f:
                dois = [line.strip() for line in f if line.strip()]
        
        # Clean up
        temp_input.unlink(missing_ok=True)
        temp_output.unlink(missing_ok=True)
        
        return jsonify({
            'success': result.success,
            'dois': dois,
            'count': result.unique_count,
            'duplicates_removed': result.duplicates_removed,
            'errors': result.errors
        })
        
    except Exception as e:
        logger.error(f"Error in extract_bibtex_api: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/extract/rayyan', methods=['POST'])
def extract_rayyan_api():
    """Extract DOIs from Rayyan CSV content via API"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing CSV content in request body'}), 400
        
        csv_content = data['content']
        
        # Save content to temporary file
        config = current_app.config['SCIENCE_CONFIG']
        temp_input = config.uploads_dir / "temp_rayyan.csv"
        temp_output = config.uploads_dir / "temp_dois.txt"
        
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # Extract DOIs
        extractor = RayyanExtractor()
        result = extractor.extract(temp_input, temp_output)
        
        # Read extracted DOIs
        dois = []
        if temp_output.exists():
            with open(temp_output, 'r', encoding='utf-8') as f:
                dois = [line.strip() for line in f if line.strip()]
        
        # Clean up
        temp_input.unlink(missing_ok=True)
        temp_output.unlink(missing_ok=True)
        
        return jsonify({
            'success': result.success,
            'dois': dois,
            'count': result.unique_count,
            'duplicates_removed': result.duplicates_removed,
            'errors': result.errors
        })
        
    except Exception as e:
        logger.error(f"Error in extract_rayyan_api: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/download/status')
def download_status():
    """Get download status"""
    # This would integrate with the global downloader instance
    # For now, return basic status
    return jsonify({
        'status': 'not_implemented',
        'message': 'Download status API not yet implemented'
    })


@api_bp.errorhandler(404)
def api_not_found(error):
    """API 404 handler"""
    return jsonify({
        'error': 'API endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404


@api_bp.errorhandler(405)
def api_method_not_allowed(error):
    """API 405 handler"""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405 