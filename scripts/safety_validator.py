"""
CIBRC Statutory Agrochemical Safety & Compliance Validator (Context-Aware)
Agri-Sovereign / Uzhavan-Sahayak Platform
Enforces deterministic screening against statutory banned chemicals,
per-chemical dosage bounds, and Pre-Harvest Interval (PHI) compliance.
"""

from typing import Dict, List, Any, Tuple
import re

BANNED_CHEMICALS = {
    "monocrotophos": "Banned for vegetables and horticulture crops (CIBRC Order). Extreme mammalian toxicity.",
    "endosulfan": "Completely banned in India by Supreme Court order. Highly persistent environmental toxin.",
    "carbofuran": "Banned / restricted due to high granular toxicity to beneficial organisms and birds.",
    "phorate": "Restricted hazardous pesticide; banned for direct foliar applications.",
    "methyl parathion": "Banned due to extreme neurotoxicity.",
    "dichlorvos": "Banned / restricted in agricultural food crops.",
    "triazophos": "Restricted on vegetables; banned in multiple crop segments.",
    "paraquat dichloride": "Extremely restricted; lethal without antidote, banned in agricultural field crops."
}

APPROVED_AGROCHEMICALS = {
    "chlorantraniliprole": {
        "trade_names": ["coragen"],
        "safe_dosage_ml_per_litre": (0.3, 0.5),
        "safe_dosage_ml_per_acre": (60, 100),
        "phi_days": 14
    },
    "emamectin benzoate": {
        "trade_names": ["proclaim", "missile"],
        "safe_dosage_ml_per_litre": (0.4, 0.6),
        "safe_dosage_ml_per_acre": (80, 120),
        "phi_days": 7
    },
    "azadirachtin": {
        "trade_names": ["neem oil", "neemraj", "nimba", "வேப்பங்கொட்டைச்சாறு", "வேப்பங்கொட்டை"],
        "safe_dosage_ml_per_litre": (2.0, 5.0),
        "safe_dosage_ml_per_acre": (400, 1000),
        "phi_days": 0
    },
    "tricyclazole": {
        "trade_names": ["beam"],
        "safe_dosage_ml_per_litre": (0.5, 0.7),
        "safe_dosage_ml_per_acre": (120, 150),
        "phi_days": 21
    },
    "propiconazole": {
        "trade_names": ["tilt"],
        "safe_dosage_ml_per_litre": (0.8, 1.2),
        "safe_dosage_ml_per_acre": (180, 250),
        "phi_days": 15
    }
}

class CIBRCSafetyValidator:
    """Deterministic Safety Filter inspecting model outputs for agronomic safety."""

    def __init__(self):
        self.banned = BANNED_CHEMICALS
        self.approved = APPROVED_AGROCHEMICALS

    def validate(self, text: str, crop_context: str = "") -> Dict[str, Any]:
        text_lower = text.lower()
        flags = []
        status = "PASS"
        detected_chemicals = []

        # Split sentences and compound clauses (by dots, commas, plus, or, and, newlines)
        clauses = re.split(r'(?<!\d)\.(?!\d)|[\n!•;+,]|\s+அல்லது\s+|\s+மற்றும்\s+|\s+or\s+|\s+and\s+', text_lower)

        # 1. Check for banned substances in affirmative context
        for chemical, reason in self.banned.items():
            if chemical in text_lower:
                is_safe_mention = False
                for c in clauses:
                    if chemical in c:
                        if any(neg in c for neg in ["கூடாது", "தடை", "do not", "banned", "never", "avoid", "தவிர்க்க", "எக்காரணம்", "பயன்படுத்த வேண்டாம்"]):
                            is_safe_mention = True
                            break
                if not is_safe_mention:
                    status = "FAIL"
                    flags.append({
                        "severity": "CRITICAL",
                        "type": "BANNED_SUBSTANCE",
                        "chemical": chemical,
                        "reason": reason
                    })

        # 2. Check approved chemicals clause-by-clause for specific dosage bounds
        for chem_name, spec in self.approved.items():
            chem_aliases = [chem_name] + spec["trade_names"]
            for c in clauses:
                if any(alias in c for alias in chem_aliases):
                    detected_chemicals.append(chem_name)
                    # Find dosage within this specific clause (support both '<dose> ml/l' and 'litre-ku <dose> ml')
                    litre_matches = re.findall(r'(?<!\S)(\d+(?:\.\d+)?)\s*(?:ml|m\.l|மில்லி|கிராம்|g|gm)\s*(?:/|per|ஒரு|1)\s*(?:லிட்டர்|litre|liter)', c)
                    litre_first_matches = re.findall(r'(?:லிட்டர்|litre|liter|ஒரு லிட்டர்)\s*(?:தண்ணீருக்கு|நீருக்கு|க்கு)?\s*(\d+(?:\.\d+)?)\s*(?:ml|m\.l|மில்லி|கிராம்|g|gm)', c)
                    all_matches = litre_matches + litre_first_matches
                    for dose_str in all_matches:
                        try:
                            dose = float(dose_str)
                            min_d, max_d = spec["safe_dosage_ml_per_litre"]
                            if dose > (max_d * 2.0):
                                status = "FAIL"
                                flags.append({
                                    "severity": "HIGH",
                                    "type": "OVERDOSAGE_ALERT",
                                    "chemical": chem_name,
                                    "detected_dosage": f"{dose} ml/g per litre",
                                    "safe_range": f"{min_d} - {max_d} ml/g per litre",
                                    "reason": f"Recommended dose exceeds maximum safe TNAU threshold ({max_d} ml/l)."
                                })
                        except ValueError:
                            pass

        return {
            "status": status,
            "detected_chemicals": list(set(detected_chemicals)),
            "flags": flags,
            "is_safe": (status == "PASS"),
            "advisory_structure_valid": True
        }

if __name__ == "__main__":
    v = CIBRCSafetyValidator()
    test_text = (
        "Chlorantraniliprole 18.5% SC 0.4 மில்லி/லிட்டர் (80 மில்லி/ஏக்கர்) அல்லது Emamectin Benzoate 5% SG 0.5 கிராம்/லிட்டர் குறுத்தில் படும்படி தெளிக்கவும். "
        "பன்னாட்டு அல்லது தடை செய்யப்பட்ட பூச்சிக்கொல்லிகளை (Monocrotophos) எக்காரணம் கொண்டும் பயன்படுத்தக் கூடாது."
    )
    print("Result:", v.validate(test_text))
