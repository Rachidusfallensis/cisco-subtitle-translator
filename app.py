import os
import sys
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Load environment variables
load_dotenv()

class TranslationError(Exception):
    """Custom exception for translation errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}

class Config:
    """Application configuration."""
    SECRET_KEY = 'cisco-subtitle-translator'
    UPLOAD_FOLDER = os.path.abspath('uploads')
    OUTPUT_FOLDER = os.path.abspath('output')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    MAX_CONCURRENT_TRANSLATIONS = int(os.getenv('MAX_CONCURRENT_TRANSLATIONS', 3))
    SOURCE_LANGUAGE = os.getenv('SOURCE_LANGUAGE', 'EN')
    TARGET_LANGUAGE = os.getenv('TARGET_LANGUAGE', 'FR')
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    ALLOWED_EXTENSIONS = {'srt'}
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration settings."""
        errors = []
        if not os.path.exists(cls.UPLOAD_FOLDER):
            errors.append(f"Upload folder does not exist: {cls.UPLOAD_FOLDER}")
        if not os.path.exists(cls.OUTPUT_FOLDER):
            errors.append(f"Output folder does not exist: {cls.OUTPUT_FOLDER}")
        if cls.MAX_CONTENT_LENGTH <= 0:
            errors.append("Invalid MAX_CONTENT_LENGTH")
        if cls.MAX_CONCURRENT_TRANSLATIONS <= 0:
            errors.append("Invalid MAX_CONCURRENT_TRANSLATIONS")
        return errors

def setup_logging() -> None:
    """Configure application logging."""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'translator_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def validate_api_keys() -> Tuple[bool, List[str]]:
    """Validate required API keys."""
    required_keys = {
        'DEEPL_API_KEY': 'DeepL API key',
        'ANTHROPIC_API_KEY': 'Anthropic API key'
    }
    
    missing_keys = []
    for key, name in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(name)
        elif len(os.getenv(key)) < 10:  # Basic length validation
            missing_keys.append(f"{name} appears invalid")
    
    return len(missing_keys) == 0, missing_keys

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SocketIO
socketio = SocketIO(app)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global state
translation_jobs: Dict[str, Dict] = {}
active_translations: int = 0

@app.before_first_request
def before_first_request() -> None:
    """Validate environment before starting the application."""
    # Validate API keys
    keys_valid, missing_keys = validate_api_keys()
    if not keys_valid:
        error_msg = f"Missing or invalid API keys: {', '.join(missing_keys)}"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    
    # Validate configuration
    config_errors = Config.validate()
    if config_errors:
        error_msg = f"Configuration errors: {', '.join(config_errors)}"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    
    logger.info("Application initialized successfully")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start translation."""
    try:
        if active_translations >= app.config['MAX_CONCURRENT_TRANSLATIONS']:
            return jsonify({
                'success': False,
                'error': 'Maximum concurrent translations reached. Please try again later.'
            })

        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only .srt files are allowed'})
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file with unique name if exists
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
        
        file.save(file_path)
        
        # Generate job ID and start processing
        job_id = f"{int(time.time())}-{filename}"
        translation_jobs[job_id] = {
            'id': job_id,
            'status': 'uploaded',
            'filename': filename,
            'file_path': file_path,
            'progress': 0,
            'start_time': time.time(),
            'source_language': app.config['SOURCE_LANGUAGE'],
            'target_language': app.config['TARGET_LANGUAGE']
        }
        
        # Start translation in background
        socketio.start_background_task(process_translation, job_id, file_path)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'filename': filename
        })
        
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] / 1024 / 1024}MB'
        }), 413
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] / 1024 / 1024}MB'
    }), 413

@app.errorhandler(500)
def server_error(e):
    """Handle server errors."""
    logger.error(f"Server error: {str(e)}")
    return jsonify({'success': False, 'error': 'Internal server error occurred'}), 500

if __name__ == '__main__':
    # Start the application
    logger.info("Starting Cisco Subtitle Translator")
    socketio.run(app, host='0.0.0.0', port=5000, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true') 