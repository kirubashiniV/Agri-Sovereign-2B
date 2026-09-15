"""
Inspect Parquet Datasets from Windows Partition
Agri-Sovereign / Uzhavan-Sahayak Platform
"""

import os
import glob

DATASET_ROOT = "/media/Windows-SSD/Users/Pavithran/dataset download"

def inspect_datasets():
    print("=" * 85)
    print("                    DATASET INVENTORY INSPECTION (TNAU / INDIC)")
    print("=" * 85)
    
    dirs = [
        "01_AI4Bharat_IndicCorpV2",
        "02_AI4Bharat_Sangraha",
        "03_TNAU_Agritech_Guides",
        "04_ICAR_CRIDA_IMD",
        "05_Synthetic_Agronomic_Chains",
        "06_AI4Bharat_Samanantar",
        "07_TNAU_KCC_Logs"
    ]
    
    for d in dirs:
        full_path = os.path.join(DATASET_ROOT, d)
        if os.path.exists(full_path):
            files = glob.glob(os.path.join(full_path, "*"))
            total_size_mb = sum(os.path.getsize(f) for f in files if os.path.isfile(f)) / (1024 * 1024)
            print(f"📁 {d:<32} | {len(files):>3} files | {total_size_mb:>10.2f} MB")
        else:
            print(f"❌ {d:<32} | Not found")
    print("=" * 85)

if __name__ == "__main__":
    inspect_datasets()
