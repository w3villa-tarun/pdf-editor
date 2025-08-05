import os
import logging
from typing import List, Callable, Optional
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError


class PDFMergerCore:
    """Core PDF merging functionality with error handling and progress tracking."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_pdf_file(self, file_path: str) -> bool:
        """Validate if a file is a readable PDF."""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                # Try to access the first page to ensure the PDF is readable
                if len(reader.pages) > 0:
                    _ = reader.pages[0]
                return True
        except (PdfReadError, FileNotFoundError, PermissionError, Exception) as e:
            self.logger.error(f"Invalid PDF file {file_path}: {str(e)}")
            return False
    
    def get_pdf_info(self, file_path: str) -> dict:
        """Get basic information about a PDF file."""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                return {
                    'pages': len(reader.pages),
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'file_size': os.path.getsize(file_path)
                }
        except Exception as e:
            self.logger.error(f"Could not get info for {file_path}: {str(e)}")
            return {'pages': 0, 'title': '', 'author': '', 'file_size': 0}
    
    def merge_pdfs(self, 
                   input_files: List[str], 
                   output_path: str,
                   progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        Merge multiple PDF files into a single output file.
        
        Args:
            input_files: List of input PDF file paths
            output_path: Path for the output merged PDF
            progress_callback: Optional callback function for progress updates
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not input_files:
            self.logger.error("No input files provided")
            return False
            
        # Validate all input files first
        valid_files = []
        for file_path in input_files:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                continue
            if not self.validate_pdf_file(file_path):
                self.logger.error(f"Invalid PDF file: {file_path}")
                continue
            valid_files.append(file_path)
        
        if not valid_files:
            self.logger.error("No valid PDF files to merge")
            return False
        
        try:
            writer = PdfWriter()
            total_files = len(valid_files)
            
            for i, file_path in enumerate(valid_files):
                self.logger.info(f"Processing file {i+1}/{total_files}: {file_path}")
                
                try:
                    with open(file_path, 'rb') as file:
                        reader = PdfReader(file)
                        for page in reader.pages:
                            writer.add_page(page)
                    
                    if progress_callback:
                        progress_callback(i + 1, total_files)
                        
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    continue
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Write the merged PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            self.logger.info(f"Successfully merged {len(valid_files)} files into {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during merge operation: {str(e)}")
            return False
    
    def get_file_list_info(self, file_paths: List[str]) -> dict:
        """Get summary information about a list of PDF files."""
        total_pages = 0
        total_size = 0
        valid_files = 0
        
        for file_path in file_paths:
            if self.validate_pdf_file(file_path):
                info = self.get_pdf_info(file_path)
                total_pages += info['pages']
                total_size += info['file_size']
                valid_files += 1
        
        return {
            'total_files': len(file_paths),
            'valid_files': valid_files,
            'total_pages': total_pages,
            'total_size': total_size
        }


def setup_logging(level=logging.INFO):
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pdf_merger.log')
        ]
    )