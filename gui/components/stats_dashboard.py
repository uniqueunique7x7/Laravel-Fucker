"""
Statistics Dashboard Component

Real-time statistics display with golden-themed visuals.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from datetime import timedelta


class StatsDashboard(ttk.Frame):
    """Dashboard showing real-time scanning statistics."""
    
    def __init__(self, parent, theme, **kwargs):
        """
        Initialize the statistics dashboard.
        
        Args:
            parent: Parent widget
            theme: GoldenTheme instance
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        
        # Stats variables
        self._stats = {
            'total_scanned': 0,
            'successful': 0,
            'failed': 0,
            'rate': 0.0,
            'elapsed': 0.0,
            'remaining': 0.0,
            'success_rate': 0.0,
            'total_targets': 0
        }
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        
        # Progress section
        progress_frame = ttk.Frame(self, style='Secondary.TFrame')
        progress_frame.grid(row=0, column=0, columnspan=4, sticky='ew', padx=10, pady=(10, 15))
        
        self.progress_label = ttk.Label(
            progress_frame,
            text="Progress: 0%",
            style='Header.TLabel'
        )
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400,
            style='Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Stats cards
        self._create_stat_card(0, "Total Scanned", "total_scanned", "0")
        self._create_stat_card(1, "Successful", "successful", "0", highlight=True)
        self._create_stat_card(2, "Failed", "failed", "0")
        self._create_stat_card(3, "Rate", "rate", "0.0/s")
        
        # Second row of stats
        self._create_stat_card(0, "Success Rate", "success_rate", "0.0%", row=2)
        self._create_stat_card(1, "Elapsed Time", "elapsed", "00:00:00", row=2)
        self._create_stat_card(2, "Remaining", "remaining", "--:--:--", row=2)
        self._create_stat_card(3, "Total Targets", "total_targets", "0", row=2)
        
        # Store label references
        self.stat_labels = {}
    
    def _create_stat_card(
        self,
        col: int,
        title: str,
        key: str,
        initial_value: str,
        row: int = 1,
        highlight: bool = False
    ) -> None:
        """Create a statistics card."""
        frame = ttk.Frame(self, style='Card.TFrame')
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Title
        ttk.Label(
            frame,
            text=title,
            style='Stats.TLabel'
        ).pack(pady=(8, 2))
        
        # Value
        style = 'Gold.TLabel' if highlight else 'StatsValue.TLabel'
        value_label = ttk.Label(
            frame,
            text=initial_value,
            style=style
        )
        value_label.pack(pady=(2, 8))
        
        # Store reference
        if not hasattr(self, 'stat_labels'):
            self.stat_labels = {}
        self.stat_labels[key] = value_label
    
    def update_stats(
        self,
        total_scanned: int = 0,
        successful: int = 0,
        failed: int = 0,
        rate: float = 0.0,
        elapsed: float = 0.0,
        remaining: float = 0.0,
        success_rate: float = 0.0,
        total_targets: int = 0
    ) -> None:
        """
        Update all statistics.
        
        Args:
            total_scanned: Total number of targets scanned
            successful: Number of successful finds
            failed: Number of failed attempts
            rate: Requests per second
            elapsed: Elapsed time in seconds
            remaining: Estimated remaining time in seconds
            success_rate: Success rate percentage
            total_targets: Total number of targets
        """
        self._stats = {
            'total_scanned': total_scanned,
            'successful': successful,
            'failed': failed,
            'rate': rate,
            'elapsed': elapsed,
            'remaining': remaining,
            'success_rate': success_rate,
            'total_targets': total_targets
        }
        
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the display with current stats."""
        s = self._stats
        
        # Update labels
        if 'total_scanned' in self.stat_labels:
            self.stat_labels['total_scanned'].config(text=f"{s['total_scanned']:,}")
        
        if 'successful' in self.stat_labels:
            self.stat_labels['successful'].config(text=f"{s['successful']:,}")
        
        if 'failed' in self.stat_labels:
            self.stat_labels['failed'].config(text=f"{s['failed']:,}")
        
        if 'rate' in self.stat_labels:
            self.stat_labels['rate'].config(text=f"{s['rate']:.1f}/s")
        
        if 'success_rate' in self.stat_labels:
            self.stat_labels['success_rate'].config(text=f"{s['success_rate']:.2f}%")
        
        if 'elapsed' in self.stat_labels:
            self.stat_labels['elapsed'].config(text=self._format_time(s['elapsed']))
        
        if 'remaining' in self.stat_labels:
            if s['remaining'] > 0:
                self.stat_labels['remaining'].config(text=self._format_time(s['remaining']))
            else:
                self.stat_labels['remaining'].config(text="∞" if s['total_targets'] == 0 else "--:--:--")
        
        if 'total_targets' in self.stat_labels:
            if s['total_targets'] > 0:
                self.stat_labels['total_targets'].config(text=f"{s['total_targets']:,}")
            else:
                self.stat_labels['total_targets'].config(text="∞")
        
        # Update progress bar
        if s['total_targets'] > 0:
            progress = (s['total_scanned'] / s['total_targets']) * 100
            self.progress_bar['value'] = progress
            self.progress_label.config(text=f"Progress: {progress:.1f}%")
        else:
            # Indeterminate mode for infinite scanning
            self.progress_bar['mode'] = 'indeterminate'
            self.progress_label.config(text="Progress: ∞ (Infinite mode)")
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS."""
        if seconds <= 0:
            return "00:00:00"
        
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds + td.days * 86400, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def reset(self) -> None:
        """Reset all statistics to zero."""
        self._stats = {
            'total_scanned': 0,
            'successful': 0,
            'failed': 0,
            'rate': 0.0,
            'elapsed': 0.0,
            'remaining': 0.0,
            'success_rate': 0.0,
            'total_targets': 0
        }
        
        self.progress_bar['mode'] = 'determinate'
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Progress: 0%")
        
        self._update_display()
    
    def start_indeterminate(self) -> None:
        """Start indeterminate progress animation."""
        self.progress_bar['mode'] = 'indeterminate'
        self.progress_bar.start(10)
    
    def stop_indeterminate(self) -> None:
        """Stop indeterminate progress animation."""
        self.progress_bar.stop()
        self.progress_bar['mode'] = 'determinate'
