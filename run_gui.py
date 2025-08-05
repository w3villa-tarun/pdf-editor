#!/usr/bin/env python3
"""
Launcher script for the PDF Merger GUI application.
This script handles import errors gracefully and provides helpful error messages.
"""

import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    try:
        import PyPDF2
    except ImportError:
        missing_deps.append('PyPDF2')
    
    try:
        import tkinterdnd2
        print("✓ Drag-and-drop support available")
    except ImportError:
        print("⚠ tkinterdnd2 not found - drag-and-drop will not be available")
        print("  Install with: pip install tkinterdnd2")
    
    try:
        import tqdm
    except ImportError:
        missing_deps.append('tqdm')
    
    if missing_deps:
        print(f"✗ Missing required dependencies: {', '.join(missing_deps)}")
        print(f"Install with: pip install {' '.join(missing_deps)}")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("PDF Merger Tool - GUI Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        sys.exit(1)
    
    print("✓ All core dependencies found")
    print("Starting GUI application...\n")
    
    try:
        from pdf_merger_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"✗ Error importing GUI module: {e}")
        print("Make sure pdf_merger_gui.py is in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error starting GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()