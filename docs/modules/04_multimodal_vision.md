# MODULE 0.4 — MULTIMODAL CROP IMAGE → AGRICULTURAL ADVISORY

## 1. Overview & Architecture
Module 0.4 enables multi-modal farmer interaction: farmers can take a live photo or upload an image of an affected crop leaf/pest symptom from their mobile/web interface, coupled with an optional Tamil question.

### Architectural Flow:
```
Farmer Crop Image (Upload / Camera)
         ↓
CropVisionObserver (Groq qwen/qwen3.8-27b Vision / Local Deterministic Fallback)
         ↓
Structured Visual Observations JSON (Symptom features, confidence, summary_ta)
         ↓
AgriculturalRAGEngine.search(observations + query)
         ↓
Authoritative TNAU & ICAR Grounding Context
         ↓
Groq LLM Reasoning (Grounded Tamil Advisory)
         ↓
Deterministic CIBRCSafetyValidator (Pesticide ban & dosage filter)
         ↓
TamilSpeechNormalizer & Asynchronous Edge-TTS Pipeline
         ↓
Next.js UI (Image preview, observations pill, validated Tamil answer, TNAU evidence)
```

## 2. Capability Verification
- **Vision Model**: `qwen/qwen3.8-27b` via Groq OpenAI-compatible endpoint.
- **Multimodal Payload**: Verified with standard base64 data URLs in `user` message `content` array (`{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}`).
- **Structured Observation Prompt**: Strictly instructs the model to act as an objective visual symptom observer (e.g. leaf spots, margin chlorosis, insect boring holes) rather than an authoritative disease diagnostician.
- **Uncertainty & Robustness**: If visual symptoms are ambiguous or confidence is low, the system explicitly advises the farmer to provide a clearer close-up photo rather than hallucinating agricultural diagnoses.

## 3. Automated Verification Results (5/5 Tests Passed)
Verified via `python scripts/test_module_04_multimodal_vision.py`:
1. **TEST 1 (Crop Leaf Image Input)**: PASSED (Returned structured visual observations, retrieved TNAU Blast Disease evidence, generated grounded Tamil advisory, vision latency ~503ms).
2. **TEST 2 (Unclear / Solid Image Input)**: PASSED (Returned low confidence, communicated visual uncertainty gracefully).
3. **TEST 3 (Image + Tamil Question)**: PASSED (Seamlessly integrated query context + visual observations).
4. **TEST 4 (Corrupt Image / Fallback Handling)**: PASSED (Fails over to deterministic local observer, text pathway 100% operational).
5. **TEST 5 (Safety Interception on Multimodal Query)**: PASSED (CIBRC safety validator blocked prohibited chemical query).

## 4. Cost & Constraints Compliance
- **Total Implementation Cost**: ₹0.00 (Zero billing required).
- **Person 1 Isolation**: 0 changes to training code, QLoRA adapters, tokenizers, or model weights.
- **API Continuity**: Extended `POST /api/query` in-place, retaining all existing contracts.
