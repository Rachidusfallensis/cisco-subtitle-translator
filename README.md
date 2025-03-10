# Video Subtitle Translator

A web-based application for translating SRT subtitle files from English to French using DeepL API and Claude 3.5. The application features a modern, intuitive interface with real-time translation progress tracking and quality analysis.

## Features

### Translation
- Batch processing of multiple SRT files
- Real-time translation progress tracking
- Maximum file size of 16MB
- Concurrent translation support (up to 3 files simultaneously)
- Rate limiting to prevent API abuse

### Quality Analysis
- Translation confidence scoring
- Length ratio analysis
- Placeholder preservation checking
- Quality indicators (high/medium/low)
- Processing time tracking

### File Management
- Automatic cleanup of files older than 24 hours
- Storage statistics monitoring
- Secure file handling
- Input validation for SRT files

### User Interface
- Drag-and-drop file upload
- Multiple file upload support
- Real-time progress tracking
- File preview functionality
- Quality metrics display
- Translation status badges
- Download management
- Statistics dashboard

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/video-translator.git
cd video-translator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with:
```
DEEPL_API_KEY=your_deepl_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

1. Start the application:
```bash
python web/app.py
```

2. Access the web interface at `http://localhost:5000`

3. Upload SRT files by either:
   - Dragging and dropping files into the upload zone
   - Clicking the upload zone to select files

4. Monitor translation progress in real-time:
   - View individual file progress
   - Check translation quality metrics
   - Download completed translations

## Project Structure

```
video-translator/
├── web/
│   ├── app.py              # Main Flask application
│   └── templates/
│       └── index.html      # Web interface
├── scripts/
│   ├── srt_translator.py   # Translation logic
│   ├── translation_quality.py  # Quality analysis
│   └── file_manager.py     # File management
├── input_srt/             # Upload directory
├── output/
│   └── srt/              # Translated files
├── requirements.txt       # Project dependencies
└── .env                  # Environment variables
```

## Dependencies

- Flask - Web framework
- Flask-SocketIO - Real-time communication
- Flask-Limiter - Rate limiting
- Anthropic - Claude API integration
- DeepL API - Translation service
- Other dependencies listed in requirements.txt

## Error Handling

- File size limits (16MB max)
- SRT format validation
- Concurrent translation limits
- API rate limiting
- Automatic file cleanup
- Comprehensive error logging

## Monitoring

- Translation success rate
- Processing time statistics
- Storage usage tracking
- Active translation monitoring
- Error logging and tracking

## Security Features

- Secure file handling
- Rate limiting
- Maximum file size restrictions
- Automatic file cleanup
- Input validation

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]