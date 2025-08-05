#!/usr/bin/env python3
"""
Flask web application for PDF merging.
Provides a browser-based interface for the PDF merger tool.
"""

import os
import json
import uuid
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from pdf_merger_core import PDFMergerCore, setup_logging

# Configure Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix='pdf_merger_')
app.config['SECRET_KEY'] = 'pdf-merger-secret-key-change-in-production'

# Global storage for merge jobs
merge_jobs: Dict[str, dict] = {}
merger = PDFMergerCore()

# Setup logging
setup_logging()

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def cleanup_old_files():
    """Clean up old uploaded files and completed jobs."""
    current_time = datetime.now()
    to_remove = []
    
    for job_id, job_data in merge_jobs.items():
        job_time = datetime.fromisoformat(job_data['created_at'])
        # Remove jobs older than 1 hour
        if (current_time - job_time).total_seconds() > 3600:
            to_remove.append(job_id)
            # Clean up files
            for file_path in job_data.get('uploaded_files', []):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
            # Clean up output file
            output_path = job_data.get('output_path')
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
    
    for job_id in to_remove:
        del merge_jobs[job_id]

@app.route('/')
def index():
    """Main application page."""
    cleanup_old_files()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Create new job
        job_id = str(uuid.uuid4())
        uploaded_files = []
        file_info = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Secure filename and save
                filename = secure_filename(file.filename)
                if not filename:
                    continue
                    
                # Add timestamp to avoid conflicts
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Validate PDF
                if merger.validate_pdf_file(file_path):
                    info = merger.get_pdf_info(file_path)
                    uploaded_files.append(file_path)
                    file_info.append({
                        'filename': file.filename,  # Original filename
                        'path': file_path,
                        'pages': info['pages'],
                        'size': info['file_size'],
                        'title': info.get('title', ''),
                        'valid': True
                    })
                else:
                    # Remove invalid file
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    file_info.append({
                        'filename': file.filename,
                        'path': None,
                        'pages': 0,
                        'size': 0,
                        'title': '',
                        'valid': False,
                        'error': 'Invalid PDF file'
                    })
        
        if not uploaded_files:
            return jsonify({'error': 'No valid PDF files uploaded'}), 400
        
        # Store job data
        merge_jobs[job_id] = {
            'id': job_id,
            'status': 'uploaded',
            'uploaded_files': uploaded_files,
            'file_info': file_info,
            'created_at': datetime.now().isoformat(),
            'progress': 0,
            'output_path': None,
            'error': None
        }
        
        return jsonify({
            'job_id': job_id,
            'files': file_info,
            'valid_count': len(uploaded_files),
            'total_count': len(file_info)
        })
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size is 100MB per request.'}), 413
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/reorder', methods=['POST'])
def reorder_files():
    """Reorder files for a job."""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        new_order = data.get('order', [])
        
        if job_id not in merge_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = merge_jobs[job_id]
        if job['status'] != 'uploaded':
            return jsonify({'error': 'Cannot reorder files after merge started'}), 400
        
        # Reorder files based on indices
        original_files = job['uploaded_files'].copy()
        original_info = job['file_info'].copy()
        
        reordered_files = []
        reordered_info = []
        
        valid_indices = [i for i in new_order if 0 <= i < len(original_files)]
        
        for index in valid_indices:
            reordered_files.append(original_files[index])
            reordered_info.append(original_info[index])
        
        job['uploaded_files'] = reordered_files
        job['file_info'] = reordered_info
        
        return jsonify({'success': True, 'files': reordered_info})
        
    except Exception as e:
        return jsonify({'error': f'Reorder failed: {str(e)}'}), 500

@app.route('/merge', methods=['POST'])
def start_merge():
    """Start the PDF merge process."""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        output_filename = data.get('output_filename', 'merged.pdf')
        
        if job_id not in merge_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = merge_jobs[job_id]
        if job['status'] != 'uploaded':
            return jsonify({'error': 'Job already processing or completed'}), 400
        
        if not job['uploaded_files']:
            return jsonify({'error': 'No files to merge'}), 400
        
        # Secure output filename
        output_filename = secure_filename(output_filename)
        if not output_filename.endswith('.pdf'):
            output_filename += '.pdf'
        
        # Set job status
        job['status'] = 'merging'
        job['progress'] = 0
        job['output_filename'] = output_filename
        
        # Start merge in background thread
        def merge_thread():
            try:
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                         f"{job_id}_{output_filename}")
                
                def progress_callback(current, total):
                    job['progress'] = int((current / total) * 100)
                
                success = merger.merge_pdfs(
                    job['uploaded_files'], 
                    output_path, 
                    progress_callback
                )
                
                if success:
                    job['status'] = 'completed'
                    job['output_path'] = output_path
                    job['progress'] = 100
                else:
                    job['status'] = 'failed'
                    job['error'] = 'Merge operation failed'
                    
            except Exception as e:
                job['status'] = 'failed'
                job['error'] = str(e)
        
        thread = threading.Thread(target=merge_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Merge started'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to start merge: {str(e)}'}), 500

@app.route('/status/<job_id>')
def get_status(job_id):
    """Get job status and progress."""
    if job_id not in merge_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = merge_jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'error': job.get('error'),
        'output_filename': job.get('output_filename'),
        'file_count': len(job['uploaded_files']),
        'created_at': job['created_at']
    })

@app.route('/download/<job_id>')
def download_file(job_id):
    """Download the merged PDF file."""
    if job_id not in merge_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = merge_jobs[job_id]
    if job['status'] != 'completed' or not job.get('output_path'):
        return jsonify({'error': 'File not ready for download'}), 400
    
    output_path = job['output_path']
    if not os.path.exists(output_path):
        return jsonify({'error': 'Output file not found'}), 404
    
    output_filename = job.get('output_filename', 'merged.pdf')
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=output_filename,
        mimetype='application/pdf'
    )

@app.route('/delete/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job and its files."""
    if job_id not in merge_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = merge_jobs[job_id]
    
    # Clean up files
    for file_path in job.get('uploaded_files', []):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
    
    # Clean up output file
    output_path = job.get('output_path')
    if output_path and os.path.exists(output_path):
        try:
            os.remove(output_path)
        except:
            pass
    
    # Remove job
    del merge_jobs[job_id]
    
    return jsonify({'success': True})

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 100MB per request.'}), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("PDF Merger Web Application")
    print("=" * 40)
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5000)