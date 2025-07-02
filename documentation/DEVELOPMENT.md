# Development Guide

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Setup
```bash
# Clone repository
git clone <repository-url>
cd science-downloader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Development Dependencies
```bash
# Install development tools
pip install -r requirements.txt[dev]

# Install build tools
pip install -r requirements.txt[build]
```

## Project Structure

```
science-downloader/
├── app.py                 # Main entry point
├── downloader/            # Core application
│   ├── __init__.py       # Package initialization
│   ├── config/           # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/             # Business logic
│   │   ├── __init__.py
│   │   ├── downloaders/  # Download engines
│   │   ├── extractors/   # DOI extractors
│   │   └── models/       # Data models
│   ├── utils/            # Utilities
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── validation.py
│   └── web/              # Web interface
│       ├── __init__.py
│       ├── app.py        # Flask app factory
│       ├── main.py       # Web entry point
│       ├── routes/       # Route handlers
│       ├── templates/    # HTML templates
│       └── static/       # Static assets
├── data/                 # Application data
├── portable/             # Portable builds
├── tests/                # Test suite
├── docs/                 # Documentation
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── README.md            # Project overview
```

## Development Workflow

### 1. Code Style
Follow PEP 8 guidelines with Black formatting:

```bash
# Format code
black .

# Check formatting
black --check .

# Line length: 88 characters
# Target Python versions: 3.8+
```

### 2. Type Checking
Use MyPy for static type checking:

```bash
# Run type checker
mypy downloader/

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
disallow_untyped_defs = true
```

### 3. Linting
Use Flake8 for code quality:

```bash
# Run linter
flake8 downloader/

# Configuration
max-line-length = 88
exclude = .git,__pycache__,venv
```

### 4. Testing
Use pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=downloader

# Run specific test file
pytest tests/test_extractors.py

# Run with verbose output
pytest -v
```

## Testing Strategy

### Test Structure
```
tests/
├── conftest.py          # Pytest configuration
├── test_extractors.py   # Extractor tests
├── test_downloaders.py  # Downloader tests
├── test_web.py          # Web interface tests
├── test_utils.py        # Utility tests
└── fixtures/            # Test data
    ├── sample.bib       # Sample BibTeX file
    ├── sample.csv       # Sample CSV file
    └── test_dois.txt    # Test DOI list
```

### Test Categories

#### Unit Tests
- Individual component testing
- Mock external dependencies
- Fast execution
- High coverage

#### Integration Tests
- Component interaction testing
- File system operations
- Database operations
- API endpoint testing

#### End-to-End Tests
- Complete workflow testing
- User interface testing
- Real file processing
- Download simulation

### Test Examples

#### Extractor Test
```python
import pytest
from downloader.core.extractors import BibTeXExtractor

def test_bibtex_extractor():
    extractor = BibTeXExtractor()
    with open('tests/fixtures/sample.bib', 'r') as f:
        content = f.read()
    
    result = extractor.extract(content)
    
    assert result.success is True
    assert len(result.extracted_dois) > 0
    assert all(doi.startswith('10.') for doi in result.extracted_dois)
```

#### Web API Test
```python
import pytest
from downloader.web import create_app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_upload_endpoint(client):
    with open('tests/fixtures/sample.bib', 'rb') as f:
        response = client.post('/upload', 
                             data={'file': (f, 'sample.bib')})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
```

## Configuration Management

### Environment Variables
```bash
# Development
export FLASK_ENV=development
export FLASK_DEBUG=true
export DATA_DIR=./data
export LOGS_DIR=./data/logs

# Production
export FLASK_ENV=production
export FLASK_DEBUG=false
export DATA_DIR=/var/lib/science-downloader
export LOGS_DIR=/var/log/science-downloader
```

### Configuration Classes
```python
# downloader/config/settings.py
class Config:
    """Base configuration"""
    DEBUG = False
    DATA_DIR = Path("./data")
    LOGS_DIR = Path("./data/logs")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_PORT = 5000

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_PORT = 8080
```

## Debugging

### Logging
```python
from downloader.utils import get_logger

logger = get_logger(__name__)

# Debug logging
logger.debug("Processing file: %s", filename)

# Error logging
logger.error("Download failed: %s", error)
```

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=true
python app.py

# Features:
# - Auto-reload on file changes
# - Detailed error pages
# - Debug logging
# - Interactive debugger
```

### Common Issues

#### Port Conflicts
```bash
# Check port usage
lsof -i :5000

# Kill process using port
kill -9 <PID>

# Or use different port
export FLASK_PORT=5001
```

#### File Permissions
```bash
# Fix data directory permissions
chmod 755 data/
chmod 644 data/*.json
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Add current directory to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Building

### Portable Apps

#### macOS
```bash
cd portable/macos/builder
./build.sh

# Creates:
# - Science Downloader.app
# - science-downloader.dmg
```

#### Windows
```bash
cd portable/windows/builder
python build_windows.py

# Creates:
# - science-downloader.exe
```

### Distribution
```bash
# Build wheel
python -m build

# Build source distribution
python setup.py sdist

# Upload to PyPI (if applicable)
twine upload dist/*
```

## Performance Optimization

### Profiling
```python
import cProfile
import pstats

# Profile function
def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

### Memory Optimization
```python
# Use generators for large files
def process_large_file(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield process_line(line)

# Batch processing
def batch_process(items, batch_size=100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield process_batch(batch)
```

## Security

### Input Validation
```python
from downloader.utils.validation import validate_doi, validate_file

# Validate DOI
if not validate_doi(doi):
    raise ValueError("Invalid DOI format")

# Validate file
if not validate_file(file_path):
    raise ValueError("Invalid file type")
```

### File Security
```python
import os
from pathlib import Path

# Secure file path
def secure_path(file_path):
    return Path(file_path).resolve().relative_to(Path.cwd())

# Check file permissions
def check_permissions(file_path):
    return os.access(file_path, os.R_OK)
```

## Contributing

### Code Review Process
1. Create feature branch
2. Write tests
3. Update documentation
4. Submit pull request
5. Code review
6. Merge to main

### Commit Guidelines
```
feat: add new DOI extractor for Scopus format
fix: resolve port conflict in development mode
docs: update API documentation
test: add integration tests for downloader
refactor: improve error handling in extractors
```

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

## Troubleshooting

### Common Development Issues

#### Import Errors
```bash
# Solution: Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Test Failures
```bash
# Solution: Clear cache
pytest --cache-clear

# Solution: Update test data
python -m pytest --update-snapshots
```

#### Build Failures
```bash
# Solution: Clean build artifacts
rm -rf build/ dist/ *.egg-info/

# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Getting Help
- Check existing issues on GitHub
- Review documentation
- Run tests to isolate problems
- Use debug mode for detailed error information 