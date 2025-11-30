"""
AWS IP Range Fetcher

Fetches and parses AWS IP ranges from the official AWS IP ranges JSON file.
Supports filtering by region and service type.
"""

import json
import os
import random
import time
import ipaddress
from typing import List, Dict, Generator, Optional, Set
import requests
from threading import Lock


class AWSIPFetcher:
    """Fetches and manages AWS IP ranges."""
    
    AWS_IP_RANGES_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    CACHE_FILE = "aws_ip_ranges_cache.json"
    CACHE_EXPIRY_HOURS = 24
    
    # Common AWS services
    SERVICES = [
        "AMAZON",
        "AMAZON_APPFLOW",
        "AMAZON_CONNECT",
        "API_GATEWAY",
        "CHIME_MEETINGS",
        "CHIME_VOICECONNECTOR",
        "CLOUD9",
        "CLOUDFRONT",
        "CLOUDFRONT_ORIGIN_FACING",
        "CODEBUILD",
        "DYNAMODB",
        "EBS",
        "EC2",
        "EC2_INSTANCE_CONNECT",
        "GLOBALACCELERATOR",
        "IVS_REALTIME",
        "KINESIS_VIDEO_STREAMS",
        "MEDIA_PACKAGE_V2",
        "ROUTE53",
        "ROUTE53_HEALTHCHECKS",
        "ROUTE53_HEALTHCHECKS_PUBLISHING",
        "ROUTE53_RESOLVER",
        "S3",
        "WORKSPACES_GATEWAYS"
    ]
    
    # AWS Regions
    REGIONS = [
        "af-south-1",
        "ap-east-1",
        "ap-northeast-1",
        "ap-northeast-2",
        "ap-northeast-3",
        "ap-south-1",
        "ap-south-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-southeast-3",
        "ap-southeast-4",
        "ca-central-1",
        "ca-west-1",
        "cn-north-1",
        "cn-northwest-1",
        "eu-central-1",
        "eu-central-2",
        "eu-north-1",
        "eu-south-1",
        "eu-south-2",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "il-central-1",
        "me-central-1",
        "me-south-1",
        "sa-east-1",
        "us-east-1",
        "us-east-2",
        "us-gov-east-1",
        "us-gov-west-1",
        "us-west-1",
        "us-west-2",
        "GLOBAL"
    ]
    
    def __init__(self, cache_dir: str = "."):
        """
        Initialize the AWS IP Fetcher.
        
        Args:
            cache_dir: Directory to store the cache file
        """
        self.cache_dir = cache_dir
        self.cache_path = os.path.join(cache_dir, self.CACHE_FILE)
        self._data: Optional[Dict] = None
        self._lock = Lock()
        self._ip_count_cache: Dict[str, int] = {}
    
    def fetch_ip_ranges(self, force_refresh: bool = False) -> Dict:
        """
        Fetch AWS IP ranges from the official source.
        
        Args:
            force_refresh: If True, ignore cache and fetch fresh data
            
        Returns:
            Dictionary containing AWS IP ranges
        """
        with self._lock:
            # Check cache first
            if not force_refresh:
                cached_data = self._load_cache()
                if cached_data:
                    self._data = cached_data
                    return cached_data
            
            # Fetch from AWS
            try:
                response = requests.get(
                    self.AWS_IP_RANGES_URL,
                    timeout=30,
                    headers={'User-Agent': 'AWS-IP-Fetcher/1.0'}
                )
                response.raise_for_status()
                data = response.json()
                
                # Save to cache
                self._save_cache(data)
                self._data = data
                return data
                
            except requests.RequestException as e:
                # Try to load from cache even if expired
                cached_data = self._load_cache(ignore_expiry=True)
                if cached_data:
                    self._data = cached_data
                    return cached_data
                raise Exception(f"Failed to fetch AWS IP ranges: {e}")
    
    def _load_cache(self, ignore_expiry: bool = False) -> Optional[Dict]:
        """Load cached IP ranges if available and not expired."""
        if not os.path.exists(self.cache_path):
            return None
        
        try:
            with open(self.cache_path, 'r') as f:
                cache_data = json.load(f)
            
            if not ignore_expiry:
                cache_time = cache_data.get('cache_time', 0)
                if time.time() - cache_time > self.CACHE_EXPIRY_HOURS * 3600:
                    return None
            
            return cache_data.get('data')
            
        except (json.JSONDecodeError, IOError):
            return None
    
    def _save_cache(self, data: Dict) -> None:
        """Save IP ranges to cache."""
        try:
            cache_data = {
                'cache_time': time.time(),
                'data': data
            }
            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f)
        except IOError:
            pass  # Cache save failure is not critical
    
    def get_prefixes(
        self,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        ipv6: bool = False
    ) -> List[Dict]:
        """
        Get IP prefixes filtered by region and service.
        
        Args:
            regions: List of AWS regions to filter (None for all)
            services: List of AWS services to filter (None for all)
            ipv6: If True, return IPv6 prefixes instead of IPv4
            
        Returns:
            List of prefix dictionaries
        """
        if self._data is None:
            self.fetch_ip_ranges()
        
        prefix_key = 'ipv6_prefixes' if ipv6 else 'prefixes'
        ip_prefix_key = 'ipv6_prefix' if ipv6 else 'ip_prefix'
        
        prefixes = self._data.get(prefix_key, [])
        
        # Filter by region
        if regions:
            regions_set = set(regions)
            prefixes = [p for p in prefixes if p.get('region') in regions_set]
        
        # Filter by service
        if services:
            services_set = set(services)
            prefixes = [p for p in prefixes if p.get('service') in services_set]
        
        return prefixes
    
    def get_cidr_ranges(
        self,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        ipv6: bool = False
    ) -> List[str]:
        """
        Get CIDR ranges as strings.
        
        Args:
            regions: List of AWS regions to filter (None for all)
            services: List of AWS services to filter (None for all)
            ipv6: If True, return IPv6 ranges instead of IPv4
            
        Returns:
            List of CIDR range strings
        """
        prefixes = self.get_prefixes(regions, services, ipv6)
        ip_prefix_key = 'ipv6_prefix' if ipv6 else 'ip_prefix'
        
        return list(set(p[ip_prefix_key] for p in prefixes))
    
    def generate_ips(
        self,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        max_ips_per_cidr: int = 256,
        randomize: bool = True
    ) -> Generator[str, None, None]:
        """
        Generate individual IP addresses from CIDR ranges.
        
        This is a generator to avoid memory overflow with large ranges.
        
        Args:
            regions: List of AWS regions to filter (None for all)
            services: List of AWS services to filter (None for all)
            max_ips_per_cidr: Maximum IPs to generate per CIDR (for large ranges)
            randomize: If True, randomize IP selection within each CIDR
            
        Yields:
            Individual IP address strings
        """
        cidr_ranges = self.get_cidr_ranges(regions, services, ipv6=False)
        
        if randomize:
            random.shuffle(cidr_ranges)
        
        for cidr in cidr_ranges:
            try:
                network = ipaddress.ip_network(cidr, strict=False)
                
                # For very large networks, sample randomly
                num_hosts = network.num_addresses
                
                if num_hosts <= max_ips_per_cidr:
                    # Small enough to enumerate all
                    hosts = list(network.hosts())
                    if randomize:
                        random.shuffle(hosts)
                    for ip in hosts:
                        yield str(ip)
                else:
                    # Sample randomly from large network
                    if randomize:
                        seen: Set[str] = set()
                        attempts = 0
                        while len(seen) < max_ips_per_cidr and attempts < max_ips_per_cidr * 2:
                            # Generate random offset within network
                            offset = random.randint(1, num_hosts - 2)  # Avoid network/broadcast
                            ip = network.network_address + offset
                            ip_str = str(ip)
                            if ip_str not in seen:
                                seen.add(ip_str)
                                yield ip_str
                            attempts += 1
                    else:
                        # Sequential sampling
                        count = 0
                        for ip in network.hosts():
                            if count >= max_ips_per_cidr:
                                break
                            yield str(ip)
                            count += 1
                            
            except ValueError:
                continue  # Skip invalid CIDR ranges
    
    def infinite_ip_generator(
        self,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        max_ips_per_cidr: int = 256
    ) -> Generator[str, None, None]:
        """
        Generate IPs infinitely in a loop.
        
        This generator continuously yields IPs from AWS ranges,
        starting over from the beginning when exhausted.
        
        Args:
            regions: List of AWS regions to filter (None for all)
            services: List of AWS services to filter (None for all)
            max_ips_per_cidr: Maximum IPs to generate per CIDR
            
        Yields:
            Individual IP address strings (infinite loop)
        """
        while True:
            for ip in self.generate_ips(regions, services, max_ips_per_cidr, randomize=True):
                yield ip
    
    def count_ips(
        self,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None
    ) -> int:
        """
        Estimate the total number of IPs in the selected ranges.
        
        Args:
            regions: List of AWS regions to filter (None for all)
            services: List of AWS services to filter (None for all)
            
        Returns:
            Estimated total number of IP addresses
        """
        cache_key = f"{regions}_{services}"
        if cache_key in self._ip_count_cache:
            return self._ip_count_cache[cache_key]
        
        cidr_ranges = self.get_cidr_ranges(regions, services, ipv6=False)
        total = 0
        
        for cidr in cidr_ranges:
            try:
                network = ipaddress.ip_network(cidr, strict=False)
                total += network.num_addresses - 2  # Exclude network and broadcast
            except ValueError:
                continue
        
        self._ip_count_cache[cache_key] = total
        return total
    
    def get_available_regions(self) -> List[str]:
        """Get list of available AWS regions from the data."""
        if self._data is None:
            try:
                self.fetch_ip_ranges()
            except Exception:
                # Return static list if fetch fails
                return self.REGIONS.copy()
        
        if self._data is None:
            return self.REGIONS.copy()
        
        regions = set()
        for prefix in self._data.get('prefixes', []):
            regions.add(prefix.get('region', ''))
        
        return sorted(list(regions)) if regions else self.REGIONS.copy()
    
    def get_available_services(self) -> List[str]:
        """Get list of available AWS services from the data."""
        if self._data is None:
            try:
                self.fetch_ip_ranges()
            except Exception:
                # Return static list if fetch fails
                return self.SERVICES.copy()
        
        if self._data is None:
            return self.SERVICES.copy()
        
        services = set()
        for prefix in self._data.get('prefixes', []):
            services.add(prefix.get('service', ''))
        
        return sorted(list(services)) if services else self.SERVICES.copy()
    
    def get_sync_token(self) -> str:
        """Get the sync token from AWS IP ranges data."""
        if self._data is None:
            self.fetch_ip_ranges()
        return self._data.get('syncToken', '')
    
    def get_create_date(self) -> str:
        """Get the creation date of the AWS IP ranges data."""
        if self._data is None:
            self.fetch_ip_ranges()
        return self._data.get('createDate', '')


# Create a default instance for convenience
_default_fetcher: Optional[AWSIPFetcher] = None


def get_default_fetcher() -> AWSIPFetcher:
    """Get or create the default AWS IP Fetcher instance."""
    global _default_fetcher
    if _default_fetcher is None:
        _default_fetcher = AWSIPFetcher()
    return _default_fetcher
