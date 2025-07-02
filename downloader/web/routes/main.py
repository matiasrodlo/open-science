"""
Main routes for the Science Downloader web interface
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from pathlib import Path
from werkzeug.utils import secure_filename

from ...core.extractors import BibtexExtractor, RayyanExtractor, ScopusExtractor
from ...utils import get_logger

main_bp = Blueprint('main', __name__)
logger = get_logger(__name__)


@main_bp.route('/')
def index():
    """Main dashboard page"""
    config = current_app.config['SCIENCE_CONFIG']
    return render_template('index.html', 
                         app_version=config.version,
                         app_name="Science Downloader")


@main_bp.route('/status')
def status():
    """Check DOI status for homepage"""
    try:
        config = current_app.config['SCIENCE_CONFIG']
        dois_file = config.extracted_dois_file
        
        if dois_file.exists():
            with open(dois_file, 'r', encoding='utf-8') as f:
                dois = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                count = len(dois)
            
            return jsonify({
                'dois_available': count > 0,
                'count': count
            })
        else:
            return jsonify({
                'dois_available': False,
                'count': 0
            })
            
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({
            'dois_available': False,
            'count': 0
        })


@main_bp.route('/extract-bibtex', methods=['GET', 'POST'])
def extract_bibtex():
    """Extract DOIs from BibTeX files"""
    if request.method == 'GET':
        return render_template('extract_bibtex.html')
    
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get output path from form
        output_path = request.form.get('output_path', '').strip()
        config = current_app.config['SCIENCE_CONFIG']
        
        if not output_path:
            output_path = config.extracted_dois_file
        else:
            output_path = Path(output_path)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / filename
        file.save(file_path)
        
        # Extract DOIs using the modern extractor
        extractor = BibtexExtractor()
        result = extractor.extract(file_path, output_path)
        
        # Clean up uploaded file
        file_path.unlink(missing_ok=True)
        
        if result.success:
            return jsonify({
                'success': True,
                'message': f'Successfully extracted {result.unique_count} DOIs to {output_path}',
                'count': result.unique_count,
                'output_path': str(output_path),
                'duplicates_removed': result.duplicates_removed,
                'errors': result.errors[:5]  # Limit errors shown
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No DOIs found in the uploaded file',
                'details': result.errors
            }), 400
            
    except Exception as e:
        logger.error(f"Error in extract_bibtex: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/extract-rayyan', methods=['GET', 'POST'])
def extract_rayyan():
    """Extract DOIs from Rayyan CSV files"""
    if request.method == 'GET':
        return render_template('extract_rayyan.html')
    
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get output path from form
        output_path = request.form.get('output_path', '').strip()
        config = current_app.config['SCIENCE_CONFIG']
        
        if not output_path:
            output_path = config.extracted_dois_file
        else:
            output_path = Path(output_path)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / filename
        file.save(file_path)
        
        # Extract DOIs using the modern extractor
        extractor = RayyanExtractor()
        result = extractor.extract(file_path, output_path)
        
        # Clean up uploaded file
        file_path.unlink(missing_ok=True)
        
        if result.success:
            return jsonify({
                'success': True,
                'message': f'Successfully extracted {result.unique_count} DOIs from Rayyan CSV to {output_path}',
                'count': result.unique_count,
                'output_path': str(output_path),
                'duplicates_removed': result.duplicates_removed,
                'errors': result.errors[:5]  # Limit errors shown
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No DOIs found in the uploaded Rayyan CSV file',
                'details': result.errors
            }), 400
            
    except Exception as e:
        logger.error(f"Error in extract_rayyan: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/extract-scopus', methods=['GET', 'POST'])
def extract_scopus():
    """Extract DOIs from Scopus BibTeX files"""
    if request.method == 'GET':
        return render_template('extract_scopus.html')
    
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get output path from form
        output_path = request.form.get('output_path', '').strip()
        config = current_app.config['SCIENCE_CONFIG']
        
        if not output_path:
            output_path = config.extracted_dois_file
        else:
            output_path = Path(output_path)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / filename
        file.save(file_path)
        
        # Extract DOIs using the Scopus extractor
        extractor = ScopusExtractor()
        result = extractor.extract(file_path, output_path)
        
        # Clean up uploaded file
        file_path.unlink(missing_ok=True)
        
        if result.success:
            return jsonify({
                'success': True,
                'message': f'Successfully extracted {result.unique_count} DOIs from Scopus BibTeX to {output_path}',
                'count': result.unique_count,
                'output_path': str(output_path),
                'duplicates_removed': result.duplicates_removed,
                'errors': result.errors[:5]  # Limit errors shown
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No DOIs found in the uploaded Scopus BibTeX file',
                'details': result.errors
            }), 400
            
    except Exception as e:
        logger.error(f"Error in extract_scopus: {e}")
        return jsonify({'error': str(e)}), 500 