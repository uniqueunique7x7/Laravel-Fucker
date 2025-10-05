# ENV File Extractor

A high-performance, multi-threaded Python tool designed to scan millions of domains for exposed `.env` files. This tool is optimized for speed and efficiency, capable of processing 10M+ domains with checkpoint/resume functionality.

## ⚠️ Disclaimer

This tool is intended for **security research and educational purposes only**. Always ensure you have proper authorization before scanning any domains. Unauthorized access to computer systems is illegal.

## Features

- 🚀 **High-Performance**: Optimized for scanning millions of domains with 200+ concurrent threads
- 💾 **Checkpoint System**: Automatic progress saving with resume capability
- 📊 **Real-time Progress**: Live statistics showing processing rate and success count
- 🔄 **Auto-retry**: Attempts both HTTPS and HTTP protocols
- 🎯 **Smart Detection**: Validates .env files by checking for common environment variable patterns
- 📝 **Buffered Writing**: Efficient disk I/O with configurable buffer sizes
- ⚡ **Aggressive Optimization**: Socket-level optimizations for maximum throughput

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd Env
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Create a `domains.txt` file with one domain per line:
```
example.com
subdomain.example.com
another-site.org
```

2. Run the scanner:
```bash
python env.py
```

3. If interrupted, simply run again to resume from the last checkpoint:
```bash
python env.py
```

## Configuration

Edit the configuration variables in `env.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_THREADS` | 200 | Number of concurrent threads (increase for faster processing) |
| `TIMEOUT` | 2 | HTTP request timeout in seconds |
| `WRITE_BUFFER_SIZE` | 50 | Number of results to buffer before writing to disk |
| `CHECKPOINT_INTERVAL` | 1000 | Save progress every N domains |
| `PROGRESS_INTERVAL` | 5000 | Display progress every N domains |

## Output

### Extracted Data
Results are saved to `extracted_env_data.txt` with the following format:

```
================================================================================
SOURCE: https://example.com/.env
TIMESTAMP: 2025-10-05 12:34:56
================================================================================
DATABASE_URL=postgresql://user:pass@localhost/db
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
...
```

### Checkpoint File
Progress is saved to `progress_checkpoint.txt` in the format:
```
processed_count,success_count
```

## Performance Tips

1. **Increase threads**: For faster processing on powerful systems, increase `MAX_THREADS` to 500-1000
2. **Reduce timeout**: Lower `TIMEOUT` to 1 second for faster failure detection
3. **Adjust buffer size**: Increase `WRITE_BUFFER_SIZE` to reduce disk I/O frequency
4. **Network optimization**: Run on a server with high bandwidth and low latency

## Example Output

```
================================================================================
ENV FILE EXTRACTOR - Optimized for 10M+ Domains
================================================================================

[*] Starting fresh scan...

[*] Configuration:
    - Domain file: domains.txt
    - Output file: extracted_env_data.txt
    - Max threads: 200
    - Timeout: 2s
    - Checkpoint interval: 1,000 domains
    - Write buffer size: 50

[*] Processing domains from domains.txt...

[*] Starting scan...

[CHECKPOINT] Processed: 1,000 | Success: 5 | Rate: 125.3/s
[CHECKPOINT] Processed: 2,000 | Success: 12 | Rate: 133.7/s
[PROGRESS] Processed: 5,000 | Success: 28 | Rate: 138.9/s
```

## Technical Details

### Optimizations

- **Socket-level tuning**: Disabled keepalive, Nagle's algorithm, and immediate socket closure
- **Connection pooling**: Thread-local session management with aggressive pool settings
- **Buffered I/O**: Minimizes disk writes for better performance
- **Memory management**: Sliding window approach prevents memory buildup
- **Fail-fast design**: Quick timeouts and no retries for maximum throughput

### Thread Safety

- Thread-local sessions prevent conflicts
- Locks protect shared counters and write operations
- Atomic checkpoint saves prevent corruption

## Troubleshooting

### "Too many open files" error
Increase your system's file descriptor limit:
- **Linux/Mac**: `ulimit -n 65535`
- **Windows**: Usually not an issue, but reduce `MAX_THREADS` if problems occur

### Slow processing
- Increase `MAX_THREADS`
- Reduce `TIMEOUT`
- Check your network connection
- Ensure you have sufficient CPU and memory

### Memory issues
- Reduce `MAX_THREADS`
- Decrease the sliding window size in the code

## License

This project is provided as-is for educational purposes. Use responsibly and legally.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Security Considerations

**Important**: This tool can discover sensitive information. If you find exposed .env files:

1. **Do not exploit** the information found
2. **Report responsibly** to the website owner or through proper channels
3. **Comply with laws** - unauthorized access is illegal
4. **Use ethically** - only scan domains you have permission to test

## Author

By: @username_uNique
Created for security research and educational purposes.

## Acknowledgments

Built with Python's `requests` and `concurrent.futures` libraries for high-performance concurrent HTTP operations.
