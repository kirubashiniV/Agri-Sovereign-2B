"""
Test qwen/qwen3.8-27b with valid sized crop/leaf image
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

# Create a small valid 50x50 PNG in python or load a real sample image
import struct
import zlib

def make_test_png(w=50, h=50, color=(34, 139, 34)): # Forest Green
    raw_data = b"".join(b"\x00" + bytes(color) * w for _ in range(h))
    def chunk(tag, data):
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xffffffff)
    header = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack("!IIBBBBB", w, h, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(raw_data))
    iend = chunk(b"IEND", b"")
    return header + ihdr + idat + iend

png_bytes = make_test_png()
b64_img = base64.b64encode(png_bytes).decode("utf-8")

print(f"Generated test green leaf image ({len(png_bytes)} bytes)")
print(f"Testing model: {configured_model}")

payload = {
    "model": configured_model,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": (
                        "You are an agricultural plant vision observer. Inspect this crop image and output structured JSON with:\n"
                        "- 'crop': estimated crop type or 'unclear'\n"
                        "- 'observations': list of visible symptoms (e.g. leaf color, spot patterns, damage location)\n"
                        "- 'confidence': 'high', 'medium', or 'low'\n"
                        "- 'summary_ta': short 1-sentence Tamil description of visible symptoms\n"
                        "Output ONLY valid JSON."
                    )
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64_img}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 300,
    "temperature": 0.1
}

req = urllib.request.Request(
    f"{base_url}/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        print("\n[SUCCESS] HTTP 200 OK from Groq!")
        print(f"Vision Response:\n{content}")
except urllib.error.HTTPError as e:
    print(f"\n[FAILED] HTTP {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"\n[ERROR]: {e}")
