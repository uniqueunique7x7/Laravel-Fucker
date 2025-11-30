"""
Log Console Component

Collapsible log panel with color-coded log levels.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, List
from datetime import datetime


class LogConsole(ttk.Frame):
    """Collapsible log console with color-coded levels."""
    
    def __init__(
        self,
        parent,
        theme,
        initial_height: int = 150,
        **kwargs
    ):
        """
        Initialize the log console.
        
        Args:
            parent: Parent widget
            theme: GoldenTheme instance
            initial_height: Initial height of the console
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        self._initial_height = initial_height
        self._is_collapsed = False
        self._auto_scroll = True
        self._log_entries: List[dict] = []
        self._filter_text = ""
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Header bar
        header = ttk.Frame(self, style='Secondary.TFrame')
        header.pack(fill=tk.X)
        
        # Toggle button
        self.toggle_btn = ttk.Button(
            header,
            text="▼ Console",
            command=self._toggle_console,
            style='TButton'
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Filter entry
        ttk.Label(header, text="Filter:", style='TLabel').pack(side=tk.LEFT, padx=(10, 5))
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._apply_filter)
        
        self.filter_entry = ttk.Entry(
            header,
            textvariable=self.filter_var,
            width=20
        )
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        btn_frame = ttk.Frame(header, style='Secondary.TFrame')
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Clear",
            command=self.clear_logs
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Save",
            command=self._save_logs
        ).pack(side=tk.LEFT, padx=2)
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            btn_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            command=self._toggle_auto_scroll,
            style='TCheckbutton'
        ).pack(side=tk.LEFT, padx=5)
        
        # Log level filters
        level_frame = ttk.Frame(header, style='Secondary.TFrame')
        level_frame.pack(side=tk.RIGHT, padx=10)
        
        self.level_vars = {}
        for level in ['DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR']:
            var = tk.BooleanVar(value=True)
            self.level_vars[level] = var
            ttk.Checkbutton(
                level_frame,
                text=level[:1],
                variable=var,
                command=self._apply_filter,
                style='TCheckbutton'
            ).pack(side=tk.LEFT)
        
        # Content frame
        self.content_frame = ttk.Frame(self, style='Secondary.TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget for logs
        self.log_text = tk.Text(
            self.content_frame,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED,
            **self.theme.get_text_widget_config()
        )
        
        vsb = ttk.Scrollbar(self.content_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=vsb.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags for log levels
        self._configure_tags()
    
    def _configure_tags(self) -> None:
        """Configure text tags for log levels."""
        self.log_text.tag_configure('DEBUG', foreground='#888888')
        self.log_text.tag_configure('INFO', foreground='#2196F3')
        self.log_text.tag_configure('SUCCESS', foreground='#4CAF50')
        self.log_text.tag_configure('WARNING', foreground='#FFA500')
        self.log_text.tag_configure('ERROR', foreground='#f44336')
        self.log_text.tag_configure('CRITICAL', foreground='#ff0000', font=('Consolas', 10, 'bold'))
        self.log_text.tag_configure('timestamp', foreground='#666666')
    
    def _toggle_console(self) -> None:
        """Toggle console visibility."""
        if self._is_collapsed:
            self.content_frame.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.configure(text="▼ Console")
            self._is_collapsed = False
        else:
            self.content_frame.pack_forget()
            self.toggle_btn.configure(text="▶ Console")
            self._is_collapsed = True
    
    def _toggle_auto_scroll(self) -> None:
        """Toggle auto-scroll."""
        self._auto_scroll = self.auto_scroll_var.get()
    
    def _apply_filter(self, *args) -> None:
        """Apply filter to log entries."""
        self._filter_text = self.filter_var.get().lower()
        self._refresh_display()
    
    def _refresh_display(self) -> None:
        """Refresh the log display with filters applied."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        
        for entry in self._log_entries:
            if self._should_display(entry):
                self._insert_entry(entry)
        
        self.log_text.configure(state=tk.DISABLED)
        
        if self._auto_scroll:
            self.log_text.see(tk.END)
    
    def _should_display(self, entry: dict) -> bool:
        """Check if entry should be displayed based on filters."""
        # Check level filter
        level = entry.get('level_name', 'INFO')
        if level in self.level_vars and not self.level_vars[level].get():
            return False
        
        # Check text filter
        if self._filter_text:
            message = entry.get('message', '').lower()
            if self._filter_text not in message:
                return False
        
        return True
    
    def _insert_entry(self, entry: dict) -> None:
        """Insert a log entry into the text widget."""
        timestamp = entry.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            time_str = timestamp
        else:
            time_str = timestamp.strftime('%H:%M:%S')
        
        level = entry.get('level_name', 'INFO')
        message = entry.get('message', '')
        
        self.log_text.insert(tk.END, f"[{time_str}] ", 'timestamp')
        self.log_text.insert(tk.END, f"[{level}] ", level)
        self.log_text.insert(tk.END, f"{message}\n")
    
    def log(self, level: str, message: str, timestamp: Optional[datetime] = None) -> None:
        """
        Add a log entry.
        
        Args:
            level: Log level (DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
            message: Log message
            timestamp: Optional timestamp
        """
        entry = {
            'level_name': level.upper(),
            'message': message,
            'timestamp': timestamp or datetime.now()
        }
        
        self._log_entries.append(entry)
        
        # Limit entries to prevent memory issues
        if len(self._log_entries) > 10000:
            self._log_entries = self._log_entries[-5000:]
            self._refresh_display()
            return
        
        # Add to display if should be shown
        if self._should_display(entry):
            self.log_text.configure(state=tk.NORMAL)
            self._insert_entry(entry)
            self.log_text.configure(state=tk.DISABLED)
            
            if self._auto_scroll:
                self.log_text.see(tk.END)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.log('DEBUG', message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.log('INFO', message)
    
    def success(self, message: str) -> None:
        """Log success message."""
        self.log('SUCCESS', message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.log('WARNING', message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.log('ERROR', message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.log('CRITICAL', message)
    
    def clear_logs(self) -> None:
        """Clear all logs."""
        self._log_entries.clear()
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def _save_logs(self) -> None:
        """Save logs to file."""
        filepath = filedialog.asksaveasfilename(
            title="Save Logs",
            defaultextension=".log",
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for entry in self._log_entries:
                        timestamp = entry.get('timestamp', datetime.now())
                        if isinstance(timestamp, datetime):
                            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            time_str = str(timestamp)
                        
                        level = entry.get('level_name', 'INFO')
                        message = entry.get('message', '')
                        
                        f.write(f"[{time_str}] [{level}] {message}\n")
            except Exception as e:
                self.error(f"Failed to save logs: {e}")
    
    def collapse(self) -> None:
        """Collapse the console."""
        if not self._is_collapsed:
            self._toggle_console()
    
    def expand(self) -> None:
        """Expand the console."""
        if self._is_collapsed:
            self._toggle_console()
    
    def get_logs(self) -> List[dict]:
        """Get all log entries."""
        return self._log_entries.copy()
