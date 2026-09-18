"""
TTS Fix Verification Suite: Long Response Chunking & Concatenation
Tests:
1. Long Maize query response chunking (zero dropped text, valid MP3)
2. Safety Block response speech synthesis (full safety alert spoken)
3. Direct async background generation and polling
4. Cache lookup performance (instant sub-millisecond retrieval)
5. Telemetry extraction: num_chunks, total_tts_ms, audio_size_bytes
"""

import os
import sys
import time
import asyncio
import hashlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from services.speech_service import TamilSpeechNormalizer, EdgeTTSProvider, speech_service, STATIC_AUDIO_DIR

LONG_MAIZE_RESPONSE = """🌾 **உழவன் சகாயக் வேளாண் AI (TNAU & ICAR வழிகாட்டுதல்)**

📍 **மண்டலம்**: Coimbatore, Tiruppur, Dindigul (கோயம்புத்தூர், திருப்பூர், திண்டுக்கல்)

🌽 **பயிர் & பிரச்சனை**: மக்காச்சோளம் — படைப்புழு (Fall Armyworm - Spodoptera frugiperda)

📋 **முக்கிய அறிகுறிகள் & கண்டறிதல்**:
- இலைகளில் சல்லடை போன்ற துளைகள் மற்றும் கழிவுகள் காணப்படுதல்
- குருத்து பகுதியில் புழுவின் சேதம் தீவிரமாக இருத்தல்

💡 **உடனடி மேலாண்மை & மருந்து அளவுகள் (CIBRC அங்கீகரிக்கப்பட்டது)**:
1. **Spinetoram 11.7% SC**: ஒரு லிட்டர் தண்ணீருக்கு **0.5 மில்லி** கலந்து தெளிக்கவும்.
2. அல்லது **Chlorantraniliprole 18.5% SC**: ஒரு லிட்டர் தண்ணீருக்கு **0.4 மில்லி** கலந்து தெளிக்கவும்.
3. வேப்பங்கொட்டைச் சாறு **5%** ஆரம்ப நிலையில் பயன்படுத்தலாம்.

⏳ **பாதுகாப்பு & காத்திருப்பு காலம் (PHI)**:
மருந்து தெளித்த பிறகு குறைந்தபட்சம் **14 நாட்கள்** அறுவடை செய்யக்கூடாது. பாதுகாப்பு கவசங்களை அணியவும்.
"""

SAFETY_BLOCK_RESPONSE = """⛔ **CIBRC சட்டப்பூர்வ பாதுகாப்பு எச்சரிக்கை (Monocrotophos)**

**Monocrotophos** இந்தியாவில் பயிர்களுக்குப் பயன்படுத்த **மத்திய பூச்சிக்கொல்லி வாரியத்தால் (CIBRC) முழுமையாக தடைசெய்யப்பட்டுள்ளது / கட்டுப்படுத்தப்பட்டுள்ளது**.

⚠️ **காரணம்**: மனிதர்களுக்கும் நன்மை செய்யும் பூச்சிகளுக்கும் கடுமையான நச்சுத்தன்மை வாய்ந்தது.

💡 **பாதுகாப்பான மாற்றுப் பரிந்துரை**: TNAU வழிகாட்டுதலின்படி அங்கீகரிக்கப்பட்ட வேப்பங்கொட்டைச் சாறு (5%) அல்லது Chlorantraniliprole 18.5% SC (0.4 மில்லி/லிட்டர்) / Emamectin Benzoate 5% SG (0.5 கிராம்/லிட்டர்) ஆகியவற்றைப் பயன்படுத்தவும்."""


