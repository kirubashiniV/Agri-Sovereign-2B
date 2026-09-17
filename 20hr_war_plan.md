# 20-HOUR WAR PLAN
### Tamil Agricultural AI — Ministral 3 8B + QLoRA Sprint
*Two developers · Agentic IDE (Antigravity) · One shot · Maximum measurable performance*

---

| 20 hrs | 2 | 70 GB | ≤15 GB | 10 hrs | 25 Q |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Sprint Window** | **Developers** | **Raw Data** | **Curated Corpus** | **Training Budget** | **Frozen Benchmark** |

> **"Ship does not mean perfect. Ship means measurable, defended, and running at demo time."**

* 🛑 **PERSON 1 never stops training to help Person 2.**
* 🛑 **PERSON 2 never waits for Person 1's model.**
* 🛑 **No new features after Hour 17.**
* 🛑 **One config. One run. No experiments.**
* ⚡ **Agentic IDE — Antigravity**: Let the agent handle boilerplate. You drive architecture. Every hour saved on scaffolding = one more hour training.

---

## ZERO HOUR — PRE-STAGING
*Both people work together 60–90 min before kickoff. Hour 0 is the END of preparation, not the beginning of setup.*

### 👤 PERSON 1 (Model / Data)
- [ ] Ministral-3-8B-Base-2512 downloaded & 4-bit loading verified
- [ ] Vision inference smoke test passed
- [ ] Tamil prompt smoke test passed
- [ ] `transformers` / `datasets` / `peft` / `trl` / `bitsandbytes` installed
- [ ] QLoRA training script starts on dummy data without error
- [ ] Tiny dummy training run completes — checkpoint saves correctly
- [ ] OOM stress test: one real training step passes without OOM
- [ ] GPU VRAM baseline recorded (`nvidia-smi`)
- [ ] Raw 70 GB dataset accessible & filtering script ready
- [ ] Instruction generation script tested on 100 sample examples
- [ ] Image dataset located OR vision training subset explicitly DROPPED
- [ ] Benchmark questions NEVER seen by Person 1 (contamination check)

### 👤 PERSON 2 (Product / System)
- [ ] FAISS installed + embedding model working + RAG retrieval smoke test
- [ ] Tamil ASR tested + latency noted
- [ ] Tamil TTS #1 (AI4Bharat IndicTTS) tested
- [ ] Tamil TTS #2 (Google Cloud Tamil) tested — one selected, committed
- [ ] TTS normalizer skeleton exists (numbers, units, PHI, NPK, pH)
- [ ] Safety database / banned chemical rules loaded
- [ ] FastAPI running + `/api/query` returns 200
- [ ] Frontend running + connects to FastAPI
- [ ] WhatsApp integration: VERIFIED or explicitly marked FALLBACK
- [ ] 25 Tamil agricultural questions written + reference answers written
- [ ] Benchmark frozen as JSON + SHA hash recorded
- [ ] Benchmark excluded from ALL training/RAG data (verified)
- [ ] Scoring script (LLM-as-judge) written + tested on 5 dummy examples

### 🤝 SHARED CONTRACTS
- [ ] `/contracts/query.schema.json` committed to repo
- [ ] `/evaluation/benchmark_25.json` committed to repo
- [ ] `/evaluation/base_results.json` placeholder created
- [ ] `/data/rag_seed/` source identified (TNAU + ICAR priority docs)
- [ ] Audio contract resolved: Option A (server TTS → URL) or Option B (`spoken_ta` text)
- [ ] Team agrees: one config, one run, no experiments after Hour 0

> **"The team that ships a working demo always beats the team that almost finished a perfect one."**

---

## THE 20-HOUR SPRINT
*Every block below is a hard commitment. Deviation requires team consensus.*

### ⏱️ HOUR 0 — FREEZE & BASELINE
#### 👤 PERSON 1 — MODEL / DATA
* Run frozen 25-question benchmark against unadapted Ministral 3 8B Base
* Record: question / response / latency / tokens / score for all 25
* Save → `evaluation/baseline.json` (this is your BEFORE — guard it)

#### 👤 PERSON 2 — PRODUCT / SYSTEM
* Start the application using the BASE model immediately
* By end of Hour 1: `TEXT → FastAPI → Base 8B → Response` must work
* Hours 1–3: TTS normalizer (numbers, units, PHI, NPK, pH, ml/L, kg/acre)
* Hours 1–3: ASR integration + latency test
* Hours 1–3: Safety database loading + rule validation
* Hours 1–3: `/api/query` contract integration test against base model
* *Antigravity: scaffold FastAPI route stubs + Pydantic models in < 5 min.*

