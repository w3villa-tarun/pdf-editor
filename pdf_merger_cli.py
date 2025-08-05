#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path
from typing import List
from tqdm import tqdm
from pdf_merger_core import PDFMergerCore, setup_logging


class PDFMergerCLI:
    """Command-line interface for PDF merging."""
    
    def __init__(self):
        self.merger = PDFMergerCore()
        
    def parse_arguments(self):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description="Merge multiple PDF files into a single PDF",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s file1.pdf file2.pdf -o merged.pdf
  %(prog)s *.pdf -o combined.pdf
  %(prog)s -i files.txt -o output.pdf
  %(prog)s file1.pdf file2.pdf -o merged.pdf --verbose
            """
        )
        
        # Input options (mutually exclusive)
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument(
            'files', 
            nargs='*', 
            help='PDF files to merge'
        )
        input_group.add_argument(
            '-i', '--input-list',
            type=str,
            help='Text file containing list of PDF files (one per line)'
        )
        
        # Output options
        parser.add_argument(
            '-o', '--output',
            type=str,
            required=True,
            help='Output PDF file path'
        )
        
        # Optional arguments
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate input files without merging'
        )
        
        parser.add_argument(
            '--info',
            action='store_true',
            help='Show information about input files'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        parser.add_argument(
            '--no-progress',
            action='store_true',
            help='Disable progress bar'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite output file if it exists'
        )
        
        return parser.parse_args()
    
    def load_file_list(self, list_file: str) -> List[str]:
        """Load file paths from a text file."""
        try:
            with open(list_file, 'r') as f:
                files = [line.strip() for line in f if line.strip()]
            return files
        except FileNotFoundError:
            print(f"Error: Input list file '{list_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading input list file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def validate_files(self, files: List[str]) -> List[str]:
        """Validate input files and return valid ones."""
        valid_files = []
        
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}", file=sys.stderr)
                continue
                
            if not file_path.lower().endswith('.pdf'):
                print(f"Warning: Not a PDF file: {file_path}", file=sys.stderr)
                continue
                
            if not self.merger.validate_pdf_file(file_path):
                print(f"Warning: Invalid or corrupted PDF: {file_path}", file=sys.stderr)
                continue
                
            valid_files.append(file_path)
        
        return valid_files
    
    def show_file_info(self, files: List[str]):
        """Display information about the PDF files."""
        print(f"\n{'='*60}")
        print(f"{'FILE INFORMATION':^60}")
        print(f"{'='*60}")
        
        total_pages = 0
        total_size = 0
        
        for i, file_path in enumerate(files, 1):
            info = self.merger.get_pdf_info(file_path)
            size_mb = info['file_size'] / (1024 * 1024)
            
            print(f"\n{i:2d}. {os.path.basename(file_path)}")
            print(f"     Path: {file_path}")
            print(f"     Pages: {info['pages']}")
            print(f"     Size: {size_mb:.2f} MB")
            if info['title']:
                print(f"     Title: {info['title']}")
            if info['author']:
                print(f"     Author: {info['author']}")
            
            total_pages += info['pages']
            total_size += info['file_size']
        
        print(f"\n{'='*60}")
        print(f"Total files: {len(files)}")
        print(f"Total pages: {total_pages}")
        print(f"Total size: {total_size / (1024 * 1024):.2f} MB")
        print(f"{'='*60}\n")
    
    def run(self):
        """Main CLI execution function."""
        args = self.parse_arguments()
        
        # Setup logging
        log_level = 'DEBUG' if args.verbose else 'INFO'
        setup_logging(getattr(__import__('logging'), log_level))
        
        # Get input files
        if args.input_list:
            input_files = self.load_file_list(args.input_list)
        else:
            input_files = args.files
        
        if not input_files:
            print("Error: No input files specified.", file=sys.stderr)
            sys.exit(1)
        
        # Validate files
        print("Validating PDF files...")
        valid_files = self.validate_files(input_files)
        
        if not valid_files:
            print("Error: No valid PDF files found.", file=sys.stderr)
            sys.exit(1)
        
        print(f"Found {len(valid_files)} valid PDF file(s).")
        
        # Show file information if requested
        if args.info:
            self.show_file_info(valid_files)
        
        # If validate-only mode, exit here
        if args.validate_only:
            print("Validation complete. All files are valid PDFs.")
            sys.exit(0)
        
        # Check if output file exists
        if os.path.exists(args.output) and not args.force:
            response = input(f"Output file '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
        
        # Create output directory if needed
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except Exception as e:
                print(f"Error creating output directory: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Setup progress tracking
        if not args.no_progress:
            pbar = tqdm(total=len(valid_files), desc="Merging PDFs", unit="file")
            
            def progress_callback(current: int, total: int):
                pbar.n = current
                pbar.refresh()
        else:
            pbar = None
            progress_callback = None
        
        # Perform the merge
        print(f"\nMerging {len(valid_files)} PDF files...")
        try:
            success = self.merger.merge_pdfs(
                valid_files, 
                args.output, 
                progress_callback
            )
            
            if pbar:
                pbar.close()
            
            if success:
                # Get final file info
                output_size = os.path.getsize(args.output) / (1024 * 1024)
                print(f"\n✓ Successfully created: {args.output}")
                print(f"  Output size: {output_size:.2f} MB")
                
                if args.verbose:
                    # Show summary
                    info = self.merger.get_file_list_info(valid_files)
                    print(f"  Total input pages: {info['total_pages']}")
                    print(f"  Files processed: {info['valid_files']}/{info['total_files']}")
                    
            else:
                print(f"\n✗ Failed to merge PDFs. Check the log file for details.", file=sys.stderr)
                sys.exit(1)
                
        except KeyboardInterrupt:
            if pbar:
                pbar.close()
            print(f"\n\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            if pbar:
                pbar.close()
            print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for CLI application."""
    cli = PDFMergerCLI()
    cli.run()


if __name__ == "__main__":
    main()