# 🏛️ Architecture Decision Records (ADR) — Person 2

### Decision 1: Black-Box LLM Provider Abstraction with Groq as Development Engine
* **Date:** 2026-09-16
* **Decision:** Decoupled LLM generation behind `LLMProvider` interface, using `GroqProvider` as the active development engine and `LocalFallbackProvider` as zero-cost offline failover.
* **Reason:** Allows Person 2 to rapidly iterate on full-stack product, RAG, speech, vision, and WhatsApp pipelines without waiting for Person 1's model training to complete.
* **Tradeoff:** LLM responses during development originate from Groq free tier rather than local weights, but the contract and grounding prompts remain 100% identical.
* **Impact:** ₹0 mandatory cost, zero training dependencies, 100% crash protection.

### Decision 2: Strict Pre-LLM Grounding with Authoritative TNAU/ICAR RAG
* **Date:** 2026-09-16
* **Decision:** RAG retrieval executes strictly *before* LLM prompt construction; raw LLM outputs are inspected by deterministic CIBRC safety filters *before* client delivery.
* **Reason:** Prevents hallucinated pesticide dosages and statutory banned chemical usage.
* **Impact:** Full regulatory compliance and verifiable source citations on every query.
