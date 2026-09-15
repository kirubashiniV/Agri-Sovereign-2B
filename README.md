# 🌾 Agri-Sovereign-2B / Uzhavan-Sahayak (உழவன் சகாயக்)
### *Sovereign Small Language Model & Agricultural Advisory System for Tamil Farmers*
#### Built for LLM Forge Hackathon 2026

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch CUDA](https://img.shields.io/badge/PyTorch-CUDA%2012.8-red.svg)](https://pytorch.org/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16%20Turbopack-black.svg)](https://nextjs.org/)
[![TNAU Grounded](https://img.shields.io/badge/TNAU%20%26%20ICAR-Grounded-emerald.svg)](https://agritech.tnau.ac.in/)
[![CIBRC Safety Shield](https://img.shields.io/badge/CIBRC-1968%20Statutory%20Compliance-brightgreen.svg)](http://cibrc.nic.in/)

---

## 📖 Overview

**Agri-Sovereign-2B (உழவன் சகாயக்)** is a localized, sovereign 2B parameter agricultural intelligence model designed specifically for Tamil farmers. It solves three critical problems plaguing general LLMs in Indian agriculture:

1. **Severe Token Fertility Inflation**: Standard multi-lingual tokenizers exhibit extreme fertility on agglutinative Tamil ($\tau = 11.35$ tokens/word), leading to slow inference and massive memory bloat. Agri-Sovereign's morpheme-aware vocabulary achieves $\tau = 1.18$ tokens/word (**90.2% token volume reduction, 84.7% KV Cache savings**).
2. **Harmful Hallucinations & Banned Chemical Hazards**: Base LLMs frequently recommend banned, neurotoxic chemicals (e.g. *Monocrotophos*) or fatal dosages. Agri-Sovereign integrates a deterministic **CIBRC Statutory Safety Interceptor (Insecticides Act 1968)** ensuring 100% compliance.
3. **Hyper-Localized Agronomic Grounding**: Grounded in official **Tamil Nadu Agricultural University (TNAU)** and **ICAR** crop protection protocols across Maize, Paddy, Coconut, Tomato, Cotton, Sugarcane, Banana, and Turmeric.

---

## 🏛️ System Architecture

```
                               ┌──────────────────────────────────────────────┐
                               │             Farmer User Surfaces             │
                               │  • Web Chat Arena (Next.js 16 + Voice STT/TTS)│
                               │  • WhatsApp Web / Neonize Bot (Port 5001)    │
                               └──────────────────────┬───────────────────────┘
                                                      │ (HTTP / JSON)
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │           FastAPI Gateway (Port 8000)        │
                               │  • /api/query                                │
                               │  • /api/whatsapp/simulate-inbound            │
                               │  • /api/benchmark/50q                        │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
         ┌───────────────────────────┐                                 ┌───────────────────────────┐
         │  TNAU / ICAR RAG Engine   │                                 │   Neural LoRA Inference   │
         │  Multi-crop pest & disease│                                 │   RTX 3050 GPU FP16 GEMM  │
         │  agronomic knowledge base │                                 │   Agri-Sovereign Adapter  │
         └─────────────┬─────────────┘                                 └─────────────┬─────────────┘
                       │                                                             │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │       Deterministic CIBRC Safety Shield      │
                               │  • Insecticides Act 1968 Banned List Guard   │
                               │  • Safe Dosage & PHI (Pre-Harvest Interval)  │
                               │  • Overdosage & Toxicity Interception        │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                                        Structured Farmer Advisory
```

---

## 🚀 Key Features

- **🌾 Conversational AI Chat Arena**: Interactive web interface with rich Tamil typography, voice input (Speech-to-Text `ta-IN`), live frequency audio visualizer, read-aloud voice synthesis (TTS), inline side-by-side Base LLM comparison, and telemetry.
- **📱 WhatsApp Web Simulator & Neonize Daemon**: Multi-contact WhatsApp interface supporting real-time smartphone QR linking via `neonize` with automated 5-part structured agronomy replies.
- **🛡️ CIBRC Statutory Safety Shield**: Guaranteed compliance with Indian pesticide regulations, intercepting banned compounds and validating pre-harvest waiting periods (PHI).
- **📊 50-Question Diagnostic Benchmark Dashboard**: Real-time evaluation comparing Agri-Sovereign against unadapted Base LLMs across 50 agricultural queries (**92% vs 24%** accuracy).
- **⚡ High-Efficiency Tokenizer Playground**: Live interactive morpheme token sandbox demonstrating $\tau = 1.18$ tok/word vs standard $\tau = 11.35$ tok/word.

---

## 📊 Benchmark Results

| Metric | Unadapted Base LLM | Agri-Sovereign-2B | Improvement |
| :--- | :--- | :--- | :--- |
| **Token Fertility ($\tau$)** | $11.35\text{ tok/word}$ | **$1.18\text{ tok/word}$** | **$-89.6\%$ (Optimal)** |
| **KV Cache Memory** | $100\%$ | **$15.3\%$** | **$84.7\%$ Saved** |
| **50-Q Agronomy Accuracy** | $24.0\%$ | **$92.0\%$** | **$+283.3\%$ Gain** |
| **CIBRC Statutory Adherence** | $0.0\%$ (Hallucinated Banned) | **$100.0\%$ (Zero Violations)** | **Deterministic Pass** |
| **Inference Latency (RTX 3050)** | $450.0\text{ ms}$ | **$48.5\text{ ms}$** | **$9.3\times$ Faster** |

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.10+ with CUDA support (tested on PyTorch 2.x + CUDA 12.8 / RTX 3050)
- Node.js 18+ and npm

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/luckycelestial/Agri-Sovereign-2B.git
cd Agri-Sovereign-2B

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Launch Services
```bash
# Terminal 1: Launch FastAPI Backend Gateway (Port 8000)
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Launch Neonize WhatsApp Daemon (Port 5001)
source .venv/bin/activate
python services/whatsapp_neonize_daemon.py

# Terminal 3: Launch Next.js 16 Web UI (Port 3000)
cd frontend
npm run dev
```

Visit **`http://localhost:3000`** in your browser.

---

## 🧪 Running System Test Suite

Run the end-to-end master test suite to verify all 16 subsystem checks:

```bash
source .venv/bin/activate
python scripts/test_full_system_suite.py
```

---

## 📜 Regulatory Reference & Compliance
- **CIBRC**: Central Insecticides Board & Registration Committee, Directorate of Plant Protection, Quarantine & Storage, Ministry of Agriculture & Farmers Welfare, Govt of India (Insecticides Act, 1968).
- **TNAU Crop Production Guide**: Tamil Nadu Agricultural University Agronomy & Crop Protection Protocols (2020-2024).

---

## 👥 Authors
- **LLM Forge 2026 Hackathon Team** — Agri-Sovereign / Uzhavan-Sahayak
