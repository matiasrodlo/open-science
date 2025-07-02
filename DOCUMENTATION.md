# Science Downloader - Complete Documentation

## Overview

Science Downloader is a modern, lightweight web application for downloading scientific papers from legal open-access sources. It features DOI extraction from research database files (BibTeX, Rayyan CSV, Scopus) and a clean web interface.

**Version**: 2.0.0  
**Language**: Python 3.8+  
**Architecture**: Flask web application with modular design

## Architecture

```
science-downloader/
├── app.py                 # Main entry point
├── downloader/            # Core application package
│   ├── __init__.py       # Package initialization
│   ├── config/           # Configuration management
│   ├── core/             # Core business logic
│   │   ├── downloaders/  # Paper download engines
│   │   ├── extractors/   # DOI extraction modules
│   │   └── models/       # Data models
│   ├── utils/            # Utility functions
│   └── web/              # Web interface
│       ├── routes/       # Flask route handlers
│       ├── templates/    # HTML templates
│       └── static/       # CSS, JS, assets
├── data/                 # Application data storage
├── portable/             # Portable app builds
└── requirements.txt      # Python dependencies
```

## Core Components

### 1. Entry Point (`app.py`)
- **Purpose**: Application bootstrap and server startup
- **Key Features**:
  - Automatic port detection (5000-5009)
  - Browser auto-launch
  - Graceful shutdown handling
  - Configuration initialization

### 2. Configuration (`downloader/config/`)
- **Purpose**: Centralized configuration management
- **Features**:
  - Environment-based settings
  - Default configurations
  - Development/production modes

### 3. Core Logic (`downloader/core/`)

#### Downloaders (`downloader/core/downloaders/`)
- **openaccess.py**: Legal open-access paper download engine
- **Features**:
  - DOI validation
  - PDF retrieval from legal sources
  - Error handling
  - Progress tracking

#### Extractors (`downloader/core/extractors/`)
- **base.py**: Abstract base class for extractors
- **bibtex.py**: BibTeX file DOI extraction
- **rayyan.py**: Rayyan CSV DOI extraction  
- **scopus.py**: Scopus CSV DOI extraction
- **Features**:
  - Multiple format support
  - Duplicate detection
  - Error reporting
  - Validation

### 4. Web Interface (`downloader/web/`)

#### Routes (`downloader/web/routes/`)
- **main.py**: Homepage and navigation
- **download.py**: Download management
- **api.py**: REST API endpoints
- **Features**:
  - RESTful API design
  - File upload handling
  - Progress tracking
  - Error responses

#### Templates (`downloader/web/templates/`)
- **index.html**: Main dashboard
- **download.html**: Download interface
- **extract_*.html**: Format-specific extraction pages
- **Features**:
  - Responsive design
  - Progress indicators
  - Error handling
  - Modern UI/UX

### 5. Utilities (`downloader/utils/`)
- **logging.py**: Centralized logging system
- **validation.py**: Input validation utilities
- **Features**:
  - Structured logging
  - Error tracking
  - Input sanitization

## Data Management

### File Structure (`data/`)
```
data/
├── extracted_dois.txt     # Extracted DOIs from uploads
├── downloaded_library.txt # Successfully downloaded papers
├── failed_dois.txt       # Failed download attempts
├── library.txt           # Master research library
├── download_history.json # Download session logs
├── download_progress.json # Current download status
├── extraction_summary.json # Extraction process results
├── stop_download.flag    # Download control signal
└── README.md            # Data files documentation
```

### Data Flow
1. **Upload**: User uploads research database file
2. **Extraction**: System extracts DOIs using appropriate extractor
3. **Validation**: DOIs are validated and deduplicated
4. **Download**: Papers are downloaded from legal open-access sources
5. **Tracking**: Progress and results are logged

## API Reference

### Web Routes

#### GET `/`
- **Purpose**: Main dashboard
- **Response**: HTML dashboard with upload options

#### POST `/upload`
- **Purpose**: File upload and DOI extraction
- **Input**: Multipart form data with file
- **Response**: JSON with extraction results

#### POST `/download`
- **Purpose**: Initiate paper downloads
- **Input**: JSON with DOI list and output directory
- **Response**: JSON with download session ID

#### GET `/api/progress/<session_id>`
- **Purpose**: Get download progress
- **Response**: JSON with current progress status

#### POST `/api/stop`
- **Purpose**: Stop current download session
- **Response**: JSON confirmation

### Data Models

#### Download Session
```json
{
  "timestamp": "2025-01-01T12:00:00",
  "doi_file": "/path/to/dois.txt",
  "output_folder": "/path/to/output",
  "total_requested": 100,
  "filtered_out": 5,
  "attempted": 95,
  "downloaded": 90,
  "failed": 3,
  "skipped": 2
}
```

#### Progress Status
```json
{
  "current": 45,
  "total": 100,
  "progress_percent": 45.0,
  "downloaded": 42,
  "failed": 2,
  "skipped": 1,
  "current_doi": "10.1000/example.2024.001",
  "status": "downloading"
}
```

## Configuration

### Environment Variables
- `FLASK_ENV`: Development/production mode
- `FLASK_DEBUG`: Debug logging (True/False)
- `DATA_DIR`: Application data directory
- `LOGS_DIR`: Log files directory

### Default Settings
- **Port**: 5000 (auto-detects if busy)
- **Host**: localhost
- **Data Directory**: ./data
- **Logs Directory**: ./data/logs

## Development

### Setup
```bash
# Clone repository
git clone <repository-url>
cd science-downloader

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Testing
```bash
# Run tests
pytest

# Code formatting
black .

# Type checking
mypy downloader/

# Linting
flake8 downloader/
```

### Building
```bash
# Build portable app
cd portable/macos/builder
./build.sh

# Build Windows executable
cd portable/windows/builder
python build_windows.py
```

## Deployment

### Production Setup
1. Set `FLASK_ENV=production`
2. Configure logging directory
3. Set up reverse proxy (nginx/Apache)
4. Configure SSL certificates
5. Set up monitoring

### Portable Deployment
- **macOS**: Use built .app bundle or DMG installer
- **Windows**: Use built .exe executable
- **Features**: Zero dependencies, self-contained

## Security Considerations

### Input Validation
- File type validation for uploads
- DOI format validation
- Path traversal prevention
- File size limits

### Error Handling
- Graceful failure handling
- User-friendly error messages
- Logging of security events
- Rate limiting

### Data Privacy
- No persistent user data storage
- Temporary file cleanup
- Secure file handling
- Privacy-focused design

## Performance

### Optimization Features
- Asynchronous download processing
- Progress streaming
- Memory-efficient file handling
- Connection pooling
- Caching strategies

### Monitoring
- Download progress tracking
- Performance metrics logging
- Error rate monitoring
- Resource usage tracking

## Troubleshooting

### Common Issues
1. **Port conflicts**: Application auto-detects available ports
2. **File permissions**: Ensure write access to data directory
3. **Network issues**: Check internet connectivity
4. **Memory usage**: Large downloads may require more RAM

### Logs
- Application logs: `data/logs/`
- Download history: `data/download_history.json`
- Error tracking: Check console output

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings
- Maintain test coverage

### Architecture Principles
- Modular design
- Separation of concerns
- Dependency injection
- Error handling
- Logging

## License

MIT License - See LICENSE file for details.

---

*This documentation is optimized for LLM consumption with clear structure, comprehensive coverage, and practical examples.* 