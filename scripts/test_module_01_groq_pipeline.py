"""
Automated Test Verification Suite for Module 0.1: Groq LLM Provider & FastAPI Pipeline
Tests all 8 requirements specified in the master implementation directive.
"""

import asyncio
import os
import sys
import time
import json
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from services.llm_provider import GroqProvider, LocalFallbackProvider, get_llm_provider
from scripts.build_agricultural_rag import AgriculturalRAGEngine
from scripts.safety_validator import CIBRCSafetyValidator


async def run_all_tests():
    print("=" * 85)
    print("🌾 MODULE 0.1 — GROQ LLM PROVIDER & PIPELINE VERIFICATION SUITE")
    print("=" * 85)

    rag = AgriculturalRAGEngine()
    safety = CIBRCSafetyValidator()
    results = []

    # -------------------------------------------------------------
    # TEST 1: Normal Tamil Agricultural Query (End-to-End Pipeline)
    # -------------------------------------------------------------
    print("\n[TEST 1] Normal Tamil Agricultural Query:")
    query_1 = "மக்காச்சோளத்தில் படைப்புழு தாக்குதல் உள்ளது, என்ன மருந்து தெளிக்க வேண்டும்?"
    
    t0 = time.monotonic()
    docs_1 = rag.search(query_1, top_k=2)
    t_rag_1 = round((time.monotonic() - t0) * 1000, 2)
    
    provider_1 = get_llm_provider()
    system_prompt = "You are Uzhavan-Sahayak, an expert agricultural AI. Ground advice strictly in TNAU context. Answer in Tamil."
    user_prompt = f"விவசாயி கேள்வி: {query_1}"
    
    t0_llm = time.monotonic()
    llm_res_1 = await provider_1.generate(system_prompt=system_prompt, user_prompt=user_prompt, context=docs_1)
    t_llm_1 = round((time.monotonic() - t0_llm) * 1000, 2)
    
    t0_safe = time.monotonic()
    safe_res_1 = safety.validate(llm_res_1["text"])
    t_safe_1 = round((time.monotonic() - t0_safe) * 1000, 2)
    
    t_total_1 = round(t_rag_1 + t_llm_1 + t_safe_1, 2)
    
    t1_pass = len(llm_res_1["text"]) > 20 and len(docs_1) > 0
    print(f"  Provider Used : {llm_res_1['provider']} ({llm_res_1['model']})")
    print(f"  Fallback Used : {llm_res_1['fallback_used']}")
    print(f"  RAG Latency   : {t_rag_1} ms")
    print(f"  LLM Latency   : {t_llm_1} ms")
    print(f"  Safety Latency: {t_safe_1} ms")
    print(f"  Total Latency : {t_total_1} ms")
    print(f"  Safety Status : {safe_res_1['status']}")
    print(f"  Response Sample: {llm_res_1['text'][:120]}...")
    print(f"  Result        : {'✅ PASS' if t1_pass else '❌ FAIL'}")
    results.append({"test": "TEST 1: Normal Query", "pass": t1_pass, "latency_ms": t_total_1})

    # -------------------------------------------------------------
    # TEST 2: No API Key -> LocalFallbackProvider
    # -------------------------------------------------------------
    print("\n[TEST 2] Missing API Key Fallback:")
    provider_no_key = GroqProvider(api_key="")
    t0 = time.monotonic()
    res_2 = await provider_no_key.generate(system_prompt=system_prompt, user_prompt=user_prompt, context=docs_1)
    t_2 = round((time.monotonic() - t0) * 1000, 2)
    t2_pass = res_2["provider"] == "local_fallback" and res_2["fallback_used"] is True
    print(f"  Provider Used : {res_2['provider']}")
    print(f"  Latency       : {t_2} ms")
    print(f"  Result        : {'✅ PASS' if t2_pass else '❌ FAIL'}")
    results.append({"test": "TEST 2: No Key Fallback", "pass": t2_pass, "latency_ms": t_2})

    # -------------------------------------------------------------
    # TEST 3: Invalid API Key -> Graceful Local Fallback
    # -------------------------------------------------------------
    print("\n[TEST 3] Invalid API Key Failover:")
    provider_invalid_key = GroqProvider(api_key="gsk_invalid_test_key_1234567890abcdef")
    t0 = time.monotonic()
    res_3 = await provider_invalid_key.generate(system_prompt=system_prompt, user_prompt=user_prompt, context=docs_1)
    t_3 = round((time.monotonic() - t0) * 1000, 2)
    t3_pass = res_3["provider"] == "local_fallback" and res_3["fallback_used"] is True
    print(f"  Provider Used : {res_3['provider']}")
    print(f"  Error Status  : {res_3.get('error_status')}")
    print(f"  Latency       : {t_3} ms")
    print(f"  Result        : {'✅ PASS' if t3_pass else '❌ FAIL'}")
    results.append({"test": "TEST 3: Invalid Key Failover", "pass": t3_pass, "latency_ms": t_3})

    # -------------------------------------------------------------
    # TEST 4: Network Timeout / Unreachable Base URL -> Graceful Failover
    # -------------------------------------------------------------
    print("\n[TEST 4] Network Timeout / Bad URL Failover:")
    provider_bad_url = GroqProvider(api_key="gsk_mock_valid_key", base_url="https://10.255.255.1/invalid")
    t0 = time.monotonic()
    res_4 = await provider_bad_url.generate(system_prompt=system_prompt, user_prompt=user_prompt, context=docs_1)
    t_4 = round((time.monotonic() - t0) * 1000, 2)
    t4_pass = res_4["provider"] == "local_fallback" and res_4["fallback_used"] is True
    print(f"  Provider Used : {res_4['provider']}")
    print(f"  Error Type    : {res_4.get('error_type')}")
    print(f"  Latency       : {t_4} ms")
    print(f"  Result        : {'✅ PASS' if t4_pass else '❌ FAIL'}")
    results.append({"test": "TEST 4: Network Timeout Failover", "pass": t4_pass, "latency_ms": t_4})

    # -------------------------------------------------------------
    # TEST 5: Known Prohibited Chemical -> Safety BLOCK
    # -------------------------------------------------------------
    print("\n[TEST 5] Prohibited Chemical Safety Interception:")
    prohibited_text = "பயிருக்கு Monocrotophos அல்லது Endosulfan 5 மில்லி கலந்து தெளிக்கலாம்."
    safe_res_5 = safety.validate(prohibited_text)
    t5_pass = safe_res_5["status"] == "FAIL" and len(safe_res_5["flags"]) > 0
    print(f"  Input Text    : {prohibited_text}")
    print(f"  Safety Status : {safe_res_5['status']} (Mapped to BLOCK)")
    print(f"  Flags Caught  : {[f['chemical'] for f in safe_res_5['flags']]}")
    print(f"  Result        : {'✅ PASS' if t5_pass else '❌ FAIL'}")
    results.append({"test": "TEST 5: Prohibited Chemical BLOCK", "pass": t5_pass, "latency_ms": 0.5})

    # -------------------------------------------------------------
    # TEST 6: Dangerous Overdosage -> Safety OVERDOSAGE ALERT
    # -------------------------------------------------------------
    print("\n[TEST 6] Overdosage Detection:")
    overdose_text = "Chlorantraniliprole 18.5% SC மருந்தை ஒரு லிட்டர் தண்ணீருக்கு 5.0 மில்லி கலந்து தெளிக்கவும்."
    safe_res_6 = safety.validate(overdose_text)
    t6_pass = safe_res_6["status"] == "FAIL" and any(f["type"] == "OVERDOSAGE_ALERT" for f in safe_res_6["flags"])
    print(f"  Input Text    : {overdose_text}")
    print(f"  Safety Status : {safe_res_6['status']}")
    print(f"  Overdose Flag : {safe_res_6['flags']}")
    print(f"  Result        : {'✅ PASS' if t6_pass else '❌ FAIL'}")
    results.append({"test": "TEST 6: Overdosage Detection", "pass": t6_pass, "latency_ms": 0.5})

    # -------------------------------------------------------------
    # TEST 7: No RAG Result / General Query -> No Fabricated Evidence
    # -------------------------------------------------------------
    print("\n[TEST 7] No RAG Result Handling:")
    general_query = "விண்வெளியில் விவசாயம் செய்வது எப்படி?"
    fallback_prov = LocalFallbackProvider()
    res_7 = await fallback_prov.generate(system_prompt=system_prompt, user_prompt=general_query, context=[])
    t7_pass = "அதிகாரப்பூர்வ தரவுகள்" in res_7["text"] or "KVK" in res_7["text"]
    print(f"  Response      : {res_7['text'][:140]}...")
    print(f"  Result        : {'✅ PASS' if t7_pass else '❌ FAIL'}")
    results.append({"test": "TEST 7: No RAG Fabrication", "pass": t7_pass, "latency_ms": res_7["latency_ms"]})

    # -------------------------------------------------------------
    # TEST 8: API Key Leakage Audit in Logs & Output
    # -------------------------------------------------------------
    print("\n[TEST 8] API Key Leakage Prevention Audit:")
    mock_secret = "gsk_super_secret_test_key_xyz987"
    prov_secret = GroqProvider(api_key=mock_secret)
    out_dict = await prov_secret.generate(system_prompt=system_prompt, user_prompt="test", context=[])
    out_str = json.dumps(out_dict)
    t8_pass = mock_secret not in out_str
    print(f"  Secret in output payload: {'NO (SAFE)' if t8_pass else 'YES (LEAKED!)'}")
    print(f"  Result        : {'✅ PASS' if t8_pass else '❌ FAIL'}")
    results.append({"test": "TEST 8: Zero Secret Leakage", "pass": t8_pass, "latency_ms": 0.1})

    # Summary
    print("\n" + "=" * 85)
    passed_count = sum(1 for r in results if r["pass"])
    print(f"🏆 SUMMARY: {passed_count}/{len(results)} Tests Passed ({(passed_count/len(results))*100:.1f}%)")
    print("=" * 85)
    return passed_count == len(results)


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
