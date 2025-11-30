"""
Golden Theme

Professional golden-themed styling for the GUI.
Color scheme: Golden/amber theme with dark backgrounds.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ColorScheme:
    """Color scheme definition."""
    # Primary golden colors
    gold_primary: str = "#FFD700"
    gold_light: str = "#FFE55C"
    gold_dark: str = "#DAA520"
    gold_muted: str = "#B8860B"
    amber: str = "#FFA500"
    bronze: str = "#CD7F32"
    
    # Background colors (dark mode)
    bg_primary: str = "#1a1a1a"
    bg_secondary: str = "#2d2d2d"
    bg_tertiary: str = "#3d3d3d"
    bg_hover: str = "#4d4d4d"
    bg_active: str = "#5d5d5d"
    
    # Text colors
    text_primary: str = "#ffffff"
    text_secondary: str = "#cccccc"
    text_muted: str = "#888888"
    text_gold: str = "#FFD700"
    
    # Status colors
    success: str = "#4CAF50"
    success_dark: str = "#388E3C"
    warning: str = "#FFA500"
    error: str = "#f44336"
    error_dark: str = "#c62828"
    info: str = "#2196F3"
    
    # Border colors
    border_light: str = "#4d4d4d"
    border_gold: str = "#B8860B"
    
    # Light mode variants
    bg_primary_light: str = "#f5f5f5"
    bg_secondary_light: str = "#ffffff"
    bg_tertiary_light: str = "#e0e0e0"
    text_primary_light: str = "#333333"
    text_secondary_light: str = "#666666"


# Default color schemes
DARK_THEME = ColorScheme()
LIGHT_THEME = ColorScheme(
    bg_primary="#f5f5f5",
    bg_secondary="#ffffff",
    bg_tertiary="#e0e0e0",
    bg_hover="#d0d0d0",
    bg_active="#c0c0c0",
    text_primary="#333333",
    text_secondary="#666666",
    text_muted="#999999",
    border_light="#cccccc"
)


class GoldenTheme:
    """Golden theme manager for tkinter."""
    
    def __init__(self, dark_mode: bool = True):
        """
        Initialize the golden theme.
        
        Args:
            dark_mode: If True, use dark theme variant
        """
        self.dark_mode = dark_mode
        self.colors = DARK_THEME if dark_mode else LIGHT_THEME
    
    def set_dark_mode(self, enabled: bool) -> None:
        """Toggle dark mode."""
        self.dark_mode = enabled
        self.colors = DARK_THEME if enabled else LIGHT_THEME
    
    def get_style_config(self) -> Dict[str, Any]:
        """
        Get ttk style configuration.
        
        Returns:
            Dictionary of style configurations
        """
        c = self.colors
        
        return {
            # Root window
            'root': {
                'bg': c.bg_primary
            },
            
            # Frame styles
            'TFrame': {
                'configure': {
                    'background': c.bg_primary
                }
            },
            'Secondary.TFrame': {
                'configure': {
                    'background': c.bg_secondary
                }
            },
            'Card.TFrame': {
                'configure': {
                    'background': c.bg_secondary,
                    'relief': 'flat'
                }
            },
            
            # Label styles
            'TLabel': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.text_primary,
                    'font': ('Segoe UI', 10)
                }
            },
            'Title.TLabel': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.gold_primary,
                    'font': ('Segoe UI', 24, 'bold')
                }
            },
            'Subtitle.TLabel': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.gold_dark,
                    'font': ('Segoe UI', 14)
                }
            },
            'Header.TLabel': {
                'configure': {
                    'background': c.bg_secondary,
                    'foreground': c.gold_primary,
                    'font': ('Segoe UI', 12, 'bold')
                }
            },
            'Gold.TLabel': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.gold_primary,
                    'font': ('Segoe UI', 10, 'bold')
                }
            },
            'Success.TLabel': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.success,
                    'font': ('Segoe UI', 10)
                }
            },
            'Error.TLabel': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.error,
                    'font': ('Segoe UI', 10)
                }
            },
            'Stats.TLabel': {
                'configure': {
                    'background': c.bg_secondary,
                    'foreground': c.text_primary,
                    'font': ('Segoe UI', 11)
                }
            },
            'StatsValue.TLabel': {
                'configure': {
                    'background': c.bg_secondary,
                    'foreground': c.gold_primary,
                    'font': ('Segoe UI', 14, 'bold')
                }
            },
            
            # Button styles
            'TButton': {
                'configure': {
                    'background': c.bg_tertiary,
                    'foreground': c.text_primary,
                    'font': ('Segoe UI', 10),
                    'padding': (15, 8)
                },
                'map': {
                    'background': [
                        ('active', c.bg_hover),
                        ('disabled', c.bg_tertiary)
                    ],
                    'foreground': [
                        ('disabled', c.text_muted)
                    ]
                }
            },
            'Gold.TButton': {
                'configure': {
                    'background': c.gold_dark,
                    'foreground': c.bg_primary,
                    'font': ('Segoe UI', 10, 'bold'),
                    'padding': (20, 10)
                },
                'map': {
                    'background': [
                        ('active', c.gold_primary),
                        ('disabled', c.gold_muted)
                    ]
                }
            },
            'Danger.TButton': {
                'configure': {
                    'background': c.error_dark,
                    'foreground': c.text_primary,
                    'font': ('Segoe UI', 10),
                    'padding': (15, 8)
                },
                'map': {
                    'background': [
                        ('active', c.error)
                    ]
                }
            },
            'Success.TButton': {
                'configure': {
                    'background': c.success_dark,
                    'foreground': c.text_primary,
                    'font': ('Segoe UI', 10),
                    'padding': (15, 8)
                },
                'map': {
                    'background': [
                        ('active', c.success)
                    ]
                }
            },
            
            # Entry styles
            'TEntry': {
                'configure': {
                    'fieldbackground': c.bg_tertiary,
                    'foreground': c.text_primary,
                    'insertcolor': c.gold_primary,
                    'font': ('Segoe UI', 10),
                    'padding': 8
                },
                'map': {
                    'fieldbackground': [
                        ('focus', c.bg_hover)
                    ],
                    'bordercolor': [
                        ('focus', c.gold_dark)
                    ]
                }
            },
            
            # Combobox styles
            'TCombobox': {
                'configure': {
                    'fieldbackground': c.bg_tertiary,
                    'background': c.bg_tertiary,
                    'foreground': c.text_primary,
                    'arrowcolor': c.gold_primary,
                    'font': ('Segoe UI', 10),
                    'padding': 8
                },
                'map': {
                    'fieldbackground': [
                        ('readonly', c.bg_tertiary)
                    ],
                    'selectbackground': [
                        ('readonly', c.gold_dark)
                    ]
                }
            },
            
            # Scale/Slider styles
            'TScale': {
                'configure': {
                    'background': c.bg_primary,
                    'troughcolor': c.bg_tertiary,
                    'slidercolor': c.gold_primary
                }
            },
            'Horizontal.TScale': {
                'configure': {
                    'background': c.bg_primary,
                    'troughcolor': c.bg_tertiary
                }
            },
            
            # Checkbutton styles
            'TCheckbutton': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.text_primary,
                    'font': ('Segoe UI', 10)
                },
                'map': {
                    'background': [
                        ('active', c.bg_primary)
                    ]
                }
            },
            'Gold.TCheckbutton': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.gold_primary,
                    'font': ('Segoe UI', 10)
                }
            },
            
            # Radiobutton styles
            'TRadiobutton': {
                'configure': {
                    'background': c.bg_primary,
                    'foreground': c.text_primary,
                    'font': ('Segoe UI', 10)
                },
                'map': {
                    'background': [
                        ('active', c.bg_primary)
                    ]
                }
            },
            
            # Notebook (tabs) styles
            'TNotebook': {
                'configure': {
                    'background': c.bg_primary,
                    'tabmargins': [2, 5, 2, 0]
                }
            },
            'TNotebook.Tab': {
                'configure': {
                    'background': c.bg_secondary,
                    'foreground': c.text_secondary,
                    'padding': [15, 8],
                    'font': ('Segoe UI', 10)
                },
                'map': {
                    'background': [
                        ('selected', c.bg_tertiary),
                        ('active', c.bg_hover)
                    ],
                    'foreground': [
                        ('selected', c.gold_primary),
                        ('active', c.gold_light)
                    ]
                }
            },
            
            # Progressbar styles
            'TProgressbar': {
                'configure': {
                    'background': c.gold_primary,
                    'troughcolor': c.bg_tertiary,
                    'bordercolor': c.bg_tertiary,
                    'lightcolor': c.gold_light,
                    'darkcolor': c.gold_dark
                }
            },
            'Horizontal.TProgressbar': {
                'configure': {
                    'background': c.gold_primary,
                    'troughcolor': c.bg_tertiary
                }
            },
            
            # Scrollbar styles
            'TScrollbar': {
                'configure': {
                    'background': c.bg_tertiary,
                    'troughcolor': c.bg_secondary,
                    'arrowcolor': c.gold_primary
                },
                'map': {
                    'background': [
                        ('active', c.gold_dark)
                    ]
                }
            },
            
            # Separator styles
            'TSeparator': {
                'configure': {
                    'background': c.border_gold
                }
            },
            
            # LabelFrame styles
            'TLabelframe': {
                'configure': {
                    'background': c.bg_secondary,
                    'foreground': c.gold_primary,
                    'bordercolor': c.border_gold
                }
            },
            'TLabelframe.Label': {
                'configure': {
                    'background': c.bg_secondary,
                    'foreground': c.gold_primary,
                    'font': ('Segoe UI', 10, 'bold')
                }
            },
            
            # Treeview styles
            'Treeview': {
                'configure': {
                    'background': c.bg_secondary,
                    'foreground': c.text_primary,
                    'fieldbackground': c.bg_secondary,
                    'font': ('Segoe UI', 10)
                },
                'map': {
                    'background': [
                        ('selected', c.gold_dark)
                    ],
                    'foreground': [
                        ('selected', c.bg_primary)
                    ]
                }
            },
            'Treeview.Heading': {
                'configure': {
                    'background': c.bg_tertiary,
                    'foreground': c.gold_primary,
                    'font': ('Segoe UI', 10, 'bold')
                },
                'map': {
                    'background': [
                        ('active', c.gold_dark)
                    ]
                }
            },
            
            # PanedWindow styles
            'TPanedwindow': {
                'configure': {
                    'background': c.bg_primary
                }
            },
            
            # Menu styles (for reference - menus use different styling)
            'Menu': {
                'bg': c.bg_secondary,
                'fg': c.text_primary,
                'activebackground': c.gold_dark,
                'activeforeground': c.bg_primary,
                'font': ('Segoe UI', 10)
            }
        }
    
    def apply_to_style(self, style) -> None:
        """
        Apply theme to a ttk.Style object.
        
        Args:
            style: ttk.Style instance
        """
        config = self.get_style_config()
        
        for style_name, style_config in config.items():
            if style_name in ('root', 'Menu'):
                continue
            
            if 'configure' in style_config:
                try:
                    style.configure(style_name, **style_config['configure'])
                except:
                    pass
            
            if 'map' in style_config:
                try:
                    style.map(style_name, **style_config['map'])
                except:
                    pass
    
    def get_text_widget_config(self) -> Dict[str, Any]:
        """Get configuration for Text widgets."""
        c = self.colors
        return {
            'bg': c.bg_secondary,
            'fg': c.text_primary,
            'insertbackground': c.gold_primary,
            'selectbackground': c.gold_dark,
            'selectforeground': c.bg_primary,
            'font': ('Consolas', 10),
            'relief': 'flat',
            'borderwidth': 0
        }
    
    def get_listbox_config(self) -> Dict[str, Any]:
        """Get configuration for Listbox widgets."""
        c = self.colors
        return {
            'bg': c.bg_secondary,
            'fg': c.text_primary,
            'selectbackground': c.gold_dark,
            'selectforeground': c.bg_primary,
            'font': ('Segoe UI', 10),
            'relief': 'flat',
            'borderwidth': 0,
            'highlightthickness': 0
        }
    
    def get_canvas_config(self) -> Dict[str, Any]:
        """Get configuration for Canvas widgets."""
        c = self.colors
        return {
            'bg': c.bg_primary,
            'highlightthickness': 0
        }
    
    def get_menu_config(self) -> Dict[str, Any]:
        """Get configuration for Menu widgets."""
        c = self.colors
        return {
            'bg': c.bg_secondary,
            'fg': c.text_primary,
            'activebackground': c.gold_dark,
            'activeforeground': c.bg_primary,
            'font': ('Segoe UI', 10),
            'relief': 'flat',
            'borderwidth': 0,
            'tearoff': False
        }


# Global theme instance
_theme: GoldenTheme = None


def get_theme(dark_mode: bool = True) -> GoldenTheme:
    """Get or create the global theme instance."""
    global _theme
    if _theme is None:
        _theme = GoldenTheme(dark_mode)
    return _theme


def set_dark_mode(enabled: bool) -> None:
    """Set dark mode globally."""
    theme = get_theme()
    theme.set_dark_mode(enabled)
