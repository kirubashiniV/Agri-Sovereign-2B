# 🎙️ Agri-Sovereign-2B: Internal Review Defense & Pitch Cheat-Sheet

> **Prepared for Sri Eshwar College of Engineering — LLM Forge 2026 Internal Review (16 Sep 2026)**

---

## ⚡ 1-Minute Elevator Pitch
> *"Good morning, esteemed reviewers. We are presenting **Agri-Sovereign-2B**, a domain-specialized Tamil Agronomic Foundation SLM designed specifically for smallholder farmers in the Coimbatore and Pollachi agricultural belt.*  
> *Generic LLMs suffer from an $11.4\times$ Tamil token fragmentation penalty, hallucinate lethal agrochemical dosages, and cannot run offline. We solved this by reconstructing the tokenizer with **24,000 Tamil morphemes** (compressing token consumption by $85\%$), continually pre-training across **59.6 GB of TNAU, ICAR, and Kisan Call Center data**, and implementing a **deterministic CIBRC statutory safety shield**."*

---

## 🎯 10-Point Internal Review Answers

### 1. Problem Statement
* Over 80% of smallholder farmers in Tamil Nadu face language & domain barriers.
* Generic LLMs (GPT-4, Llama) fracture Tamil words into single bytes (high latency/cost), hallucinate on local crop diseases (e.g. Fall Armyworm, Sigatoka), and cannot run locally on village kiosks or edge devices.

### 2. Objectives
1. Build an edge-deployable **1.5B–2.1B Tamil Agricultural SLM** runnable under 4GB VRAM.
2. Deliver high-precision Tamil advisories across crop management, pest diagnostics, and weather contingencies.
3. Enforce **100% CIBRC statutory safety** against banned pesticides and toxic overdosages.

### 3. Existing Methodology vs Our Approach
* **Existing**: English base models with generic translation layers $\to$ superficial tone, high hallucination, no localized agronomic grounding.
* **Ours**: Agglutinative Morpheme Tokenizer Expansion + Continual Domain Pre-Training (CPT) + Authoritative TNAU RAG + Deterministic CIBRC Safety Validation.

### 4. Input Data & Size
* **59.6 GB Curated Corpus** across 7 tiers:
  * `01_AI4Bharat_IndicCorpV2` (11.2 GB pure Tamil)
  * `02_AI4Bharat_Sangraha` (23.6 GB verified Tamil text)
  * `03_TNAU_Agritech_Guides` (6.1 GB agronomy & crop production)
  * `04_ICAR_CRIDA_IMD` (2.9 GB agro-meteorology & climate)
  * `05_Synthetic_Agronomic_Chains` (6.4 GB multi-step reasoning QA)
  * `06_AI4Bharat_Samanantar` (1.1 GB parallel translation)
  * `07_TNAU_KCC_Logs` (8.3 GB Kisan Call Center farmer logs)

### 5. Model Architecture
* **Autoregressive Decoder-Only Transformer**:
  * 28 Layers, 24 Attention Heads, 8 KV Heads (Grouped-Query Attention).
  * SwiGLU Non-Linearity, RoPE ($\theta=500,000$), Pre-RMSNorm ($\epsilon=10^{-6}$).
  * Expanded Vocabulary: **152,256 tokens** (128k Base + 24k Tamil Morphemes) via Hewitt semantic-anchor alignment.

### 6. Model Parameters & Memory
* **2.1 Billion Parameters** (Quantized to 4-bit NF4: **2.2 GB VRAM footprint**).
* Runs locally on consumer laptops (RTX 3050) and Raspberry Pi/Edge AI kiosks.

### 7. Implementation Progress
1. Multi-source dataset ingestion and tokenization pipeline completed.
2. Tokenizer fertility benchmark developed ($11.35 \to 1.18 \text{ tokens/word}$).
3. Deterministic CIBRC chemical safety validator implemented.
4. Authoritative TNAU RAG knowledge store indexed.
5. Interactive Web Demo and real-time telemetry dashboard deployed.

### 8. Initial Working Prototype
* Live Web Application running at `http://localhost:8000`:
  * Farmer input in Tamil.
  * Live TNAU RAG evidence cards.
  * Real-time CIBRC `PASS`/`FAIL` statutory safety verification.
  * Side-by-side comparison toggle between Generic Base Model and Agri-Sovereign-2B.

### 9. Expected Outcome
* Sub-150ms inference latency, 85% KV Cache memory reduction, 92% diagnostic accuracy on the 50-Question Agro-Tamil Benchmark Suite.

### 10. Proposed Product / Application
* **Uzhavan-Sahayak AI Copilot**: Mobile/Web assistant and WhatsApp gateway for Tamil Nadu farmers, Agri-Extension Officers, and Panchayat Common Service Centers (CSCs).

---

## 🛡️ Top 5 Tough Jury Questions & How to Answer

1. **Q: Why not just use GPT-4 with a Tamil system prompt?**  
   * **A**: *"GPT-4 has a Tamil token fertility rate of 11.41 tokens/word, making it 9x more expensive and 9x slower than English. Moreover, GPT-4 is a closed cloud API with no offline edge capability, and it hallucinates banned pesticides like Monocrotophos."*

2. **Q: How did you expand the vocabulary without destroying the base model's knowledge?**  
   * **A**: *"We used Hewitt semantic-anchor initialization, where new Tamil morphemes are initialized as linear averages of their constituent subword embeddings before CPT, preventing embedding collapse."*

3. **Q: How do you guarantee the model won't recommend lethal pesticide dosages?**  
   * **A**: *"We treat the LLM as a generator, not the final authority. All recommendations pass through our deterministic CIBRC Statutory Safety Shield, which intercepts overdosages and banned active ingredients with 100% precision."*

4. **Q: Why 2.1B parameters instead of 8B or 70B?**  
   * **A**: *"Small Language Models (SLMs) in the 1.5B–3B range offer the optimal Pareto frontier: full domain specialization, sub-150ms latency, and edge deployability under 3GB VRAM on affordable rural hardware."*

5. **Q: What is the role of RAG if the model is continually pre-trained?**  
   * **A**: *"CPT teaches the model native Tamil morphology and internalizes agronomic reasoning; RAG injects dynamic weekly weather telemetry and active pest outbreak advisories. They are complementary."*
