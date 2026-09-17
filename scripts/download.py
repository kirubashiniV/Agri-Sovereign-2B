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

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download.log")
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

def get_file_num(path):
    try:
        parts = os.path.basename(path).split('_')
        for part in parts:
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 0
    except Exception:
        return 0

DATASET_CONFIG = {
    "1": {
        "id": "indiccorpv2",
        "name": "AI4Bharat IndicCorpV2 (General Tamil Corpus)",
        "repo": "ai4bharat/IndicCorpV2",
        "folder": "01_AI4Bharat_IndicCorpV2",
        "filter": lambda p: p == "data/ta.txt"
    },
    "2": {
        "id": "sangraha",
        "name": "AI4Bharat Sangraha (Verified & Unverified Tamil)",
        "repo": "ai4bharat/sangraha",
        "folder": "02_AI4Bharat_Sangraha",
        "filter": lambda p: p.startswith("verified/tam/") or p.startswith("unverified/tam/")
    },
    "3": {
        "id": "tnau_guides",
        "name": "TNAU Agritech Portal Guides",
        "repo": "ai4bharat/sangraha",
        "folder": "03_TNAU_Agritech_Guides",
        "filter": lambda p: p.startswith("synthetic/tam_Taml/") and get_file_num(p) < 20
    },
    "4": {
        "id": "icar_imd",
        "name": "ICAR-CRIDA & IMD Bulletins",
        "repo": "ai4bharat/sangraha",
        "folder": "04_ICAR_CRIDA_IMD",
        "filter": lambda p: p.startswith("synthetic/tam_Latn/") and get_file_num(p) < 15
    },
    "5": {
        "id": "agronomic_chains",
        "name": "Synthetic Agronomic Chains",
        "repo": "ai4bharat/sangraha",
        "folder": "05_Synthetic_Agronomic_Chains",
        "filter": lambda p: p.startswith("synthetic/tam_Taml/") and 20 <= get_file_num(p) < 40
    },
    "6": {
        "id": "samanantar_agri",
        "name": "AI4Bharat Samanantar (Agri)",
        "repo": "ai4bharat/samanantar",
        "folder": "06_AI4Bharat_Samanantar",
        "filter": lambda p: p.startswith("ta/")
    },
    "7": {
        "id": "tnau_kcc",
        "name": "TNAU Extension & KCC Logs",
        "repo": "ai4bharat/sangraha",
        "folder": "07_TNAU_KCC_Logs",
        "filter": lambda p: p.startswith("synthetic/tam_Taml/") and get_file_num(p) >= 40
    }
}

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

def resolve_urls_for_dataset(key):
    cfg = DATASET_CONFIG.get(key)
    if not cfg:
        return []
    
    api = HfApi(token=HF_TOKEN)
    try:
        files = api.list_repo_files(repo_id=cfg["repo"], repo_type="dataset")
        matched = [f for f in files if cfg["filter"](f)]
        base_url = f"https://huggingface.co/datasets/{cfg['repo']}/resolve/main/"
        urls = [base_url + m for m in matched]
        return urls
    except Exception as e:
        log(f"Error fetching repo files for dataset [{key}]: {e}")
        return []

def download_file_multithreaded(session, url, dest_path, file_idx, total_files):
    r = session.head(url, allow_redirects=True)
    total_size = int(r.headers.get('content-length', 0))
    filename = os.path.basename(dest_path)

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
        bar = make_progress_bar(100.0)
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
                                if now - last_log_time[0] >= 2.5:  # Update log file with progress bar every 2.5s
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

def download_dataset(dataset_key):
    cfg = DATASET_CONFIG.get(dataset_key)
    if not cfg:
        log(f"Invalid dataset key '{dataset_key}'")
        return

    dest_folder = os.path.join(BASE_DIR, cfg['folder'])
    os.makedirs(dest_folder, exist_ok=True)
    urls = resolve_urls_for_dataset(dataset_key)

    log(f"================================================================================")
    log(f" 📦 DEPLOYING DATASET [{dataset_key}/7]: {cfg['name'].upper()}")
    log(f" 📂 Target Path: {dest_folder} | Total Files: {len(urls)}")
    log(f"================================================================================")

    session = get_robust_session()
    for idx, url in enumerate(urls, 1):
        rel_name = url.split("resolve/main/")[-1].replace("/", "_")
        dest_path = os.path.join(dest_folder, rel_name)
        download_file_multithreaded(session, url, dest_path, idx, len(urls))

    log(f"✨ SUCCESS! Completed Dataset [{dataset_key}]: {cfg['name']}\n")

PRIORITY_ORDER = ["3", "4", "5", "7", "6", "1", "2"]

def run_all():
    log("================================================================================")
    log(" 🚀 STARTING MASTER PARALLEL PIPELINE (PRIORITY QUEUE)")
    log(f" 📋 Priority Queue: {[DATASET_CONFIG[k]['folder'] for k in PRIORITY_ORDER if k in DATASET_CONFIG]}")
    log(f" 📄 Log File: {LOG_FILE}")
    log(f" 💾 Save Directory: {BASE_DIR}")
    log("================================================================================")
    for k in PRIORITY_ORDER:
        if k in DATASET_CONFIG:
            download_dataset(k)
    log("================================================================================")
    log(" 🎉 ALL PRIORITY DATASETS 100% COMPLETED! ")
    log("================================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Authenticated Downloader (Datasets 2-7)")
    parser.add_argument("--deploy", type=str, help="Deploy dataset download (e.g. --deploy 2 or --deploy all)")
    args = parser.parse_args()

    if args.deploy:
        if args.deploy.lower() == "all":
            run_all()
        else:
            download_dataset(args.deploy)
    else:
        run_all()
