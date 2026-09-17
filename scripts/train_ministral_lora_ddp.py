import os
import sys
import json
import time
import datetime
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, TaskType

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT_DIR, "models", "base_checkpoint")
TRAIN_FILE = os.path.join(ROOT_DIR, "data", "final_training.jsonl")
VAL_FILE = os.path.join(ROOT_DIR, "data", "final_validation.jsonl")
OUTPUT_DIR = os.path.join(ROOT_DIR, "models", "checkpoints")
FINAL_ADAPTER_DIR = os.path.join(ROOT_DIR, "models", "final_adapter")
LOG_FILE = os.path.join(ROOT_DIR, "logs", "training.log")

local_rank = int(os.environ.get("LOCAL_RANK", 0))
world_size = int(os.environ.get("WORLD_SIZE", 1))

def log(msg):
    if local_rank == 0:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{now}] {msg}"
        print(formatted, flush=True)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
            f.flush()

def get_latest_checkpoint(checkpoint_dir):
    if not os.path.exists(checkpoint_dir):
        return None
    checkpoints = [
        os.path.join(checkpoint_dir, d)
        for d in os.listdir(checkpoint_dir)
        if d.startswith("checkpoint-") and os.path.isdir(os.path.join(checkpoint_dir, d))
    ]
    if not checkpoints:
        return None
    checkpoints.sort(key=lambda x: int(x.split("-")[-1]) if x.split("-")[-1].isdigit() else 0)
    return checkpoints[-1]

