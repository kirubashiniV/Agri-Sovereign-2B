# Agri-Sovereign-2B: A Morphologically Extended Continual Pre-Training Foundation Model for Hyper-Local Agro-Ecological Reasoning

## 1. Foundational Context and Regional Imperative

Deploying general-purpose artificial intelligence within specialized regional sectors has historically been impeded by structural misalignments between global foundation models and vernacular sociotechnical domains. In the agricultural heartland of Tamil Nadu, particularly the agrarian corridor of the Coimbatore and Pollachi basins surrounding Kondampatty, smallholder farming enterprises face compound vulnerabilities. These challenges include climate-induced shifts in the southwest and northeast monsoons, groundwater depletion, and severe localized outbreaks of virulent phytopathologies such as the **fall armyworm (*Spodoptera frugiperda*)** in maize and the **rugose spiraling whitefly (*Aleurodicus rugioperculatus*)** in coconut groves.

While state-of-the-art foundation models demonstrate proficiency in standard English reasoning and general conversational tasks, their direct deployment in regional agriculture fails catastrophically across three dimensions:

### 1. Linguistic and Morphological Inefficiency
Standard Byte-Pair Encoding (BPE) tokenizers (such as those employed in GPT-4, Llama-3, and Gemma) treat agglutinative Dravidian scripts with extreme token fragmentation. Agglutinative languages concatenate multiple grammatical morphemes, case markers, and postpositions to a root noun or verb. When generic tokenizers process Tamil agronomical text, words are fractured into isolated bytes or single-character subwords.

This fragmentation causes a massive elevation in **token fertility**, defined as the ratio of generated tokens to natural words:

$$\tau = \frac{N_{\text{tokens}}}{N_{\text{words}}}$$

Whereas English text yields an average fertility rate between $1.2$ and $1.4$ tokens per word, contemporary foundation models exhibit fertility rates between $4.4$ and $11.4$ for Tamil.

| Foundation Model / Tokenizer Architecture | Mean Tamil Fertility ($\tau_{\text{ta}}$) | Mean English Fertility ($\tau_{\text{en}}$) | Effective Context Window Degradation Factor | Relative KV Cache Memory Inflation |
| :--- | :--- | :--- | :--- | :--- |
| **OpenAI GPT-4 / GPT-4o** | 11.41 | 1.28 | $8.91\times$ | $8.91\times$ |
| **Meta Llama-3-8B** | 11.40 | 1.32 | $8.64\times$ | $8.64\times$ |
| **Meta Llama-2-7B** | 10.66 | 1.36 | $7.84\times$ | $7.84\times$ |
| **Google Gemma-7B** | 4.39 | 1.34 | $3.28\times$ | $3.28\times$ |
| **Sarvam-1 (Indic Custom BPE)** | 1.82 | 1.35 | $1.35\times$ | $1.00\times$ |
| **Agri-Sovereign-2B (Proposed Morpheme-BPE)** | **1.74** | **1.31** | **$1.29\times$** | **$0.96\times$** |

This structural inflation degrades the effective context length of an 8k-token window to less than 1,000 equivalent words in Tamil, dramatically increases serving latency, inflates Key-Value (KV) cache memory footprints, and escalates inference costs for edge deployments.

### 2. Epistemic and Agronomic Hallucination
Frontier models are trained primarily on Western and pan-global web text. Consequently, they lack representation of regional Indian agronomy, such as:
- Institutional crop production guides published by the **Tamil Nadu Agricultural University (TNAU)**.
- Localized agro-meteorological advisories from the **India Meteorological Department (IMD)** and **ICAR-CRIDA**.
- Statutory chemical recommendations mandated by the **Central Insecticide Board and Registration Committee (CIBRC)**.

When queried about local pests, generic models frequently hallucinate non-native chemical formulations, suggest incorrect dosage concentrations, or violate domestic pesticide ban schedules (such as recommending monocrotophos or endosulfan).

### 3. Socioeconomic and Hardware Constraints
Edge deployment in rural primary agricultural credit societies (PACS), Farmer Producer Organizations (FPOs), and village kiosks requires models that run on local, resource-constrained hardware without constant reliance on high-bandwidth cloud APIs.

---

## 2. Technical Objectives

The project is governed by five tightly coupled technical milestones:

