"""
Domain Scanner Module

Scanner implementation for domain list scanning.
"""

import os
from typing import Generator, Optional, List, Callable
from .scanner_core import ScannerCore, ScanResult, ScanStats, ScannerState


class DomainScanner(ScannerCore):
    """Scanner for domain lists."""
    
    def __init__(self, **kwargs):
        """Initialize the domain scanner."""
        super().__init__(**kwargs)
        self._domains_file: Optional[str] = None
        self._domains_list: List[str] = []
        self._total_domains: int = 0
    
    def load_domains_from_file(self, filepath: str) -> int:
        """
        Load domains from a file.
        
        Args:
            filepath: Path to file containing domains (one per line)
            
        Returns:
            Number of domains loaded
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        self._domains_file = filepath
        self._domains_list = []
        self._total_domains = 0
        
        # Count lines for progress tracking
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip():
                    self._total_domains += 1
        
        return self._total_domains
    
    def load_domains_from_list(self, domains: List[str]) -> int:
        """
        Load domains from a list.
        
        Args:
            domains: List of domain strings
            
        Returns:
            Number of domains loaded
        """
        self._domains_file = None
        self._domains_list = [d.strip() for d in domains if d.strip()]
        self._total_domains = len(self._domains_list)
        return self._total_domains
    
    def _domain_generator(self) -> Generator[str, None, None]:
        """Generate domains from file or list."""
        if self._domains_file:
            with open(self._domains_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    domain = line.strip()
                    if domain:
                        yield domain
        else:
            for domain in self._domains_list:
                yield domain
    
    def start_scan(self) -> None:
        """Start scanning the loaded domains."""
        if self._total_domains == 0:
            raise ValueError("No domains loaded. Call load_domains_from_file or load_domains_from_list first.")
        
        self.scan(
            targets=self._domain_generator(),
            total_targets=self._total_domains,
            infinite=False
        )
    
    def scan_single_domain(self, domain: str) -> ScanResult:
        """
        Scan a single domain synchronously.
        
        Args:
            domain: Domain to scan
            
        Returns:
            ScanResult object
        """
        return self._process_target(domain)
    
    @property
    def total_domains(self) -> int:
        """Get total number of domains loaded."""
        return self._total_domains
