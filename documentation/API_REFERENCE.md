# API Reference

## Overview

Science Downloader provides both web interface routes and REST API endpoints for programmatic access.

## Web Routes

### Main Interface

#### GET `/`
**Purpose**: Main dashboard  
**Response**: HTML dashboard with upload options  
**Features**: File upload forms, navigation, status display

#### GET `/download`
**Purpose**: Download management interface  
**Response**: HTML download page  
**Features**: DOI list display, download controls, progress tracking

#### GET `/extract/<format>`
**Purpose**: Format-specific extraction interface  
**Parameters**: `format` (bibtex, rayyan, scopus)  
**Response**: HTML extraction page  
**Features**: Format-specific upload forms, extraction options

### File Upload & Processing

#### POST `/upload`
**Purpose**: File upload and DOI extraction  
**Input**: Multipart form data  
**Parameters**:
- `file`: Uploaded file (BibTeX, CSV)
- `format`: File format (auto-detected if not specified)

**Response**: JSON
```json
{
  "success": true,
  "format": "bibtex",
  "total_found": 150,
  "unique_count": 145,
  "duplicates_removed": 5,
  "errors": [],
  "extracted_dois": ["10.1000/example.2024.001", ...]
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Invalid file format",
  "details": "File must be BibTeX or CSV format"
}
```

### Download Management

#### POST `/download`
**Purpose**: Initiate paper downloads  
**Input**: JSON
```json
{
  "dois": ["10.1000/example.2024.001", ...],
  "output_folder": "/path/to/output",
  "overwrite": false
}
```

**Response**: JSON
```json
{
  "success": true,
  "session_id": "download_20250101_120000",
  "total_requested": 100,
  "message": "Download started"
}
```

#### GET `/download/progress`
**Purpose**: Get current download progress  
**Response**: JSON
```json
{
  "current": 45,
  "total": 100,
  "progress_percent": 45.0,
  "downloaded": 42,
  "failed": 2,
  "skipped": 1,
  "current_doi": "10.1000/example.2024.001",
  "status": "downloading",
  "output_folder": "/path/to/output"
}
```

## REST API Endpoints

### Session Management

#### GET `/api/sessions`
**Purpose**: List all download sessions  
**Response**: JSON array of session objects

#### GET `/api/sessions/<session_id>`
**Purpose**: Get specific session details  
**Parameters**: `session_id` (string)  
**Response**: Session object with full details

#### DELETE `/api/sessions/<session_id>`
**Purpose**: Cancel/delete session  
**Parameters**: `session_id` (string)  
**Response**: Success confirmation

### Download Control

#### POST `/api/download/start`
**Purpose**: Start new download session  
**Input**: JSON
```json
{
  "dois": ["10.1000/example.2024.001"],
  "output_folder": "/path/to/output",
  "options": {
    "overwrite": false,
    "retry_failed": true,
    "max_retries": 3
  }
}
```

#### POST `/api/download/stop`
**Purpose**: Stop current download session  
**Response**: Success confirmation

#### GET `/api/download/status`
**Purpose**: Get current download status  
**Response**: Current progress object

### DOI Management

#### GET `/api/dois`
**Purpose**: List all DOIs in library  
**Query Parameters**:
- `format`: Filter by source format
- `status`: Filter by download status
- `limit`: Limit results (default: 100)
- `offset`: Pagination offset

**Response**: JSON array of DOI objects

#### POST `/api/dois/validate`
**Purpose**: Validate DOI format  
**Input**: JSON
```json
{
  "dois": ["10.1000/example.2024.001", "invalid-doi"]
}
```

**Response**: JSON
```json
{
  "valid": ["10.1000/example.2024.001"],
  "invalid": ["invalid-doi"],
  "total_valid": 1,
  "total_invalid": 1
}
```

#### POST `/api/dois/extract`
**Purpose**: Extract DOIs from file  
**Input**: Multipart form data with file  
**Response**: Extraction results object

### Statistics & Analytics

