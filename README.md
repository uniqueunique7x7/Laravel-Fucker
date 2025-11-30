# Laravel-Fucker v2.0.0 - Golden Edition

A high-performance, multi-threaded Python tool designed to scan millions of domains and AWS IP ranges for exposed `.env` files. Features a professional golden-themed GUI and supports infinite scanning mode.

## ⚠️ Disclaimer

This tool is intended for **security research and educational purposes only**. Always ensure you have proper authorization before scanning any domains or IP ranges. Unauthorized access to computer systems is illegal.

## ✨ What's New in v2.0.0

- 🌐 **AWS IP Range Scanner**: Scan Amazon AWS IP ranges for exposed .env files
- 🎨 **Golden-Themed GUI**: Professional, modern interface with dark mode
- ♾️ **Infinite Scanning Mode**: Continuously scan AWS IP ranges in a loop
- 📊 **Real-time Statistics**: Live dashboard with progress, rates, and success metrics
- 💾 **Export Options**: Export results in JSON, CSV, or TXT format
- ⚙️ **Configurable Settings**: Thread count, timeout, delays, and more
- 📝 **Log Console**: Color-coded, filterable log output

## Features

### Core Features
- 🚀 **High-Performance**: Multi-threaded scanning with up to 100+ concurrent connections
- 🌐 **AWS IP Range Support**: Fetch and scan official AWS IP ranges by region and service
- ♾️ **Infinite Mode**: Continuous scanning loop for AWS IP ranges
- 💾 **Checkpoint System**: Automatic progress saving with resume capability
- 📊 **Real-time Progress**: Live statistics showing processing rate and success count
- 🔄 **Auto-retry**: Configurable retry attempts with exponential backoff
- 🎯 **Smart Detection**: Validates .env files by checking for common patterns

### GUI Features
- 🎨 **Golden Theme**: Professional amber/gold color scheme with dark mode
- 📋 **Tab-based Input**: Single URL, Domain List, or AWS IP Range modes
- 📈 **Statistics Dashboard**: Real-time metrics and progress bars
- 📝 **Results Panel**: Live feed, successful finds, and detailed view
- 🔍 **Log Console**: Filterable, color-coded log output
- ⚙️ **Settings Panel**: Easy configuration management
- ⌨️ **Keyboard Shortcuts**: Quick access to common actions

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- See `requirements.txt` for additional dependencies

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd Laravel-Fucker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode (Recommended)

Launch the graphical interface:
```bash
python main.py
```

### CLI Mode (Original)

Run the original command-line scanner:
```bash
python main.py --cli
```

Or directly:
```bash
python env.py
```

### Scan Modes

#### 1. Single URL Mode
Enter a single domain or URL to scan for .env files.

#### 2. Domain List Mode
Load a text file with one domain per line:
```
example.com
subdomain.example.com
another-site.org
```

#### 3. AWS IP Range Mode
- Select AWS regions to scan (e.g., us-east-1, eu-west-1)
- Select AWS services to target (e.g., EC2, CLOUDFRONT)
- Enable infinite mode for continuous scanning
- AWS IP ranges are fetched from the official AWS IP ranges JSON

## Configuration

### GUI Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Thread Count | 50 | Concurrent scanning threads (1-100) |
| Timeout | 5s | HTTP request timeout |
| Request Delay | 0.1s | Delay between requests (rate limiting) |
| Retry Attempts | 3 | Number of retries on failure |
| Max IPs per CIDR | 256 | Maximum IPs to scan per CIDR range |

### CLI Configuration

Edit variables in `env.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_THREADS` | 200 | Number of concurrent threads |
| `TIMEOUT` | 2 | HTTP request timeout in seconds |
| `WRITE_BUFFER_SIZE` | 50 | Results buffer before writing |
| `CHECKPOINT_INTERVAL` | 1000 | Save progress every N domains |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Load domain file |
| Ctrl+S | Save results |
| F5 | Start scan |
| Escape | Stop scan |
| F11 | Toggle fullscreen |
| Ctrl+Q | Exit application |

## Output

### GUI Export Formats

- **JSON**: Structured data with all details
- **CSV**: Spreadsheet-compatible format
- **TXT**: Human-readable text format

### CLI Output

Results are saved to `extracted_env_data.txt`:

```
================================================================================
SOURCE: https://example.com/.env
TIMESTAMP: 2025-10-05 12:34:56
================================================================================
DATABASE_URL=postgresql://user:pass@localhost/db
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
...
```

## Project Structure

```
Laravel-Fucker/
├── main.py                    # GUI launcher
├── env.py                     # Original CLI scanner
├── requirements.txt           # Python dependencies
├── gui/
│   ├── main_window.py         # Main application window
│   ├── components/
│   │   ├── input_panel.py     # Input configuration
│   │   ├── stats_dashboard.py # Statistics display
│   │   ├── results_panel.py   # Results viewer
│   │   ├── log_console.py     # Log output
│   │   └── config_panel.py    # Settings panel
│   └── themes/
│       └── golden_theme.py    # Golden color theme
├── scanner/
│   ├── scanner_core.py        # Core scanning logic
│   ├── domain_scanner.py      # Domain list scanner
│   └── aws_scanner.py         # AWS IP range scanner
└── utils/
    ├── aws_ip_fetcher.py      # AWS IP range fetcher
    ├── config_manager.py      # Configuration management
    └── logger.py              # Logging utilities
```

## Technical Details

### AWS IP Range Scanning

- Fetches official AWS IP ranges from https://ip-ranges.amazonaws.com/ip-ranges.json
- Caches IP ranges locally with 24-hour expiration
- Supports filtering by region and service type
- Generates IPs from CIDR ranges efficiently
- Infinite mode continuously loops through all ranges

### Performance Optimizations

- Socket-level tuning for maximum throughput
- Thread-local session management
- Connection pooling with aggressive settings
- Efficient IP generation without memory overflow
- Rate limiting to avoid detection

### Thread Safety

- Thread-local HTTP sessions
- Queue-based GUI updates
- Atomic state management
- Thread-safe statistics

## Troubleshooting

### "Too many open files" error
```bash
ulimit -n 65535  # Linux/Mac
```

### tkinter not found
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (with Homebrew)
brew install python-tk
```

### Slow scanning
- Increase thread count
- Reduce timeout value
- Check network connection
- Disable request delay for faster scanning

## Security Considerations

**Important**: This tool can discover sensitive information. If you find exposed .env files:

1. **Do not exploit** the information found
2. **Report responsibly** to the website owner or through proper channels
3. **Comply with laws** - unauthorized access is illegal
4. **Use ethically** - only scan domains/IPs you have permission to test

## License

This project is provided as-is for educational purposes. Use responsibly and legally.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

By: @username_uNique
Created for security research and educational purposes.

## Acknowledgments

- Built with Python's tkinter for the GUI
- Uses `requests` and `concurrent.futures` for high-performance HTTP operations
- AWS IP ranges from the official Amazon Web Services IP address ranges JSON
