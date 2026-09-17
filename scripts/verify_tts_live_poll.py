import sys
import time
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("Sending live /api/query for Maize...", flush=True)
resp = requests.post(
    "http://127.0.0.1:8000/api/query",
    json={
        "query": "மக்காச்சோளம் படைப்புழு தாக்குதலுக்கு மருந்து என்ன?",
        "crop": "Maize",
        "district": "கோயம்புத்தூர்"
    },
    timeout=30
)
print(f"HTTP Status: {resp.status_code}", flush=True)
data = resp.json()
print(f"Model: {data.get('model')}", flush=True)
print(f"Spoken TA Length: {len(data.get('spoken_ta', ''))}", flush=True)
print(f"Audio ID: {data.get('audio_id')}", flush=True)
print(f"Audio Status: {data.get('audio_status')}", flush=True)

audio_id = data.get("audio_id")
if audio_id:
    for i in range(25):
        time.sleep(1)
        st = requests.get(f"http://127.0.0.1:8000/api/tts/{audio_id}").json()
        print(f"Poll {i+1}: status={st.get('status')} num_chunks={st.get('num_chunks')} tts_ms={st.get('tts_ms')} size={st.get('audio_size_bytes')}", flush=True)
        if st.get("status") == "ready":
            print(f"SUCCESS! Audio Ready URL: {st.get('audio_url')}", flush=True)
            break
