"""
Prepare Unified Training Dataset (CPT + SFT Instruction Tuning)
Agri-Sovereign / Uzhavan-Sahayak Platform
"""

import json
import os

def build_training_set():
    os.makedirs("data", exist_ok=True)
    all_examples = []
    
    # 1. Load SFT Instruction Templates
    sft_path = "data/uzhavan_agri_sft_train.jsonl"
    if os.path.exists(sft_path):
        with open(sft_path, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line.strip())
                formatted = f"<|im_start|>system\nநீங்கள் தமிழ்நாட்டின் முதன்மையான வேளாண் AI உதவியாளர் (Agri-Sovereign).<|im_end|>\n<|im_start|>user\n{item['instruction']} ({item.get('input','')})<|im_end|>\n<|im_start|>assistant\n{item['output']}<|im_end|>"
                all_examples.append({"text": formatted})

    # 2. Load CPT Filtered Agricultural Corpus
    corpus_path = "data/agri_filtered_corpus.jsonl"
    if os.path.exists(corpus_path):
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line.strip())
                text = item["text"].strip()
                if text:
                    formatted = f"<|im_start|>system\nவேளாண் அறிவுக்களஞ்சியம் (TNAU Agronomy Documentation)<|im_end|>\n<|im_start|>text\n{text}<|im_end|>"
                    all_examples.append({"text": formatted})

    out_path = "data/agri_sovereign_full_train.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
            
    print(f"✔ Unified Training Dataset Generated: {out_path} ({len(all_examples)} training sequences)")

if __name__ == "__main__":
    build_training_set()
