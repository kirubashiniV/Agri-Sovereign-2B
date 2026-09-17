"""
Module 0.2 Verification Script: Farmer Experience, RAG, Groq, Deterministic Safety, and Edge-TTS
Person 2 Verification Suite
"""

import sys
import os
import io
import time
import asyncio
import unittest

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure repository root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.speech_service import TamilSpeechNormalizer, EdgeTTSProvider, speech_service, STATIC_AUDIO_DIR
from scripts.safety_validator import CIBRCSafetyValidator
from services.llm_provider import GroqProvider, get_llm_provider
from app.main import app
from fastapi.testclient import TestClient


class TestModule02FarmerExperience(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.safety_validator = CIBRCSafetyValidator()

    def test_01_tamil_speech_normalizer_dosages_and_numbers(self):
        """Test Tamil phonetic normalization for dosages and numbers."""
        test_cases = [
            ("1.5 ml/L தெளிக்க வேண்டும்", "ஒன்று புள்ளி ஐந்து மில்லி லிட்டர்"),
            ("14 நாட்கள் காத்திருக்க வேண்டும்", "பதினான்கு நாட்கள்"),
            ("500 g தூள் பயன்படுத்தவும்", "ஐந்நூறு கிராம்"),
            ("TNAU பரிந்துரைப்படி CIBRC விதிகளை பின்பற்றவும்", "தமிழ்நாடு வேளாண்மை பல்கலைக்கழகம்"),
        ]
        for raw, expected_substr in test_cases:
            normalized = TamilSpeechNormalizer.normalize(raw)
            self.assertIn(expected_substr, normalized, f"Failed normalizing '{raw}' -> got '{normalized}'")
        print("  [PASS] test_01_tamil_speech_normalizer_dosages_and_numbers")

    async def test_02_edge_tts_synthesis(self):
        """Test zero-cost Edge-TTS Tamil neural speech synthesis."""
        sample_text = "வணக்கம் உழவரே. மக்காச்சோளப் படைப்புழு மேலாண்மைக்கு எமாமெக்டின் பென்சோயேட் பயன்படுத்தலாம்."
        res = await speech_service.synthesize(sample_text)
        
        self.assertIsNotNone(res.get("audio_url"))
        self.assertTrue(res["audio_url"].startswith("/audio/resp_"))
        self.assertTrue(res["audio_url"].endswith(".mp3"))
        
        # Verify file exists on disk
        filename = res["audio_url"].replace("/audio/", "")
        filepath = os.path.join(STATIC_AUDIO_DIR, filename)
        self.assertTrue(os.path.exists(filepath), f"Audio file {filepath} not found on disk")
        self.assertGreater(os.path.getsize(filepath), 1000, "Audio file is too small or empty")
        
        print(f"  [PASS] test_02_edge_tts_synthesis (latency: {res['latency_ms']}ms, file: {filename}, size: {os.path.getsize(filepath)} bytes)")

    def test_03_query_test_1_maize_fall_armyworm(self):
        """Test Demo Query 1: Maize Fall Armyworm."""
        time.sleep(1.5)
        payload = {
            "query": "என் மக்காச்சோளத்தில் படைப்புழு தாக்குதல் உள்ளது. என்ன செய்யலாம்?",
            "crop": "Maize",
            "district": "Coimbatore",
            "mode": "agri_sovereign"
        }
        resp = self.client.post("/api/query", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn("answer_ta", data)
        self.assertIn("audio_url", data)
        self.assertIsNotNone(data["audio_url"])
        self.assertIn("sources", data)
        self.assertGreater(len(data["sources"]), 0)
        self.assertEqual(data["safety"]["verdict"], "PASS")
        self.assertTrue(data["safety"]["is_safe"])
        self.assertGreater(data["telemetry"]["total_ms"], 0)
        
        print(f"  [PASS] test_03_query_test_1_maize_fall_armyworm (total: {data['telemetry']['total_ms']}ms, llm: {data['telemetry']['llm_ms']}ms, tts: {data['telemetry']['tts_ms']}ms)")

    def test_04_query_test_2_paddy_yellowing(self):
        """Test Demo Query 2: Paddy Leaf Yellowing."""
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
        self.assertIn("audio_url", data)
        self.assertIsNotNone(data["audio_url"])
        self.assertEqual(data["safety"]["verdict"], "PASS")
        
        print(f"  [PASS] test_04_query_test_2_paddy_yellowing (total: {data['telemetry']['total_ms']}ms, llm: {data['telemetry']['llm_ms']}ms, tts: {data['telemetry']['tts_ms']}ms)")

    def test_05_query_test_3_monocrotophos_safety_block(self):
        """Test Demo Query 3: Monocrotophos Banned Pesticide Safety BLOCK."""
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
        
        # Verify safety blocked
        self.assertEqual(data["safety"]["verdict"], "FAIL")
        self.assertFalse(data["safety"]["is_safe"])
        self.assertIn("monocrotophos", [c.lower() for c in data["safety"]["banned_chemicals_found"]])
        
        # Verify answer warns the farmer explicitly
        self.assertIn("தடைசெய்யப்பட்ட", data["answer_ta"])
        self.assertIsNotNone(data["audio_url"])
        
        print(f"  [PASS] test_05_query_test_3_monocrotophos_safety_block (safety: FAIL/BLOCK, total: {data['telemetry']['total_ms']}ms)")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING MODULE 0.2 VERIFICATION SUITE")
    print("=" * 60)
    unittest.main()
