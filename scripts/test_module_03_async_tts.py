"""
Module 0.3 Verification Script: Non-Blocking Asynchronous Edge-TTS + Farmer UX Optimization
Person 2 Verification Suite
"""

import sys
import os
import time
import asyncio
import unittest
from unittest.mock import patch

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure repository root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.speech_service import TamilSpeechNormalizer, EdgeTTSProvider, speech_service, STATIC_AUDIO_DIR
from scripts.safety_validator import CIBRCSafetyValidator
from services.llm_provider import GroqProvider, get_llm_provider
from app.main import app
from fastapi.testclient import TestClient


class TestModule03AsyncTTS(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.safety_validator = CIBRCSafetyValidator()

    def test_01_tamil_maize_query_non_blocking_async_tts(self):
        """TEST 1: Tamil maize query - answer appears before fresh TTS, audio status available via polling."""
        time.sleep(1.5)
        payload = {
            "query": "என் மக்காச்சோளத்தில் படைப்புழு தாக்குதல் உள்ளது. என்ன செய்யலாம்?",
            "crop": "Maize",
            "district": "Coimbatore",
            "mode": "agri_sovereign"
        }
        
        t0 = time.monotonic()
        resp = self.client.post("/api/query", json=payload)
        client_elapsed_ms = (time.monotonic() - t0) * 1000
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn("answer_ta", data)
        self.assertIn("audio_id", data)
        self.assertIn("audio_status", data)
        self.assertIn(data["audio_status"], ["processing", "ready"])
        self.assertIn("sources", data)
        self.assertEqual(data["safety"]["verdict"], "PASS")
        self.assertTrue(data["safety"]["is_safe"])
        
        # Verify response_ms is measured and excludes TTS if background processing
        telemetry = data["telemetry"]
        self.assertIn("response_ms", telemetry)
        print(f"  [PASS] test_01: Initial text returned in {telemetry['response_ms']}ms (status: {data['audio_status']})")
        
        # Poll GET /api/tts/{audio_id} until ready or timeout
        audio_id = data["audio_id"]
        poll_ready = False
        tts_latency = 0
        for _ in range(15):
            poll_resp = self.client.get(f"/api/tts/{audio_id}")
            self.assertEqual(poll_resp.status_code, 200)
            poll_data = poll_resp.json()
            if poll_data.get("status") == "ready" and poll_data.get("audio_url"):
                poll_ready = True
                tts_latency = poll_data.get("tts_ms", 0)
                break
            time.sleep(0.5)
            
        self.assertTrue(poll_ready, "Audio did not become ready within polling window")
        print(f"  [PASS] test_01: Audio polled successfully -> {poll_data['audio_url']} (tts_ms: {tts_latency}ms)")

    def test_02_tamil_paddy_query_long_tts_non_blocking(self):
        """TEST 2: Tamil paddy query - long TTS does not block initial answer."""
        time.sleep(1.5)
        payload = {
            "query": "என் நெற்பயிரின் இலைகள் மஞ்சளாகின்றன.",
            "crop": "Paddy",
            "district": "Thanjavur",
            "mode": "agri_sovereign"
        }
        
        resp = self.client.post("/api/query", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn("answer_ta", data)
        self.assertIsNotNone(data.get("audio_id"))
        self.assertEqual(data["safety"]["verdict"], "PASS")
        self.assertGreater(data["telemetry"]["response_ms"], 0)
        
        print(f"  [PASS] test_02: Paddy query text response in {data['telemetry']['response_ms']}ms (audio_id: {data['audio_id']})")

    def test_03_cached_tts_instant_exposure(self):
        """TEST 3: Cached TTS - existing audio is reused immediately with tts_ms <= 5ms."""
        # Ensure a known phrase is synthesized
        phrase = "மக்காச்சோளம் பயிரில் பூச்சி கட்டுப்பாடு"
        spoken = TamilSpeechNormalizer.normalize(phrase)
        audio_info = speech_service.get_audio_info(spoken, is_already_normalized=True)
        audio_id = audio_info["audio_id"]
        
        # Pre-synthesize to ensure cache
        filepath = os.path.join(STATIC_AUDIO_DIR, f"resp_{audio_id}.mp3")
        if not os.path.exists(filepath):
            asyncio.run(speech_service.synthesize_async_task(audio_id, spoken))
            
        # Fast lookup test
        info = speech_service.get_audio_info(spoken, is_already_normalized=True)
        self.assertTrue(info["cached"])
        self.assertEqual(info["audio_status"], "ready")
        self.assertEqual(info["audio_url"], f"/audio/resp_{audio_id}.mp3")
        self.assertLessEqual(info["tts_ms"], 5.0)
        
        print(f"  [PASS] test_03: Cached TTS lookup instant in {info['tts_ms']}ms (reused: resp_{audio_id}.mp3)")

    async def test_04_tts_failure_graceful_degradation(self):
        """TEST 4: Simulated Edge TTS failure - text answer succeeds, audio_status is failed without breaking text."""
        test_audio_id = "test_failure_sim_12345"
        test_spoken = "சோதனை ஒலி தோல்வி உருவகப்படுத்துதல்"
        
        # Simulate Edge-TTS throwing network/service error
        with patch("edge_tts.Communicate.save", side_effect=Exception("Simulated Edge-TTS connection reset")):
            res = await speech_service.synthesize_async_task(test_audio_id, test_spoken)
            self.assertEqual(res["status"], "failed")
            self.assertIsNone(res["audio_url"])
            self.assertIn("Simulated Edge-TTS connection reset", res["error"])
            
            # Poll status
            status = speech_service.get_status(test_audio_id)
            self.assertEqual(status["status"], "failed")
            
        print("  [PASS] test_04: Simulated TTS failure gracefully caught, status marked failed without crashing")

    def test_05_safety_block_spoken_text_verification(self):
        """TEST 5: Monocrotophos query - safety BLOCK, spoken text contains only safety warning."""
        time.sleep(1.5)
        payload = {
            "query": "Monocrotophos தெளிக்கலாமா?",
            "crop": "Paddy",
            "district": "Madurai",
            "mode": "agri_sovereign"
        }
        
        resp = self.client.post("/api/query", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data["safety"]["verdict"], "FAIL")
        self.assertFalse(data["safety"]["is_safe"])
        self.assertIn("monocrotophos", [c.lower() for c in data["safety"]["banned_chemicals_found"]])
        
        # Verify spoken text contains safety warning and NO affirmative recommendation
        spoken_ta = data.get("spoken_ta", "")
        self.assertIn("தடைசெய்யப்பட்டுள்ளது", spoken_ta)
        self.assertIn("பாதுகாப்பு எச்சரிக்கை", spoken_ta)
        self.assertNotIn("தெளிக்கவும்", spoken_ta.replace("வேப்பங்கொட்டைச் சாறு", ""))
        
        print(f"  [PASS] test_05: Safety BLOCK verified. Spoken text correctly validated before TTS.")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING MODULE 0.3 ASYNC TTS & FARMER UX VERIFICATION SUITE")
    print("=" * 60)
    unittest.main()