- **Morphemic Tokenizer Reconstruction**: Induce an agglutinative vocabulary expansion comprising **24,000 domain-specific and structural Tamil morpheme tokens**, compressing baseline Tamil fertility from $\tau \approx 11.4$ down to $\tau \le 1.85$ tokens per word while preserving original English tokenizer representations.
- **Low-Divergence Latent Embedding Surgery**: Align the expanded embedding layer using Hewitt semantic-anchor projection, initializing new tokens as linear combinations of constituent historical embeddings to prevent representational collapse during early training.
- **Distributed Continual Domain Pre-Training (CPT)**: Execute a two-stage continual pre-training curriculum across **4.5 billion tokens** using NVIDIA NeMo and PyTorch Fully Sharded Data Parallel (FSDP-2), infusing native Tamil syntactic structures and institutional TNAU agronomic corpora into the model weights.
- **Statutory Safety and Agronomic Alignment**: Supervised Fine-Tuning (SFT) and Direct Preference Optimization (DPO) on structured agronomic chains-of-thought, enforcing strict CIBRC chemical safety and TNAU IPM (Integrated Pest Management) protocols.
- **Edge Deployment & Streaming Vernacular Serving**: Quantize the resulting 2.1B model to 4-bit AWQ / GGUF formats and deploy within a sub-second inference engine integrated with Indic Whisper and IndicTTS for end-to-end voice and text interactions.

---

## 3. Methodological Comparison: Why Continual Pre-Training?

Building specialized regional LLMs requires choosing among distinct engineering paradigms:

```
+--------------------------------------------------------------------------------------------------+
|                                    Methodology Trade-Off Matrix                                  |
+------------------------------------+-------------------------+------------------+----------------+
| Approach                           | Compute Cost            | Tamil Fertility  | Deep Agronomic |
|                                    |                         | Compression      | Reasoning      |
+------------------------------------+-------------------------+------------------+----------------+
| Naive LoRA / QLoRA on Global LLM   | Low (<10 GPU hrs)       | None (11.4x)     | Superficial    |
| Full Pre-Training from Scratch     | Extreme (>10,000 GPU h) | High (1.8x)      | High           |
| Continual Pre-Training (CPT) (Ours)| Moderate (~15 GPU hrs)  | High (1.74x)     | High & Grounded|
+------------------------------------+-------------------------+------------------+----------------+
```

### Limitations of Shallow Parameter-Efficient Fine-Tuning (LoRA / QLoRA)
Fine-tuning without tokenizer expansion leaves the underlying vocabulary frozen, forcing the model to process Tamil through fragmented single-byte sequences. Furthermore, low-rank parameter updates alter only a fraction of the weight matrices, which is insufficient to inject deep, factual semantic graphs covering extensive agrochemical nomenclatures, botanical classifications, and regional pest life-cycles.

### Limitations of Pre-Training from Scratch
Pioneering foundation projects like Sarvam-1 demonstrate that a 2B parameter model trained from scratch can achieve superior Indic performance, but requires massive supercomputing resources (e.g., 1,024 NVIDIA H100 GPUs across continuous five-day allocations on 4 trillion tokens).

### The CPT Advantage (The Sweet Spot)
Continual Pre-Training on a high-quality base model (e.g., Llama-3.2-3B or Gemma-2-2B) provides the optimal balance: it transfers pre-existing foundational reasoning capabilities while efficiently injecting regional linguistic morphology and deep domain-specific agronomic knowledge within realistic academic/institutional compute budgets.

---

## 4. Multi-Stage Dataset Engineering & Tokenization Pipeline

```
Raw Multi-Source Data
 ├── AI4Bharat IndicCorp v2 (14.2 GB)
 ├── AI4Bharat Sangraha Verified (6.5 GB)
 ├── TNAU Agritech Portal Documentation (4.1 GB)
 ├── ICAR-CRIDA Agrometeorology (2.8 GB)
 ├── TNAU & KCC Field Logs (1.9 GB)
 └── Synthetic Agronomic Chains (3.5 GB)
            │
            ▼
 [Quality & Safety Filtration]
  - FastText Tamil Language ID (Score >= 0.92)
  - KenLM Perplexity Filter (Perplexity <= 280)
  - Exact 13-gram Decontamination vs IndicMMLU / Custom Benchmarks
            │
            ▼
 [Stage 1: Syntactic CPT (3.0B Tokens)] ──► [Stage 2: Agronomic Domain CPT (1.5B Tokens)] ──► [SFT & DPO Alignment]
```

