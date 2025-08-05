import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading
from typing import List
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    
from pdf_merger_core import PDFMergerCore, setup_logging


class PDFMergerGUI:
    """GUI application for PDF merging with drag-and-drop support."""
    
    def __init__(self):
        # Initialize the main window
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
            
        self.root.title("PDF Merger Tool")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize core merger
        self.merger = PDFMergerCore()
        setup_logging()
        
        # File list storage
        self.file_paths = []
        
        # Create GUI elements
        self.create_widgets()
        self.setup_drag_and_drop()
        
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Merger Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="PDF Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(file_frame)
        buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Add Files", 
                  command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Remove Selected", 
                  command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear All", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Move Up", 
                  command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Move Down", 
                  command=self.move_down).pack(side=tk.LEFT, padx=5)
        
        # Drag and drop instruction
        if DND_AVAILABLE:
            instruction_text = "Drag and drop PDF files here, or use the buttons above"
        else:
            instruction_text = "Use the buttons above to add PDF files (drag-and-drop not available)"
            
        instruction_label = ttk.Label(file_frame, text=instruction_text, 
                                    font=('Arial', 9, 'italic'))
        instruction_label.grid(row=1, column=0, sticky=tk.W)
        
        # File list with scrollbar
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        file_frame.rowconfigure(2, weight=1)
        
        # Treeview for file list
        self.file_tree = ttk.Treeview(list_frame, columns=('pages', 'size'), 
                                     show='tree headings', height=8)
        self.file_tree.heading('#0', text='File Name')
        self.file_tree.heading('pages', text='Pages')
        self.file_tree.heading('size', text='Size')
        
        self.file_tree.column('#0', width=400)
        self.file_tree.column('pages', width=80)
        self.file_tree.column('size', width=100)
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                   command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, 
                                   command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, 
                                xscrollcommand=h_scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, 
                                                         sticky=tk.W, padx=(0, 10))
        
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="Browse", 
                  command=self.browse_output).grid(row=0, column=2)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 10))
        
        # Merge button
        self.merge_button = ttk.Button(progress_frame, text="Merge PDFs", 
                                      command=self.start_merge, state=tk.DISABLED)
        self.merge_button.grid(row=2, column=0, pady=5)
        
        # Status section
        self.status_var = tk.StringVar(value="Add PDF files to begin")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_drag_and_drop(self):
        """Setup drag and drop functionality if available."""
        if DND_AVAILABLE:
            self.file_tree.drop_target_register(DND_FILES)
            self.file_tree.dnd_bind('<<Drop>>', self.on_drop)
            
    def on_drop(self, event):
        """Handle drag and drop events."""
        files = self.root.tk.splitlist(event.data)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            self.add_files_to_list(pdf_files)
            
    def add_files(self):
        """Open file dialog to add PDF files."""
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if files:
            self.add_files_to_list(files)
            
    def add_files_to_list(self, files: List[str]):
        """Add files to the file list with validation."""
        added_count = 0
        for file_path in files:
            if file_path not in self.file_paths:
                if self.merger.validate_pdf_file(file_path):
                    self.file_paths.append(file_path)
                    info = self.merger.get_pdf_info(file_path)
                    
                    # Add to treeview
                    filename = os.path.basename(file_path)
                    size_mb = info['file_size'] / (1024 * 1024)
                    
                    self.file_tree.insert('', tk.END, text=filename,
                                        values=(info['pages'], f"{size_mb:.1f} MB"))
                    added_count += 1
                else:
                    messagebox.showerror("Invalid File", 
                                       f"Cannot read PDF file:\n{file_path}")
        
        if added_count > 0:
            self.update_status()
            self.update_merge_button_state()
            
    def remove_selected(self):
        """Remove selected files from the list."""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select files to remove.")
            return
            
        # Get indices of selected items
        indices_to_remove = []
        for item in selection:
            index = self.file_tree.index(item)
            indices_to_remove.append(index)
            
        # Remove from file_paths and treeview (in reverse order to maintain indices)
        for index in sorted(indices_to_remove, reverse=True):
            del self.file_paths[index]
            
        for item in selection:
            self.file_tree.delete(item)
            
        self.update_status()
        self.update_merge_button_state()
        
    def clear_all(self):
        """Clear all files from the list."""
        if self.file_paths and messagebox.askyesno("Confirm Clear", 
                                                  "Remove all files from the list?"):
            self.file_paths.clear()
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            self.update_status()
            self.update_merge_button_state()
            
    def move_up(self):
        """Move selected file up in the list."""
        selection = self.file_tree.selection()
        if len(selection) != 1:
            messagebox.showwarning("Selection Error", 
                                 "Please select exactly one file to move.")
            return
            
        item = selection[0]
        index = self.file_tree.index(item)
        
        if index > 0:
            # Swap in file_paths
            self.file_paths[index], self.file_paths[index-1] = \
                self.file_paths[index-1], self.file_paths[index]
            
            # Move in treeview
            self.file_tree.move(item, '', index-1)
            
    def move_down(self):
        """Move selected file down in the list."""
        selection = self.file_tree.selection()
        if len(selection) != 1:
            messagebox.showwarning("Selection Error", 
                                 "Please select exactly one file to move.")
            return
            
        item = selection[0]
        index = self.file_tree.index(item)
        
        if index < len(self.file_paths) - 1:
            # Swap in file_paths
            self.file_paths[index], self.file_paths[index+1] = \
                self.file_paths[index+1], self.file_paths[index]
            
            # Move in treeview
            self.file_tree.move(item, '', index+1)
            
    def browse_output(self):
        """Browse for output file location."""
        filename = filedialog.asksaveasfilename(
            title="Save Merged PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.output_var.set(filename)
            self.update_merge_button_state()
            
    def update_status(self):
        """Update the status bar with file information."""
        if not self.file_paths:
            self.status_var.set("Add PDF files to begin")
        else:
            info = self.merger.get_file_list_info(self.file_paths)
            self.status_var.set(
                f"{info['valid_files']} files, {info['total_pages']} pages, "
                f"{info['total_size']/(1024*1024):.1f} MB total"
            )
            
    def update_merge_button_state(self):
        """Enable/disable merge button based on current state."""
        if self.file_paths and self.output_var.get().strip():
            self.merge_button.config(state=tk.NORMAL)
        else:
            self.merge_button.config(state=tk.DISABLED)
            
    def start_merge(self):
        """Start the PDF merging process in a separate thread."""
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please add PDF files to merge.")
            return
            
        output_path = self.output_var.get().strip()
        if not output_path:
            messagebox.showwarning("No Output", "Please specify an output file.")
            return
            
        # Disable UI during merge
        self.merge_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_var.set("Merging PDFs...")
        
        # Start merge in separate thread
        thread = threading.Thread(target=self.merge_pdfs_thread, 
                                 args=(self.file_paths.copy(), output_path))
        thread.daemon = True
        thread.start()
        
    def merge_pdfs_thread(self, file_paths: List[str], output_path: str):
        """Thread function for PDF merging."""
        def progress_callback(current: int, total: int):
            progress = (current / total) * 100
            self.root.after(0, lambda: self.progress_bar.config(value=progress))
            self.root.after(0, lambda: self.progress_var.set(
                f"Processing file {current}/{total}..."))
            
        success = self.merger.merge_pdfs(file_paths, output_path, progress_callback)
        
        # Update UI on main thread
        self.root.after(0, lambda: self.merge_complete(success, output_path))
        
    def merge_complete(self, success: bool, output_path: str):
        """Handle merge completion."""
        self.merge_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = 100 if success else 0
        
        if success:
            self.progress_var.set("Merge completed successfully!")
            messagebox.showinfo("Success", 
                              f"PDFs merged successfully!\nSaved to: {output_path}")
        else:
            self.progress_var.set("Merge failed!")
            messagebox.showerror("Error", 
                               "Failed to merge PDFs. Check the log file for details.")
            
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main function to run the GUI application."""
    app = PDFMergerGUI()
    app.run()


if __name__ == "__main__":
    main()