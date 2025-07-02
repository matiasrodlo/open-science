"""
Download routes for the Science Downloader web interface
"""

import threading
from flask import Blueprint, render_template, request, jsonify, current_app
from pathlib import Path
from werkzeug.utils import secure_filename

from ...core.downloaders import ScienceDownloader
from ...utils import get_logger

download_bp = Blueprint('download', __name__)
logger = get_logger(__name__)

# Global downloader instance for progress tracking
_downloader = None


@download_bp.route('/')
def download_page():
    """Download papers page"""
    return render_template('download.html')


@download_bp.route('/custom', methods=['POST'])
def download_papers_custom():
    """Download papers from custom DOI file"""
    global _downloader
    
    try:
        # Validate file upload
        if 'doi_file' not in request.files:
            return jsonify({'error': 'No DOI file uploaded'}), 400
        
        file = request.files['doi_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get output folder from form
        output_folder = request.form.get('output_folder', '').strip()
        config = current_app.config['SCIENCE_CONFIG']
        
        if not output_folder:
            output_folder = config.data_dir / "papers"
        else:
            output_folder = Path(output_folder).expanduser()
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / filename
        file.save(file_path)
        
        # Count DOIs in the uploaded file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dois = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                doi_count = len(dois)
            
            if doi_count == 0:
                file_path.unlink(missing_ok=True)
                return jsonify({'error': 'No valid DOIs found in the uploaded file'}), 400
                
        except Exception as e:
            file_path.unlink(missing_ok=True)
            return jsonify({'error': f'Error reading DOI file: {str(e)}'}), 400
        
        # Initialize downloader
        _downloader = ScienceDownloader(config)
        
        # Start download in background thread
        def download_thread():
            try:
                result = _downloader.download_papers(file_path, output_folder)
                logger.info(f"Download completed: {result}")
            except Exception as e:
                logger.error(f"Download thread error: {e}")
            finally:
                # Clean up uploaded file after download
                file_path.unlink(missing_ok=True)
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Download started for {doi_count} DOIs. Files will be saved to: {output_folder}',
            'doi_count': doi_count,
            'output_folder': str(output_folder)
        })
        
    except Exception as e:
        logger.error(f"Error in download_papers_custom: {e}")
        return jsonify({'error': str(e)}), 500


@download_bp.route('/progress')
def get_download_progress():
    """Get current download progress"""
    global _downloader
    
    try:
        if _downloader is None:
            return jsonify({
                'status': 'idle',
                'current': 0,
                'total': 0,
                'progress_percent': 0,
                'downloaded': 0,
                'failed': 0,
                'skipped': 0
            })
        
        progress = _downloader.get_progress()
        if progress:
            return jsonify(progress.to_dict())
        else:
            return jsonify({
                'status': 'idle',
                'current': 0,
                'total': 0,
                'progress_percent': 0,
                'downloaded': 0,
                'failed': 0,
                'skipped': 0
            })
            
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        return jsonify({'error': str(e)}), 500


@download_bp.route('/stats')
def get_download_stats():
    """Get comprehensive download statistics"""
    global _downloader
    
    try:
        if _downloader is None:
            _downloader = ScienceDownloader()
        
        stats = _downloader.get_download_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@download_bp.route('/stop', methods=['POST'])
def stop_download():
    """Stop current download"""
    global _downloader
    
    try:
        if _downloader is None:
            return jsonify({'error': 'No download in progress'}), 400
        
        _downloader.set_stop_flag()
        
        return jsonify({
            'success': True,
            'message': 'Download stop requested'
        })
        
    except Exception as e:
        logger.error(f"Error stopping download: {e}")
        return jsonify({'error': str(e)}), 500


@download_bp.route('/clear-progress', methods=['POST'])
def clear_progress():
    """Clear current download progress (not persistent data)"""
    global _downloader
    
    try:
        if _downloader:
            _downloader.clear_progress()
        
        return jsonify({
            'success': True,
            'message': 'Current progress cleared (download history preserved)'
        })
        
    except Exception as e:
        logger.error(f"Error clearing progress: {e}")
        return jsonify({'error': str(e)}), 500


@download_bp.route('/reset-tracking', methods=['POST'])
def reset_all_tracking():
    """Clear all persistent tracking files (dangerous operation!)"""
    global _downloader
    
    try:
        if _downloader is None:
            _downloader = ScienceDownloader()
        
        cleared_count = _downloader.clear_all_tracking()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {cleared_count} tracking files. All download history reset.',
            'cleared_files': cleared_count
        })
        
    except Exception as e:
        logger.error(f"Error resetting tracking: {e}")
        return jsonify({'error': str(e)}), 500


@download_bp.route('/library')
def get_library():
    """Get list of successfully downloaded papers"""
    global _downloader
    
    try:
        if _downloader is None:
            _downloader = ScienceDownloader()
        
        downloaded_dois = list(_downloader._get_downloaded_dois())
        failed_dois = list(_downloader._get_failed_dois())
        
        return jsonify({
            'success': True,
            'library': {
                'downloaded': downloaded_dois,
                'failed': failed_dois,
                'downloaded_count': len(downloaded_dois),
                'failed_count': len(failed_dois)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting library: {e}")
        return jsonify({'error': str(e)}), 500 