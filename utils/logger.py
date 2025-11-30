"""
Logger Utility

Provides logging functionality to both file and GUI console.
"""

import logging
import os
import sys
import time
from datetime import datetime
from queue import Queue
from threading import Lock
from typing import Optional, Callable, List


class LogLevel:
    """Log level constants."""
    DEBUG = 10
    INFO = 20
    SUCCESS = 25  # Custom level for successful operations
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


# Add custom log level
logging.addLevelName(LogLevel.SUCCESS, 'SUCCESS')


class LogRecord:
    """Represents a single log entry."""
    
    def __init__(self, level: int, message: str, timestamp: Optional[datetime] = None):
        self.level = level
        self.level_name = logging.getLevelName(level)
        self.message = message
        self.timestamp = timestamp or datetime.now()
    
    def __str__(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M:%S')}] [{self.level_name}] {self.message}"
    
    def to_dict(self) -> dict:
        """Convert log record to dictionary."""
        return {
            'level': self.level,
            'level_name': self.level_name,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }


class AppLogger:
    """Application logger with GUI support."""
    
    def __init__(
        self,
        name: str = "LaravelFucker",
        log_file: Optional[str] = None,
        max_queue_size: int = 10000
    ):
        """
        Initialize the application logger.
        
        Args:
            name: Logger name
            log_file: Path to log file (None for no file logging)
            max_queue_size: Maximum size of the log queue
        """
        self.name = name
        self.log_file = log_file
        self._queue: Queue = Queue(maxsize=max_queue_size)
        self._callbacks: List[Callable[[LogRecord], None]] = []
        self._lock = Lock()
        self._file_handler: Optional[logging.FileHandler] = None
        
        # Setup file logging if specified
        if log_file:
            self._setup_file_logging(log_file)
    
    def _setup_file_logging(self, log_file: str) -> None:
        """Setup file logging."""
        try:
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            self._file_handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            self._file_handler.setFormatter(formatter)
        except IOError:
            self._file_handler = None
    
    def add_callback(self, callback: Callable[[LogRecord], None]) -> None:
        """
        Add a callback to be notified of new log messages.
        
        Args:
            callback: Function that takes a LogRecord
        """
        with self._lock:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[LogRecord], None]) -> None:
        """Remove a callback."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def _log(self, level: int, message: str) -> None:
        """Internal logging method."""
        record = LogRecord(level, message)
        
        # Add to queue (non-blocking)
        try:
            self._queue.put_nowait(record)
        except:
            pass  # Queue full, drop message
        
        # Write to file if configured
        if self._file_handler:
            try:
                log_record = logging.LogRecord(
                    name=self.name,
                    level=level,
                    pathname="",
                    lineno=0,
                    msg=message,
                    args=(),
                    exc_info=None
                )
                self._file_handler.emit(log_record)
            except:
                pass
        
        # Notify callbacks
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback(record)
                except:
                    pass
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, message)
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, message)
    
    def success(self, message: str) -> None:
        """Log a success message."""
        self._log(LogLevel.SUCCESS, message)
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, message)
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self._log(LogLevel.ERROR, message)
    
    def critical(self, message: str) -> None:
        """Log a critical message."""
        self._log(LogLevel.CRITICAL, message)
    
    def get_logs(self, count: int = 100) -> List[LogRecord]:
        """
        Get recent log records from the queue.
        
        Args:
            count: Maximum number of records to retrieve
            
        Returns:
            List of LogRecord objects
        """
        logs = []
        while len(logs) < count:
            try:
                logs.append(self._queue.get_nowait())
            except:
                break
        return logs
    
    def clear_queue(self) -> None:
        """Clear the log queue."""
        while True:
            try:
                self._queue.get_nowait()
            except:
                break
    
    def set_log_file(self, log_file: str) -> None:
        """Change the log file."""
        if self._file_handler:
            self._file_handler.close()
        self._setup_file_logging(log_file)
    
    def save_logs_to_file(self, filepath: str, logs: List[LogRecord]) -> bool:
        """
        Save log records to a file.
        
        Args:
            filepath: Path to save file
            logs: List of log records
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for log in logs:
                    f.write(str(log) + '\n')
            return True
        except IOError:
            return False
    
    def close(self) -> None:
        """Close the logger and release resources."""
        if self._file_handler:
            self._file_handler.close()
            self._file_handler = None


# Global logger instance
_app_logger: Optional[AppLogger] = None


def get_logger() -> AppLogger:
    """Get or create the global application logger."""
    global _app_logger
    if _app_logger is None:
        # Create logs directory
        if not os.path.exists('logs'):
            try:
                os.makedirs('logs')
            except:
                pass
        
        log_file = f"logs/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        _app_logger = AppLogger(log_file=log_file)
    return _app_logger
