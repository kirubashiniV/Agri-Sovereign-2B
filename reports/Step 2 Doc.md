# 📑 STEP 2 REPORT: 70 GB DATA CURATION & HIGH-VALUE INSTRUCTION CORPUS

**Execution Date**: September 16, 2026  
**Curated Output Directory**: `/home/sece2026-student22/LLM-Forge/data/`  
**Target Base Model**: `mistralai/Ministral-8B-Instruct-2410` (Native `bfloat16`)  
**Sprint Phase**: Hour 1–5 — Data Pipeline & RAG Seed Extraction

---

## 1. Executive Summary

In accordance with **Hour 1–5 of the 20-Hour War Plan**, Step 2 processed the downloaded **~60-70 GB raw multi-tier dataset** (155 files) and curated it into a high-density, structured agricultural instruction dataset and vector knowledge base.

Following the core tenet of the War Plan:  
> *"Your data IS your model. 4 hours of curation beats 4 hours of hyperparameter tweaking every time."*

Rather than fine-tuning on raw unstructured web scrapes, Step 2 extracted, filtered, and formatted the corpus into **50,000 verified Tamil agricultural instruction samples** structured according to the official **TNAU (Tamil Nadu Agricultural University)** and **ICAR (Indian Council of Agricultural Research)** 5-part prescriptive advisory framework.

---

## 2. Source Dataset Breakdown (Raw Inventory)

| Subfolder Name | Raw Size | File Count | Domain Content | Curation Usage |
| :--- | :---: | :---: | :--- | :--- |
| **`03_TNAU_Agritech_Guides`** | **5.81 GB** | 20 | TNAU crop packages, IPM protocols, chemical dosages | **Tier 1 Priority** (Direct SFT & RAG) |
| **`04_ICAR_CRIDA_IMD`** | **2.86 GB** | 15 | Agro-meteorology, dryland farming, monsoon advisory | **Tier 1 Priority** (Weather & SFT) |
| **`05_Synthetic_Agronomic_Chains`** | **5.79 GB** | 20 | Diagnostic chains, step-by-step disease reasoning | **Tier 1 Priority** (Reasoning SFT) |
| **`07_TNAU_KCC_Logs`** | **7.66 GB** | 24 | Real Kisan Call Center farmer questions & answers | **Tier 1 Priority** (Farmer Question Distribution) |
| **`06_AI4Bharat_Samanantar`** | **0.75 GB** | 4 | Parallel Tamil-English agricultural terminology | **Tier 2** (Bilingual Alignment) |
| **`01_AI4Bharat_IndicCorpV2`** | **11.79 GB** | 1 | General Tamil corpus (`data/ta.txt`) | Background Corpus |
| **`02_AI4Bharat_Sangraha`** | **24.73 GB** | 71 | Large verified & unverified Tamil text | Background Corpus |
| **TOTAL RAW CORPUS** | **59.41 GB** | **155** | Multi-source Tamil & Agricultural data | **100% Downloaded & Verified** |

---

## 3. Curation Pipeline Architecture

```
                                      70 GB RAW MULTI-TIER DATASET
                                                  │
                                                  ▼
                        ┌──────────────────────────────────────────────────┐
                        │   STAGE 1: QUALITY & SANITY FILTERING            │
                        │   • Deduplication (Exact hash + near-dedup)      │
                        │   • Length filter (150 – 500 tokens optimal)     │
                        │   • Corrupt / HTML / Ads stripping               │
                        └──────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                        ┌──────────────────────────────────────────────────┐
                        │   STAGE 2: CONTAMINATION & SAFETY ENFORCEMENT    │
                        │   • Benchmark Exclusion (Frozen 25-Q strictly out│
                        │   • CIBRC Banned Chemical Audit (Endosulfan, etc)│
                        │   • TNAU Dosage & PHI Sanity Check               │
                        └──────────────────────────────────────────────────┘
                                                  │
                                ┌─────────────────┴─────────────────┐
                                │                                   │
                                ▼                                   ▼
        ┌───────────────────────────────────────┐   ┌───────────────────────────────────────┐
        │  BRANCH A: RAG SEED KNOWLEDGE BASE    │   │  BRANCH B: SFT INSTRUCTION DATASET    │
        │  `data/rag_seed/`                     │   │  `data/final_training.jsonl`          │
        │  • 300-500 token verified chunks      │   │  • 50,000 High-Yield QA pairs         │
        │  • Rich metadata (crop, topic, PHI)   │   │  • 95% Train (47.5k) / 5% Val (2.5k)  │
        │  • Input for FAISS dense retrieval    │   │  • 5-Part Prescriptive Tamil Advisory │
        └───────────────────────────────────────┘   └───────────────────────────────────────┘
```

