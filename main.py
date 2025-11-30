#!/usr/bin/env python3
"""
Laravel-Fucker v2.0.0

A high-performance tool for scanning domains and AWS IP ranges 
for exposed .env files.

Features:
- AWS IP range scanning with infinite loop mode
- Professional golden-themed GUI
- Multi-threaded scanning
- Real-time statistics
- Export to JSON, CSV, TXT

Usage:
    python main.py          # Launch GUI
    python main.py --cli    # Use CLI mode (original behavior)

Author: @username_uNique
License: MIT
"""

import sys
import os
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def check_dependencies():
    """Check and install required dependencies."""
    required = [
        'requests',
        'urllib3'
    ]
    
    optional = [
        'pyperclip'
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Installing...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Installation complete.")
    
    # Try to install optional packages (don't fail if they can't be installed)
    for package in optional:
        try:
            __import__(package)
        except ImportError:
            try:
                import subprocess
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', package],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                pass


def run_gui():
    """Launch the GUI application."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("ERROR: tkinter is not available.")
        print("Please install tkinter for your Python installation.")
        print("\nOn Ubuntu/Debian: sudo apt-get install python3-tk")
        print("On Fedora: sudo dnf install python3-tkinter")
        print("On macOS: tkinter should be included with Python")
        print("On Windows: tkinter should be included with Python")
        sys.exit(1)
    
    # Import and run main window
    from gui.main_window import create_main_window
    
    print("Starting Laravel-Fucker GUI...")
    window = create_main_window()
    window.run()


def run_cli():
    """Run the original CLI scanner."""
    print("Running in CLI mode...")
    
    # Import and run original env.py
    import env
    env.main()


def show_splash():
    """Show ASCII art splash screen."""
    splash = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██╗      █████╗ ██████╗  █████╗ ██╗   ██╗███████╗██╗           ║
║   ██║     ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝██║           ║
║   ██║     ███████║██████╔╝███████║██║   ██║█████╗  ██║           ║
║   ██║     ██╔══██║██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║           ║
║   ███████╗██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗      ║
║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝      ║
║                                                                  ║
║           ███████╗██╗   ██╗ ██████╗██╗  ██╗███████╗██████╗       ║
║           ██╔════╝██║   ██║██╔════╝██║ ██╔╝██╔════╝██╔══██╗      ║
║           █████╗  ██║   ██║██║     █████╔╝ █████╗  ██████╔╝      ║
║           ██╔══╝  ██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗      ║
║           ██║     ╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║      ║
║           ╚═╝      ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝      ║
║                                                                  ║
║                     v2.0.0 - Golden Edition                      ║
║                                                                  ║
║           AWS IP Range Scanner | Professional GUI                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(splash)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Laravel-Fucker - .env File Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Launch the GUI
  python main.py --cli        Use CLI mode (original behavior)
  python main.py --help       Show this help message
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run in CLI mode (original behavior without GUI)'
    )
    
    parser.add_argument(
        '--no-splash',
        action='store_true',
        help='Skip the splash screen'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Laravel-Fucker v2.0.0'
    )
    
    args = parser.parse_args()
    
    # Show splash
    if not args.no_splash:
        show_splash()
    
    # Check dependencies
    check_dependencies()
    
    # Run appropriate mode
    if args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()
