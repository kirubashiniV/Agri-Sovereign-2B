# 📦 Module 0.1: Groq LLM Provider & Live Pipeline Verification

## Status
**PASS** (100.0% — Live Groq API Connectivity & End-to-End Pipeline Verified)

---

## 1. Objective
Establish and verify the black-box `LLMProvider` using official Groq API developer access (`https://api.groq.com/openai/v1/chat/completions`) wired into the complete text pipeline:
$$\mathbf{Farmer\ Query} \longrightarrow \mathbf{Local\ TNAU\ RAG} \longrightarrow \mathbf{Live\ Groq\ (Qwen-27B)} \longrightarrow \mathbf{CIBRC\ Safety\ Validator} \longrightarrow \mathbf{QueryResponse}$$

---

## 2. Live Groq Verification Results

* **Authentication:** **SUCCESS (HTTP 200)**
* **Endpoint:** `https://api.groq.com/openai/v1/chat/completions`
* **Model Used:** `qwen/qwen3.8-27b`
* **Fallback Used:** `False` (**Live Groq Provider Active**)
* **RAG Retrieval:** **2 Authoritative TNAU Records Retrieved** (*Maize FAW & Cotton PBW*)
* **Safety Status:** **PASS** (CIBRC Compliant)
* **Detected Chemicals:** `['azadirachtin', 'chlorantraniliprole', 'emamectin benzoate']`

### Measured Telemetry Breakdown:
* **RAG Latency (`rag_ms`):** $0.41\text{ ms}$
* **LLM Latency (`llm_ms`):** $2,354.69\text{ ms}$
* **Safety Latency (`safety_ms`):** $2.35\text{ ms}$
* **Total Measured Pipeline Latency (`total_ms`):** $2,357.62\text{ ms}$
* **Input Tokens:** $535$
* **Output Tokens:** $560$

---

## 3. Automated Test Suite (8/8 Tests Passed — 100.0%)

| # | Test Scenario | Verified Behavior | Status | Measured Latency |
| :--- | :--- | :--- | :--- | :--- |
| **TEST 1** | Normal Tamil Agricultural Query | Grounded in TNAU context, returns live Groq Tamil advisory | **✅ PASS** | $2,938.36\text{ ms}$ (`fallback_used=False`) |
| **TEST 2** | Missing API Key | Seamlessly uses `LocalFallbackProvider` | **✅ PASS** | $1,839.62\text{ ms}$ |
| **TEST 3** | Invalid API Key | Catches HTTP 401 and routes to fallback without crashing | **✅ PASS** | $1,022.82\text{ ms}$ |
| **TEST 4** | Timeout / Unreachable URL | Catches connection error and routes to fallback | **✅ PASS** | $12,591.15\text{ ms}$ |
| **TEST 5** | Prohibited Chemical | Intercepts *Monocrotophos / Endosulfan* with `status="BLOCK"` | **✅ PASS** | $0.50\text{ ms}$ |
| **TEST 6** | Dangerous Overdosage | Flags *Chlorantraniliprole 5.0 ml/L* ($> 2\times$ threshold) with `OVERDOSAGE_ALERT` | **✅ PASS** | $0.50\text{ ms}$ |
| **TEST 7** | No RAG Result | Returns polite unverified notice without inventing evidence | **✅ PASS** | $0.18\text{ ms}$ |
| **TEST 8** | API Key Leakage Audit | Confirms API keys never leak to responses, logs, or error payloads | **✅ PASS** | $0.10\text{ ms}$ |

---

## 4. Live API Response Sample (`POST /api/query`)

```json
{
  "answer_ta": "வணக்கம்! கோயம்புத்தூர் மாவட்டத்தில் மக்காச்சோளப் பயிரில் படைப்புழு (Fall Armyworm) தாக்குதலைக் கட்டுப்படுத்த, TNAU/ICAR ஆராய்ச்சி அடிப்படையில் பின்வரும் முறைகளைப் பின்பற்றவும்:\n\n**1. உயிரியல் மேலாண்மை (Biological Management):**\n*   **வேப்பங்கொட்டைச்சாறு (NSKE):** 5% அடர்த்தியில் தயார் செய்து தெளிக்கவும்.\n*   **அசாடிராக்டின் (Azadirachtin):** 1500 ppm மருந்தை ஒரு லிட்டர் தண்ணீருக்கு 5 மில்லி என்ற அளவில் கலந்து தெளிக்கவும்.\n*   டிரைக்கோடெர்மா மற்றும் இனக்கவர்ச்சிப் பொறிகளை ஏக்கருக்கு 5 வீதம் வயலில் வைக்கவும்.\n\n**2. இரசாயன மேலாண்மை (Chemical Management):**\n*   **Chlorantraniliprole 18.5% SC:** ஒரு லிட்டர் தண்ணீருக்கு 0.4 மில்லி (ஏக்கருக்கு 80 மில்லி) கலந்து பயிரின் நடுக்குருத்தில் படும்படி தெளிக்கவும்.\n*   அல்லது **Emamectin Benzoate 5% SG:** ஒரு லிட்டர் தண்ணீருக்கு 0.5 கிராம் (ஏக்கருக்கு 100 கிராம்) கலந்து தெளிக்கவும்.\n\n**3. பாதுகாப்பு மற்றும் காத்திருப்பு காலம் (PHI):**\n*   அறுவடைக்கு முன் காத்திருப்பு காலம்: 14 நாட்கள்.\n*   பாதுகாப்பு முகக்கவசம் மற்றும் கையுறை அணிந்து தெளிக்கவும்.",
  "spoken_ta": "வணக்கம்! கோயம்புத்தூர் மாவட்டத்தில் மக்காச்சோளப் பயிரில் படைப்புழு...",
  "audio_url": null,
  "sources": [
    {
      "title": "Maize (மक्काச்சோளம்) — Fall Armyworm (படைப்புழு - Spodoptera frugiperda)",
      "source": "TNAU Agritech Portal & ICAR",
      "url": "https://agritech.tnau.ac.in",
      "id": "TNAU_MAIZE_FAW_01"
    }
  ],
  "safety": {
    "status": "PASS",
    "warnings": [],
    "detected_chemicals": [
      "azadirachtin",
      "chlorantraniliprole",
      "emamectin benzoate"
    ],
    "is_safe": true
  },
  "model": "groq (qwen/qwen3.8-27b)",
  "telemetry": {
    "rag_ms": 0.41,
    "llm_ms": 2354.69,
    "safety_ms": 2.35,
    "total_ms": 2357.62,
    "input_tokens": 535,
    "output_tokens": 560,
    "fallback_used": false
  },
  "response": "வணக்கம்! கோயம்புத்தூர் மாவட்டத்தில்...",
  "mode": "farmer",
  "evidence": {
    "id": "TNAU_MAIZE_FAW_01",
    "crop": "Maize (மக்காச்சோளம்)",
    "pest_disease": "Fall Armyworm (படைப்புழு - Spodoptera frugiperda)"
  }
}
```

---

## 5. Security & Isolation Confirmation
* The `GROQ_API_KEY` remains securely loaded in `.env` (gitignored).
* No secrets are printed, logged, or serialized into JSON responses.
* Zero external cost incurred (runs on free developer credits).