---

### ⏱️ HOUR 1–5 — 70 GB → HIGH-VALUE CORPUS
#### 👤 PERSON 1 — MODEL / DATA
* Run filtering pipeline: corrupt removal → lang detect → agri relevance → authority scoring → quality scoring → exact dedup → near dedup → length/garbage filter → **≤15 GB ceiling** (quality floor, not volume target)
* **HOUR 2 HARD DEADLINE**: deliver `/data/rag_seed/` (TNAU + ICAR top docs)
* Branch output EARLY: training JSONL (150–400 tok Q&A) vs RAG chunks (300–500 tok)
* **Tier 1 keep**: TNAU, ICAR, Govt agri, university docs, pest/disease/IPM
* **Tier 4 eliminate**: blogs, forums, SEO articles, ads

#### 👤 PERSON 2 — PRODUCT / SYSTEM
* Hours 3–5: RAG pipeline — chunk `rag_seed` → embed → FAISS index
* Every chunk carries: source, title, url, crop, topic metadata
* Hours 3–5: Safety shield — chemical extraction → banned/approved lookup → dosage validation → PHI validation → PASS / REVIEW / BLOCK
* **RULE**: No verified evidence = REVIEW. Never let LLM guess pesticide info.
* **HOUR 5**: Re-ingest `rag_final/` when Person 1 delivers — replace FAISS index
* *Antigravity: generate chunking + embedding pipeline from docstring spec.*

> **"Your data IS your model. 4 hours of curation beats 4 hours of hyperparameter tweaking every time."**

---

### ⏱️ HOUR 5 — DATA FREEZE
#### 👤 PERSON 1 — MODEL / DATA
* Deliver: `final_training.jsonl` + `final_validation.jsonl` + `dataset_report.json`
* Report must include: `raw_size`, `filtered_size`, `Tamil%`, `agriculture%`, `token_count`
* Do NOT force 15 GB — 8.7 GB of excellent data > 14.9 GB containing garbage
* Target 40k–60k instruction examples (quality distributions, not 60k clones)

---

### ⏱️ HOUR 5–6 — QLoRA LOCK
#### 👤 PERSON 1 — MODEL / DATA
* **Config**: Ministral 3 8B Base | 4-bit NF4 | BF16 compute | LoRA r=16
* gradient checkpointing ON | microbatch=1 | gradient accumulation
* **Target modules**: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
* `r=16` not `r=32` — preserves VRAM headroom, eliminates OOM risk on 20 GB

#### 👤 PERSON 2 — PRODUCT / SYSTEM
* Hours 5–8: TTS — test AI4Bharat IndicTTS first, Google Cloud Tamil second
* Commit to whichever works in < 30 min. Build normalizer around it.
* Normalizer outputs TWO strings: `answer_ta` (display) + `spoken_ta` (TTS input)
* 🚫 **NO**: r=8 experiment | 🚫 **NO**: r=32 experiment | 🚫 **NO**: different LR experiment
* 🚫 **NO**: different optimizer | 🚫 **NO**: different model ← **ONE SHOT. COMMIT.**

---

### ⏱️ THE TRAINING BLOCK — HOURS 6–16
*Person 1 essentially disappears into the GPU for 10 hours. This is not multitasking time. This is monitoring time.*

| Loss | Tokens/sec | VRAM | GPU Util | Step | LR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Drops steadily or plateaus | Stable > 200 | < 19 GB always | > 90% | Advancing | Schedule followed |

#### Checkpoint Schedule
* **Hour 8**: `checkpoint-early` (Safety net against catastrophic divergence)
* **Hour 11**: `checkpoint-mid` (Usable model if hours 11-16 go wrong)
* **Hour 14**: `checkpoint-late` (Near-final, likely best candidate)
* **Hour 15**: `checkpoint-final` (Training STOPS here — not hour 17)

#### OOM Recovery Protocol
* OOM hit ➔ **Step 1**: reduce `gradient_accumulation_steps` by half
* Still OOM ➔ **Step 2**: reduce `max_seq_length` by 25%
* Still OOM ➔ **Step 3**: drop LoRA `r=16` ➔ `r=8`
* Still OOM ➔ **Step 4**: `microbatch=1`, `accumulation=1`, no further reduction
* **NEVER**: switch model | disable 4-bit | remove gradient checkpointing

