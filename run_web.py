#!/usr/bin/env python3
"""
Launcher script for the PDF Merger Web Application.
Handles dependency checking and provides helpful startup information.
"""

import sys
import subprocess
import webbrowser
import time
import threading
import os

def check_dependencies():
    """Check if all required web dependencies are installed."""
    missing_deps = []
    
    try:
        import PyPDF2
    except ImportError:
        missing_deps.append('PyPDF2')
    
    try:
        import flask
    except ImportError:
        missing_deps.append('Flask')
    
    try:
        import werkzeug
    except ImportError:
        missing_deps.append('Werkzeug')
    
    if missing_deps:
        print(f"✗ Missing required dependencies: {', '.join(missing_deps)}")
        print(f"Install with: pip install {' '.join(missing_deps)}")
        return False
    
    return True

def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:5000')

def main():
    """Main launcher function."""
    print("PDF Merger Tool - Web Application Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("✓ All dependencies found")
    print("✓ Starting web server...")
    print()
    print("Server will be available at: http://localhost:5000")
    print("Opening browser automatically...")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        from pdf_merger_web import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"✗ Error importing web module: {e}")
        print("Make sure pdf_merger_web.py is in the same directory.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error starting web server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()