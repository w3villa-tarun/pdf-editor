#!/usr/bin/env python3
"""
Sample test script to demonstrate PDF merger functionality.
This creates sample text files and converts them to demonstrate the merger.
"""

import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pdf_merger_core import PDFMergerCore, setup_logging

def create_sample_pdf(filename, title, pages=3):
    """Create a sample PDF with multiple pages for testing."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
    except ImportError:
        print("⚠ ReportLab not available - cannot create sample PDFs")
        print("  Install with: pip install reportlab")
        return False
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    for page in range(1, pages + 1):
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 100, f"{title}")
        
        # Add page number
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 130, f"Page {page} of {pages}")
        
        # Add some content
        c.setFont("Helvetica", 10)
        content_lines = [
            f"This is a sample PDF document: {title}",
            f"Created for testing the PDF merger tool.",
            f"Current page: {page}",
            "",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco",
            "laboris nisi ut aliquip ex ea commodo consequat.",
        ]
        
        y_position = height - 180
        for line in content_lines:
            c.drawString(100, y_position, line)
            y_position -= 15
        
        # Add a box for visual distinction
        c.rect(80, height - 250, width - 160, 100, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 220, f"Document: {title}")
        c.drawString(100, height - 240, f"Page {page}")
        
        if page < pages:
            c.showPage()
    
    c.save()
    return True

def run_sample_test():
    """Run a complete test of the PDF merger functionality."""
    print("PDF Merger - Sample Test")
    print("=" * 40)
    
    # Setup logging
    setup_logging()
    
    # Create merger instance
    merger = PDFMergerCore()
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating test files in: {temp_dir}")
        
        # Create sample PDFs
        sample_files = []
        sample_data = [
            ("Document_A", 2),
            ("Document_B", 3),
            ("Document_C", 1)
        ]
        
        for doc_name, pages in sample_data:
            filename = os.path.join(temp_dir, f"{doc_name}.pdf")
            if create_sample_pdf(filename, doc_name, pages):
                sample_files.append(filename)
                print(f"✓ Created {doc_name}.pdf ({pages} pages)")
            else:
                print(f"✗ Failed to create {doc_name}.pdf")
        
        if not sample_files:
            print("✗ No sample files created - cannot test merger")
            return False
        
        # Test file validation
        print(f"\nTesting file validation...")
        for file_path in sample_files:
            is_valid = merger.validate_pdf_file(file_path)
            print(f"  {os.path.basename(file_path)}: {'✓ Valid' if is_valid else '✗ Invalid'}")
        
        # Test file info
        print(f"\nGetting file information...")
        for file_path in sample_files:
            info = merger.get_pdf_info(file_path)
            filename = os.path.basename(file_path)
            size_kb = info['file_size'] / 1024
            print(f"  {filename}: {info['pages']} pages, {size_kb:.1f} KB")
        
        # Test list info
        list_info = merger.get_file_list_info(sample_files)
        print(f"\nList summary:")
        print(f"  Total files: {list_info['total_files']}")
        print(f"  Valid files: {list_info['valid_files']}")
        print(f"  Total pages: {list_info['total_pages']}")
        print(f"  Total size: {list_info['total_size']/1024:.1f} KB")
        
        # Test merging
        output_file = os.path.join(temp_dir, "merged_output.pdf")
        print(f"\nMerging files into: {os.path.basename(output_file)}")
        
        def progress_callback(current, total):
            percent = (current / total) * 100
            print(f"  Progress: {current}/{total} files ({percent:.0f}%)")
        
        success = merger.merge_pdfs(sample_files, output_file, progress_callback)
        
        if success:
            print("✓ Merge completed successfully!")
            
            # Verify output
            if os.path.exists(output_file):
                output_info = merger.get_pdf_info(output_file)
                output_size_kb = output_info['file_size'] / 1024
                print(f"  Output: {output_info['pages']} pages, {output_size_kb:.1f} KB")
                
                # Validate merged file
                if merger.validate_pdf_file(output_file):
                    print("✓ Merged file is valid")
                else:
                    print("✗ Merged file validation failed")
            else:
                print("✗ Output file not found")
                return False
        else:
            print("✗ Merge failed!")
            return False
    
    print(f"\n{'='*40}")
    print("✓ All tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = run_sample_test()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\nTest cancelled by user.")
        exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)