#### Divergence Recovery
* **ABORT CONDITION**: Persistent loss regression over 3+ consecutive checkpoints, OR NaN/Inf values, OR exploding gradients.
* **ACTION**: STOP ➔ restore last healthy checkpoint ➔ `LR × 0.3` ➔ resume. *(NOT an abort: normal stochastic loss variation between batches).*

> **"10 hours of uninterrupted training is the hardest discipline in this sprint. Protect it."**

#### 👤 PERSON 2 — WHILE PERSON 1 TRAINS (HOURS 6–16)
* **H 6–8 (TTS)**: AI4Bharat ➔ Google fallback | Build Tamil normalizer | Test 2 providers max | Commit
* **H 8–11 (UI)**: One farmer screen: Tamil | Image | Answer card | Sources | Audio
* **H 10–12 (Vision)**: `IMAGE → Vision encoder → text description → RAG query → LLM response`
* **H 12–14 (Integration)**: `TEXT + VOICE (ASR) + IMAGE → FastAPI → RAG ⊕ 8B → Safety → TTS → UI`
* **H 14–16 (WhatsApp)**: Test Neonize: authorized sender ➔ same pipeline ➔ Tamil advisory reply
  * ⚠️ **WHATSAPP HARD STOP**: If WhatsApp auth consumes > 30 min without working — **ABANDON IT**. Your web/voice/image workflow is more valuable than proving production WhatsApp infra in 20 hours.

---

### ⏱️ FINAL HOURS — MERGE, MEASURE, DEMO

#### ⏱️ HOUR 15–16 — TRAINING ENDS + ADAPTER EXPORT
##### 👤 PERSON 1 — MODEL / DATA
* Training STOPS at Hour 15 — not Hour 17 (10 hours training budget)
* Select best checkpoint (compare val loss across hour 8 / 11 / 14 / 15)
* Export adapter → `final_adapter/`
* Person 2 sets: `MODEL_ADAPTER_PATH=/.../final_adapter` — **ONE ENV VAR**
* Same application. Same API. No architecture changes.

##### 👤 PERSON 2 — PRODUCT / SYSTEM
* Hours 15–16: Full pipeline integration test
* `TEXT + VOICE + IMAGE → FastAPI → RAG + Adapted 8B → Safety → TTS`
* Fix integration bugs NOW — not after Hour 17

---

### ⏱️ HOUR 16–17 — FREEZE
* **NO new features. NO new models. NO new datasets. NO UI redesign.**
* Run the complete demo end-to-end once. Fix only what is broken.
* If something non-critical is broken — **LEAVE IT**. Note it for the jury.
* 🛑 **HARD FREEZE AT HOUR 17. Both people agree on this before the sprint starts.**

---

### ⏱️ HOUR 17–18 — BENCHMARK
#### 👤 PERSON 1 — MODEL / DATA
* Run EXACT same 25 questions against adapted model
* Save → `evaluation/adapted.json` + `evaluation/comparison.json`
* Calculate absolute improvement + relative improvement per category
* If adaptation is worse — report it honestly. The story still holds.

#### 👤 PERSON 2 — PRODUCT / SYSTEM
* Run system benchmark: ASR latency, TTS latency, RAG latency, LLM latency
* Run safety benchmark: total tests / blocked / passed / review / false negatives
* Record token fertility, groundedness rate, end-to-end latency

---

## THE NUMBERS THAT WIN

| Metric | Base 8B | Adapted 8B | Delta |
| :--- | :---: | :---: | :---: |
| **Tamil benchmark accuracy** | — % | — % | ▲ — % |
| **Agricultural accuracy** | — % | — % | ▲ — % |
| **Groundedness (source-backed)** | — % | — % | ▲ — % |
| **Token fertility (ta/en)** | — | — | — |
| **Avg inference latency** | — ms | — ms | — |
| **Training VRAM peak** | — | — | — |

| Safety Test | Total Cases | Intercepted |
| :--- | :---: | :---: |
| **Prohibited chemical test cases** | — | — |
| **Unsupported dosage cases** | — | — |
| **PHI violation cases** | — | — |

---

## ⏱️ HOUR 19–20 — JURY MODE
*Run ONE 3-minute demo, end-to-end, repeatedly. No live coding.*

