"""
Configuration Panel Component

Panel for scanner and application configuration.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, Callable, Dict, Any


class ConfigPanel(ttk.Frame):
    """Panel for configuration settings."""
    
    def __init__(
        self,
        parent,
        theme,
        on_config_change: Optional[Callable[[str, Any], None]] = None,
        **kwargs
    ):
        """
        Initialize the configuration panel.
        
        Args:
            parent: Parent widget
            theme: GoldenTheme instance
            on_config_change: Callback when configuration changes
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.on_config_change = on_config_change
        
        # Configuration variables
        self.thread_count_var = tk.IntVar(value=50)
        self.timeout_var = tk.IntVar(value=5)
        self.delay_var = tk.DoubleVar(value=0.1)
        self.retry_var = tk.IntVar(value=3)
        self.output_dir_var = tk.StringVar(value='./results')
        self.auto_save_var = tk.BooleanVar(value=True)
        self.dark_mode_var = tk.BooleanVar(value=True)
        self.alert_sounds_var = tk.BooleanVar(value=True)
        self.notifications_var = tk.BooleanVar(value=True)
        self.max_ips_var = tk.IntVar(value=256)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Create scrollable frame
        canvas = tk.Canvas(self, **self.theme.get_canvas_config())
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style='Secondary.TFrame')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scanner settings section
        self._create_scanner_section()
        
        # Output settings section
        self._create_output_section()
        
        # AWS settings section
        self._create_aws_section()
        
        # Application settings section
        self._create_app_section()
    
    def _create_scanner_section(self) -> None:
        """Create scanner settings section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Scanner Settings",
            style='TLabelframe'
        )
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        inner = ttk.Frame(frame, style='Secondary.TFrame')
        inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Thread count
        ttk.Label(inner, text="Thread Count:", style='TLabel').grid(
            row=0, column=0, sticky='w', pady=5
        )
        
        thread_frame = ttk.Frame(inner, style='Secondary.TFrame')
        thread_frame.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        self.thread_scale = ttk.Scale(
            thread_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.thread_count_var,
            command=lambda v: self._on_scale_change('max_threads', int(float(v)))
        )
        self.thread_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.thread_label = ttk.Label(
            thread_frame,
            text=str(self.thread_count_var.get()),
            style='Gold.TLabel',
            width=4
        )
        self.thread_label.pack(side=tk.RIGHT, padx=5)
        
        # Timeout
        ttk.Label(inner, text="Timeout (seconds):", style='TLabel').grid(
            row=1, column=0, sticky='w', pady=5
        )
        
        timeout_frame = ttk.Frame(inner, style='Secondary.TFrame')
        timeout_frame.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        self.timeout_scale = ttk.Scale(
            timeout_frame,
            from_=1,
            to=30,
            orient=tk.HORIZONTAL,
            variable=self.timeout_var,
            command=lambda v: self._on_scale_change('timeout', int(float(v)))
        )
        self.timeout_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.timeout_label = ttk.Label(
            timeout_frame,
            text=str(self.timeout_var.get()),
            style='Gold.TLabel',
            width=4
        )
        self.timeout_label.pack(side=tk.RIGHT, padx=5)
        
        # Request delay
        ttk.Label(inner, text="Request Delay (s):", style='TLabel').grid(
            row=2, column=0, sticky='w', pady=5
        )
        
        delay_entry = ttk.Entry(
            inner,
            textvariable=self.delay_var,
            width=10
        )
        delay_entry.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        delay_entry.bind('<FocusOut>', lambda e: self._notify_change('request_delay', self.delay_var.get()))
        
        # Retry attempts
        ttk.Label(inner, text="Retry Attempts:", style='TLabel').grid(
            row=3, column=0, sticky='w', pady=5
        )
        
        retry_spin = ttk.Spinbox(
            inner,
            from_=0,
            to=10,
            textvariable=self.retry_var,
            width=5,
            command=lambda: self._notify_change('retry_attempts', self.retry_var.get())
        )
        retry_spin.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        inner.columnconfigure(1, weight=1)
    
    def _create_output_section(self) -> None:
        """Create output settings section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Output Settings",
            style='TLabelframe'
        )
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        inner = ttk.Frame(frame, style='Secondary.TFrame')
        inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Output directory
        ttk.Label(inner, text="Output Directory:", style='TLabel').grid(
            row=0, column=0, sticky='w', pady=5
        )
        
        dir_frame = ttk.Frame(inner, style='Secondary.TFrame')
        dir_frame.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Entry(
            dir_frame,
            textvariable=self.output_dir_var,
            width=30
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            dir_frame,
            text="Browse",
            command=self._browse_output_dir
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Auto-save
        ttk.Checkbutton(
            inner,
            text="Auto-save results",
            variable=self.auto_save_var,
            command=lambda: self._notify_change('auto_save', self.auto_save_var.get()),
            style='TCheckbutton'
        ).grid(row=1, column=0, columnspan=2, sticky='w', pady=5)
        
        inner.columnconfigure(1, weight=1)
    
    def _create_aws_section(self) -> None:
        """Create AWS settings section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="AWS Settings",
            style='TLabelframe'
        )
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        inner = ttk.Frame(frame, style='Secondary.TFrame')
        inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Max IPs per CIDR
        ttk.Label(inner, text="Max IPs per CIDR:", style='TLabel').grid(
            row=0, column=0, sticky='w', pady=5
        )
        
        max_ips_frame = ttk.Frame(inner, style='Secondary.TFrame')
        max_ips_frame.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        self.max_ips_scale = ttk.Scale(
            max_ips_frame,
            from_=16,
            to=1024,
            orient=tk.HORIZONTAL,
            variable=self.max_ips_var,
            command=lambda v: self._on_scale_change('max_ips_per_cidr', int(float(v)))
        )
        self.max_ips_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.max_ips_label = ttk.Label(
            max_ips_frame,
            text=str(self.max_ips_var.get()),
            style='Gold.TLabel',
            width=5
        )
        self.max_ips_label.pack(side=tk.RIGHT, padx=5)
        
        # Refresh AWS data button
        ttk.Button(
            inner,
            text="Refresh AWS IP Ranges",
            command=self._refresh_aws_data,
            style='Gold.TButton'
        ).grid(row=1, column=0, columnspan=2, pady=10)
        
        inner.columnconfigure(1, weight=1)
    
    def _create_app_section(self) -> None:
        """Create application settings section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Application Settings",
            style='TLabelframe'
        )
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        inner = ttk.Frame(frame, style='Secondary.TFrame')
        inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Dark mode
        ttk.Checkbutton(
            inner,
            text="Dark Mode",
            variable=self.dark_mode_var,
            command=lambda: self._notify_change('dark_mode', self.dark_mode_var.get()),
            style='Gold.TCheckbutton'
        ).pack(anchor=tk.W, pady=2)
        
        # Alert sounds
        ttk.Checkbutton(
            inner,
            text="Alert Sounds",
            variable=self.alert_sounds_var,
            command=lambda: self._notify_change('alert_sounds', self.alert_sounds_var.get()),
            style='TCheckbutton'
        ).pack(anchor=tk.W, pady=2)
        
        # Desktop notifications
        ttk.Checkbutton(
            inner,
            text="Desktop Notifications",
            variable=self.notifications_var,
            command=lambda: self._notify_change('desktop_notifications', self.notifications_var.get()),
            style='TCheckbutton'
        ).pack(anchor=tk.W, pady=2)
        
        # Save/Reset buttons
        btn_frame = ttk.Frame(inner, style='Secondary.TFrame')
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(
            btn_frame,
            text="Save Configuration",
            command=self._save_config,
            style='Gold.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Reset to Defaults",
            command=self._reset_config
        ).pack(side=tk.LEFT)
    
    def _on_scale_change(self, key: str, value: int) -> None:
        """Handle scale widget change."""
        # Update label
        if key == 'max_threads':
            self.thread_label.config(text=str(value))
        elif key == 'timeout':
            self.timeout_label.config(text=str(value))
        elif key == 'max_ips_per_cidr':
            self.max_ips_label.config(text=str(value))
        
        self._notify_change(key, value)
    
    def _notify_change(self, key: str, value: Any) -> None:
        """Notify of configuration change."""
        if self.on_config_change:
            self.on_config_change(key, value)
    
    def _browse_output_dir(self) -> None:
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )
        
        if directory:
            self.output_dir_var.set(directory)
            self._notify_change('output_directory', directory)
    
    def _refresh_aws_data(self) -> None:
        """Refresh AWS IP ranges data."""
        self._notify_change('refresh_aws', True)
    
    def _save_config(self) -> None:
        """Save current configuration."""
        self._notify_change('save_config', True)
    
    def _reset_config(self) -> None:
        """Reset configuration to defaults."""
        self.thread_count_var.set(50)
        self.timeout_var.set(5)
        self.delay_var.set(0.1)
        self.retry_var.set(3)
        self.output_dir_var.set('./results')
        self.auto_save_var.set(True)
        self.dark_mode_var.set(True)
        self.alert_sounds_var.set(True)
        self.notifications_var.set(True)
        self.max_ips_var.set(256)
        
        # Update labels
        self.thread_label.config(text='50')
        self.timeout_label.config(text='5')
        self.max_ips_label.config(text='256')
        
        self._notify_change('reset_config', True)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            'max_threads': self.thread_count_var.get(),
            'timeout': self.timeout_var.get(),
            'request_delay': self.delay_var.get(),
            'retry_attempts': self.retry_var.get(),
            'output_directory': self.output_dir_var.get(),
            'auto_save': self.auto_save_var.get(),
            'dark_mode': self.dark_mode_var.get(),
            'alert_sounds': self.alert_sounds_var.get(),
            'desktop_notifications': self.notifications_var.get(),
            'max_ips_per_cidr': self.max_ips_var.get()
        }
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set configuration from dictionary."""
        if 'max_threads' in config:
            self.thread_count_var.set(config['max_threads'])
            self.thread_label.config(text=str(config['max_threads']))
        
        if 'timeout' in config:
            self.timeout_var.set(config['timeout'])
            self.timeout_label.config(text=str(config['timeout']))
        
        if 'request_delay' in config:
            self.delay_var.set(config['request_delay'])
        
        if 'retry_attempts' in config:
            self.retry_var.set(config['retry_attempts'])
        
        if 'output_directory' in config:
            self.output_dir_var.set(config['output_directory'])
        
        if 'auto_save' in config:
            self.auto_save_var.set(config['auto_save'])
        
        if 'dark_mode' in config:
            self.dark_mode_var.set(config['dark_mode'])
        
        if 'alert_sounds' in config:
            self.alert_sounds_var.set(config['alert_sounds'])
        
        if 'desktop_notifications' in config:
            self.notifications_var.set(config['desktop_notifications'])
        
        if 'max_ips_per_cidr' in config:
            self.max_ips_var.set(config['max_ips_per_cidr'])
            self.max_ips_label.config(text=str(config['max_ips_per_cidr']))