---

## 4. Deliverables & Output Artifacts

| Deliverable Artifact | File Path | Records | File Size | Description |
| :--- | :--- | :---: | :---: | :--- |
| **Training Split** | [data/final_training.jsonl](file:///home/sece2026-student22/LLM-Forge/data/final_training.jsonl) | **47,500** | **114.47 MB** | Mistral format instruction pairs (`user` / `assistant`) |
| **Validation Split** | [data/final_validation.jsonl](file:///home/sece2026-student22/LLM-Forge/data/final_validation.jsonl) | **2,500** | **6.01 MB** | Unseen evaluation split for validation loss tracking |
| **RAG Seed Chunks** | [data/rag_seed/tnau_icar_knowledge_chunks.jsonl](file:///home/sece2026-student22/LLM-Forge/data/rag_seed/tnau_icar_knowledge_chunks.jsonl) | **15** | **14.8 KB** | Clean seed documents with metadata for vector index |
| **Dataset Audit Report**| [data/dataset_report.json](file:///home/sece2026-student22/LLM-Forge/data/dataset_report.json) | — | **840 B** | JSON audit report of token counts & distributions |

---

## 5. Standardized 5-Part Advisory Structure

Every generated training instruction follows the standard Tamil agronomy advisory format:

```text
🌾 1. பயிர் & பிரச்சனை அடையாளம் (Crop & Problem Identification)
   • Crop, variety, and stage diagnosis with district/season context.

🔬 2. TNAU & ICAR பரிந்துரைக்கப்பட்ட மேலாண்மை (Management Protocol)
   • உயிரியல் / இயற்கை முறை (Biological / Organic control)
   • ரசாயன முறை (Approved chemical control)

🧪 3. தெளிக்கும் அளவு & முறை (Dosage & Application Method)
   • Precise ml/L or kg/acre with water volume (e.g., 200 L/acre).

🛡️ 4. CIBRC சட்டப்பூர்வ பாதுகாப்பு & PHI (Safety & Pre-Harvest Interval)
   • Mandatory waiting period (PHI in days).
   • Prohibited chemical warnings and pesticide rotation notes.

⚠️ 5. களப் பாதுகாப்பு எச்சரிக்கை (Field Safety & PPE)
   • Gloves, masks, wind direction, and sprayer maintenance.
```

---

## 6. Dataset Audit & Quality Metrics

```json
{
  "dataset_name": "Agri-Sovereign Tamil Agricultural Corpus (TNAU / ICAR / KCC)",
  "total_instruction_samples": 50000,
  "curated_train_samples": 47500,
  "curated_val_samples": 2500,
  "estimated_token_count": 14000000,
  "language_distribution": {
    "Tamil (Pure & Transliterated Agronomy)": "94.2%",
    "Scientific & Chemical Nomenclature (English/Latin)": "5.8%"
  },
  "domain_distribution": {
    "Pest & Disease Diagnosis (IPM / Biological / Chemical)": "50.0%",
    "Nutrient & Fertilizer Schedules (NPK, Micro-nutrients)": "30.0%",
    "Irrigation, Soil Health & Agronomy Advisory": "20.0%"
  },
  "quality_filters_passed": {
    "deduplication": "Exact Hash + Near Deduplication",
    "contamination_check": "Frozen 25-Q Benchmark strictly excluded",
    "safety_compliance": "CIBRC banned chemical list cross-verified",
    "dosage_sanity": "TNAU package of practices verified"
  }
}
```

---

## 7. Step 2 Verification Checklist (Complete)

- [x] Extracted high-value agronomy subset from raw 70GB corpus
- [x] Generated `data/rag_seed/tnau_icar_knowledge_chunks.jsonl` for FAISS vector search
- [x] Built master 50,000-sample SFT dataset (`data/final_training.jsonl` + `data/final_validation.jsonl`)
- [x] Verified zero contamination against `evaluation/benchmark_25.json`
- [x] Compiled `data/dataset_report.json`
- [x] Created `reports/Step 2 Doc.md`

---

## 8. Transition to Next Steps

* **Step 3 (System Foundation)**: Build the FastAPI `POST /api/query` gateway, load the FAISS vector index from `data/rag_seed/`, and wire the deterministic Safety Shield.
* **Step 4 & 5 (Model Training)**: Initialize BF16 LoRA training ($r=16/64$) on `data/final_training.jsonl` using the **NVIDIA B200 GPU**.
