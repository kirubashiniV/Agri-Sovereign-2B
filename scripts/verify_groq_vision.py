"""
Verify Groq Vision Model Capabilities
Safe check using legitimate existing GROQ_API_KEY from .env
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "").strip()
base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
configured_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()

print(f"Configured Text Model: {configured_model}")
print(f"Base URL: {base_url}")
print(f"API Key Present: {'Yes' if api_key else 'No'}")

# 1x1 green pixel PNG as a minimal test image
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

models_to_test = [
    configured_model,
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
    "meta-llama/llama-4-scout-17b-16k"
]

results = {}

for model in models_to_test:
    print(f"\n--- Testing Vision on Model: {model} ---")
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image? Reply concisely in 1 sentence."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{TEST_IMAGE_BASE64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AgriSovereign-VisionCheck/1.0"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            results[model] = {"status": "SUCCESS", "response": content}
            print(f"  [SUCCESS] HTTP 200 - Response: {content}")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        results[model] = {"status": f"HTTP {e.code}", "error": err_msg}
        print(f"  [FAILED] HTTP {e.code} - {err_msg[:200]}")
    except Exception as e:
        results[model] = {"status": "ERROR", "error": str(e)}
        print(f"  [ERROR] {e}")

print("\n" + "="*50)
print("VISION CAPABILITY SUMMARY:")
for m, r in results.items():
    print(f"{m}: {r['status']}")
print("="*50)