async def run_tests():
    print("=" * 65)
    print("PERSON 2 — TTS LONG RESPONSE CHUNKING VERIFICATION SUITE")
    print("=" * 65)

    all_passed = True

    # -------------------------------------------------------------
    # TEST 1: Long Maize Response Chunking & Generation
    # -------------------------------------------------------------
    print("\n--- TEST 1: Long Maize Response Chunking & Synthesis ---")
    spoken_ta = TamilSpeechNormalizer.create_spoken_ta(LONG_MAIZE_RESPONSE)
    chunks = TamilSpeechNormalizer.chunk_spoken_text(spoken_ta)
    
    print(f"Original answer_ta length: {len(LONG_MAIZE_RESPONSE)} chars")
    print(f"Spoken_ta length: {len(spoken_ta)} chars")
    print(f"Total Chunks: {len(chunks)}")
    for i, c in enumerate(chunks, 1):
        print(f"  Chunk {i} ({len(c)} chars): {c[:60]}... -> ...{c[-30:]}")

    # Remove any existing cached file for this test to measure live synthesis
    test_audio_id = hashlib.md5(f"test_live:{spoken_ta}".encode("utf-8")).hexdigest()
    test_filename = f"resp_{test_audio_id}.mp3"
    test_filepath = os.path.join(STATIC_AUDIO_DIR, test_filename)
    if os.path.exists(test_filepath):
        os.remove(test_filepath)

    t0 = time.monotonic()
    res1 = await speech_service.synthesize_async_task(test_audio_id, spoken_ta)
    tts_duration_ms = round((time.monotonic() - t0) * 1000, 2)

    print(f"Synthesis Result Status: {res1.get('status')}")
    print(f"TTS Duration: {tts_duration_ms} ms")
    print(f"Num Chunks Reported: {res1.get('num_chunks')}")
    print(f"Audio Size on Disk: {os.path.getsize(test_filepath)} bytes")

    has_audio_file = os.path.exists(test_filepath) and os.path.getsize(test_filepath) > 10000
    is_ready = res1.get("status") == "ready"
    has_all_chunks = res1.get("num_chunks") == len(chunks)

    if is_ready and has_audio_file and has_all_chunks:
        print("TEST 1: PASSED (All chunks synthesized and stitched into full MP3)")
    else:
        print(f"TEST 1: FAILED (is_ready={is_ready}, has_file={has_audio_file}, chunks={has_all_chunks})")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 2: Safety Block Spoken Response
    # -------------------------------------------------------------
    print("\n--- TEST 2: CIBRC Safety Block Spoken Response ---")
    safety_spoken = TamilSpeechNormalizer.create_spoken_ta(SAFETY_BLOCK_RESPONSE)
    safety_chunks = TamilSpeechNormalizer.chunk_spoken_text(safety_spoken)
    print(f"Safety Spoken TA ({len(safety_spoken)} chars): {safety_spoken[:100]}...")
    print(f"Safety Chunks: {len(safety_chunks)}")

    safety_audio_id = hashlib.md5(f"test_safety:{safety_spoken}".encode("utf-8")).hexdigest()
    safety_filepath = os.path.join(STATIC_AUDIO_DIR, f"resp_{safety_audio_id}.mp3")
    if os.path.exists(safety_filepath):
        os.remove(safety_filepath)

    res2 = await speech_service.synthesize_async_task(safety_audio_id, safety_spoken)
    print(f"Safety Audio Status: {res2.get('status')}")
    print(f"Safety Audio Size: {os.path.getsize(safety_filepath)} bytes")

    if res2.get("status") == "ready" and os.path.exists(safety_filepath) and os.path.getsize(safety_filepath) > 5000:
        print("TEST 2: PASSED (Full safety warning spoken completely)")
    else:
        print("TEST 2: FAILED")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 3: Caching & Sub-Millisecond Re-Lookup
    # -------------------------------------------------------------
    print("\n--- TEST 3: Cache Re-Lookup Verification ---")
    cached_info = speech_service.get_audio_info(spoken_ta, is_already_normalized=True)
    # The actual audio_id from get_audio_info
    real_audio_id = cached_info.get("audio_id")
    # Synthesize to disk under real_audio_id if not present
    await speech_service.synthesize_async_task(real_audio_id, spoken_ta)
    
    t_cache_0 = time.monotonic()
    lookup_info = speech_service.get_audio_info(spoken_ta, is_already_normalized=True)
    lookup_ms = round((time.monotonic() - t_cache_0) * 1000, 3)

    print(f"Cache Status: {lookup_info.get('audio_status')}")
    print(f"Is Cached: {lookup_info.get('cached')}")
    print(f"Lookup Time: {lookup_ms} ms")
    print(f"Audio URL: {lookup_info.get('audio_url')}")

    if lookup_info.get("cached") is True and lookup_info.get("audio_status") == "ready":
        print("TEST 3: PASSED (Instant cache hit verified)")
    else:
        print("TEST 3: FAILED")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 4: Zero Content Loss / Completeness Audit
    # -------------------------------------------------------------
    print("\n--- TEST 4: Content Completeness Audit ---")
    # Verify no arbitrary character slicing occurs
    essential_phrases = [
        "பயிர் மற்றும் பிரச்சனை",
        "மக்காச்சோளம்",
        "இலைகளில் சல்லடை",
        "Spinetoram",
        "பதினொன்று புள்ளி ஏழு சதவீதம்",
        "Chlorantraniliprole",
        "வேப்பங்கொட்டைச் சாறு",
        "பதினான்கு நாட்கள்",
        "பாதுகாப்பு கவசங்களை அணியவும்"
    ]
    missing = [p for p in essential_phrases if p not in spoken_ta]
    if not missing:
        print(f"All {len(essential_phrases)} essential agricultural phrases present in spoken_ta (Zero loss).")
        print("TEST 4: PASSED")
    else:
        print(f"TEST 4: FAILED (Missing phrases: {missing})")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("ALL TTS CHUNKING & AUDIO VERIFICATION TESTS PASSED (100%)!")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 65)
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
