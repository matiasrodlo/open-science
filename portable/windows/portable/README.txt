# Science Downloader Portable

Download research papers with ease.

## Features

- 🌐 Web-based interface for easy use
- 📄 Extract DOIs from research files (BibTeX, Rayyan, Scopus)
- 📥 Download research papers automatically
- 💾 Portable - no installation required
- 🔍 Support for multiple research platforms

## How to Use

1. **Start the Application**
   - Double-click `science-downloader.exe` to launch
   - Your web browser will open automatically to `http://localhost:5000`

2. **Extract DOIs (Step 1)**
   - Choose your research platform: BibTeX, Rayyan, or Scopus
   - Upload your research file (BibTeX file, Rayyan export, or Scopus CSV)
   - The system will extract all DOIs from your file

3. **Download Papers (Step 2)**
   - Review the extracted DOIs
   - Click "Download Papers" to start downloading
   - Papers will be saved to your data directory

## Data Storage

All data is stored in:
```
%USERPROFILE%\AppData\Local\Science Downloader\
```

This includes:
- 📁 Downloads: Downloaded research papers
- 📁 Logs: Application logs
- 📁 Uploads: Temporary uploaded files

## System Requirements

- **OS**: Windows 7 or later (64-bit recommended)
- **Memory**: 4GB RAM minimum
- **Storage**: 1GB free space
- **Network**: Internet connection required
- **Browser**: Any modern web browser (Chrome, Firefox, Edge, Safari)

## Troubleshooting

**If the application doesn't start:**
1. Check if your antivirus is blocking the executable
2. Ensure you have sufficient disk space
3. Try running as administrator if needed

**If downloads fail:**
1. Check your internet connection
2. Verify the DOI is valid
3. Check the logs in the data directory

**If the web interface doesn't open:**
1. Manually open your browser and go to `http://localhost:5000`
2. Check if another application is using port 5000

## Legal Notice

⚠️ **Important**: This tool is for research and educational purposes only.

- Users are responsible for compliance with applicable copyright laws
- Respect institutional access policies
- Use responsibly and ethically
- The developers are not responsible for misuse

## Privacy

- No data is sent to external servers except for paper downloads
- All processing is done locally on your machine
- Uploaded files are automatically cleaned up after processing

## Support

- **GitHub**: https://github.com/your-repo/science-downloader
- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the main repository for detailed documentation

## Version

This is a portable build of Science Downloader.
For the latest version and source code, visit the GitHub repository.

---
*Made with ❤️ for the research community*
