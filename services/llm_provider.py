"""
LLM Provider Abstraction Layer for Agri-Sovereign / Uzhavan-Sahayak
Person 2 Implementation: Black-box provider architecture supporting Groq,
Local Grounded Fallback, and future Ministral interfaces.
"""

import os
import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger("uzhavan.llm_provider")


class LLMProvider(ABC):
    """Abstract Base Class for all LLM inference providers."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[List[Dict[str, Any]]] = None,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes generation and returns standardized payload.
        Expected return structure:
        {
            "text": str,
            "provider": str,
            "model": str,
            "latency_ms": float,
            "input_tokens": Optional[int],
            "output_tokens": Optional[int],
            "fallback_used": bool
        }
        """
        pass


class LocalFallbackProvider(LLMProvider):
    """
    Zero-network, zero-cost deterministic fallback provider.
    Constructs high-precision Tamil agro-advisories strictly from TNAU/ICAR context.
    Never invents chemicals, dosages, or PHI.
    """

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[List[Dict[str, Any]]] = None,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        t0 = time.monotonic()

        if context and len(context) > 0:
            doc = context[0]
            crop = doc.get("crop", "பயிர்")
            pest = doc.get("pest_disease", "பாதிப்பு")
            bio = doc.get("management_biological", "இயற்கை கட்டுப்பாடு முறை")
            chem = doc.get("management_chemical", "பரிந்துரைக்கப்பட்ட இரசாயன முறை")
            phi = doc.get("safety_phi", "பாதுகாப்பு விதிகளைப் பின்பற்றவும்")
            district = doc.get("district", "தமிழ்நாடு")

            text = (
                f"🌾 **உழவன் சகாயக் வேளாண் AI (TNAU & ICAR வழிகாட்டுதல்)**\n\n"
                f"📍 **மண்டலம்**: {district}\n"
                f"🌱 **பயிர் & பாதிப்பு**: {crop} — {pest}\n\n"
                f"🔬 **TNAU பரிந்துரைக்கும் வேளாண் மேலாண்மை**:\n"
                f"• **இயற்கை / உயிரியல் முறை**: {bio}\n"
                f"• **இரசாயன முறை**: {chem}\n\n"
                f"🛡️ **CIBRC பாதுகாப்பு & காத்திருப்பு காலம் (PHI)**:\n{phi}\n\n"
                f"⚠️ *பாதுகாப்பு முகக்கவசம் மற்றும் கையுறை அணிந்து பரிந்துரைக்கப்பட்ட அளவில் மட்டுமே தெளிக்கவும்.*"
            )
        else:
            text = (
                f"🌾 **உழவன் சகாயக் வேளாண் AI**\n\n"
                f"வணக்கம்! உங்கள் கேள்விக்கான சரிபார்க்கப்பட்ட TNAU / ICAR அதிகாரப்பூர்வ தரவுகள் "
                f"கணினியில் நேரடியாகக் கிடைக்கவில்லை.\n\n"
                f"பாதுகாப்பு கருதி, அங்கீகரிக்கப்படாத இரசாயனப் பரிந்துரைகள் வழங்கப்படமாட்டாது. "
                f"உங்கள் பகுதி வேளாண் அறிவியல் நிலைய (KVK) அல்லது உதவி வேளாண்மை அலுவலரைத் தொடர்பு கொள்ளவும்."
            )

        latency_ms = round((time.monotonic() - t0) * 1000, 2)
        return {
            "text": text,
            "provider": "local_fallback",
            "model": "local-tnau-deterministic",
            "latency_ms": latency_ms,
            "input_tokens": len(user_prompt.split()),
            "output_tokens": len(text.split()),
            "fallback_used": True,
        }


class GroqProvider(LLMProvider):
    """
    Black-Box Groq API Provider using official OpenAI-compatible endpoint.
    Utilizes free-tier developer credits on api.groq.com.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.base_url = (base_url or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")).rstrip("/")
        self.fallback = LocalFallbackProvider()

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[List[Dict[str, Any]]] = None,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        # If API key is missing, immediately route to LocalFallbackProvider
        if not self.api_key:
            logger.warning("[GROQ_PROVIDER] No GROQ_API_KEY set. Routing to LocalFallbackProvider.")
            return await self.fallback.generate(system_prompt, user_prompt, context, image_base64)

        # Construct grounded context prompt
        context_block = ""
        if context and len(context) > 0:
            doc = context[0]
            context_block = (
                f"\n\n[AUTHORITATIVE TNAU / ICAR RESEARCH EVIDENCE]\n"
                f"- Crop: {doc.get('crop', 'N/A')}\n"
                f"- Target Pest/Disease: {doc.get('pest_disease', 'N/A')}\n"
                f"- Biological Management: {doc.get('management_biological', 'N/A')}\n"
                f"- Chemical Management & Dosage: {doc.get('management_chemical', 'N/A')}\n"
                f"- Safety & Pre-Harvest Interval (PHI): {doc.get('safety_phi', 'N/A')}\n"
                f"- District/Region: {doc.get('district', 'N/A')}\n\n"
                f"Instruction: Ground your reply strictly in the facts above. Do NOT invent new dosages or banned chemicals."
            )
        else:
            context_block = "\n\n[NOTE: No specific TNAU record found for this query. Advise verification.]"

        full_user_content = f"{user_prompt}{context_block}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_content},
        ]

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 800,
        }

        t0 = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)

            latency_ms = round((time.monotonic() - t0) * 1000, 2)

            if response.status_code == 200:
                data = response.json()
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "").strip()
                usage = data.get("usage", {})
                input_tokens = usage.get("prompt_tokens")
                output_tokens = usage.get("completion_tokens")

                return {
                    "text": text,
                    "provider": "groq",
                    "model": self.model,
                    "latency_ms": latency_ms,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "fallback_used": False,
                }
            else:
                logger.warning(
                    f"[GROQ_PROVIDER] Groq HTTP {response.status_code} response. Failing over to LocalFallbackProvider."
                )
                fallback_res = await self.fallback.generate(system_prompt, user_prompt, context, image_base64)
                fallback_res["error_status"] = response.status_code
                return fallback_res

        except Exception as e:
            logger.warning(f"[GROQ_PROVIDER] Request exception: {type(e).__name__}. Failing over to LocalFallbackProvider.")
            fallback_res = await self.fallback.generate(system_prompt, user_prompt, context, image_base64)
            fallback_res["error_type"] = type(e).__name__
            return fallback_res


class MinistralProvider(LLMProvider):
    """
    Interface placeholder for Person 1's future adapted Ministral 3 8B model.
    """

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[List[Dict[str, Any]]] = None,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        fallback = LocalFallbackProvider()
        res = await fallback.generate(system_prompt, user_prompt, context, image_base64)
        res["provider"] = "ministral_placeholder"
        res["model"] = "ministral-3-8b-qlora (pending Person 1 checkpoint)"
        return res


def get_llm_provider(provider_type: Optional[str] = None) -> LLMProvider:
    """
    Factory function to instantiate the active LLM provider.
    Reads configuration from LLM_PROVIDER in environment.
    """
    selected = (provider_type or os.getenv("LLM_PROVIDER", "groq")).lower().strip()

    if selected == "groq":
        return GroqProvider()
    elif selected == "local_fallback":
        return LocalFallbackProvider()
    elif selected == "ministral":
        return MinistralProvider()
    else:
        logger.warning(f"Unknown LLM_PROVIDER '{selected}'. Defaulting to GroqProvider.")
        return GroqProvider()
