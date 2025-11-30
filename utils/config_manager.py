"""
Configuration Manager

Handles saving and loading of application configuration.
"""

import json
import os
from typing import Any, Dict, Optional
from threading import Lock


class ConfigManager:
    """Manages application configuration with file persistence."""
    
    DEFAULT_CONFIG = {
        # Scanner settings
        'max_threads': 50,
        'timeout': 5,
        'request_delay': 0.1,
        'retry_attempts': 3,
        'output_directory': './results',
        'auto_save': True,
        
        # AWS settings
        'aws_regions': [],
        'aws_services': ['EC2'],
        'max_ips_per_cidr': 256,
        
        # GUI settings
        'theme': 'golden',
        'dark_mode': True,
        'window_width': 1200,
        'window_height': 800,
        'log_console_visible': True,
        'auto_scroll_logs': True,
        'alert_sounds': True,
        'desktop_notifications': True,
        
        # Recent files
        'recent_domain_files': [],
        'last_domain_file': '',
        
        # Session state
        'last_scan_mode': 'domain_list',
    }
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._lock = Lock()
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file."""
        with self._lock:
            self._config = self.DEFAULT_CONFIG.copy()
            
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r') as f:
                        saved_config = json.load(f)
                        # Merge saved config with defaults
                        self._config.update(saved_config)
                except (json.JSONDecodeError, IOError):
                    pass  # Use defaults on error
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if save was successful, False otherwise
        """
        with self._lock:
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self._config, f, indent=2)
                return True
            except IOError:
                return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        with self._lock:
            return self._config.get(key, default)
    
    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
            auto_save: If True, automatically save after setting
        """
        with self._lock:
            self._config[key] = value
        
        if auto_save:
            self.save()
    
    def update(self, config: Dict[str, Any], auto_save: bool = True) -> None:
        """
        Update multiple configuration values.
        
        Args:
            config: Dictionary of configuration values
            auto_save: If True, automatically save after updating
        """
        with self._lock:
            self._config.update(config)
        
        if auto_save:
            self.save()
    
    def reset(self, auto_save: bool = True) -> None:
        """
        Reset configuration to defaults.
        
        Args:
            auto_save: If True, automatically save after resetting
        """
        with self._lock:
            self._config = self.DEFAULT_CONFIG.copy()
        
        if auto_save:
            self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Copy of all configuration values
        """
        with self._lock:
            return self._config.copy()
    
    def add_recent_file(self, filepath: str, max_recent: int = 10) -> None:
        """
        Add a file to the recent files list.
        
        Args:
            filepath: Path to add
            max_recent: Maximum number of recent files to keep
        """
        with self._lock:
            recent = self._config.get('recent_domain_files', [])
            
            # Remove if already exists
            if filepath in recent:
                recent.remove(filepath)
            
            # Add to front
            recent.insert(0, filepath)
            
            # Trim to max
            self._config['recent_domain_files'] = recent[:max_recent]
            self._config['last_domain_file'] = filepath
        
        self.save()


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get or create the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