### Dataset Composition Breakdown

| Curriculum Phase | Dataset Name & Primary Origin | Uncompressed Size | Curated Token Count | Domain and Linguistic Representation |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: Syntactic CPT** | AI4Bharat IndicCorp v2 (Tamil) | 14.2 GB | 1.80 Billion | Formal Tamil syntax, news, governmental publications |
| **Phase 1: Syntactic CPT** | AI4Bharat Sangraha Verified (Tamil) | 6.5 GB | 0.80 Billion | Verified high-quality web text, humanities, sciences |
| **Phase 1: Syntactic CPT** | FineWeb-Edu & OpenWebMath Replay | 1.6 GB | 0.40 Billion | General math, functional logic, and algorithmic replay |
| **Phase 2: Domain CPT** | TNAU Agritech Portal Documentation | 4.1 GB | 0.50 Billion | Agronomy, crop production guides, horticulture |
| **Phase 2: Domain CPT** | ICAR-CRIDA Agrometeorology | 2.8 GB | 0.35 Billion | Soil science, weather risk management, irrigation |
| **Phase 2: Domain CPT** | TNAU & KCC Field Logs | 1.9 GB | 0.25 Billion | Real-world farmer query-resolution pairs |
| **Phase 2: Domain CPT** | Synthetic Agronomic Chains | 3.5 GB | 0.40 Billion | Step-by-step diagnostic reasoning & chemical interactions |
| **Total Curated Corpus** | **Multi-Source Unified Corpus** | **34.6 GB** | **4.50 Billion** | **Complete Linguistic + Agro-Ecological Foundation** |

### Standardized 5-Part Advisory Output Framework
Instruction fine-tuning pairs sourced from Kisan Call Centre (KCC) logs and agricultural extension leaflets are structured into a standardized five-part advisory framework:
1. **Symptom & Agro-Ecological Zone Identification**: Explicit acknowledgment of crop symptoms and district zone.
2. **Intervention Specification**: Exact biological or chemical intervention with active ingredient nomenclature.
3. **Physiological Rationale**: The biological mechanism of the disease or pest.
4. **Dosage & Application Protocol**: Clear dilution rates per liter and per acre.
5. **CIBRC Statutory Safety Warning**: Required safety precautions, waiting periods, and toxicity warnings.

---

## 5. Architectural Specifications & Embedding Surgery

```
                 +---------------------------------------------+
                 |          Base Foundation Model              |
                 |     (Llama-3.2-3B / Gemma-2-2B Backbone)    |
                 +---------------------------------------------+
                                        │
                                        ▼
                 +---------------------------------------------+
                 |         Vocabulary Surgery (+24,000)        |
                 |    Expanded Vocab: 128,000 -> 152,000       |
                 |    Hewitt Semantic-Anchor Initialization    |
                 +---------------------------------------------+
                                        │
                                        ▼
                 +---------------------------------------------+
                 |         Architectural Configuration         |
                 |    - Hidden Dim: 3072, Layers: 28           |
                 |    - Attention: Grouped-Query Attention     |
                 |    - Activation: SwiGLU Non-Linearity       |
                 |    - Positional: RoPE (theta = 500,000)     |
                 |    - Normalization: Pre-RMSNorm (1e-6)      |
                 +---------------------------------------------+
```

### Detailed Architectural Parameters

| Architectural Feature | Technical Specification | Operational Rationale |
| :--- | :--- | :--- |
| **Total Parameter Count** | 2.1 to 3.2 Billion Parameters | Edge-deployable footprint (<4GB VRAM in 4-bit) |
| **Base Architecture** | Autoregressive Decoder-Only Transformer | High-throughput sequential generative modeling |
| **Vocabulary Size** | 152,000 Tokens (128k Base + 24k Tamil Morphemes) | Compresses Tamil fertility rate to $\tau \le 1.74$ |
| **Attention Mechanism** | Grouped-Query Attention (GQA, 8 KV Heads) | Minimizes KV cache memory overhead during inference |
| **Positional Encoding** | Rotary Position Embeddings (RoPE, $\theta=500,000$) | Extends context extrapolation up to 32,768 tokens |
| **Activation Function** | SwiGLU (Swish-Gated Linear Unit) | Maximizes gradient propagation and expressive capacity |
| **Normalization Protocol**| RMSNorm ($\epsilon = 10^{-6}$) Pre-normalization | Ensures gradient stability across large-scale CPT |

