# PDF Merger - Web Application

A browser-based PDF merger tool with drag-and-drop functionality, real-time progress tracking, and a modern responsive interface.

## 🌐 Web Features

- **Modern Web Interface**: Beautiful, responsive design that works on desktop and mobile
- **Drag & Drop**: Simply drop PDF files onto the browser window
- **Real-time Progress**: Live progress updates during merge operations
- **File Management**: Reorder files by dragging, remove individual files
- **Instant Download**: Download merged PDFs directly from the browser
- **File Validation**: Automatic validation of PDF files with error reporting
- **Mobile Friendly**: Responsive design that adapts to all screen sizes

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment (if not already created)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Start the Web Server
```bash
# Activate virtual environment
source venv/bin/activate

# Option 1: Use the launcher (recommended)
python3 run_web.py

# Option 2: Start directly
python3 pdf_merger_web.py
```

### 3. Open Your Browser
The application will automatically open in your browser at:
**http://localhost:5000**

## 📱 How to Use

1. **Upload Files**: 
   - Drag PDF files onto the drop zone
   - Or click the drop zone to browse for files

2. **Arrange Files**:
   - Drag files to reorder them
   - Use arrow buttons to move files up/down
   - Remove unwanted files with the × button

3. **Merge**:
   - Enter a filename for the output (optional)
   - Click "Merge PDFs"
   - Watch the real-time progress

4. **Download**:
   - Click "Download Merged PDF" when complete
   - File downloads automatically to your browser's download folder

## 🔧 Configuration

### Server Settings
Edit `pdf_merger_web.py` to customize:

```python
# Maximum file size (default: 100MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Server host and port
app.run(host='0.0.0.0', port=5000)
```

### File Storage
- Uploaded files are stored in a temporary directory
- Files are automatically cleaned up after 1 hour
- Output files are deleted after download or session timeout

## 🌍 Network Access

To access from other devices on your network:

1. Find your computer's IP address:
   ```bash
   # On macOS/Linux
   ifconfig | grep inet

   # On Windows
   ipconfig
   ```

2. Start the server with network access:
   ```bash
   python3 pdf_merger_web.py
   ```

3. Access from other devices:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

## 🔒 Security Notes

- **File Privacy**: Files are processed locally on your server
- **Temporary Storage**: Files are automatically deleted after processing
- **No Cloud Upload**: All processing happens on your machine
- **HTTPS**: Consider using a reverse proxy for HTTPS in production

## 🐛 Troubleshooting

### Common Issues

**"Connection refused"**
- Make sure the server is running
- Check if port 5000 is available
- Try restarting the application

**"File too large"**
- Check the file size limit (default 100MB)
- Split large PDFs before merging

**"Invalid PDF"**
- Ensure files are valid PDF documents
- Try opening the PDF in a PDF viewer first
- Some password-protected PDFs may not work

**Browser compatibility**
- Works best in modern browsers (Chrome, Firefox, Safari, Edge)
- JavaScript must be enabled
- Cookies should be allowed for session management

### Debug Mode

To enable debug mode for development:

```python
# In pdf_merger_web.py, change:
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Logs

Check the console output and log files:
- Server logs appear in the terminal
- PDF processing logs are in `pdf_merger.log`

## 📊 Performance

- **File Limits**: 100MB per upload session
- **Concurrent Users**: Supports multiple simultaneous users
- **Memory Usage**: Optimized for large PDF files
- **Processing Speed**: Depends on PDF size and complexity

## 🔄 Updates

To update the application:

1. Pull latest changes
2. Update dependencies: `pip install -r requirements.txt`
3. Restart the server

## 📂 File Structure

```
pdf-merger/
├── pdf_merger_web.py       # Flask web application
├── templates/
│   └── index.html         # Main web interface
├── static/
│   └── app.js            # Frontend JavaScript
├── run_web.py            # Web application launcher
├── requirements.txt      # Python dependencies
└── README_WEB.md        # This file
```

## 🤝 API Endpoints

The web application provides these REST API endpoints:

- `GET /` - Main application page
- `POST /upload` - Upload PDF files
- `POST /reorder` - Reorder files in merge queue
- `POST /merge` - Start merge operation
- `GET /status/<job_id>` - Get merge progress
- `GET /download/<job_id>` - Download merged PDF
- `DELETE /delete/<job_id>` - Clean up job files

## 💡 Tips

- **Large Files**: For many large PDFs, consider using the CLI version
- **Batch Processing**: Upload multiple files at once for efficiency
- **Mobile Use**: The interface works well on tablets and phones
- **Bookmarking**: Bookmark http://localhost:5000 for quick access
- **Multiple Sessions**: Each browser tab creates a separate merge session