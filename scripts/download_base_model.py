import os
import sys
import mmap
import time
import argparse
import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from huggingface_hub import HfApi
from tqdm import tqdm
import threading

HF_TOKEN = os.environ.get("HF_TOKEN", "")
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN

MODEL_ID = "mistralai/Ministral-8B-Instruct-2410"
DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "base_checkpoint")
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "download_model.log")

NUM_THREADS = 24  # 24 parallel worker streams
CHUNK_BLOCK_SIZE = 16 * 1024 * 1024  # 16MB dynamic range chunks
BUFFER_SIZE = 2 * 1024 * 1024  # 2MB stream buffer

log_lock = threading.Lock()

def make_progress_bar(pct, width=25):
    filled = int(width * pct / 100)
    filled = max(0, min(width, filled))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"

def log(msg, to_console=True):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now}] {msg}"
    if to_console:
        print(formatted, flush=True)
    with log_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
            f.flush()

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"

def format_time(seconds):
    if seconds < 0 or seconds > 86400 * 7:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m:02d}m {s:02d}s"

def get_robust_session():
    session = requests.Session()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    session.headers.update(headers)
    retries = Retry(
        total=10,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=32, pool_maxsize=32)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def download_file_multithreaded(session, url, dest_path, file_idx, total_files):
    r = session.head(url, allow_redirects=True)
    total_size = int(r.headers.get('content-length', 0))
    filename = os.path.basename(dest_path)

    # For tiny files (< 5MB), download directly
    if total_size < 5 * 1024 * 1024:
        log(f"[{file_idx:02d}/{total_files:02d}] Downloading config file: {filename} ({format_size(total_size)})")
        res = session.get(url, stream=True)
        res.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024*64):
                if chunk:
                    f.write(chunk)
        bar_full = make_progress_bar(100.0, width=20)
        log(f"[{file_idx:02d}/{total_files:02d}] {bar_full} 100.0% | [SAVED] {filename}")
        return

    if not os.path.exists(dest_path):
        with open(dest_path, "wb") as f:
            f.truncate(total_size)
    elif os.path.getsize(dest_path) != total_size:
        with open(dest_path, "r+b") as f:
            f.truncate(total_size)

    missing_chunks = []
    existing_bytes = 0
    with open(dest_path, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for start in range(0, total_size, CHUNK_BLOCK_SIZE):
                end = min(start + CHUNK_BLOCK_SIZE - 1, total_size - 1)
                if mm[start:start+1024] != b'\x00' * 1024 and mm[end-1024:end+1] != b'\x00' * 1024:
                    existing_bytes += (end - start + 1)
                else:
                    missing_chunks.append((start, end))

    if existing_bytes >= total_size:
        bar = make_progress_bar(100.0, width=20)
        log(f"[{file_idx:02d}/{total_files:02d}] {bar} 100.0% | [SKIP] {filename} (Already Downloaded - {format_size(total_size)})")
        return

    log(f"[{file_idx:02d}/{total_files:02d}] [START] {filename} ({format_size(total_size)}, {len(missing_chunks)} chunks)")

    pbar = tqdm(total=total_size, initial=existing_bytes, unit="iB", unit_scale=True, desc=f" {filename} ({NUM_THREADS} Streams)")

    downloaded_lock = threading.Lock()
    current_downloaded = [existing_bytes]
    start_time = time.time()
    last_log_time = [time.time()]

    def fetch_chunk_with_retry(chunk_tuple):
        start, end = chunk_tuple
        headers = {"Range": f"bytes={start}-{end}"}
        
        for attempt in range(5):
            try:
                resp = session.get(url, headers=headers, stream=True, timeout=30)
                resp.raise_for_status()
                with open(dest_path, "r+b") as f:
                    f.seek(start)
                    for block in resp.iter_content(chunk_size=BUFFER_SIZE):
                        if block:
                            f.write(block)
                            pbar.update(len(block))
                            with downloaded_lock:
                                current_downloaded[0] += len(block)
                                now = time.time()
                                if now - last_log_time[0] >= 2.5:
                                    elapsed = now - start_time
                                    bytes_so_far = current_downloaded[0]
                                    pct = (bytes_so_far / total_size * 100) if total_size > 0 else 0
                                    speed = (bytes_so_far - existing_bytes) / elapsed if elapsed > 0 else 0
                                    rem_bytes = max(0, total_size - bytes_so_far)
                                    eta = (rem_bytes / speed) if speed > 0 else 0
                                    bar = make_progress_bar(pct, width=20)
                                    log_str = (
                                        f"[{file_idx:02d}/{total_files:02d}] {bar} {pct:5.1f}% | "
                                        f"{format_size(bytes_so_far):>9s} / {format_size(total_size):<9s} | "
                                        f"⚡ {format_size(speed):>8s}/s | ⏱️ ETA: {format_time(eta):>8s} | {filename}"
                                    )
                                    log(log_str, to_console=False)
                                    last_log_time[0] = now
                return start
            except Exception:
                if attempt == 4:
                    return None
                time.sleep(1)
        return None

    if missing_chunks:
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = [executor.submit(fetch_chunk_with_retry, c) for c in missing_chunks]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass

    pbar.close()
    elapsed_total = time.time() - start_time
    avg_speed = (total_size - existing_bytes) / elapsed_total if elapsed_total > 0 else 0
    bar_full = make_progress_bar(100.0, width=20)
    log(f"[{file_idx:02d}/{total_files:02d}] {bar_full} 100.0% | [COMPLETED] {filename} ({format_size(total_size)}) in {format_time(elapsed_total)} @ {format_size(avg_speed)}/s")

def download_model():
    os.makedirs(DEST_DIR, exist_ok=True)
    api = HfApi(token=HF_TOKEN)
    files = api.list_repo_files(repo_id=MODEL_ID)
    
    # Filter only relevant weights and config files (exclude consolidated if sharded safetensors present)
    target_files = [
        f for f in files if not f.startswith(".") and f != "consolidated.safetensors" and f != "README.md" and f != "passkey_example.json"
    ]

    log("================================================================================")
    log(f" 🚀 DOWNLOADING BASE MODEL: {MODEL_ID}")
    log(f" 📂 Target Directory: {DEST_DIR}")
    log(f" 📄 Log File: {LOG_FILE}")
    log(f" 📦 Total Files: {len(target_files)}")
    log("================================================================================")

    session = get_robust_session()
    base_url = f"https://huggingface.co/{MODEL_ID}/resolve/main/"
    
    for idx, fname in enumerate(target_files, 1):
        url = base_url + fname
        dest_path = os.path.join(DEST_DIR, fname)
        download_file_multithreaded(session, url, dest_path, idx, len(target_files))

    log("================================================================================")
    log(" 🎉 BASE MODEL DOWNLOAD 100% COMPLETED AND READY FOR TRAINING!")
    log("================================================================================")

if __name__ == "__main__":
    download_model()