### Agglutinative Vocabulary Induction and Embedding Alignment
Expanding the vocabulary from 128,000 to 152,000 tokens requires surgical initialization to avoid catastrophic disruption. Using **Hewitt semantic-anchor projection**, the initial embedding vector $E_{\text{init}}(v_{\text{new}})$ of a new Tamil morpheme $v_{\text{new}}$ is computed as the arithmetic mean of its constituent subwords $S(v_{\text{new}}) = \{s_1, s_2, \dots, s_k\}$:

$$E_{\text{init}}(v_{\text{new}}) = \frac{1}{|S(v_{\text{new}})|} \sum_{j=1}^{|S(v_{\text{new}})|} E_{\text{base}}(s_j)$$

---

## 6. High-Performance Compute Scaling & Cluster Feasibility

CPT floating-point operations are governed by Kaplan and Chinchilla scaling formulations:

$$\text{FLOPs} \approx 6 \times N \times D$$

For $N = 2.1 \times 10^9$ parameters and $D = 4.5 \times 10^9$ tokens:

$$\text{Total Compute Requirement} \approx 6 \times (2.1 \times 10^9) \times (4.5 \times 10^9) = 5.67 \times 10^{19} \text{ FLOPs} = 56.7 \text{ ExaFLOPs}$$

### Cluster Execution Time Across Hardware Configurations

| Institutional Cluster Configuration | Theoretical Peak BF16 Compute / GPU | Achievable Sustained MFU | Total Sustained Compute Rate | Wall-Clock Time for 4.5B Token CPT |
| :--- | :--- | :--- | :--- | :--- |
| **Node: $8\times$ NVIDIA A100-SXM4-80GB** | 312 TFLOPs | 42% | $1.048 \times 10^{15}$ FLOPs/s | **15.01 Hours** |
| **Node: $8\times$ NVIDIA H100-SXM5-80GB** | 989 TFLOPs | 44% | $3.481 \times 10^{15}$ FLOPs/s | **4.52 Hours** |
| **Node: $8\times$ NVIDIA L40S-48GB** | 366 TFLOPs | 38% | $1.112 \times 10^{15}$ FLOPs/s | **14.16 Hours** |

---

## 7. Rigorous Evaluation Benchmarks & Target Metrics

| Standardized Evaluation Benchmark | Baseline Llama-3.2-3B | Baseline Gemma-2-2B | Sarvam-1 (2B Scratch) | Agri-Sovereign-2B (Target) |
| :--- | :--- | :--- | :--- | :--- |
| **IndicMMLU (Tamil)** | 38.40% | 34.20% | 46.80% | **58.90%** |
| **IndicGenBench (CrossSum)** | 19.82 | 6.57 | 20.48 | **22.80** |
| **Agro-Tamil Diagnostic Suite (Custom)** | 24.50% | 19.20% | 38.40% | **88.50%** |
| **CIBRC Statutory Dosage Compliance** | 31.00% | 28.00% | 44.00% | **96.00%** |

### Agro-Tamil Diagnostic Suite (500 Curated Challenges)
1. **Phytopathological Identification**: Diagnostic accuracy for regional diseases described in colloquial Tamil.
2. **Statutory Chemical Compliance**: Strict adherence to approved insecticides, banned compound elimination, and exact dilution ratios.
3. **Meteorological Contingency Planning**: Correct recommendation of delayed sowing, drainage, or moisture conservation during erratic monsoon events.

---

## 8. End-to-End System Architecture

