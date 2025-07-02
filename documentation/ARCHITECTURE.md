# Architecture Documentation

## System Overview

Science Downloader follows a modular Flask-based architecture with clear separation of concerns.

## Component Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Core Logic    │    │   Data Layer    │
│   (Flask)       │◄──►│   (Business)    │◄──►│   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   Extractors    │    │   File System   │
│   Static Files  │    │   Downloaders   │    │   JSON Logs     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
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
  - **CORE API Integration**: API key and endpoint configuration

### 3. Core Logic (`downloader/core/`)

#### CORE API Integration (`downloader/core/downloaders/`)
- **OpenAccessDownloader**: Legal paper download engine powered by CORE API
- **Key Features**:
  - **90+ Million Papers**: Access to world's largest open access aggregator
  - **Real-time Progress**: Live download tracking with progress callbacks
  - **Smart Deduplication**: Automatically skips already downloaded papers
  - **Rate Limiting**: Respects CORE API limits (10 requests/minute)
  - **Error Handling**: Comprehensive error tracking and recovery
  - **Legal Compliance**: Only downloads properly licensed open access content

#### Download Process Flow:
1. **DOI Validation**: Validate and normalize DOI format
2. **CORE API Search**: Query CORE database for paper metadata
3. **Availability Check**: Verify PDF download URL exists
4. **Legal Download**: Download from institutional repositories
5. **Progress Tracking**: Update real-time progress indicators
6. **File Management**: Save with descriptive filenames and track success/failure

#### Extractors (`downloader/core/extractors/`)
- **bibtex.py**: Web of Science and general BibTeX DOI extraction
- **rayyan.py**: Rayyan CSV format DOI extraction  
- **scopus.py**: Scopus-specific BibTeX DOI extraction

### 4. Web Interface (`downloader/web/`)

#### Application Factory (`app.py`)
- **Responsibility**: Flask application creation and configuration
- **Features**:
  - Blueprint registration
  - Error handler setup
  - Configuration integration

#### Route Handlers (`routes/`)
- **main.py**: Dashboard and navigation routes
- **download.py**: Download management routes
- **api.py**: REST API endpoints
- **Responsibilities**:
  - Request handling
  - File upload processing
  - Progress tracking
  - Error responses

#### Templates (`templates/`)
- **index.html**: Main dashboard interface
- **download.html**: Download management interface
- **extract_*.html**: Format-specific extraction pages
- **Features**:
  - Responsive design
  - Progress indicators
  - Error handling
  - Modern UI/UX

### 5. Utilities (`downloader/utils/`)
- **logging.py**: Centralized logging system
- **validation.py**: Input validation utilities
- **Responsibilities**:
  - Structured logging
  - Input sanitization
  - Error tracking

## Data Flow Architecture

### 1. Upload Flow
```
User Upload → File Validation → Format Detection → DOI Extraction → Results Display
```

### 2. Download Flow
```
DOI List → Validation → Download Queue → Progress Tracking → File Storage → Completion
```

### 3. Progress Tracking
```
Download Session → Progress Updates → Real-time Display → Completion Logging
```

## Design Patterns

### 1. Factory Pattern
- Application factory for Flask app creation
- Extractor factory for format-specific processing

### 2. Strategy Pattern
- Different extractors for different file formats
- Configurable download strategies

### 3. Observer Pattern
- Progress tracking and real-time updates
- Event-driven architecture

### 4. Repository Pattern
- Data access abstraction
- File system operations encapsulation

## Security Architecture

### Input Validation
- File type validation
- DOI format validation
- Path traversal prevention
- File size limits

### Error Handling
- Graceful failure handling
- User-friendly error messages
- Security event logging

### Data Privacy
- No persistent user data
- Temporary file cleanup
- Secure file handling

## Performance Architecture

### Optimization Strategies
- Asynchronous processing
- Progress streaming
- Memory-efficient file handling
- Connection pooling

### Monitoring
- Progress tracking
- Performance metrics
- Error rate monitoring
- Resource usage tracking

## Deployment Architecture

### Development
- Local Flask development server
- Auto-reload on changes
- Debug mode enabled

### Production
- WSGI server (Gunicorn/uWSGI)
- Reverse proxy (nginx/Apache)
- SSL termination
- Load balancing

### Portable
- Self-contained executables
- Zero external dependencies
- Cross-platform compatibility 