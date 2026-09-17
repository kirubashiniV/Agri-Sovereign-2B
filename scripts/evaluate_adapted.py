import os
import sys
import json
import time
import datetime
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_MODEL_PATH = os.path.join(ROOT_DIR, "models", "base_checkpoint")
ADAPTER_PATH = os.path.join(ROOT_DIR, "models", "final_adapter")
BENCHMARK_FILE = os.path.join(ROOT_DIR, "evaluation", "benchmark_25.json")
OUTPUT_FILE = os.path.join(ROOT_DIR, "evaluation", "adapted.json")

def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def find_latest_checkpoint():
    if os.path.exists(os.path.join(ADAPTER_PATH, "adapter_model.safetensors")):
        return ADAPTER_PATH
    checkpoints_dir = os.path.join(ROOT_DIR, "models", "checkpoints")
    if os.path.exists(checkpoints_dir):
        checkpoints = [
            os.path.join(checkpoints_dir, d) for d in os.listdir(checkpoints_dir)
            if d.startswith("checkpoint-")
        ]
        if checkpoints:
            checkpoints.sort(key=lambda x: int(x.split("-")[-1]))
            return checkpoints[-1]
    return ADAPTER_PATH

def main():
    log("================================================================================")
    log(" 🧪 PERSON 1: HIGH-THROUGHPUT EVALUATION OF ADAPTED MODEL (25-Q BENCHMARK)")
    log("================================================================================")
    
    adapter_to_use = find_latest_checkpoint()
    log(f"📁 Base Model: {BASE_MODEL_PATH}")
    log(f"🎯 Adapter Path: {adapter_to_use}")
    log(f"📄 Benchmark: {BENCHMARK_FILE}")
    log(f"💾 Output File: {OUTPUT_FILE}")
    
    if not os.path.exists(BENCHMARK_FILE):
        log(f"❌ Benchmark file missing: {BENCHMARK_FILE}")
        sys.exit(1)
        
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)
        
    questions = benchmark_data if isinstance(benchmark_data, list) else benchmark_data.get("questions", [])
    log(f"📋 Loaded {len(questions)} Frozen Benchmark Questions.")
    
    # 1. Load Tokenizer & Base Model on GPU in Native BF16 with SDPA
    log("\n[1/3] Loading Tokenizer and Base Model in Native BF16 with SDPA...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_PATH,
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map="cuda:0"
    )
    base_model.config.use_cache = True
    log(f"✅ Base Model Loaded in {time.time()-t0:.2f}s")
    
    # 2. Attach PEFT LoRA Adapter
    log(f"\n[2/3] Attaching LoRA Adapter from: {adapter_to_use}...")
    t_lora = time.time()
    model = PeftModel.from_pretrained(base_model, adapter_to_use)
    model.config.use_cache = True
    model.eval()
    log(f"✅ LoRA Adapter Attached Successfully in {time.time()-t_lora:.2f}s!")

    # 3. Batch Benchmark Execution
    log("\n[3/3] 🚀 Executing Parallel Batch Benchmark (Batch Size = 25)...")
    log("--------------------------------------------------------------------------------")
    
    system_prompt = (
        "நீங்கள் தமிழ்நாடு வேளாண்மை பல்கலைக்கழகம் (TNAU) மற்றும் இந்திய வேளாண் ஆராய்ச்சி கழகம் (ICAR) "
        "சான்றளிக்கப்பட்ட முதன்மை வேளாண்மை ஆலோசகர். விவசாயிகளுக்கு தூய தமிழில் துல்லியமான 5-பிரிவு தீர்வு வழங்கவும்."
    )
    
    prompts = []
    for q in questions:
        question_ta = q.get("question_ta", q.get("question", ""))
        prompts.append(f"<s>[INST] {system_prompt}\n\n{question_ta} [/INST]")
        
    inputs = tokenizer(prompts, padding=True, return_tensors="pt").to("cuda:0")
    
    t_start = time.time()
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=350,
            do_sample=False,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id
        )
    total_latency = time.time() - t_start
    
    results = []
    total_tokens = 0
    
    input_length = inputs["input_ids"].shape[1]
    for i, q in enumerate(questions):
        q_id = q.get("id", f"AGRI-{i+1:02d}")
        category = q.get("category", "General")
        question_ta = q.get("question_ta", q.get("question", ""))
        expected = q.get("reference_summary", q.get("expected_reference", q.get("expected_answer", "")))
        
        gen_tokens = output_ids[i][input_length:]
        response_ta = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        num_tokens = len(gen_tokens)
        total_tokens += num_tokens
        
        log(f"[{i+1:02d}/25] {q_id} | {category[:20]} | {num_tokens} tokens")
        
        results.append({
            "id": q_id,
            "category": category,
            "question_ta": question_ta,
            "expected_reference": expected,
            "adapted_response_ta": response_ta,
            "tokens_generated": num_tokens,
            "latency_seconds": round(total_latency / len(questions), 3),
            "tokens_per_second": round(num_tokens / (total_latency / len(questions)), 1) if total_latency > 0 else 0
        })
        
    avg_speed = total_tokens / total_latency if total_latency > 0 else 0
    
    eval_artifact = {
        "timestamp": datetime.datetime.now().isoformat(),
        "model_evaluated": "Ministral-8B + Agri-LoRA (Adapted)",
        "adapter_path": adapter_to_use,
        "precision": "bfloat16",
        "gpu": torch.cuda.get_device_name(0),
        "total_questions": len(results),
        "total_tokens": total_tokens,
        "total_latency_seconds": round(total_latency, 2),
        "avg_tokens_per_second": round(avg_speed, 1),
        "results": results
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(eval_artifact, f, indent=2, ensure_ascii=False)
        
    log("================================================================================")
    log(f"✅ Adapted Evaluation Complete! Results saved to: {OUTPUT_FILE}")
    log(f"📊 Total Latency: {total_latency:.2f}s across 25 questions | Throughput: {avg_speed:.1f} tok/s")
    log("================================================================================")

if __name__ == "__main__":
    main()
