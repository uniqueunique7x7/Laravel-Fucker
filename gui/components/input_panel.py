"""
Input Panel Component

Tab-based interface for different scan modes.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable, List, Optional
import os


class InputPanel(ttk.Frame):
    """Panel for input configuration with tabs for different scan modes."""
    
    def __init__(
        self,
        parent,
        theme,
        on_mode_change: Optional[Callable[[str], None]] = None,
        on_file_load: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize the input panel.
        
        Args:
            parent: Parent widget
            theme: GoldenTheme instance
            on_mode_change: Callback when scan mode changes
            on_file_load: Callback when a file is loaded
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.on_mode_change = on_mode_change
        self.on_file_load = on_file_load
        
        # Variables
        self.single_url_var = tk.StringVar()
        self.domain_file_var = tk.StringVar()
        self.aws_regions_var = tk.StringVar()
        self.aws_services_var = tk.StringVar()
        self.infinite_mode_var = tk.BooleanVar(value=True)
        
        self._current_mode = "domain_list"
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Single URL tab
        self._create_single_url_tab()
        
        # Domain List tab
        self._create_domain_list_tab()
        
        # AWS IP Range tab
        self._create_aws_tab()
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _create_single_url_tab(self) -> None:
        """Create the single URL/domain tab."""
        frame = ttk.Frame(self.notebook, style='Secondary.TFrame')
        self.notebook.add(frame, text="Single URL")
        
        # URL input
        input_frame = ttk.Frame(frame, style='Secondary.TFrame')
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(
            input_frame,
            text="Enter URL or Domain:",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 8))
        
        self.single_url_entry = ttk.Entry(
            input_frame,
            textvariable=self.single_url_var,
            font=('Segoe UI', 11)
        )
        self.single_url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Placeholder text
        self.single_url_entry.insert(0, "example.com or https://example.com")
        self.single_url_entry.bind('<FocusIn>', self._clear_placeholder)
        self.single_url_entry.bind('<FocusOut>', self._restore_placeholder)
        
        # Info label
        ttk.Label(
            input_frame,
            text="Enter a single domain or URL to scan for .env files",
            style='TLabel'
        ).pack(anchor=tk.W)
    
    def _create_domain_list_tab(self) -> None:
        """Create the domain list tab."""
        frame = ttk.Frame(self.notebook, style='Secondary.TFrame')
        self.notebook.add(frame, text="Domain List")
        
        input_frame = ttk.Frame(frame, style='Secondary.TFrame')
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # File selection
        ttk.Label(
            input_frame,
            text="Domain List File:",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 8))
        
        file_frame = ttk.Frame(input_frame, style='Secondary.TFrame')
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_entry = ttk.Entry(
            file_frame,
            textvariable=self.domain_file_var,
            font=('Segoe UI', 11)
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            file_frame,
            text="Browse...",
            command=self._browse_file,
            style='TButton'
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Domain count label
        self.domain_count_label = ttk.Label(
            input_frame,
            text="No file loaded",
            style='TLabel'
        )
        self.domain_count_label.pack(anchor=tk.W, pady=(5, 10))
        
        # Info text
        info_text = ttk.Label(
            input_frame,
            text="Select a text file with one domain per line.\n"
                 "Supports large files with millions of domains.",
            style='TLabel'
        )
        info_text.pack(anchor=tk.W)
    
    def _create_aws_tab(self) -> None:
        """Create the AWS IP Range tab."""
        frame = ttk.Frame(self.notebook, style='Secondary.TFrame')
        self.notebook.add(frame, text="AWS IP Ranges")
        
        # Make scrollable
        canvas = tk.Canvas(frame, **self.theme.get_canvas_config())
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Secondary.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # AWS controls
        input_frame = ttk.Frame(scrollable_frame, style='Secondary.TFrame')
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Region selection
        ttk.Label(
            input_frame,
            text="AWS Regions:",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 8))
        
        # Region listbox
        region_frame = ttk.Frame(input_frame, style='Secondary.TFrame')
        region_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.region_listbox = tk.Listbox(
            region_frame,
            selectmode=tk.MULTIPLE,
            height=5,
            **self.theme.get_listbox_config()
        )
        self.region_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        region_scrollbar = ttk.Scrollbar(region_frame, orient=tk.VERTICAL)
        region_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.region_listbox.config(yscrollcommand=region_scrollbar.set)
        region_scrollbar.config(command=self.region_listbox.yview)
        
        # Populate regions
        self._populate_regions()
        
        # Select all regions button
        btn_frame = ttk.Frame(input_frame, style='Secondary.TFrame')
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(
            btn_frame,
            text="Select All Regions",
            command=self._select_all_regions
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Clear Selection",
            command=self._clear_regions
        ).pack(side=tk.LEFT)
        
        # Service selection
        ttk.Label(
            input_frame,
            text="AWS Services:",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 8))
        
        service_frame = ttk.Frame(input_frame, style='Secondary.TFrame')
        service_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.service_listbox = tk.Listbox(
            service_frame,
            selectmode=tk.MULTIPLE,
            height=5,
            **self.theme.get_listbox_config()
        )
        self.service_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        service_scrollbar = ttk.Scrollbar(service_frame, orient=tk.VERTICAL)
        service_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.service_listbox.config(yscrollcommand=service_scrollbar.set)
        service_scrollbar.config(command=self.service_listbox.yview)
        
        # Populate services
        self._populate_services()
        
        # Infinite mode checkbox
        ttk.Checkbutton(
            input_frame,
            text="Infinite Scanning Mode (loop continuously)",
            variable=self.infinite_mode_var,
            style='Gold.TCheckbutton'
        ).pack(anchor=tk.W, pady=(10, 5))
        
        # AWS info
        self.aws_info_label = ttk.Label(
            input_frame,
            text="Select regions and services to scan.\n"
                 "AWS IP ranges will be fetched from Amazon.",
            style='TLabel'
        )
        self.aws_info_label.pack(anchor=tk.W, pady=(10, 0))
    
    def _populate_regions(self) -> None:
        """Populate region listbox with AWS regions."""
        from utils.aws_ip_fetcher import AWSIPFetcher
        
        regions = AWSIPFetcher.REGIONS
        for region in regions:
            self.region_listbox.insert(tk.END, region)
        
        # Select EC2 popular regions by default
        default_regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        for i, region in enumerate(regions):
            if region in default_regions:
                self.region_listbox.selection_set(i)
    
    def _populate_services(self) -> None:
        """Populate service listbox with AWS services."""
        from utils.aws_ip_fetcher import AWSIPFetcher
        
        services = AWSIPFetcher.SERVICES
        for service in services:
            self.service_listbox.insert(tk.END, service)
        
        # Select EC2 by default
        for i, service in enumerate(services):
            if service == 'EC2':
                self.service_listbox.selection_set(i)
    
    def _select_all_regions(self) -> None:
        """Select all regions."""
        self.region_listbox.selection_set(0, tk.END)
    
    def _clear_regions(self) -> None:
        """Clear region selection."""
        self.region_listbox.selection_clear(0, tk.END)
    
    def _browse_file(self) -> None:
        """Open file browser for domain list."""
        filepath = filedialog.askopenfilename(
            title="Select Domain List",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            self.domain_file_var.set(filepath)
            self._update_domain_count(filepath)
            
            if self.on_file_load:
                self.on_file_load(filepath)
    
    def _update_domain_count(self, filepath: str) -> None:
        """Update the domain count label."""
        try:
            count = 0
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip():
                        count += 1
            
            self.domain_count_label.config(
                text=f"✓ Loaded {count:,} domains",
                style='Success.TLabel'
            )
        except Exception as e:
            self.domain_count_label.config(
                text=f"Error loading file: {str(e)}",
                style='Error.TLabel'
            )
    
    def _clear_placeholder(self, event) -> None:
        """Clear placeholder text on focus."""
        if self.single_url_var.get() == "example.com or https://example.com":
            self.single_url_entry.delete(0, tk.END)
    
    def _restore_placeholder(self, event) -> None:
        """Restore placeholder if empty."""
        if not self.single_url_var.get():
            self.single_url_entry.insert(0, "example.com or https://example.com")
    
    def _on_tab_changed(self, event) -> None:
        """Handle tab change."""
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, "text")
        
        mode_map = {
            "Single URL": "single_url",
            "Domain List": "domain_list",
            "AWS IP Ranges": "aws_ranges"
        }
        
        self._current_mode = mode_map.get(tab_text, "domain_list")
        
        if self.on_mode_change:
            self.on_mode_change(self._current_mode)
    
    def get_current_mode(self) -> str:
        """Get current scan mode."""
        return self._current_mode
    
    def get_single_url(self) -> str:
        """Get single URL input."""
        url = self.single_url_var.get()
        if url == "example.com or https://example.com":
            return ""
        return url
    
    def get_domain_file(self) -> str:
        """Get domain file path."""
        return self.domain_file_var.get()
    
    def get_selected_regions(self) -> List[str]:
        """Get selected AWS regions."""
        indices = self.region_listbox.curselection()
        return [self.region_listbox.get(i) for i in indices]
    
    def get_selected_services(self) -> List[str]:
        """Get selected AWS services."""
        indices = self.service_listbox.curselection()
        return [self.service_listbox.get(i) for i in indices]
    
    def get_infinite_mode(self) -> bool:
        """Get infinite mode setting."""
        return self.infinite_mode_var.get()
    
    def set_domain_file(self, filepath: str) -> None:
        """Set domain file path."""
        self.domain_file_var.set(filepath)
        if os.path.exists(filepath):
            self._update_domain_count(filepath)
    
    def update_aws_info(self, info: str) -> None:
        """Update AWS info label."""
        self.aws_info_label.config(text=info)
