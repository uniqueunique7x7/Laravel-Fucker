"""
Main Window

The main application window with all GUI components.
"""

import os
import sys
import json
import threading
import queue
from datetime import datetime
from typing import Optional, List, Dict, Any

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Import components
from gui.themes.golden_theme import GoldenTheme, get_theme
from gui.components.input_panel import InputPanel
from gui.components.stats_dashboard import StatsDashboard
from gui.components.results_panel import ResultsPanel
from gui.components.log_console import LogConsole
from gui.components.config_panel import ConfigPanel

# Import scanner modules
from scanner.scanner_core import ScannerCore, ScanResult, ScanStats, ScannerState
from scanner.domain_scanner import DomainScanner
from scanner.aws_scanner import AWSScanner

# Import utilities
from utils.config_manager import ConfigManager, get_config
from utils.logger import get_logger


class MainWindow:
    """Main application window."""
    
    VERSION = "2.0.0"
    APP_NAME = "Laravel-Fucker"
    
    def __init__(self):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title(f"{self.APP_NAME} v{self.VERSION}")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Theme
        self.theme = get_theme(dark_mode=True)
        
        # Configuration
        self.config = get_config()
        
        # Logger
        self.logger = get_logger()
        
        # Scanners
        self.domain_scanner: Optional[DomainScanner] = None
        self.aws_scanner: Optional[AWSScanner] = None
        self.current_scanner: Optional[ScannerCore] = None
        
        # Scan thread
        self.scan_thread: Optional[threading.Thread] = None
        
        # Update queue for thread-safe GUI updates
        self.update_queue: queue.Queue = queue.Queue()
        
        # State
        self._current_mode = "domain_list"
        self._is_scanning = False
        self._is_paused = False
        
        # Setup
        self._setup_theme()
        self._setup_ui()
        self._setup_menu()
        self._setup_bindings()
        self._load_config()
        
        # Start update loop
        self._process_updates()
        
        # Log startup
        self.log_console.info(f"Application started - v{self.VERSION}")
    
    def _setup_theme(self) -> None:
        """Setup the theme and styles."""
        self.style = ttk.Style()
        
        # Use clam theme as base
        self.style.theme_use('clam')
        
        # Apply golden theme
        self.theme.apply_to_style(self.style)
        
        # Configure root
        self.root.configure(bg=self.theme.colors.bg_primary)
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header()
        
        # Content area with paned window
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel (Input + Config)
        left_frame = ttk.Frame(self.paned_window, style='TFrame')
        self.paned_window.add(left_frame, weight=1)
        
        # Create notebook for left panel
        self.left_notebook = ttk.Notebook(left_frame)
        self.left_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Input panel tab
        self.input_panel = InputPanel(
            self.left_notebook,
            self.theme,
            on_mode_change=self._on_mode_change,
            on_file_load=self._on_file_load
        )
        self.left_notebook.add(self.input_panel, text="📋 Input")
        
        # Config panel tab
        self.config_panel = ConfigPanel(
            self.left_notebook,
            self.theme,
            on_config_change=self._on_config_change
        )
        self.left_notebook.add(self.config_panel, text="⚙️ Settings")
        
        # Right panel (Stats + Results)
        right_frame = ttk.Frame(self.paned_window, style='TFrame')
        self.paned_window.add(right_frame, weight=2)
        
        # Stats dashboard
        self.stats_dashboard = StatsDashboard(right_frame, self.theme)
        self.stats_dashboard.pack(fill=tk.X, pady=(0, 10))
        
        # Results panel
        self.results_panel = ResultsPanel(
            right_frame,
            self.theme,
            on_export=self._export_results
        )
        self.results_panel.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        self._create_control_buttons()
        
        # Log console at bottom
        self.log_console = LogConsole(self.main_frame, self.theme)
        self.log_console.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self) -> None:
        """Create the header section."""
        header_frame = ttk.Frame(self.main_frame, style='Secondary.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(header_frame, style='Secondary.TFrame')
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(
            title_frame,
            text="🔥 Laravel-Fucker",
            style='Title.TLabel'
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            title_frame,
            text=f"v{self.VERSION}",
            style='Subtitle.TLabel'
        ).pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        # Status and clock
        status_frame = ttk.Frame(header_frame, style='Secondary.TFrame')
        status_frame.pack(side=tk.RIGHT)
        
        # Status indicator
        self.status_label = ttk.Label(
            status_frame,
            text="● Idle",
            style='Gold.TLabel'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Clock
        self.clock_label = ttk.Label(
            status_frame,
            text="",
            style='TLabel'
        )
        self.clock_label.pack(side=tk.RIGHT)
        self._update_clock()
    
    def _create_control_buttons(self) -> None:
        """Create control buttons section."""
        btn_frame = ttk.Frame(self.main_frame, style='TFrame')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start button
        self.start_btn = ttk.Button(
            btn_frame,
            text="▶ Start Scan",
            command=self._start_scan,
            style='Gold.TButton'
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Pause button
        self.pause_btn = ttk.Button(
            btn_frame,
            text="⏸ Pause",
            command=self._toggle_pause,
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(
            btn_frame,
            text="⏹ Stop",
            command=self._stop_scan,
            style='Danger.TButton',
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(
            btn_frame,
            text="🗑 Clear Results",
            command=self._clear_results
        ).pack(side=tk.LEFT)
    
    def _create_status_bar(self) -> None:
        """Create status bar at bottom."""
        status_bar = ttk.Frame(self.main_frame, style='Secondary.TFrame')
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = ttk.Label(
            status_bar,
            text="Ready",
            style='TLabel'
        )
        self.status_text.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Mode indicator
        self.mode_label = ttk.Label(
            status_bar,
            text="Mode: Domain List",
            style='TLabel'
        )
        self.mode_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _setup_menu(self) -> None:
        """Setup the menu bar."""
        self.menubar = tk.Menu(self.root, **self.theme.get_menu_config())
        self.root.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, **self.theme.get_menu_config())
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Domain File", command=self._load_domain_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Results", command=self._save_results, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Load Config", command=self._load_config_file)
        file_menu.add_command(label="Save Config", command=self._save_config_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Alt+F4")
        
        # Tools menu
        tools_menu = tk.Menu(self.menubar, **self.theme.get_menu_config())
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Refresh AWS IP Ranges", command=self._refresh_aws_data)
        tools_menu.add_command(label="Clear Cache", command=self._clear_cache)
        
        # View menu
        view_menu = tk.Menu(self.menubar, **self.theme.get_menu_config())
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Console", command=self._toggle_console)
        view_menu.add_command(label="Toggle Dark Mode", command=self._toggle_dark_mode)
        view_menu.add_separator()
        view_menu.add_command(label="Fullscreen", command=self._toggle_fullscreen, accelerator="F11")
        
        # Help menu
        help_menu = tk.Menu(self.menubar, **self.theme.get_menu_config())
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_docs)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _setup_bindings(self) -> None:
        """Setup keyboard bindings."""
        self.root.bind('<Control-o>', lambda e: self._load_domain_file())
        self.root.bind('<Control-s>', lambda e: self._save_results())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.root.bind('<Control-q>', lambda e: self._on_close())
        self.root.bind('<F5>', lambda e: self._start_scan())
        self.root.bind('<Escape>', lambda e: self._stop_scan())
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _update_clock(self) -> None:
        """Update the clock display."""
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self._update_clock)
    
    def _process_updates(self) -> None:
        """Process queued updates from scanner threads."""
        try:
            while True:
                update = self.update_queue.get_nowait()
                update_type = update.get('type')
                
                if update_type == 'result':
                    result = update.get('result')
                    self.results_panel.add_result(
                        url=result.url,
                        success=result.success,
                        content=result.content,
                        timestamp=result.timestamp.strftime('%H:%M:%S')
                    )
                
                elif update_type == 'stats':
                    stats = update.get('stats')
                    self.stats_dashboard.update_stats(
                        total_scanned=stats.total_scanned,
                        successful=stats.successful,
                        failed=stats.failed,
                        rate=stats.requests_per_second,
                        elapsed=stats.elapsed_seconds,
                        remaining=stats.estimated_remaining,
                        success_rate=stats.success_rate,
                        total_targets=stats.total_targets
                    )
                
                elif update_type == 'state':
                    state = update.get('state')
                    self._update_state_display(state)
                
                elif update_type == 'log':
                    level = update.get('level', 'info')
                    message = update.get('message', '')
                    getattr(self.log_console, level)(message)
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._process_updates)
    
    def _on_mode_change(self, mode: str) -> None:
        """Handle scan mode change."""
        self._current_mode = mode
        mode_names = {
            'single_url': 'Single URL',
            'domain_list': 'Domain List',
            'aws_ranges': 'AWS IP Ranges'
        }
        self.mode_label.config(text=f"Mode: {mode_names.get(mode, mode)}")
        self.log_console.info(f"Scan mode changed to: {mode_names.get(mode, mode)}")
    
    def _on_file_load(self, filepath: str) -> None:
        """Handle file load."""
        self.log_console.info(f"Loaded domain file: {filepath}")
        self.config.add_recent_file(filepath)
    
    def _on_config_change(self, key: str, value: Any) -> None:
        """Handle configuration change."""
        if key == 'refresh_aws':
            self._refresh_aws_data()
        elif key == 'save_config':
            self._save_config()
        elif key == 'reset_config':
            self.log_console.info("Configuration reset to defaults")
        elif key == 'dark_mode':
            self._toggle_dark_mode()
        else:
            self.config.set(key, value)
            self.log_console.debug(f"Config changed: {key} = {value}")
    
    def _start_scan(self) -> None:
        """Start the scanning process."""
        if self._is_scanning:
            return
        
        mode = self._current_mode
        
        try:
            if mode == 'single_url':
                url = self.input_panel.get_single_url()
                if not url:
                    messagebox.showwarning("Warning", "Please enter a URL to scan")
                    return
                
                # Create scanner for single URL
                self.current_scanner = DomainScanner(
                    max_threads=1,
                    timeout=self.config.get('timeout', 5),
                    output_directory=self.config.get('output_directory', './results')
                )
                self.current_scanner.load_domains_from_list([url])
            
            elif mode == 'domain_list':
                filepath = self.input_panel.get_domain_file()
                if not filepath or not os.path.exists(filepath):
                    messagebox.showwarning("Warning", "Please select a valid domain file")
                    return
                
                self.current_scanner = DomainScanner(
                    max_threads=self.config.get('max_threads', 50),
                    timeout=self.config.get('timeout', 5),
                    request_delay=self.config.get('request_delay', 0.1),
                    retry_attempts=self.config.get('retry_attempts', 3),
                    output_directory=self.config.get('output_directory', './results')
                )
                count = self.current_scanner.load_domains_from_file(filepath)
                self.log_console.info(f"Loaded {count:,} domains from file")
            
            elif mode == 'aws_ranges':
                regions = self.input_panel.get_selected_regions()
                services = self.input_panel.get_selected_services()
                infinite = self.input_panel.get_infinite_mode()
                
                self.current_scanner = AWSScanner(
                    max_threads=self.config.get('max_threads', 50),
                    timeout=self.config.get('timeout', 5),
                    request_delay=self.config.get('request_delay', 0.1),
                    retry_attempts=self.config.get('retry_attempts', 3),
                    output_directory=self.config.get('output_directory', './results')
                )
                
                self.log_console.info("Fetching AWS IP ranges...")
                self.current_scanner.fetch_aws_ip_ranges()
                
                self.current_scanner.set_regions(regions)
                self.current_scanner.set_services(services)
                self.current_scanner.set_infinite_mode(infinite)
                self.current_scanner.set_max_ips_per_cidr(self.config.get('max_ips_per_cidr', 256))
                
                if infinite:
                    self.log_console.info("Starting infinite AWS IP range scan...")
                else:
                    ip_count = self.current_scanner.get_ip_count_estimate()
                    self.log_console.info(f"Estimated {ip_count:,} IPs to scan")
            
            # Setup callbacks
            self.current_scanner.add_result_callback(self._on_scan_result)
            self.current_scanner.add_stats_callback(self._on_stats_update)
            self.current_scanner.add_state_callback(self._on_state_change)
            
            # Start scan in thread
            self.scan_thread = threading.Thread(target=self._run_scan)
            self.scan_thread.daemon = True
            self.scan_thread.start()
            
            # Update UI
            self._is_scanning = True
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.status_label.config(text="● Scanning")
            self.status_text.config(text="Scan in progress...")
            
            self.log_console.success("Scan started!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scan: {str(e)}")
            self.log_console.error(f"Scan start failed: {str(e)}")
    
    def _run_scan(self) -> None:
        """Run the scan (in separate thread)."""
        try:
            if isinstance(self.current_scanner, AWSScanner):
                self.current_scanner.start_scan()
            elif isinstance(self.current_scanner, DomainScanner):
                self.current_scanner.start_scan()
        except Exception as e:
            self.update_queue.put({
                'type': 'log',
                'level': 'error',
                'message': f"Scan error: {str(e)}"
            })
    
    def _on_scan_result(self, result: ScanResult) -> None:
        """Handle scan result (called from scanner thread)."""
        self.update_queue.put({
            'type': 'result',
            'result': result
        })
        
        if result.success:
            self.update_queue.put({
                'type': 'log',
                'level': 'success',
                'message': f"Found .env: {result.url}"
            })
    
    def _on_stats_update(self, stats: ScanStats) -> None:
        """Handle stats update (called from scanner thread)."""
        self.update_queue.put({
            'type': 'stats',
            'stats': stats
        })
    
    def _on_state_change(self, state: ScannerState) -> None:
        """Handle state change (called from scanner thread)."""
        self.update_queue.put({
            'type': 'state',
            'state': state
        })
    
    def _update_state_display(self, state: ScannerState) -> None:
        """Update UI based on scanner state."""
        if state == ScannerState.IDLE or state == ScannerState.STOPPED:
            self._is_scanning = False
            self._is_paused = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED, text="⏸ Pause")
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="● Idle")
            self.status_text.config(text="Ready")
            
            if state == ScannerState.STOPPED:
                self.log_console.warning("Scan stopped")
        
        elif state == ScannerState.SCANNING:
            self._is_scanning = True
            self._is_paused = False
            self.pause_btn.config(text="⏸ Pause")
            self.status_label.config(text="● Scanning")
        
        elif state == ScannerState.PAUSED:
            self._is_paused = True
            self.pause_btn.config(text="▶ Resume")
            self.status_label.config(text="● Paused")
            self.status_text.config(text="Scan paused")
        
        elif state == ScannerState.STOPPING:
            self.status_label.config(text="● Stopping...")
            self.status_text.config(text="Stopping scan...")
        
        elif state == ScannerState.ERROR:
            self._is_scanning = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="● Error")
            self.log_console.error("Scanner encountered an error")
    
    def _toggle_pause(self) -> None:
        """Toggle pause/resume."""
        if self.current_scanner:
            if self._is_paused:
                self.current_scanner.resume()
                self.log_console.info("Scan resumed")
            else:
                self.current_scanner.pause()
                self.log_console.info("Scan paused")
    
    def _stop_scan(self) -> None:
        """Stop the current scan."""
        if self.current_scanner and self._is_scanning:
            self.current_scanner.stop()
            self.log_console.warning("Stopping scan...")
    
    def _clear_results(self) -> None:
        """Clear all results."""
        self.results_panel.clear_results()
        self.stats_dashboard.reset()
        self.log_console.info("Results cleared")
    
    def _export_results(self, format: str, results: List[dict]) -> None:
        """Export results to file."""
        if not results:
            messagebox.showinfo("Info", "No results to export")
            return
        
        extensions = {
            'json': ('.json', [("JSON files", "*.json")]),
            'csv': ('.csv', [("CSV files", "*.csv")]),
            'txt': ('.txt', [("Text files", "*.txt")])
        }
        
        ext, filetypes = extensions.get(format, ('.txt', [("Text files", "*.txt")]))
        
        filepath = filedialog.asksaveasfilename(
            title=f"Export as {format.upper()}",
            defaultextension=ext,
            filetypes=filetypes
        )
        
        if filepath:
            try:
                if format == 'json':
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, default=str)
                
                elif format == 'csv':
                    import csv
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['URL', 'Timestamp', 'Content'])
                        for r in results:
                            writer.writerow([r['url'], r['timestamp'], r.get('content', '')[:500]])
                
                else:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        for r in results:
                            f.write(f"URL: {r['url']}\n")
                            f.write(f"Timestamp: {r['timestamp']}\n")
                            f.write("=" * 60 + "\n")
                            f.write(r.get('content', '') + "\n\n")
                
                messagebox.showinfo("Success", f"Results exported to {filepath}")
                self.log_console.success(f"Exported {len(results)} results to {filepath}")
            
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
                self.log_console.error(f"Export failed: {str(e)}")
    
    def _load_domain_file(self) -> None:
        """Load a domain file."""
        filepath = filedialog.askopenfilename(
            title="Load Domain File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            self.input_panel.set_domain_file(filepath)
            self.left_notebook.select(0)  # Switch to input tab
    
    def _save_results(self) -> None:
        """Save results."""
        results = self.results_panel.get_successful_results()
        if results:
            self._export_results('txt', results)
        else:
            messagebox.showinfo("Info", "No results to save")
    
    def _load_config_file(self) -> None:
        """Load configuration from file."""
        filepath = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    config_data = json.load(f)
                self.config.update(config_data)
                self.config_panel.set_config(config_data)
                self.log_console.success(f"Configuration loaded from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def _save_config_file(self) -> None:
        """Save configuration to file."""
        filepath = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filepath:
            try:
                config_data = self.config_panel.get_config()
                with open(filepath, 'w') as f:
                    json.dump(config_data, f, indent=2)
                self.log_console.success(f"Configuration saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def _load_config(self) -> None:
        """Load configuration on startup."""
        config_data = self.config.get_all()
        self.config_panel.set_config(config_data)
    
    def _save_config(self) -> None:
        """Save current configuration."""
        config_data = self.config_panel.get_config()
        self.config.update(config_data)
        self.log_console.info("Configuration saved")
    
    def _refresh_aws_data(self) -> None:
        """Refresh AWS IP ranges data."""
        def refresh():
            try:
                from utils.aws_ip_fetcher import AWSIPFetcher
                fetcher = AWSIPFetcher()
                fetcher.fetch_ip_ranges(force_refresh=True)
                self.update_queue.put({
                    'type': 'log',
                    'level': 'success',
                    'message': 'AWS IP ranges refreshed successfully'
                })
            except Exception as e:
                self.update_queue.put({
                    'type': 'log',
                    'level': 'error',
                    'message': f'Failed to refresh AWS data: {str(e)}'
                })
        
        threading.Thread(target=refresh, daemon=True).start()
        self.log_console.info("Refreshing AWS IP ranges...")
    
    def _clear_cache(self) -> None:
        """Clear cached data."""
        cache_files = ['aws_ip_ranges_cache.json', 'config.json']
        for f in cache_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        self.log_console.info("Cache cleared")
    
    def _toggle_console(self) -> None:
        """Toggle log console visibility."""
        if self.log_console._is_collapsed:
            self.log_console.expand()
        else:
            self.log_console.collapse()
    
    def _toggle_dark_mode(self) -> None:
        """Toggle dark mode."""
        current = self.config.get('dark_mode', True)
        new_mode = not current
        self.config.set('dark_mode', new_mode)
        
        self.theme.set_dark_mode(new_mode)
        self.theme.apply_to_style(self.style)
        
        self.log_console.info(f"Dark mode {'enabled' if new_mode else 'disabled'}")
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
    
    def _show_docs(self) -> None:
        """Show documentation."""
        doc_text = """
Laravel-Fucker v2.0.0 - Documentation

FEATURES:
• Scan single URLs, domain lists, or AWS IP ranges
• Multi-threaded scanning for high performance
• Real-time statistics and progress tracking
• Export results in JSON, CSV, or TXT format
• Golden-themed professional interface

USAGE:
1. Select scan mode (Single URL, Domain List, or AWS IP Ranges)
2. Configure settings as needed
3. Click 'Start Scan' to begin
4. View results in real-time
5. Export successful finds

KEYBOARD SHORTCUTS:
• Ctrl+O: Load domain file
• Ctrl+S: Save results
• F5: Start scan
• Escape: Stop scan
• F11: Toggle fullscreen

For more information, visit the GitHub repository.
        """
        
        # Create documentation window
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentation")
        doc_window.geometry("600x500")
        doc_window.configure(bg=self.theme.colors.bg_primary)
        
        text = tk.Text(
            doc_window,
            wrap=tk.WORD,
            **self.theme.get_text_widget_config()
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', doc_text)
        text.config(state=tk.DISABLED)
    
    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = f"""
{self.APP_NAME} v{self.VERSION}

A high-performance tool for scanning domains
and AWS IP ranges for exposed .env files.

Features:
• AWS IP Range scanning
• Multi-threaded processing
• Golden-themed GUI
• Real-time statistics

Created for security research purposes.
Use responsibly and legally.

© 2024 @username_uNique
        """
        
        messagebox.showinfo("About", about_text)
    
    def _on_close(self) -> None:
        """Handle window close."""
        if self._is_scanning:
            if not messagebox.askyesno("Confirm Exit", "A scan is in progress. Are you sure you want to exit?"):
                return
            
            # Stop scanner
            if self.current_scanner:
                self.current_scanner.stop()
        
        # Save configuration
        self._save_config()
        
        # Close
        self.root.destroy()
    
    def run(self) -> None:
        """Run the application."""
        self.root.mainloop()


def create_main_window() -> MainWindow:
    """Create and return the main window instance."""
    return MainWindow()
