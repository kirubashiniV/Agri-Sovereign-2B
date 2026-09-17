import os
import sys
import time
import subprocess
import glob

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(ROOT_DIR, "logs", "training.log")
CHECKPOINTS_DIR = os.path.join(ROOT_DIR, "models", "checkpoints")

def get_gpu_telemetry():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
            text=True
        )
        lines = out.strip().split("\n")
        return [l.split(",") for l in lines]
    except Exception:
        return []

def main():
    print("================================================================================")
    print(" 🖥️  PERSON 1: GPU TRAINING WATCHDOG & TELEMETRY MONITOR")
    print("================================================================================")
    
    # 1. GPU Telemetry
    gpu_stats = get_gpu_telemetry()
    if gpu_stats:
        print("GPU Telemetry:")
        for g in gpu_stats:
            if len(g) >= 4:
                idx, name, mem_used, mem_total = g[0].strip(), g[1].strip(), g[2].strip(), g[3].strip()
                print(f"  • GPU {idx}: {name} | VRAM: {mem_used} MiB / {mem_total} MiB")
                
    # 2. Checkpoints
    checkpoints = glob.glob(os.path.join(CHECKPOINTS_DIR, "checkpoint-*"))
    print(f"\nSaved Checkpoints ({len(checkpoints)}):")
    if checkpoints:
        for ckpt in sorted(checkpoints, key=os.path.getmtime):
            size_mb = sum(os.path.getsize(os.path.join(ckpt, f)) for f in os.listdir(ckpt) if os.path.isfile(os.path.join(ckpt, f))) / (1024 * 1024)
            print(f"  • {os.path.basename(ckpt)} ({size_mb:.1f} MB)")
    else:
        print("  • None yet (saving every 250 steps)")
        
    # 3. Recent Training Loss Logs
    print(f"\nRecent Training Logs ({LOG_FILE}):")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-15:]:
                print("  " + line.strip())
    else:
        print("  • No logs found yet.")
        
    print("================================================================================")

if __name__ == "__main__":
    main()
