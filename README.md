# PDF Merger Tool

A user-friendly PDF merger application with both GUI and CLI interfaces. Merge multiple PDF files into a single document with drag-and-drop support, custom file ordering, and progress tracking.

## Features

- **Dual Interface**: Both graphical (GUI) and command-line (CLI) interfaces
- **Drag & Drop**: Easy file selection with drag-and-drop support (GUI)
- **Custom Ordering**: Reorder files before merging
- **Progress Tracking**: Real-time progress indicators for merge operations
- **Error Handling**: Comprehensive validation and error reporting
- **File Information**: View page counts, file sizes, and metadata
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies
- `PyPDF2`: PDF manipulation library
- `tkinterdnd2`: Drag-and-drop support for GUI (optional)
- `tqdm`: Progress bars for CLI

## Usage

### GUI Version

Run the graphical interface:

```bash
python pdf_merger_gui.py
```

**GUI Features:**
- Drag and drop PDF files onto the file list
- Use "Add Files" button to browse for PDFs
- Reorder files using "Move Up" and "Move Down" buttons
- Remove selected files or clear all files
- Choose output location with "Browse" button
- Real-time progress bar during merging
- File information display (pages, size)

### CLI Version

Run the command-line interface:

```bash
python pdf_merger_cli.py file1.pdf file2.pdf -o merged.pdf
```

**CLI Options:**

```bash
# Basic usage
python pdf_merger_cli.py file1.pdf file2.pdf file3.pdf -o output.pdf

# Use wildcard patterns
python pdf_merger_cli.py *.pdf -o combined.pdf

# Read file list from text file
python pdf_merger_cli.py -i filelist.txt -o merged.pdf

# Show file information
python pdf_merger_cli.py *.pdf -o output.pdf --info

# Validate files only (no merging)
python pdf_merger_cli.py *.pdf -o output.pdf --validate-only

# Verbose output
python pdf_merger_cli.py file1.pdf file2.pdf -o output.pdf --verbose

# Disable progress bar
python pdf_merger_cli.py *.pdf -o output.pdf --no-progress

# Force overwrite existing output file
python pdf_merger_cli.py *.pdf -o existing.pdf --force
```

**CLI Arguments:**
- `files`: PDF files to merge (positional arguments)
- `-i, --input-list`: Text file with list of PDF files (one per line)
- `-o, --output`: Output PDF file path (required)
- `--validate-only`: Only validate files, don't merge
- `--info`: Show detailed file information
- `--verbose, -v`: Enable verbose output
- `--no-progress`: Disable progress bar
- `--force`: Overwrite existing output file

## File Structure

```
pdf-merger/
├── pdf_merger_core.py      # Core PDF merging functionality
├── pdf_merger_gui.py       # Tkinter GUI application
├── pdf_merger_cli.py       # Command-line interface
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Error Handling

The application includes comprehensive error handling for:

- **Invalid PDF files**: Corrupted or unreadable PDFs are detected and skipped
- **Missing files**: Non-existent files are reported with clear error messages
- **Permission errors**: Read/write permission issues are handled gracefully
- **Disk space**: Insufficient disk space errors are caught and reported
- **Output conflicts**: Existing output files require confirmation or `--force` flag

## Logging

Both versions create a log file (`pdf_merger.log`) with detailed information about:
- File validation results
- Merge progress and status
- Error details and stack traces
- Performance metrics

## Examples

### GUI Workflow
1. Launch `python pdf_merger_gui.py`
2. Drag PDF files into the application window
3. Reorder files using the move buttons
4. Click "Browse" to choose output location
5. Click "Merge PDFs" to start the process
6. Monitor progress in the progress bar

### CLI Workflow
```bash
# Create a file list
echo "document1.pdf" > files.txt
echo "document2.pdf" >> files.txt
echo "document3.pdf" >> files.txt

# Merge using file list with information display
python pdf_merger_cli.py -i files.txt -o combined.pdf --info --verbose

# Quick merge with wildcards
python pdf_merger_cli.py chapter*.pdf -o book.pdf
```

## Troubleshooting

**Common Issues:**

1. **"tkinterdnd2 not found"**: Drag-and-drop won't work, but GUI will still function
   ```bash
   pip install tkinterdnd2
   ```

2. **"Permission denied"**: Check file permissions for input PDFs and output directory

3. **"Invalid PDF"**: Some PDFs may be corrupted or password-protected

4. **"Module not found"**: Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.# pdf-editor