* **Scene 1**: Farmer speaks Tamil ➔ ASR ➔ RAG + Adapted 8B ➔ Safety ➔ Tamil TTS ➔ Audio
* **Scene 2**: Farmer uploads crop photo ➔ Vision ➔ RAG ➔ Grounded advisory
* **Scene 3**: Dangerous pesticide request ➔ LLM ➔ SAFETY SHIELD ➔ BLOCK/REVIEW
* **Scene 4** (if working): Same advisory via WhatsApp
* **Final slide**: BASE vs ADAPTED table + Safety interception table. No theoretical claims.

> **"Come out saying: our adapted 8B improved X→Y on a frozen benchmark while intercepting every banned chemical. That is how you win on numbers."**

---

## THE IMMUTABLE CONTRACT
*This is committed at Hour 0. Nobody changes it without explicit team consent.*

### API Contract: `POST /api/query`
```json
// INPUT
{
  "text": "தக்காளி இலை சுருட்டல் நோய்க்கு என்ன மருந்து?",
  "image": null, // base64 or null
  "mode": "farmer"
}

// OUTPUT
{
  "answer_ta": "...", // display text (Tamil)
  "spoken_ta": "...", // normalised text -> TTS input
  "audio_url": "/audio/resp_123.mp3", // Option A: server-rendered audio
  "sources": [
    { "title": "...", "source": "TNAU", "url": "..." }
  ],
  "safety": {
    "status": "PASS | REVIEW | BLOCK",
    "warnings": []
  },
  "model": "adapted",
  "telemetry": {
    "rag_ms": 0,
    "llm_ms": 0,
    "tts_ms": 0,
    "total_ms": 0
  }
}
```

---

## SYSTEM ARCHITECTURE

```
+---------------------------------------------------------------------------------------+
|                                        FARMER                                         |
|                             [ TEXT | VOICE | IMAGE ]                                  |
+------------------------------------------+--------------------------------------------+
                                           |
                                           v
                                    [ FastAPI Gateway ]
                                           |
    +--------------------------------------+--------------------------------------+
    |                                      |                                      |
    v                                      v                                      v
[ ASR & Vision Enc. ]             [ TNAU / ICAR RAG ]                     [ Ministral 3 8B ]
(Whisper / 0.4B Vision)          (FAISS + Dense Index)                    (QLoRA r=16 Adapted)
    |                                      |                                      |
    +--------------------------------------+--------------------------------------+
                                           |
                                           v
                              [ DETERMINISTIC SAFETY SHIELD ]
                           (Banned Chemicals | Max Dosages | PHI)
                                           |
                                           v
                               [ STRUCTURED TAMIL ANSWER ]
                                           |
                     +---------------------+---------------------+
                     |                                           |
                     v                                           v
            [ Screen Display (UI) ]                     [ Tamil Normalizer + TTS ]
                 (Tamil Text)                                (Audio Stream / URL)
```

---

## ANTIGRAVITY (AGENTIC IDE) — WHERE TO USE IT
*Let the agent handle scaffolding. You drive architecture decisions.*

### 👤 PERSON 1
* [x] Generate filtering pipeline from a docstring spec — agent writes the boilerplate
* [x] Generate instruction example templates for each category — agent produces 10 variants
* [x] Generate JSONL validation script — let agent write the format checker
* [x] Generate benchmark scoring script from rubric description — agent writes the judge loop
* [x] Monitor GPU stats: ask agent to write a one-line watch script

### 👤 PERSON 2
* [x] Scaffold FastAPI router + Pydantic models from the API contract JSON — 2 minutes
* [x] Generate FAISS ingestion pipeline from chunking spec — agent writes the boilerplate
* [x] Generate TTS normalizer regex patterns for units/abbreviations — agent drafts, you verify
* [x] Generate Tamil text-to-speech wrapper with fallback logic — agent scaffolds it
* [x] Generate safety extraction patterns (chemical names, dosage regex) — agent drafts
* [x] Generate React/HTML farmer UI from ASCII wireframe — paste the wireframe, get the code

> **AGENTIC RULE**: If a task is primarily boilerplate (CRUD, schemas, wrappers, format validators, regex) — delegate it to the agent. If a task requires architectural judgment (data tier decisions, LoRA config, safety rules, benchmark design) — you own it.

> **"You have 20 hours and an agentic IDE. The developer who writes less boilerplate ships more product."**

---

## 🚀 GO BUILD IT.
* **Base 8B ➔ Adapted 8B.**
* **RAG-grounded. Safety-shielded. Tamil-voiced.**
* **Benchmarked before. Benchmarked after.**
* **Numbers on the slide. Demo runs.**
