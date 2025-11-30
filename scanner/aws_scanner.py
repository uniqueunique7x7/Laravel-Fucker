"""
AWS IP Range Scanner Module

Scanner implementation for AWS IP range scanning with infinite loop support.
"""

from typing import Generator, Optional, List, Set
from .scanner_core import ScannerCore, ScanResult, ScanStats, ScannerState
from utils.aws_ip_fetcher import AWSIPFetcher


class AWSScanner(ScannerCore):
    """Scanner for AWS IP ranges with infinite scanning support."""
    
    def __init__(self, **kwargs):
        """Initialize the AWS scanner."""
        super().__init__(**kwargs)
        self._aws_fetcher = AWSIPFetcher()
        self._selected_regions: List[str] = []
        self._selected_services: List[str] = []
        self._max_ips_per_cidr: int = 256
        self._infinite_mode: bool = False
    
    def fetch_aws_ip_ranges(self, force_refresh: bool = False) -> dict:
        """
        Fetch AWS IP ranges.
        
        Args:
            force_refresh: If True, ignore cache and fetch fresh data
            
        Returns:
            AWS IP ranges data dictionary
        """
        return self._aws_fetcher.fetch_ip_ranges(force_refresh)
    
    def get_available_regions(self) -> List[str]:
        """Get list of available AWS regions."""
        return self._aws_fetcher.get_available_regions()
    
    def get_available_services(self) -> List[str]:
        """Get list of available AWS services."""
        return self._aws_fetcher.get_available_services()
    
    def set_regions(self, regions: List[str]) -> None:
        """
        Set regions to scan.
        
        Args:
            regions: List of AWS region codes (empty for all)
        """
        self._selected_regions = regions
    
    def set_services(self, services: List[str]) -> None:
        """
        Set services to scan.
        
        Args:
            services: List of AWS service names (empty for all)
        """
        self._selected_services = services
    
    def set_max_ips_per_cidr(self, max_ips: int) -> None:
        """
        Set maximum IPs to generate per CIDR range.
        
        Args:
            max_ips: Maximum number of IPs per CIDR
        """
        self._max_ips_per_cidr = max_ips
    
    def set_infinite_mode(self, enabled: bool) -> None:
        """
        Enable or disable infinite scanning mode.
        
        Args:
            enabled: If True, scan infinitely in a loop
        """
        self._infinite_mode = enabled
    
    def get_ip_count_estimate(self) -> int:
        """
        Get estimated number of IPs in selected ranges.
        
        Returns:
            Estimated IP count
        """
        return self._aws_fetcher.count_ips(
            regions=self._selected_regions if self._selected_regions else None,
            services=self._selected_services if self._selected_services else None
        )
    
    def get_cidr_ranges(self) -> List[str]:
        """
        Get CIDR ranges for selected regions and services.
        
        Returns:
            List of CIDR range strings
        """
        return self._aws_fetcher.get_cidr_ranges(
            regions=self._selected_regions if self._selected_regions else None,
            services=self._selected_services if self._selected_services else None
        )
    
    def _ip_generator(self) -> Generator[str, None, None]:
        """Generate IPs from AWS ranges."""
        regions = self._selected_regions if self._selected_regions else None
        services = self._selected_services if self._selected_services else None
        
        if self._infinite_mode:
            for ip in self._aws_fetcher.infinite_ip_generator(
                regions=regions,
                services=services,
                max_ips_per_cidr=self._max_ips_per_cidr
            ):
                yield ip
        else:
            for ip in self._aws_fetcher.generate_ips(
                regions=regions,
                services=services,
                max_ips_per_cidr=self._max_ips_per_cidr,
                randomize=True
            ):
                yield ip
    
    def start_scan(self) -> None:
        """Start scanning AWS IP ranges."""
        # Ensure we have IP ranges
        self.fetch_aws_ip_ranges()
        
        # Get estimate for progress (only meaningful in non-infinite mode)
        total_estimate = 0 if self._infinite_mode else self.get_ip_count_estimate()
        
        self.scan(
            targets=self._ip_generator(),
            total_targets=total_estimate,
            infinite=self._infinite_mode
        )
    
    def get_aws_data_info(self) -> dict:
        """
        Get information about the current AWS IP data.
        
        Returns:
            Dictionary with sync token and create date
        """
        return {
            'sync_token': self._aws_fetcher.get_sync_token(),
            'create_date': self._aws_fetcher.get_create_date()
        }
    
    @property
    def is_infinite_mode(self) -> bool:
        """Check if infinite mode is enabled."""
        return self._infinite_mode
    
    @property
    def selected_regions(self) -> List[str]:
        """Get selected regions."""
        return self._selected_regions
    
    @property
    def selected_services(self) -> List[str]:
        """Get selected services."""
        return self._selected_services
