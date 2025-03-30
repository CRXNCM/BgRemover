import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import rembg
from pathlib import Path
import customtkinter as ctk
import warnings
import io

# Suppress specific warnings
warnings.filterwarnings(
    "ignore", 
    message="Thresholded incomplete Cholesky decomposition failed.*",
    category=UserWarning
)

# Add filter for model loading messages
warnings.filterwarnings("ignore", category=UserWarning)

# Optionally redirect stdout during model loading to suppress other messages
import sys
import os

class BgRemoverUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        
        # Set theme and appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # App variables
        self.selected_files = []
        self.current_preview_index = 0
        self.preview_original = None
        self.preview_processed = None
        self.processing_thread = None
        self.session = None
        self.photo_references = []
        self.zoom_level = 1.0
        self.original_image = None
        self.processed_image = None
        
        # Model settings
        self.model_var = ctk.StringVar(value="u2net")
        self.alpha_matting_var = ctk.BooleanVar(value=False)
        self.output_dir_var = ctk.StringVar()
        self.progress_var = ctk.DoubleVar(value=0)
        self.status_var = ctk.StringVar(value="Ready")
        
        # Create UI
        self.create_ui()
        
        # Initialize model
        self.initialize_model()
    
    def create_ui(self):
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # ===== Top Frame =====
        top_frame = ctk.CTkFrame(self.root, corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        top_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(top_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            header, 
            text="BACKGROUND REMOVER", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#6c9bcf"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # File selection
        file_frame = ctk.CTkFrame(top_frame)
        file_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        file_frame.grid_columnconfigure(1, weight=1)
        
        select_btn = ctk.CTkButton(
            file_frame, 
            text="Select Images",
            command=self.select_files,
            font=ctk.CTkFont(size=13),
            height=38,
            corner_radius=8,
            fg_color="#6c9bcf",
            hover_color="#4a7ab8"
        )
        select_btn.grid(row=0, column=0, padx=(0, 10), pady=10)
        
        self.file_label = ctk.CTkLabel(
            file_frame, 
            text="No files selected",
            font=ctk.CTkFont(size=13),
            fg_color=("#343638", "#242424"),
            corner_radius=8,
            height=38,
            padx=10
        )
        self.file_label.grid(row=0, column=1, sticky="ew", pady=10)
        
        # ===== Main Content Frame =====
        content_frame = ctk.CTkFrame(self.root)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=4)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # ===== Preview Panel =====
        preview_frame = ctk.CTkFrame(content_frame)
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Preview controls
        preview_controls = ctk.CTkFrame(preview_frame, fg_color="transparent")
        preview_controls.grid(row=0, column=0, sticky="ew", padx=0, pady=(10, 5))
        preview_controls.grid_columnconfigure(1, weight=1)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(preview_controls, fg_color="transparent")
        nav_frame.grid(row=0, column=0, sticky="w")
        
        self.prev_btn = ctk.CTkButton(
            nav_frame, 
            text="◀",
            command=self.prev_preview,
            width=40,
            height=30,
            corner_radius=8,
            fg_color="#555555",
            hover_color="#444444",
            state="disabled"
        )
        self.prev_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.preview_label = ctk.CTkLabel(
            nav_frame, 
            text="No image to preview",
            width=200
        )
        self.preview_label.grid(row=0, column=1, padx=5)
        
        self.next_btn = ctk.CTkButton(
            nav_frame, 
            text="▶",
            command=self.next_preview,
            width=40,
            height=30,
            corner_radius=8,
            fg_color="#555555",
            hover_color="#444444",
            state="disabled"
        )
        self.next_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Zoom controls
        zoom_frame = ctk.CTkFrame(preview_controls, fg_color="transparent")
        zoom_frame.grid(row=0, column=1, sticky="e")
        
        self.zoom_out_btn = ctk.CTkButton(
            zoom_frame, 
            text="−",
            command=self.zoom_out,
            width=30,
            height=30,
            corner_radius=8,
            fg_color="#555555",
            hover_color="#444444"
        )
        self.zoom_out_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.zoom_reset_btn = ctk.CTkButton(
            zoom_frame, 
            text="100%",
            command=self.zoom_reset,
            width=60,
            height=30,
            corner_radius=8,
            fg_color="#555555",
            hover_color="#444444"
        )
        self.zoom_reset_btn.grid(row=0, column=1, padx=5)
        
        self.zoom_in_btn = ctk.CTkButton(
            zoom_frame, 
            text="+",
            command=self.zoom_in,
            width=30,
            height=30,
            corner_radius=8,
            fg_color="#555555",
            hover_color="#444444"
        )
        self.zoom_in_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Preview container
        self.preview_container = ctk.CTkFrame(preview_frame, fg_color="#1a1a1a")
        self.preview_container.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(2, weight=1)
        self.preview_container.grid_rowconfigure(0, weight=1)
        
        # Original preview
        self.original_preview_frame = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        self.original_preview_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        self.original_preview = ctk.CTkLabel(
            self.original_preview_frame, 
            text="Original Image",
            fg_color="#242424",
            corner_radius=8
        )
        self.original_preview.pack(fill=tk.BOTH, expand=True)
        
        # Separator
        separator = ctk.CTkFrame(self.preview_container, width=2, fg_color="#333333")
        separator.grid(row=0, column=1, sticky="ns", pady=20)
        
        # Processed preview
        self.processed_preview_frame = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        self.processed_preview_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        
        self.processed_preview = ctk.CTkLabel(
            self.processed_preview_frame, 
            text="Processed Image",
            fg_color="#242424",
            corner_radius=8
        )
        self.processed_preview.pack(fill=tk.BOTH, expand=True)
        
        # ===== Settings Panel =====
        settings_frame = ctk.CTkFrame(content_frame)
        settings_frame.grid(row=0, column=1, sticky="nsew")
        settings_frame.grid_rowconfigure(4, weight=1)
        
        # Settings header
        settings_label = ctk.CTkLabel(
            settings_frame, 
            text="SETTINGS",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        settings_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        
        # Settings content
        settings_content = ctk.CTkFrame(settings_frame, fg_color="transparent")
        settings_content.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Model selection
        model_label = ctk.CTkLabel(settings_content, text="Model:", anchor="w")
        model_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        model_combo = ctk.CTkOptionMenu(
            settings_content,
            values=["u2net", "u2netp", "u2net_human_seg", "silueta"],
            variable=self.model_var,
            command=self.on_model_change,
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555",
            dropdown_fg_color="#333333",
            dropdown_hover_color="#444444",
            width=200
        )
        model_combo.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Alpha matting
        alpha_check = ctk.CTkCheckBox(
            settings_content,
            text="Alpha Matting (better edges)",
            variable=self.alpha_matting_var,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=4,
            border_width=2
        )
        alpha_check.grid(row=2, column=0, sticky="w", pady=(0, 15))
        
        # Output directory
        output_label = ctk.CTkLabel(settings_content, text="Output Directory:", anchor="w")
        output_label.grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        output_frame = ctk.CTkFrame(settings_content, fg_color="transparent")
        output_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_dir_var,
            height=32,
            fg_color="#333333",
            border_color="#555555"
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        output_btn = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self.select_output_dir,
            width=70,
            height=32,
            corner_radius=8,
            fg_color="#555555",
            hover_color="#444444"
        )
        output_btn.grid(row=0, column=1)
        
        # Action buttons
        action_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        action_frame.grid_columnconfigure(0, weight=1)
        
        self.process_preview_btn = ctk.CTkButton(
            action_frame,
            text="Process Preview",
            command=self.process_preview,
            state="disabled",
            height=38,
            corner_radius=8,
            fg_color="#6c9bcf",
            hover_color="#4a7ab8"
        )
        self.process_preview_btn.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.download_btn = ctk.CTkButton(
            action_frame,
            text="Download Processed Image",
            command=self.download_processed_image,
            state="disabled",
            height=38,
            corner_radius=8,
            fg_color="#555555",
            hover_color="#444444"
        )
        self.download_btn.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.process_btn = ctk.CTkButton(
            action_frame,
            text="Process All Images",
            command=self.process_images,
            state="disabled",
            height=38,
            corner_radius=8,
            fg_color="#6c9bcf",
            hover_color="#4a7ab8"
        )
        self.process_btn.grid(row=2, column=0, sticky="ew")
        
        # Progress section
        progress_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        progress_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        progress_frame.grid_columnconfigure(0, weight=1)
        
        progress_label = ctk.CTkLabel(progress_frame, text="Progress:", anchor="w")
        progress_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.progress = ctk.CTkProgressBar(
            progress_frame,
            variable=self.progress_var,
            mode="determinate",
            height=15,
            corner_radius=5,
            fg_color="#333333",
            progress_color="#6c9bcf"
        )
        self.progress.grid(row=1, column=0, sticky="ew")
        
        # Status bar
        status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0, fg_color="#1a1a1a")
        status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        status_frame.grid_columnconfigure(0, weight=1)
        
        status_label = ctk.CTkLabel(
            status_frame, 
            textvariable=self.status_var,
            anchor="w",
            padx=10
        )
        status_label.grid(row=0, column=0, sticky="ew")
    
    def initialize_model(self):
        """Initialize the background removal model in a separate thread"""
        self.status_var.set("Loading model...")
        
        def load_model():
            try:
                self.session = rembg.new_session(model_name=self.model_var.get())
                self.root.after(0, lambda: self.status_var.set("Ready - Model loaded"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error loading model: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load model: {str(e)}"))
        
        threading.Thread(target=load_model, daemon=True).start()
    
    def on_model_change(self, choice):
        """Handle model change"""
        self.initialize_model()
        # Reset preview if exists
        if self.preview_processed is not None:
            self.preview_processed = None
            self.update_preview()
    
    def select_files(self):
        """Open file dialog to select images"""
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            self.file_label.configure(text=f"{len(self.selected_files)} files selected")
            self.current_preview_index = 0
            self.preview_original = None
            self.preview_processed = None
            self.download_btn.configure(state="disabled")
            self.update_preview()
            self.update_navigation_buttons()
            self.process_btn.configure(state="normal")
    
    def select_output_dir(self):
        """Open directory dialog to select output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        if not self.selected_files:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            self.process_preview_btn.configure(state="disabled")
            return
        
        self.process_preview_btn.configure(state="normal")
        
        if len(self.selected_files) <= 1:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        else:
            self.prev_btn.configure(state="normal" if self.current_preview_index > 0 else "disabled")
            self.next_btn.configure(state="normal" if self.current_preview_index < len(self.selected_files) - 1 else "disabled")
    
    def prev_preview(self):
        """Show previous image in preview"""
        if self.current_preview_index > 0:
            self.current_preview_index -= 1
            self.preview_original = None
            self.preview_processed = None
            self.photo_references = []
            self.download_btn.configure(state="disabled")
            self.update_preview()
            self.update_navigation_buttons()
    
    def next_preview(self):
        """Show next image in preview"""
        if self.current_preview_index < len(self.selected_files) - 1:
            self.current_preview_index += 1
            self.preview_original = None
            self.preview_processed = None
            self.photo_references = []
            self.download_btn.configure(state="disabled")
            self.update_preview()
            self.update_navigation_buttons()
    
    def update_preview(self):
        """Update the preview images"""
        # Clear previous image references
        self.photo_references = []
        
        if not self.selected_files:
            self.original_preview.configure(image=None, text="No image selected")
            self.processed_preview.configure(image=None, text="No image processed")
            self.preview_label.configure(text="No image to preview")
            return
        
        current_file = self.selected_files[self.current_preview_index]
        filename = os.path.basename(current_file)
        self.preview_label.configure(text=f"Image {self.current_preview_index + 1}/{len(self.selected_files)}")
        
        # Load and display original image if not already loaded
        if self.preview_original is None:
            try:
                img = Image.open(current_file)
                self.original_image = img
                self.preview_original = self.resize_image_for_preview(img)
                self.photo_references.append(self.preview_original)
                self.original_preview.configure(image=self.preview_original, text="")
                
                # Show image info in status bar
                self.update_image_info(current_file, img)
            except Exception as e:
                self.original_preview.configure(image=None, text=f"Error loading image: {str(e)}")
        else:
            self.photo_references.append(self.preview_original)
            self.original_preview.configure(image=self.preview_original, text="")
        
        # Display processed image if available
        if self.preview_processed is not None:
            self.photo_references.append(self.preview_processed)
            self.processed_preview.configure(image=self.preview_processed, text="")
        else:
            self.processed_preview.configure(image=None, text="Click 'Process Preview'")
    
    def update_image_info(self, file_path, img):
        """Update status bar with image information"""
        # Get file size in KB or MB
        file_size_bytes = os.path.getsize(file_path)
        if file_size_bytes > 1024 * 1024:
            file_size = f"{file_size_bytes / (1024 * 1024):.2f} MB"
        else:
            file_size = f"{file_size_bytes / 1024:.2f} KB"
        
        # Get image dimensions
        width, height = img.size
        
        # Get image format
        img_format = img.format if img.format else "Unknown"
        
        # Get color mode
        color_mode = img.mode
        
        # Update status bar
        self.status_var.set(f"Image: {os.path.basename(file_path)} | Size: {file_size} | Dimensions: {width}×{height} | Format: {img_format} | Mode: {color_mode}")
    
    def resize_image_for_preview(self, img, use_zoom=False):
        """Resize image to fit in preview area while maintaining aspect ratio"""
        # Get preview container size
        width = self.preview_container.winfo_width() // 2 - 30
        height = self.preview_container.winfo_height() - 20
        
        # Ensure minimum size for initial load
        if width < 100:
            width = 400
        if height < 100:
            height = 300
        
        # Calculate new dimensions while preserving aspect ratio
        img_width, img_height = img.size
        ratio = min(width / img_width, height / img_height)
        
        # Apply zoom if requested
        if use_zoom:
            ratio *= self.zoom_level
        
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Resize and convert to CTkImage instead of PhotoImage
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Use CTkImage instead of ImageTk.PhotoImage
        photo_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, 
                                 size=(new_width, new_height))
        
        return photo_img
    
    def process_preview(self):
        """Process the current preview image"""
        if not self.selected_files or self.session is None:
            return
        
        self.status_var.set("Processing preview...")
        self.process_preview_btn.configure(state="disabled")
        self.download_btn.configure(state="disabled")
        
        def process():
            try:
                current_file = self.selected_files[self.current_preview_index]
                img = Image.open(current_file)
                
                # Process image
                result = rembg.remove(
                    img,
                    session=self.session,
                    alpha_matting=self.alpha_matting_var.get()
                )
                
                # Update UI in the main thread
                self.root.after(0, lambda: self.update_processed_preview(result))
                self.root.after(0, lambda: self.status_var.set("Preview processed"))
                self.root.after(0, lambda: self.process_preview_btn.configure(state="normal"))
                self.root.after(0, lambda: self.download_btn.configure(state="normal"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: self.process_preview_btn.configure(state="normal"))
                self.root.after(0, lambda: self.download_btn.configure(state="disabled"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process image: {str(e)}"))
        
        threading.Thread(target=process, daemon=True).start()
    
    def update_processed_preview(self, img):
        """Update the processed image preview"""
        self.processed_image = img
        # Create the resized image and store it
        self.preview_processed = self.resize_image_for_preview(img)
        # Make sure to add to photo_references before configuring the label
        self.photo_references.append(self.preview_processed)
        
        # Now configure the label with the image - use a direct reference to avoid garbage collection
        photo_ref = self.preview_processed
        self.processed_preview.configure(image=photo_ref, text="")
        
        # Store an additional reference to prevent garbage collection
        self.processed_preview.image = photo_ref
        
        # Update status with processed image info
        width, height = img.size
        self.status_var.set(f"Processed image | Dimensions: {width}×{height} | Mode: {img.mode} | Background removed successfully")
        
        # Force update to ensure the image is displayed
        self.root.update_idletasks()
        self.processed_preview.configure(image=self.preview_processed, text="")
    
    def process_images(self):
        """Process all selected images"""
        if not self.selected_files or self.session is None:
            return
        
        output_dir = self.output_dir_var.get()
        if not output_dir:
            # Use the directory of the first image if no output directory specified
            output_dir = os.path.dirname(self.selected_files[0])
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Disable UI elements during processing
        self.process_btn.configure(state="disabled")
        self.process_preview_btn.configure(state="disabled")
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")
        
        self.progress_var.set(0)
        self.status_var.set("Processing images...")
        
        # Cancel existing thread if running
        if self.processing_thread and self.processing_thread.is_alive():
            # We can't actually cancel the thread, but we can set a flag
            self.status_var.set("Waiting for current process to finish...")
            return
        
        def process_all():
            try:
                total = len(self.selected_files)
                for i, file_path in enumerate(self.selected_files):
                    if not os.path.exists(file_path):
                        continue
                    
                    # Update progress
                    progress_pct = (i / total) * 100
                    self.root.after(0, lambda p=progress_pct: self.progress_var.set(p))
                    self.root.after(0, lambda f=os.path.basename(file_path): 
                                self.status_var.set(f"Processing {f} ({i+1}/{total})"))
                    
                    try:
                        # Open image
                        img = Image.open(file_path)
                        
                        # Process image
                        result = rembg.remove(
                            img,
                            session=self.session,
                            alpha_matting=self.alpha_matting_var.get()
                        )
                        
                        # Generate output filename - always use PNG extension
                        file_name = os.path.basename(file_path)
                        file_base = os.path.splitext(file_name)[0]
                        output_path = os.path.join(output_dir, f"{file_base}_nobg.png")
                        
                        # Save result
                        result.save(output_path)
                        
                    except Exception as e:
                        self.root.after(0, lambda err=str(e), f=file_name: 
                                    messagebox.showwarning("Processing Error", 
                                                            f"Error processing {f}: {err}"))
                
                # Update UI when complete
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: self.status_var.set(f"Completed processing {total} images"))
                self.root.after(0, lambda: messagebox.showinfo("Processing Complete", 
                                                            f"Successfully processed {total} images"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Error", 
                                                            f"An error occurred during processing: {str(e)}"))
            finally:
                # Re-enable UI elements
                self.root.after(0, lambda: self.process_btn.configure(state="normal"))
                self.root.after(0, lambda: self.process_preview_btn.configure(state="normal"))
                self.root.after(0, lambda: self.update_navigation_buttons())
        
        # Start processing in a separate thread
        self.processing_thread = threading.Thread(target=process_all, daemon=True)
        self.processing_thread.start()
    
    def download_processed_image(self):
        """Save the processed image with original name + BgRemoved suffix"""
        if not self.selected_files or self.processed_image is None:
            messagebox.showinfo("Info", "No processed image to download")
            return
        
        try:
            current_file = self.selected_files[self.current_preview_index]
            file_path = Path(current_file)
            
            # Get original filename without extension
            original_name = file_path.stem
            
            # Default save location and filename (always use PNG)
            default_dir = self.output_dir_var.get() if self.output_dir_var.get() else file_path.parent
            default_filename = f"{original_name}_BgRemoved.png"
            
            # Open save file dialog
            save_path = filedialog.asksaveasfilename(
                initialdir=default_dir,
                initialfile=default_filename,
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("All files", "*.*")
                ],
                title="Save Processed Image"
            )
            
            if not save_path:
                self.status_var.set("Save operation cancelled")
                return  # User cancelled
            
            # Ensure the file has .png extension
            if not save_path.lower().endswith('.png'):
                save_path += '.png'
            
            # Save the processed image (using the already processed image in memory)
            self.processed_image.save(save_path)
            
            # Update status and notify user
            self.status_var.set(f"Image saved to {save_path}")
            messagebox.showinfo("Success", f"Image saved successfully to:\n{save_path}")
            
            # Try to open the containing folder
            try:
                os.startfile(os.path.dirname(save_path))
            except:
                # Silently fail if we can't open the folder
                pass
                
        except Exception as e:
            self.status_var.set(f"Error saving image: {str(e)}")
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def zoom_in(self):
        """Increase zoom level and update preview"""
        self.zoom_level = min(3.0, self.zoom_level + 0.1)
        self.update_zoomed_preview()
    
    def zoom_out(self):
        """Decrease zoom level and update preview"""
        self.zoom_level = max(0.1, self.zoom_level - 0.1)
        self.update_zoomed_preview()
    
    def zoom_reset(self):
        """Reset zoom level to 100%"""
        self.zoom_level = 1.0
        self.update_zoomed_preview()
    
    def update_zoomed_preview(self):
        """Update preview images with current zoom level"""
        # Update zoom button text
        self.zoom_reset_btn.configure(text=f"{int(self.zoom_level * 100)}%")
        
        # Update previews if images are loaded
        if self.original_image is not None:
            self.preview_original = self.resize_image_for_preview(self.original_image, use_zoom=True)
            self.photo_references.append(self.preview_original)
            self.original_preview.configure(image=self.preview_original)
            
        if self.processed_image is not None:
            self.preview_processed = self.resize_image_for_preview(self.processed_image, use_zoom=True)
            self.photo_references.append(self.preview_processed)
            self.processed_preview.configure(image=self.preview_processed)

# Main entry point
if __name__ == "__main__":
    root = ctk.CTk()
    app = BgRemoverUI(root)
    root.mainloop()
