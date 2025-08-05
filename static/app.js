/**
 * PDF Merger Web Application JavaScript
 * Handles file uploads, drag-and-drop, progress tracking, and UI interactions
 */

class PDFMerger {
    constructor() {
        this.jobId = null;
        this.files = [];
        this.sortable = null;
        this.progressInterval = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupSortable();
    }
    
    initializeElements() {
        // Get DOM elements
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.fileListContainer = document.getElementById('fileListContainer');
        this.fileList = document.getElementById('fileList');
        this.mergeControls = document.getElementById('mergeControls');
        this.outputFilename = document.getElementById('outputFilename');
        this.mergeBtn = document.getElementById('mergeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.statusMessage = document.getElementById('statusMessage');
        this.downloadSection = document.getElementById('downloadSection');
        this.downloadBtn = document.getElementById('downloadBtn');
    }
    
    setupEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
        
        // Drop zone click
        this.dropZone.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // Merge button
        this.mergeBtn.addEventListener('click', () => {
            this.startMerge();
        });
        
        // Clear button
        this.clearBtn.addEventListener('click', () => {
            this.clearAll();
        });
        
        // Download button
        this.downloadBtn.addEventListener('click', () => {
            this.downloadFile();
        });
    }
    
    setupDragAndDrop() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.remove('dragover');
            }, false);
        });
        
        // Handle dropped files
        this.dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            this.handleFiles(files);
        }, false);
    }
    
    setupSortable() {
        if (typeof Sortable !== 'undefined') {
            this.sortable = Sortable.create(this.fileList, {
                animation: 150,
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                onEnd: (evt) => {
                    this.reorderFiles(evt.oldIndex, evt.newIndex);
                }
            });
        }
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    async handleFiles(fileList) {
        const files = Array.from(fileList);
        const pdfFiles = files.filter(file => file.type === 'application/pdf');
        
        if (pdfFiles.length === 0) {
            this.showMessage('Please select PDF files only.', 'error');
            return;
        }
        
        if (pdfFiles.length !== files.length) {
            this.showMessage(`${files.length - pdfFiles.length} non-PDF files were ignored.`, 'info');
        }
        
        this.showMessage('Uploading files...', 'info');
        
        try {
            const formData = new FormData();
            pdfFiles.forEach(file => {
                formData.append('files', file);
            });
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Upload failed');
            }
            
            this.jobId = result.job_id;
            this.files = result.files;
            
            this.displayFiles();
            this.showControls();
            this.hideMessage();
            
            if (result.valid_count < result.total_count) {
                this.showMessage(
                    `${result.valid_count} of ${result.total_count} files are valid PDFs.`, 
                    'info'
                );
            }
            
        } catch (error) {
            this.showMessage(`Upload failed: ${error.message}`, 'error');
        }
    }
    
    displayFiles() {
        this.fileList.innerHTML = '';
        
        this.files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = `file-item ${file.valid ? '' : 'invalid'}`;
            fileItem.dataset.index = index;
            
            const sizeText = file.size > 0 ? this.formatBytes(file.size) : 'Unknown size';
            const pagesText = file.pages > 0 ? `${file.pages} pages` : 'No pages';
            
            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-name">
                        <i class="fas fa-file-pdf text-danger"></i>
                        ${file.filename}
                        ${!file.valid ? '<i class="fas fa-exclamation-triangle text-warning ms-2"></i>' : ''}
                    </div>
                    <div class="file-details">
                        ${file.valid ? `${pagesText} • ${sizeText}` : file.error || 'Invalid PDF'}
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-outline-primary btn-icon" 
                            onclick="pdfMerger.moveFile(${index}, -1)" 
                            title="Move up" ${index === 0 ? 'disabled' : ''}>
                        <i class="fas fa-arrow-up"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-primary btn-icon" 
                            onclick="pdfMerger.moveFile(${index}, 1)" 
                            title="Move down" ${index === this.files.length - 1 ? 'disabled' : ''}>
                        <i class="fas fa-arrow-down"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger btn-icon" 
                            onclick="pdfMerger.removeFile(${index})" 
                            title="Remove">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            this.fileList.appendChild(fileItem);
        });
        
        this.fileListContainer.style.display = 'block';
    }
    
    showControls() {
        this.mergeControls.style.display = 'block';
        const validFiles = this.files.filter(f => f.valid);
        this.mergeBtn.disabled = validFiles.length === 0;
    }
    
    moveFile(index, direction) {
        const newIndex = index + direction;
        if (newIndex < 0 || newIndex >= this.files.length) return;
        
        // Swap files
        [this.files[index], this.files[newIndex]] = [this.files[newIndex], this.files[index]];
        
        this.displayFiles();
        this.updateFileOrder();
    }
    
    removeFile(index) {
        this.files.splice(index, 1);
        this.displayFiles();
        
        if (this.files.length === 0) {
            this.clearAll();
        } else {
            this.updateFileOrder();
        }
    }
    
    async reorderFiles(oldIndex, newIndex) {
        // Move item in array
        const item = this.files.splice(oldIndex, 1)[0];
        this.files.splice(newIndex, 0, item);
        
        this.displayFiles();
        this.updateFileOrder();
    }
    
    async updateFileOrder() {
        if (!this.jobId) return;
        
        try {
            const validIndices = this.files
                .map((file, index) => file.valid ? index : -1)
                .filter(index => index !== -1);
            
            await fetch('/reorder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_id: this.jobId,
                    order: validIndices
                })
            });
        } catch (error) {
            console.error('Failed to update file order:', error);
        }
    }
    
    async startMerge() {
        const validFiles = this.files.filter(f => f.valid);
        if (validFiles.length === 0) {
            this.showMessage('No valid PDF files to merge.', 'error');
            return;
        }
        
        const outputFilename = this.outputFilename.value.trim() || 'merged.pdf';
        
        try {
            this.mergeBtn.disabled = true;
            this.clearBtn.disabled = true;
            this.hideMessage();
            
            const response = await fetch('/merge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_id: this.jobId,
                    output_filename: outputFilename
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Merge failed');
            }
            
            this.showProgress();
            this.startProgressMonitoring();
            
        } catch (error) {
            this.showMessage(`Merge failed: ${error.message}`, 'error');
            this.mergeBtn.disabled = false;
            this.clearBtn.disabled = false;
        }
    }
    
    showProgress() {
        this.progressContainer.style.display = 'block';
        this.progressBar.style.width = '0%';
        this.progressText.textContent = 'Starting merge...';
    }
    
    startProgressMonitoring() {
        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${this.jobId}`);
                const status = await response.json();
                
                if (!response.ok) {
                    throw new Error(status.error || 'Status check failed');
                }
                
                this.updateProgress(status);
                
                if (status.status === 'completed') {
                    this.onMergeComplete(status);
                } else if (status.status === 'failed') {
                    this.onMergeError(status.error || 'Merge failed');
                }
                
            } catch (error) {
                this.onMergeError(error.message);
            }
        }, 500);
    }
    
    updateProgress(status) {
        this.progressBar.style.width = `${status.progress}%`;
        
        if (status.progress < 100) {
            this.progressText.textContent = `Processing... ${status.progress}%`;
        } else {
            this.progressText.textContent = 'Finalizing...';
        }
    }
    
    onMergeComplete(status) {
        clearInterval(this.progressInterval);
        this.progressContainer.style.display = 'none';
        this.downloadSection.style.display = 'block';
        
        // Reset buttons
        this.mergeBtn.disabled = false;
        this.clearBtn.disabled = false;
    }
    
    onMergeError(error) {
        clearInterval(this.progressInterval);
        this.progressContainer.style.display = 'none';
        this.showMessage(`Merge failed: ${error}`, 'error');
        
        // Reset buttons
        this.mergeBtn.disabled = false;
        this.clearBtn.disabled = false;
    }
    
    downloadFile() {
        if (this.jobId) {
            console.log('Starting download for job:', this.jobId);
            const downloadUrl = `/download/${this.jobId}`;
            console.log('Download URL:', downloadUrl);
            
            // Try using a link element for better download handling
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = ''; // Let server set the filename
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Also try the original method as fallback
            setTimeout(() => {
                window.location.href = downloadUrl;
            }, 100);
        } else {
            console.error('No job ID available for download');
        }
    }
    
    clearAll() {
        if (this.jobId) {
            // Clean up server-side
            fetch(`/delete/${this.jobId}`, { method: 'DELETE' })
                .catch(console.error);
        }
        
        // Reset UI
        this.jobId = null;
        this.files = [];
        this.fileInput.value = '';
        this.fileListContainer.style.display = 'none';
        this.mergeControls.style.display = 'none';
        this.progressContainer.style.display = 'none';
        this.downloadSection.style.display = 'none';
        this.outputFilename.value = 'merged.pdf';
        this.hideMessage();
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }
    
    showMessage(message, type = 'info') {
        this.statusMessage.className = `status-message status-${type}`;
        this.statusMessage.innerHTML = `
            <i class="fas fa-${this.getIconForType(type)}"></i>
            ${message}
        `;
        this.statusMessage.style.display = 'block';
        
        // Auto-hide info messages after 5 seconds
        if (type === 'info') {
            setTimeout(() => {
                this.hideMessage();
            }, 5000);
        }
    }
    
    hideMessage() {
        this.statusMessage.style.display = 'none';
    }
    
    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pdfMerger = new PDFMerger();
});

// Handle page unload to clean up
window.addEventListener('beforeunload', () => {
    if (window.pdfMerger && window.pdfMerger.jobId) {
        // Clean up server-side resources
        navigator.sendBeacon(`/delete/${window.pdfMerger.jobId}`, new FormData());
    }
});