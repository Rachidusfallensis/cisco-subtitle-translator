import os
import sys
import time
import json
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.srt_translator import translate_srt
from scripts.translation_quality import QualityAnalyzer
from scripts.file_manager import FileManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.update(
    SECRET_KEY='video-translator',
    UPLOAD_FOLDER=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'input_srt')),
    OUTPUT_FOLDER=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'srt')),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    MAX_CONCURRENT_TRANSLATIONS=3
)

# Initialize extensions
socketio = SocketIO(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize managers
file_manager = FileManager(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])
translation_jobs = {}
active_translations = 0

def can_start_translation():
    """Check if we can start a new translation."""
    return active_translations < app.config['MAX_CONCURRENT_TRANSLATIONS']

def validate_srt_file(file_path):
    """Validate SRT file format."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return False, "File is empty"
        
        blocks = content.split('\n\n')
        if not blocks:
            return False, "No subtitle blocks found"
        
        lines = blocks[0].split('\n')
        if len(lines) < 3:
            return False, "Invalid subtitle block format"
        
        if not lines[0].isdigit():
            return False, "Invalid subtitle number"
        
        if ' --> ' not in lines[1]:
            return False, "Invalid timestamp format"
        
        return True, "File is valid"
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@limiter.limit("30 per minute")
def upload_file():
    """Handle file upload and start translation."""
    if not can_start_translation():
        return jsonify({
            'success': False,
            'error': 'Maximum concurrent translations reached. Please try again later.'
        })

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not file.filename.endswith('.srt'):
        return jsonify({'success': False, 'error': 'Only .srt files are allowed'})
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Validate SRT file
        is_valid, message = validate_srt_file(file_path)
        if not is_valid:
            os.remove(file_path)
            return jsonify({'success': False, 'error': message})
        
        # Generate job ID and start processing
        job_id = f"{int(time.time())}-{filename}"
        translation_jobs[job_id] = {
            'status': 'uploaded',
            'filename': filename,
            'file_path': file_path,
            'progress': 0,
            'start_time': time.time()
        }
        
        threading.Thread(target=process_translation, args=(job_id, file_path)).start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def process_translation(job_id, file_path):
    """Process translation in background thread with progress updates."""
    global active_translations
    active_translations += 1
    
    try:
        translation_jobs[job_id]['status'] = 'processing'
        socketio.emit('status_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 0
        })
        
        # Initialize quality analyzer
        quality_analyzer = QualityAnalyzer()
        
        # Translate file
        output_file = translate_srt(file_path)
        
        # Analyze translation quality
        with open(file_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
        with open(output_file, 'r', encoding='utf-8') as f:
            translated_text = f.read()
        
        quality_metrics = quality_analyzer.analyze_translation(original_text, translated_text)
        
        # Update job status
        translation_jobs[job_id].update({
            'status': 'completed',
            'progress': 100,
            'output_file': os.path.basename(output_file),
            'quality_metrics': quality_metrics,
            'completion_time': time.time(),
            'processing_time': time.time() - translation_jobs[job_id]['start_time']
        })
        
        socketio.emit('status_update', {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'output_file': os.path.basename(output_file),
            'quality_metrics': quality_analyzer.get_quality_summary()
        })
        
        logger.info(f"Translation completed for job {job_id}")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Translation error for job {job_id}: {error_message}")
        
        translation_jobs[job_id].update({
            'status': 'error',
            'error': error_message
        })
        
        socketio.emit('status_update', {
            'job_id': job_id,
            'status': 'error',
            'error': error_message
        })
    
    finally:
        active_translations -= 1

@app.route('/download/<filename>')
def download_file(filename):
    """Download translated file."""
    try:
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 404

@app.route('/stats')
def get_stats():
    """Get translation statistics."""
    try:
        storage_stats = file_manager.get_storage_stats()
        translation_stats = {
            'active_translations': active_translations,
            'total_jobs': len(translation_jobs),
            'completed_jobs': sum(1 for job in translation_jobs.values() if job['status'] == 'completed'),
            'failed_jobs': sum(1 for job in translation_jobs.values() if job['status'] == 'error'),
            'average_processing_time': sum(job.get('processing_time', 0) 
                                        for job in translation_jobs.values() 
                                        if job['status'] == 'completed') / 
                                    max(1, sum(1 for job in translation_jobs.values() 
                                             if job['status'] == 'completed'))
        }
        return jsonify({
            'storage': storage_stats,
            'translations': translation_stats
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'success': False, 'error': 'File is too large. Maximum size is 16MB'}), 413

@app.errorhandler(500)
def server_error(e):
    """Handle server errors."""
    logger.error(f"Server error: {str(e)}")
    return jsonify({'success': False, 'error': 'Internal server error occurred'}), 500

def cleanup_scheduler():
    """Schedule periodic cleanup of old files."""
    while True:
        try:
            cleaned, errors = file_manager.cleanup_old_files()
            if cleaned > 0 or errors:
                logger.info(f"Cleanup: removed {cleaned} files, {len(errors)} errors")
        except Exception as e:
            logger.error(f"Error in cleanup scheduler: {str(e)}")
        time.sleep(3600)  # Run every hour

if __name__ == '__main__':
    # Start cleanup scheduler
    threading.Thread(target=cleanup_scheduler, daemon=True).start()
    
    # Start the application
    logger.info("Starting Video Subtitle Translator")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 