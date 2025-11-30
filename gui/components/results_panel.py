"""
Results Panel Component

Display and manage scan results with tabs for different views.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional, Callable

# Try to import pyperclip, fall back to tkinter clipboard if not available
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


class ResultsPanel(ttk.Frame):
    """Panel for displaying scan results."""
    
    def __init__(
        self,
        parent,
        theme,
        on_export: Optional[Callable[[str, str], None]] = None,
        **kwargs
    ):
        """
        Initialize the results panel.
        
        Args:
            parent: Parent widget
            theme: GoldenTheme instance
            on_export: Callback for exporting results
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.on_export = on_export
        
        self._results = []
        self._successful_results = []
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Header
        header_frame = ttk.Frame(self, style='Secondary.TFrame')
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            header_frame,
            text="📊 Results",
            style='Header.TLabel'
        ).pack(side=tk.LEFT)
        
        # Export buttons
        btn_frame = ttk.Frame(header_frame, style='Secondary.TFrame')
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="Export JSON",
            command=lambda: self._export('json')
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Export CSV",
            command=lambda: self._export('csv')
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Export TXT",
            command=lambda: self._export('txt')
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Clear",
            command=self.clear_results,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Live feed tab
        self._create_live_feed_tab()
        
        # Successful finds tab
        self._create_successful_tab()
        
        # Details tab
        self._create_details_tab()
    
    def _create_live_feed_tab(self) -> None:
        """Create the live results feed tab."""
        frame = ttk.Frame(self.notebook, style='Secondary.TFrame')
        self.notebook.add(frame, text="Live Feed")
        
        # Treeview for results
        columns = ('time', 'url', 'status')
        self.live_tree = ttk.Treeview(
            frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        self.live_tree.heading('time', text='Time')
        self.live_tree.heading('url', text='URL')
        self.live_tree.heading('status', text='Status')
        
        self.live_tree.column('time', width=80, anchor='center')
        self.live_tree.column('url', width=400, anchor='w')
        self.live_tree.column('status', width=100, anchor='center')
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient='vertical', command=self.live_tree.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal', command=self.live_tree.xview)
        self.live_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.live_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            style='TCheckbutton'
        ).grid(row=2, column=0, sticky='w', pady=5)
        
        # Context menu
        self._create_live_context_menu()
    
    def _create_successful_tab(self) -> None:
        """Create the successful finds tab."""
        frame = ttk.Frame(self.notebook, style='Secondary.TFrame')
        self.notebook.add(frame, text="✓ Successful Finds")
        
        # Treeview
        columns = ('time', 'url', 'preview')
        self.success_tree = ttk.Treeview(
            frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        self.success_tree.heading('time', text='Time')
        self.success_tree.heading('url', text='URL')
        self.success_tree.heading('preview', text='Content Preview')
        
        self.success_tree.column('time', width=80, anchor='center')
        self.success_tree.column('url', width=350, anchor='w')
        self.success_tree.column('preview', width=250, anchor='w')
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient='vertical', command=self.success_tree.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal', command=self.success_tree.xview)
        self.success_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.success_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Double-click to view details
        self.success_tree.bind('<Double-1>', self._show_result_details)
        
        # Context menu
        self._create_success_context_menu()
    
    def _create_details_tab(self) -> None:
        """Create the details view tab."""
        frame = ttk.Frame(self.notebook, style='Secondary.TFrame')
        self.notebook.add(frame, text="Details")
        
        # Text widget for content
        self.details_text = tk.Text(
            frame,
            wrap=tk.WORD,
            **self.theme.get_text_widget_config()
        )
        
        vsb = ttk.Scrollbar(frame, orient='vertical', command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=vsb.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags for syntax highlighting
        self.details_text.tag_configure('key', foreground='#FFD700')
        self.details_text.tag_configure('value', foreground='#98D8C8')
        self.details_text.tag_configure('comment', foreground='#888888')
        self.details_text.tag_configure('header', foreground='#FFA500', font=('Consolas', 10, 'bold'))
        
        # Buttons
        btn_frame = ttk.Frame(frame, style='Secondary.TFrame')
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Copy to Clipboard",
            command=self._copy_details
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Save to File",
            command=self._save_details
        ).pack(side=tk.LEFT)
    
    def _create_live_context_menu(self) -> None:
        """Create context menu for live feed."""
        self.live_menu = tk.Menu(self, tearoff=0, **self.theme.get_menu_config())
        self.live_menu.add_command(label="Copy URL", command=self._copy_url)
        self.live_menu.add_command(label="View Details", command=self._view_selected)
        self.live_menu.add_separator()
        self.live_menu.add_command(label="Clear All", command=self.clear_results)
        
        self.live_tree.bind('<Button-3>', self._show_live_menu)
    
    def _create_success_context_menu(self) -> None:
        """Create context menu for successful finds."""
        self.success_menu = tk.Menu(self, tearoff=0, **self.theme.get_menu_config())
        self.success_menu.add_command(label="Copy URL", command=self._copy_success_url)
        self.success_menu.add_command(label="Copy Content", command=self._copy_success_content)
        self.success_menu.add_command(label="View Details", command=self._view_success_details)
        self.success_menu.add_separator()
        self.success_menu.add_command(label="Export This Result", command=self._export_single)
        
        self.success_tree.bind('<Button-3>', self._show_success_menu)
    
    def _show_live_menu(self, event) -> None:
        """Show context menu for live feed."""
        item = self.live_tree.identify_row(event.y)
        if item:
            self.live_tree.selection_set(item)
            self.live_menu.post(event.x_root, event.y_root)
    
    def _show_success_menu(self, event) -> None:
        """Show context menu for successful finds."""
        item = self.success_tree.identify_row(event.y)
        if item:
            self.success_tree.selection_set(item)
            self.success_menu.post(event.x_root, event.y_root)
    
    def add_result(self, url: str, success: bool, content: Optional[str] = None, timestamp: str = "") -> None:
        """
        Add a new result to the display.
        
        Args:
            url: Scanned URL
            success: Whether the scan was successful
            content: Content if successful
            timestamp: Timestamp string
        """
        # Add to live feed
        status = "✓ Found" if success else "✗ Not Found"
        time_str = timestamp if timestamp else "now"
        
        item_id = self.live_tree.insert(
            '',
            0,
            values=(time_str, url, status)
        )
        
        # Apply tag based on status
        if success:
            self.live_tree.item(item_id, tags=('success',))
        
        # Auto-scroll
        if self.auto_scroll_var.get():
            self.live_tree.see(item_id)
        
        # Add to successful if found
        if success and content:
            preview = content[:100].replace('\n', ' ').replace('\r', '')
            self.success_tree.insert(
                '',
                0,
                values=(time_str, url, preview)
            )
            
            self._successful_results.append({
                'url': url,
                'content': content,
                'timestamp': timestamp
            })
        
        # Limit items to prevent memory issues
        if len(self.live_tree.get_children()) > 1000:
            # Remove oldest items
            children = self.live_tree.get_children()
            for item in children[500:]:
                self.live_tree.delete(item)
    
    def _show_result_details(self, event) -> None:
        """Show details of selected result."""
        selection = self.success_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.success_tree.item(item, 'values')
        
        if len(values) >= 2:
            url = values[1]
            # Find content
            for result in self._successful_results:
                if result['url'] == url:
                    self._display_content(url, result['content'])
                    self.notebook.select(2)  # Switch to details tab
                    break
    
    def _display_content(self, url: str, content: str) -> None:
        """Display content in details tab with syntax highlighting."""
        self.details_text.delete('1.0', tk.END)
        
        # Header
        self.details_text.insert(tk.END, f"URL: {url}\n", 'header')
        self.details_text.insert(tk.END, "=" * 60 + "\n\n", 'header')
        
        # Content with basic syntax highlighting
        for line in content.split('\n'):
            if line.strip().startswith('#'):
                self.details_text.insert(tk.END, line + '\n', 'comment')
            elif '=' in line:
                parts = line.split('=', 1)
                self.details_text.insert(tk.END, parts[0] + '=', 'key')
                if len(parts) > 1:
                    self.details_text.insert(tk.END, parts[1] + '\n', 'value')
                else:
                    self.details_text.insert(tk.END, '\n')
            else:
                self.details_text.insert(tk.END, line + '\n')
    
    def _copy_url(self) -> None:
        """Copy selected URL from live feed."""
        selection = self.live_tree.selection()
        if selection:
            values = self.live_tree.item(selection[0], 'values')
            if len(values) >= 2:
                self._copy_to_clipboard(values[1])
    
    def _copy_success_url(self) -> None:
        """Copy URL from successful finds."""
        selection = self.success_tree.selection()
        if selection:
            values = self.success_tree.item(selection[0], 'values')
            if len(values) >= 2:
                self._copy_to_clipboard(values[1])
    
    def _copy_success_content(self) -> None:
        """Copy content from successful find."""
        selection = self.success_tree.selection()
        if selection:
            values = self.success_tree.item(selection[0], 'values')
            if len(values) >= 2:
                url = values[1]
                for result in self._successful_results:
                    if result['url'] == url:
                        self._copy_to_clipboard(result['content'])
                        break
    
    def _view_selected(self) -> None:
        """View selected item details."""
        selection = self.live_tree.selection()
        if selection:
            values = self.live_tree.item(selection[0], 'values')
            if len(values) >= 2:
                url = values[1]
                for result in self._successful_results:
                    if result['url'] == url:
                        self._display_content(url, result['content'])
                        self.notebook.select(2)
                        break
    
    def _view_success_details(self) -> None:
        """View successful find details."""
        self._show_result_details(None)
    
    def _copy_details(self) -> None:
        """Copy details text to clipboard."""
        content = self.details_text.get('1.0', tk.END)
        self._copy_to_clipboard(content)
    
    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard using pyperclip or tkinter fallback."""
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
                return
            except Exception:
                pass
        # Fallback to tkinter clipboard
        self.clipboard_clear()
        self.clipboard_append(text)
    
    def _save_details(self) -> None:
        """Save details to file."""
        filepath = filedialog.asksaveasfilename(
            title="Save Details",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                content = self.details_text.get('1.0', tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
    
    def _export(self, format: str) -> None:
        """Export results in specified format."""
        if self.on_export:
            self.on_export(format, self._successful_results)
    
    def _export_single(self) -> None:
        """Export single selected result."""
        selection = self.success_tree.selection()
        if not selection:
            return
        
        values = self.success_tree.item(selection[0], 'values')
        if len(values) < 2:
            return
        
        url = values[1]
        for result in self._successful_results:
            if result['url'] == url:
                filepath = filedialog.asksaveasfilename(
                    title="Export Result",
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")]
                )
                
                if filepath:
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(f"URL: {url}\n")
                            f.write("=" * 60 + "\n")
                            f.write(result['content'])
                        messagebox.showinfo("Success", "Result exported successfully!")
                    except Exception as e:
                        messagebox.showerror("Error", f"Export failed: {e}")
                break
    
    def clear_results(self) -> None:
        """Clear all results."""
        for item in self.live_tree.get_children():
            self.live_tree.delete(item)
        
        for item in self.success_tree.get_children():
            self.success_tree.delete(item)
        
        self.details_text.delete('1.0', tk.END)
        self._successful_results.clear()
    
    def get_successful_results(self) -> List[dict]:
        """Get all successful results."""
        return self._successful_results.copy()
