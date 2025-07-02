# Open Science Downloader

Download research articles and books in bulk — completely free and legally compliant.

Access 90+ million open access research papers from thousands of repositories worldwide. Install in just 3 clicks. Effortlessly extract DOIs from Web of Science, Scopus, and Rayyan, then automatically retrieve thousands — or even millions — of open-access academic papers and documents via a clean, user-friendly interface.

[![Science Downloader Interface](https://github.com/user-attachments/assets/7349d1e2-0b3e-4dca-9abf-9966113abb57)](https://github.com/matiasrodlo/science-downloader?tab=readme-ov-file#installation)

This software is provided for educational and research purposes only. Users are solely responsible for ensuring compliance with all applicable laws, copyright regulations, and institutional policies.

## Features

### Step 1: Extract DOIs
- **Web of Science** BibTeX files
- **Scopus** BibTeX files  
- **Rayyan** CSV files
- Automatic DOI extraction and validation

### Step 2: Download Papers
- Upload DOI file (one per line)
- Real-time progress tracking
- Automatic duplicate detection
- Smart port detection (5000-5009)

## Installation

**macOS:**
1. Download the latest [DMG](https://github.com/matiasrodlo/science-downloader/raw/refs/heads/main/portable/macos/portable/science-downloader.dmg)
2. Double-click `science-downloader.dmg`
3. Drag `Science Downloader.app` to Applications
4. If you try to open the app, macOS will say the app is "damaged". Open Terminal (Applications → Utilities → Terminal) and copy/paste: `sudo xattr -rd com.apple.quarantine "/Applications/Science Downloader.app"` and press enter. If requested, enter your administrator password and press enter again. This is a one-time fix - the app will work normally after this.
5. Launch from Applications or Launchpad

**Windows:**
1. Download the latest [Install .exe](https://github.com/matiasrodlo/science-downloader/raw/refs/heads/main/portable/windows/portable/science-downloader.exe)
2. Run `science-downloader.exe`
3. If Windows shows a security alert, click "More info" → "Run anyway". Alternatively, right-click the .exe, click Properties, go to Compatibility tab and select "Run as administrator" for a one-time fix. Both methods are safe and will allow the app to run normally.

> **Note:** Both macOS and Windows show security alerts because the app is not digitally signed. This alert does not indicate any security risk. The app is completely safe to use. Digital signing requires expensive annual certificates ($99-500/year), which is why this free app remains unsigned.

**Manual Installation (for developers):**
1. Install Python 3.8+ from [python.org](https://python.org)
2. Clone the repository: `git clone https://github.com/your-repo/science-downloader.git`
3. Navigate to the project: `cd science-downloader`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`
6. Open http://localhost:5000 in your browser

## Documentation

For detailed documentation, see the [documentation/](documentation/) folder:

- **[Documentation Index](documentation/DOCS_INDEX.md)** - Complete documentation navigation
- **[Architecture](documentation/ARCHITECTURE.md)** - System design and components
- **[API Reference](documentation/API_REFERENCE.md)** - Complete API documentation
- **[Development Guide](documentation/DEVELOPMENT.md)** - Development setup and guidelines
- **[Deployment Guide](documentation/DEPLOYMENT.md)** - Production deployment instructions

## Structure

```
science-downloader/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── .gitignore              # Git ignore rules
├── documentation/           # Comprehensive documentation
│   ├── README.md           # Documentation overview
│   ├── DOCS_INDEX.md       # Documentation navigation
│   ├── ARCHITECTURE.md     # System architecture
│   ├── API_REFERENCE.md    # API documentation
│   ├── DEVELOPMENT.md      # Development guide
│   └── DEPLOYMENT.md       # Deployment guide
├── downloader/              # Core application modules
│   ├── __init__.py         # Package initialization
│   ├── config/             # Configuration settings
│   ├── core/               # Core business logic
│   │   ├── downloaders/    # Download engines
│   │   └── extractors/     # DOI extraction modules
│   ├── utils/              # Utility functions
│   └── web/                # Web interface components
├── portable/                # Portable builds
│   ├── macos/              # macOS build system
│   │   ├── builder/        # Build scripts and tools
│   │   ├── portable/       # Generated macOS app
│   │   └── meta-data-sample.bib
│   └── windows/            # Windows build system
│       ├── builder/        # Build scripts and tools
│       ├── portable/       # Generated Windows app
│       └── science-downloader-portable.rar
└── data/                   # Application data and logs
    ├── logs/               # Log files
    ├── uploads/            # User uploads
    ├── extracted_dois.txt  # Extracted DOIs
    ├── library.txt         # DOI library
    ├── download_history.json
    └── failed_dois.txt     # Failed downloads
```

## Legal

This application is designed to assist with downloading metadata and research papers from legal open-access sources only. Users are solely responsible for ensuring compliance with applicable copyright laws, licensing terms, and institutional access policies. The developers disclaim all liability for misuse or unlawful use.

**Important Legal Information:**
- This tool is provided "as is" for educational and research purposes only
- Users must ensure they have proper authorization to access any materials
- The developers do not endorse or facilitate access to copyrighted materials without proper licensing
- Use of this tool to access copyrighted materials without authorization may violate copyright laws
- Institutional policies may prohibit the use of this tool
- Users are responsible for compliance with all applicable laws and policies
- The developers disclaim all liability for any legal consequences of use

**Open Access Focus:** This tool is specifically designed to work with:
- Open access repositories (arXiv, PubMed Central, etc.)
- Institutional repositories with proper access
- Public domain materials
- Materials with Creative Commons licenses
- Materials where users have proper institutional access
