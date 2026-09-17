"""
Vision Observation Service
Person 2 Implementation: Multimodal Crop Image Symptom Observation Pipeline
Extracts structured visual observations without diagnostic over-confidence,
grounding findings strictly in TNAU/ICAR agricultural evidence.
"""

import os
import re
import json
import time
import base64
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

logger = logging.getLogger("uzhavan.vision")

class CropVisionObserver:
    """
    Multimodal visual observation extractor using Groq qwen/qwen3.8-27b.
    Converts crop images into objective symptom observations rather than speculative diagnoses.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.model = model or os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()
        self.base_url = (base_url or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")).rstrip("/")

    def extract_observations(
        self,
        image_base64: str,
        user_query: Optional[str] = None,
        crop_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes image_base64 and returns structured visual observations.
        """
        if not image_base64 or not image_base64.strip():
            return {
                "has_image": False,
                "crop": "unclear",
                "observations": [],
                "confidence": "none",
                "summary_ta": "",
                "vision_ms": 0.0
            }

        # Normalize data URI vs raw base64
        clean_b64 = image_base64
        mime_type = "image/jpeg"
        if "data:image/" in image_base64 and ";base64," in image_base64:
            parts = image_base64.split(";base64,")
            clean_b64 = parts[1].strip()
            mime_match = re.search(r'data:(image/\w+);', parts[0])
            if mime_match:
                mime_type = mime_match.group(1)

        t0 = time.monotonic()

        # If no API key configured, use local fallback observation
        if not self.api_key:
            return self._local_fallback_observation(t0, crop_hint)

        prompt = (
            "You are an agricultural plant pathologist visual observer for Tamil Nadu crops. "
            "Inspect the provided crop image carefully and output ONLY a valid JSON object with the following schema:\n"
            "{\n"
            '  "crop": "<estimated crop: Maize, Paddy, Coconut, Sugarcane, Cotton, Turmeric, Tomato, Banana, or unclear>",\n'
            '  "observations": ["<visible symptom 1>", "<visible symptom 2>"],\n'
            '  "confidence": "<high | medium | low>",\n'
            '  "summary_ta": "<concise 1-sentence Tamil description of visible symptoms>"\n'
            "}\n\n"
            "Strict Rules:\n"
            "1. Do NOT diagnose a specific disease as definite. State ONLY visible symptoms (e.g. leaf spots, color changes, hole patterns, lesion shapes).\n"
            "2. If the image is blurry, lacks clear plant disease features, or is non-agricultural, set confidence to 'low', crop to 'unclear', "
            "and summary_ta to 'படத்தில் அறிகுறிகள் தெளிவாக இல்லை. அருகிலிருந்து தெளிவான புகைப்படத்தை வழங்கவும்.'\n"
            "3. Output ONLY the JSON object, nothing else."
        )

        if crop_hint:
            prompt += f"\nNote: Farmer indicates this is: {crop_hint}"
        if user_query:
            prompt += f"\nFarmer question: {user_query}"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{clean_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 350,
            "temperature": 0.1
        }

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"].strip()
                vision_ms = round((time.monotonic() - t0) * 1000, 2)

                # Strip markdown code blocks if model wrapped JSON
                cleaned_json = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
                cleaned_json = re.sub(r'\s*```$', '', cleaned_json, flags=re.MULTILINE).strip()

                parsed = json.loads(cleaned_json)
                return {
                    "has_image": True,
                    "crop": parsed.get("crop", crop_hint or "unclear"),
                    "observations": parsed.get("observations", []),
                    "confidence": parsed.get("confidence", "medium"),
                    "summary_ta": parsed.get("summary_ta", ""),
                    "raw_response": content,
                    "vision_ms": vision_ms
                }
        except Exception as e:
            logger.warning(f"[VISION_OBSERVER] Vision API call failed: {e}. Using fallback observation.")
            return self._local_fallback_observation(t0, crop_hint, error=str(e))

    def _local_fallback_observation(self, t0: float, crop_hint: Optional[str], error: Optional[str] = None) -> Dict[str, Any]:
        vision_ms = round((time.monotonic() - t0) * 1000, 2)
        return {
            "has_image": True,
            "crop": crop_hint or "unclear",
            "observations": ["பயிரின் இலை அறிகுறிகள் பெறப்பட்டன."],
            "confidence": "low",
            "summary_ta": "படம் பெறப்பட்டது. தெளிவான அறிகுறிகளை உறுதிப்படுத்தவும்.",
            "vision_ms": vision_ms,
            "fallback_used": True,
            "error": error
        }


# Singleton instance
vision_observer = CropVisionObserver()