def main():
    log("================================================================================")
    log(f" 🚀 STEP 3: DISTRIBUTED LoRA TRAINING (MINISTRAL-8B) ON {world_size} GPUs")
    log("================================================================================")
    
    device = torch.device(f"cuda:{local_rank}" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        torch.cuda.set_device(device)
        gpu_name = torch.cuda.get_device_name(device)
        free_mem, total_mem = torch.cuda.mem_get_info(device)
        log(f"🖥️  Rank {local_rank}/{world_size} initialized on {device} ({gpu_name}) - {free_mem/(1024**3):.2f} GB Free")

    # 1. Tokenizer & Base Model Loading
    log(f"\n[1/5] Loading Tokenizer and Base Model on Rank {local_rank} in Native BF16...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map=None  # Handled by DDP
    )
    model.to(device)
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    
    base_vram = torch.cuda.memory_allocated(device) / (1024 ** 3) if torch.cuda.is_available() else 0
    log(f"✅ Base Model Loaded in {time.time()-t0:.2f}s | VRAM Allocated: {base_vram:.2f} GB")

    # 2. LoRA Configuration
    log("\n[2/5] Initializing LoRA Adapter Configuration...")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    model = get_peft_model(model, peft_config)
    trainable_params, all_params = model.get_nb_trainable_parameters()
    pct = (trainable_params / all_params) * 100
    log(f"📊 Trainable Parameters: {trainable_params:,} / {all_params:,} ({pct:.3f}%)")

    # 3. Tokenize Datasets with Label Masking
    log("\n[3/5] Tokenizing Training & Validation Datasets with Instruction Label Masking...")
    t_data = time.time()
    dataset = load_dataset("json", data_files={"train": TRAIN_FILE, "validation": VAL_FILE})

    def preprocess_function(examples):
        input_ids_list = []
        labels_list = []
        
        for messages in examples["messages"]:
            system_msg = ""
            user_msg = ""
            assistant_msg = ""
            for m in messages:
                if m["role"] == "system":
                    system_msg = m["content"]
                elif m["role"] == "user":
                    user_msg = m["content"]
                elif m["role"] == "assistant":
                    assistant_msg = m["content"]
            
            if system_msg:
                full_prompt = f"<s>[INST] {system_msg}\n\n{user_msg} [/INST]"
            else:
                full_prompt = f"<s>[INST] {user_msg} [/INST]"
                
            full_text = f"{full_prompt} {assistant_msg}</s>"
            
            prompt_tokenized = tokenizer(full_prompt, truncation=True, max_length=1024, padding=False)
            prompt_len = len(prompt_tokenized["input_ids"])
            
            full_tokenized = tokenizer(full_text, truncation=True, max_length=1024, padding=False)
            input_ids = full_tokenized["input_ids"]
            
            labels = [-100] * min(prompt_len, len(input_ids)) + input_ids[prompt_len:]
            
            input_ids_list.append(input_ids)
            labels_list.append(labels)
            
        return {"input_ids": input_ids_list, "labels": labels_list}

    tokenized_datasets = dataset.map(
        preprocess_function,
        batched=True,
        batch_size=1000,
        remove_columns=dataset["train"].column_names,
        desc="Tokenizing agricultural instructions"
    )
    log(f"✅ Tokenization complete in {time.time()-t_data:.2f}s | Train: {len(tokenized_datasets['train']):,} | Val: {len(tokenized_datasets['validation']):,}")

    # 4. Training Arguments Setup (Multi-GPU Distributed)
    # With world_size=4, per_device_train_batch_size=16 and gradient_accumulation=1 => global batch size = 64
    log(f"\n[4/5] Setting up Distributed Arguments ({world_size} GPUs, Batch: 32/GPU)...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=32,
        gradient_accumulation_steps=1,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_steps=100,
        weight_decay=0.01,
        bf16=True,
        logging_steps=15,
        save_strategy="steps",
        save_steps=150,
        save_total_limit=4,
        eval_strategy="steps",
        eval_steps=150,
        report_to="none",
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
        remove_unused_columns=False,
        max_grad_norm=1.0,
        ddp_find_unused_parameters=False
    )

    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        pad_to_multiple_of=8,
        return_tensors="pt"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator
    )

    # 5. Check for Checkpoint to Resume
    latest_ckpt = get_latest_checkpoint(OUTPUT_DIR)
    if latest_ckpt:
        log(f"🔄 Found checkpoint to resume: {latest_ckpt}")
    else:
        log("🚀 No checkpoint found, starting fresh from step 0.")

    # 6. Execute Training
    log("\n[5/5] 🚀 RESUMING DISTRIBUTED TRAINING ACROSS ALL GPUs...")
    log("================================================================================")
    
    t_start = time.time()
    train_result = trainer.train(resume_from_checkpoint=latest_ckpt)
    total_train_time = time.time() - t_start
    
    log(f"🎉 Training Completed in {total_train_time/60:.2f} minutes!")
    log(f"📉 Final Training Loss: {train_result.training_loss:.4f}")
    
    # 7. Save Final Adapter (Only Rank 0)
    if local_rank == 0:
        log(f"\nSaving final adapted weights to: {FINAL_ADAPTER_DIR}")
        os.makedirs(FINAL_ADAPTER_DIR, exist_ok=True)
        trainer.model.save_pretrained(FINAL_ADAPTER_DIR)
        tokenizer.save_pretrained(FINAL_ADAPTER_DIR)
        
        report = {
            "model": "mistralai/Ministral-8B-Instruct-2410",
            "adapter_type": "LoRA",
            "precision": "bfloat16",
            "world_size": world_size,
            "epochs": 3,
            "trainable_parameters": trainable_params,
            "all_parameters": all_params,
            "train_samples": len(tokenized_datasets["train"]),
            "val_samples": len(tokenized_datasets["validation"]),
            "training_time_minutes": round(total_train_time / 60, 2),
            "final_loss": round(train_result.training_loss, 4),
            "adapter_path": FINAL_ADAPTER_DIR
        }
        with open(os.path.join(FINAL_ADAPTER_DIR, "training_report.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        log("================================================================================")
        log(f"✅ STEP 3 ADAPTER EXPORT COMPLETE: {FINAL_ADAPTER_DIR}")
        log("================================================================================")

if __name__ == "__main__":
    main()
