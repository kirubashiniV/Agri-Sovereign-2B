"""
Live Groq API & End-to-End Pipeline Verification Script
Executes live Groq connectivity and measures real HTTP latency without leaking API keys.
"""

import os
import sys
import time
import json
import asyncio
import httpx
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Load environment
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

from services.llm_provider import GroqProvider, get_llm_provider
from scripts.build_agricultural_rag import AgriculturalRAGEngine
from scripts.safety_validator import CIBRCSafetyValidator
from fastapi.testclient import TestClient
from app.main import app


async def verify_groq_live():
    print("=" * 80)
    print("🌾 LIVE GROQ API & END-TO-END PIPELINE VERIFICATION")
    print("=" * 80)

    # 1. Inspect environment variables without printing secret
    raw_key = os.getenv("GROQ_API_KEY", "").strip()
    has_key = len(raw_key) > 5 and raw_key.startswith("gsk_")
    key_length = len(raw_key)
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()
    provider_name = os.getenv("LLM_PROVIDER", "groq").strip()

    print(f"\n1. Environment Configuration:")
    print(f"  • LLM_PROVIDER       : {provider_name}")
    print(f"  • GROQ_API_KEY Set   : {'YES (Valid Prefix gsk_)' if has_key else 'NO / UNSET'}")
    print(f"  • Key Character Count: {key_length if has_key else 0}")
    print(f"  • GROQ_MODEL         : {model}")
    print(f"  • GROQ_BASE_URL      : {base_url}")

    if not has_key:
        print("\n❌ [ERROR] GROQ_API_KEY is not set or does not start with 'gsk_'. Please ensure .env contains a valid key.")
        return False

    # 2. Test raw direct HTTP call to Groq to verify model and connectivity
    print(f"\n2. Testing Direct Groq HTTP Connectivity to {base_url}/chat/completions:")
    headers = {
        "Authorization": f"Bearer {raw_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a test assistant. Reply with: OK-LIVE-GROQ-CONNECTED"},
            {"role": "user", "content": "Ping test."},
        ],
        "max_tokens": 20,
        "temperature": 0.0,
    }

    t0 = time.monotonic()
    http_status = None
    direct_success = False
    direct_response_text = ""

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
        t_direct = round((time.monotonic() - t0) * 1000, 2)
        http_status = resp.status_code

        if resp.status_code == 200:
            direct_success = True
            data = resp.json()
            direct_response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            usage = data.get("usage", {})
            print(f"  • HTTP Status Code   : {http_status} OK")
            print(f"  • Direct HTTP Latency: {t_direct} ms")
            print(f"  • Response Text      : '{direct_response_text}'")
            print(f"  • Tokens Consumed    : Prompt={usage.get('prompt_tokens')}, Completion={usage.get('completion_tokens')}")
            print(f"  • Result             : ✅ DIRECT HTTP CALL SUCCESSFUL")
        else:
            print(f"  • HTTP Status Code   : {http_status}")
            print(f"  • Direct HTTP Latency: {t_direct} ms")
            try:
                err_data = resp.json()
                print(f"  • Error Message      : {err_data.get('error', {}).get('message', 'Unknown error')}")
                print(f"  • Error Type         : {err_data.get('error', {}).get('type', 'Unknown type')}")
            except Exception:
                print(f"  • Error Body         : {resp.text[:200]}")
            print(f"  • Result             : ❌ DIRECT HTTP CALL FAILED")
            return False

    except Exception as e:
        t_direct = round((time.monotonic() - t0) * 1000, 2)
        print(f"  • Connection Exception: {type(e).__name__} ({str(e)})")
        print(f"  • Latency            : {t_direct} ms")
        print(f"  • Result             : ❌ CONNECTION FAILED")
        return False

    # 3. Test Full Pipeline via /api/query
    print(f"\n3. Testing End-to-End Pipeline (RAG -> GroqProvider -> Safety -> /api/query):")
    client = TestClient(app)
    query_text = "மக்காச்சோளப் பயிரில் படைப்புழு தாக்குதல் மேலாண்மை முறை என்ன?"

    t_api0 = time.monotonic()
    api_resp = client.post("/api/query", json={
        "text": query_text,
        "crop": "Maize",
        "district": "Coimbatore",
        "mode": "farmer"
    })
    t_api_total = round((time.monotonic() - t_api0) * 1000, 2)

    if api_resp.status_code == 200:
        res_data = api_resp.json()
        telemetry = res_data.get("telemetry", {})
        safety_data = res_data.get("safety", {})
        model_field = res_data.get("model", "")
        fallback_used = telemetry.get("fallback_used", True)

        print(f"  • HTTP Status        : {api_resp.status_code} OK")
        print(f"  • Model Reported     : {model_field}")
        print(f"  • Fallback Used      : {fallback_used} ({'❌ Still Falling Back' if fallback_used else '✅ LIVE GROQ ENGINE ACTIVE'})")
        print(f"  • RAG Latency        : {telemetry.get('rag_ms')} ms")
        print(f"  • LLM Latency        : {telemetry.get('llm_ms')} ms")
        print(f"  • Safety Latency     : {telemetry.get('safety_ms')} ms")
        print(f"  • Measured Total     : {telemetry.get('total_ms')} ms")
        print(f"  • Input Tokens       : {telemetry.get('input_tokens')}")
        print(f"  • Output Tokens      : {telemetry.get('output_tokens')}")
        print(f"  • Safety Status      : {safety_data.get('status')}")
        print(f"  • Detected Chemicals : {safety_data.get('detected_chemicals')}")
        print(f"  • Sources Grounded   : {len(res_data.get('sources', []))} records ({[s['title'] for s in res_data.get('sources', [])]})")
        print(f"\n  --- Response Content Preview ---")
        print(f"{res_data.get('answer_ta', '')[:350]}...")
        print(f"  --------------------------------\n")
        
        pipeline_success = (not fallback_used) and (api_resp.status_code == 200)
        print(f"  • Final Verification : {'✅ GROQ LIVE VERIFICATION PASSED' if pipeline_success else '❌ FALLBACK USED'}")
        return pipeline_success
    else:
        print(f"  • API Error Status   : {api_resp.status_code}")
        print(f"  • API Response       : {api_resp.text}")
        return False


if __name__ == "__main__":
    success = asyncio.run(verify_groq_live())
    sys.exit(0 if success else 1)