#### GET `/api/stats/overview`
**Purpose**: Get application statistics  
**Response**: JSON
```json
{
  "total_sessions": 25,
  "total_downloads": 1250,
  "success_rate": 0.92,
  "average_session_size": 50,
  "most_common_formats": ["bibtex", "rayyan"],
  "recent_activity": [...]
}
```

#### GET `/api/stats/sessions`
**Purpose**: Get session statistics  
**Query Parameters**:
- `days`: Number of days to include
- `format`: Filter by file format

## Data Models

### Download Session
```json
{
  "session_id": "download_20250101_120000",
  "timestamp": "2025-01-01T12:00:00Z",
  "doi_file": "/path/to/dois.txt",
  "output_folder": "/path/to/output",
  "total_requested": 100,
  "filtered_out": 5,
  "attempted": 95,
  "downloaded": 90,
  "failed": 3,
  "skipped": 2,
  "status": "completed",
  "duration_seconds": 300,
  "average_speed": "2.5 papers/minute"
}
```

### Progress Status
```json
{
  "session_id": "download_20250101_120000",
  "current": 45,
  "total": 100,
  "progress_percent": 45.0,
  "downloaded": 42,
  "failed": 2,
  "skipped": 1,
  "current_doi": "10.1000/example.2024.001",
  "status": "downloading",
  "start_time": "2025-01-01T12:00:00Z",
  "estimated_completion": "2025-01-01T12:05:00Z",
  "output_folder": "/path/to/output"
}
```

### DOI Object
```json
{
  "doi": "10.1000/example.2024.001",
  "title": "Example Research Paper",
  "authors": ["Author 1", "Author 2"],
  "journal": "Example Journal",
  "year": 2024,
  "source_format": "bibtex",
  "extraction_date": "2025-01-01T12:00:00Z",
  "download_status": "downloaded",
  "download_date": "2025-01-01T12:01:00Z",
  "file_path": "/path/to/output/example.pdf"
}
```

### Extraction Result
```json
{
  "success": true,
  "source_format": "bibtex",
  "total_found": 150,
  "unique_count": 145,
  "duplicates_removed": 5,
  "total_errors": 0,
  "total_records_processed": 150,
  "errors": [],
  "extracted_dois": ["10.1000/example.2024.001", ...],
  "processing_time_seconds": 2.5
}
```

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": "Additional error details",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Common Error Codes
- `INVALID_FILE_FORMAT`: Unsupported file format
- `FILE_TOO_LARGE`: File exceeds size limit
- `INVALID_DOI`: Malformed DOI format
- `DOWNLOAD_FAILED`: Paper download failed
- `SESSION_NOT_FOUND`: Download session not found
- `PERMISSION_DENIED`: File system permission error

## Rate Limiting

- **Uploads**: 10 requests per minute
- **Downloads**: 5 sessions per minute
- **API calls**: 100 requests per minute

## Authentication

Currently, the API does not require authentication as it's designed for local use. For production deployments, consider implementing:

- API key authentication
- Session-based authentication
- OAuth integration

## CORS

CORS is enabled for local development. For production, configure appropriate origins:

```python
CORS_ORIGINS = ["https://yourdomain.com"]
```

## Versioning

API versioning is handled through URL prefixes:
- Current version: `/api/v1/`
- Future versions: `/api/v2/`, etc.

## Examples

### Python Client Example
```python
import requests

# Upload file and extract DOIs
with open('papers.bib', 'rb') as f:
    response = requests.post('http://localhost:5000/upload', 
                           files={'file': f})
    result = response.json()

# Start download
download_data = {
    'dois': result['extracted_dois'],
    'output_folder': '/path/to/output'
}
response = requests.post('http://localhost:5000/api/download/start',
                        json=download_data)
```

### JavaScript Client Example
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(result => {
    console.log('Extracted DOIs:', result.extracted_dois);
});

// Monitor progress
setInterval(() => {
    fetch('/api/download/status')
    .then(response => response.json())
    .then(status => {
        updateProgressBar(status.progress_percent);
    });
}, 1000);
``` 