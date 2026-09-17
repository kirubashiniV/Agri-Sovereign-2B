import os
import sys
import time
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "base_checkpoint")
BENCHMARK_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation", "benchmark_25.json")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation", "baseline.json")

def main():
    print("=" * 80)
    print(" 🚀 STEP 1: BASE MODEL SMOKE TEST & ZERO-HOUR BASELINE BENCHMARK")
    print("=" * 80)

    # 1. Hardware Check
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    total_vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3) if torch.cuda.is_available() else 0
    print(f"Target GPU: {gpu_name} ({total_vram:.2f} GB VRAM)")
    
    # 2. Load Model & Tokenizer
    print(f"\n[1/3] Loading Tokenizer & Model from: {MODEL_PATH}")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.bfloat16,
        device_map="cuda:0"
    )
    load_time = time.time() - t0
    param_count = sum(p.numel() for p in model.parameters()) / 1e9
    vram_after_load = torch.cuda.memory_allocated(0) / (1024 ** 3)
    print(f"✅ Model Loaded Successfully in {load_time:.2f}s!")
    print(f"📊 Total Parameters: {param_count:.2f} Billion")
    print(f"💾 VRAM Allocated: {vram_after_load:.2f} GB / {total_vram:.2f} GB")

    # 3. Smoke Test
    print("\n[2/3] Running Tamil Inference Smoke Test...")
    smoke_msg = [{"role": "user", "content": "விவசாயத்தில் இயற்கை உரம் இடுவதால் ஏற்படும் நன்மைகள் என்ன?"}]
    smoke_inputs = tokenizer.apply_chat_template(smoke_msg, tokenize=True, return_tensors="pt", return_dict=True).to("cuda:0")
    
    t_gen = time.time()
    with torch.no_grad():
        smoke_out = model.generate(
            **smoke_inputs,
            max_new_tokens=100,
            temperature=0.4,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    gen_time = time.time() - t_gen
    smoke_text = tokenizer.decode(smoke_out[0][smoke_inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    print(f"Smoke Output:\n{smoke_text[:200]}...")
    print(f"Smoke Latency: {gen_time*1000:.1f} ms")

    # 4. Run Benchmark
    print("\n[3/3] Running Frozen 25-Question Benchmark against Unadapted Base Model...")
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    results = []
    total_tokens_generated = 0
    total_latency_ms = 0

    print("-" * 80)
    for idx, item in enumerate(benchmark_data, 1):
        q_id = item["id"]
        category = item["category"]
        question = item["question"]
        ref = item["reference_summary"]

        messages = [
            {"role": "user", "content": f"நீங்கள் ஒரு வேளாண்மை நிபுணர். இந்த கேள்விக்கு தமிழில் துல்லியமான விடை அளியுங்கள்: {question}"}
        ]
        inputs = tokenizer.apply_chat_template(messages, tokenize=True, return_tensors="pt", return_dict=True).to("cuda:0")
        prompt_tokens = inputs.input_ids.shape[1]

        torch.cuda.synchronize()
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=250,
                temperature=0.3,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        torch.cuda.synchronize()
        latency_ms = (time.time() - start_time) * 1000

        gen_tokens = outputs.shape[1] - prompt_tokens
        response_text = tokenizer.decode(outputs[0][prompt_tokens:], skip_special_tokens=True).strip()

        tok_per_sec = (gen_tokens / (latency_ms / 1000)) if latency_ms > 0 else 0
        total_tokens_generated += gen_tokens
        total_latency_ms += latency_ms

        result_entry = {
            "id": q_id,
            "category": category,
            "question": question,
            "base_response": response_text,
            "reference_summary": ref,
            "prompt_tokens": prompt_tokens,
            "generated_tokens": gen_tokens,
            "latency_ms": round(latency_ms, 2),
            "tokens_per_sec": round(tok_per_sec, 2),
            "severity": item.get("severity", "Normal")
        }
        results.append(result_entry)
        print(f"[{idx:02d}/25] [{q_id}] ({category:<22s}) | {gen_tokens:>3d} tokens in {latency_ms:>6.1f} ms ({tok_per_sec:>4.1f} tok/s)")

    # 5. Save Output
    peak_vram_gb = torch.cuda.max_memory_allocated(0) / (1024 ** 3)
    avg_latency = total_latency_ms / len(results) if results else 0
    avg_tok_sec = (total_tokens_generated / (total_latency_ms / 1000)) if total_latency_ms > 0 else 0

    benchmark_summary = {
        "model": "mistralai/Ministral-8B-Instruct-2410",
        "model_type": "Unadapted Base 8B",
        "precision": "bfloat16",
        "gpu": gpu_name,
        "total_parameters_b": round(param_count, 2),
        "load_time_sec": round(load_time, 2),
        "base_vram_gb": round(vram_after_load, 2),
        "peak_vram_gb": round(peak_vram_gb, 2),
        "total_questions": len(results),
        "total_tokens_generated": total_tokens_generated,
        "avg_latency_ms": round(avg_latency, 2),
        "avg_throughput_tok_per_sec": round(avg_tok_sec, 2),
        "results": results
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"✅ STEP 1 BASELINE BENCHMARK COMPLETE!")
    print(f"📁 Saved: {OUTPUT_PATH}")
    print(f"📊 Avg Latency: {avg_latency:.2f} ms | Throughput: {avg_tok_sec:.2f} tok/s | Peak VRAM: {peak_vram_gb:.2f} GB")
    print("=" * 80)

if __name__ == "__main__":
    main()