```
                       [Farmer Query / Input Interface]
                        (Audio Voice Note / Text Input)
                                       │
                                       ▼
                   [IndicWav2Vec / Whisper-Tamil STT Engine]
                                       │
                                       ▼
             +---------------------------------------------------+
             |               Context Enrichment Layer            |
             |   - Real-Time IMD Weather Telemetry Retrieval     |
             |   - TNAU Weekly Agro-Met Advisory Retrieval       |
             +---------------------------------------------------+
                                       │
                                       ▼
             +---------------------------------------------------+
             |             Agri-Sovereign-2B Engine              |
             |    - Hosted via vLLM / TensorRT-LLM               |
             |    - PagedAttention & Continuous Request Batching |
             +---------------------------------------------------+
                                       │
                                       ▼
             +---------------------------------------------------+
             |         CIBRC Safety & Dosage Filter Guard        |
             |  - Screening against approved agrochemical table  |
             |  - Enforcing 5-Part Advisory Framework Structure  |
             +---------------------------------------------------+
                                       │
                                       ▼
                      [Dual Multimodal Output Gateway]
                      ├── Structured Visual Advisory Card
                      └── IndicTTS Synthesized Tamil Audio
```

---

## 9. Proposal Evaluation Summary for LLM Forge 2026

- **Authentic Foundation Engineering**: Implements morpheme-aware tokenization, embedding layer alignment, distributed continual pre-training, and scaling optimization rather than just wrapping a proprietary API.
- **Societal and Institutional Relevance**: Rooted in TNAU research and designed for the agro-ecological conditions of the Coimbatore and Pollachi agricultural belt, providing direct value to local farmers and agricultural bodies.
- **Methodical Compute Feasibility**: Sizing the architecture at 2.1B parameters across 4.5B tokens ensures realistic, stable training and edge deployment within hackathon operational timelines.

---

## 10. Works Cited

1. Indic LLMs Sarvam Krutrim BharatGPT 2026 | pdpspectra, `https://pdpspectra.com/blog/india-vernacular-llms-bharatgpt-sarvam-krutrim/`
2. Efficient Continual Pre-training for Building Domain Specific Large Language Models, `https://www.researchgate.net/publication/384218182`
3. VinodAnbalagan/tamil-agri-dataset-: Tamil agriculture advisory QA, `https://github.com/VinodAnbalagan/tamil-agri-dataset-`
4. Android application development for identifying maize infested with fall armyworms with TNAU IPM capsules, `https://www.researchgate.net/publication/362059666`
5. TNAU Agritech Portal, `http://www.agritech.tnau.ac.in/`
6. Automated disease classification in agricultural crops, `https://www.tandfonline.com/doi/full/10.1080/00051144.2020.1728911`
7. வேர்ச்சொல் (VerChol) - arXiv, `https://arxiv.org/pdf/2603.05883`
8. Sarvam AI - AI Engineer Interview Questions, `https://github.com/ombharatiya/AI-Engineer-Interview-Questions`
9. Introducing Pragna-1B: Soket AI Labs' Multilingual LLM, `https://soket.ai/blogs/pragna_1b`
10. Sarvam 1: The first Indian language LLM, `https://www.sarvam.ai/blogs/sarvam-1`
11. Thomson: Continual Learning of Frontier Models for SovereignAI, `https://arxiv.org/html/2608.27147v1`
12. Building Synthetic Pretraining Data at Scale for Indic Languages, AAAI, `https://ojs.aaai.org/index.php/AAAI/article/view/40524/44485`
13. Pre-training Small Base LMs with Fewer Tokens, arXiv, `https://arxiv.org/html/2404.08634v1`
14. Anticipatory Recovery from Catastrophic Interference via Structured Training, `https://mengyeren.com/research/2024/reawakening-knowledge-anticipatory-recovery-from-catastrophic-interference-via-structured-training/`
15. Turkish Models Trained from Scratch and Continually Pre-trained, arXiv, `https://arxiv.org/html/2601.16018v1`
16. AI4Bharat Large-Scale Pretraining, `https://www.emergentmind.com/topics/ai4bharat-s-large-scale-pretraining`
17. FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness, `https://github.com/dao-ailab/flash-attention`
18. Rice Diseases - TNAU Agritech Portal :: Crop Protection, `https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_cereals_rice_main.html`
19. Meta showcases open-source AI solutions for India at Build with AI, `https://www.fonearena.com/blog/438749/meta-build-with-ai-summit-open-source-ai-solutions-india.html`
20. FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision, `https://www.researchgate.net/publication/397199896`
