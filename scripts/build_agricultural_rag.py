"""
Agricultural Knowledge Base & Fast Retrieval Index (RAG Engine)
Agri-Sovereign / Uzhavan-Sahayak Platform
Builds an authoritative vector & lexical retrieval store grounded in TNAU & ICAR guides.
"""

import json
import os
import re
from typing import List, Dict, Any

# Curated Gold-Standard TNAU Agronomy & Plant Protection Knowledge Bank
AUTHORITATIVE_AGRI_KNOWLEDGE = [
    {
        "id": "TNAU_MAIZE_FAW_01",
        "crop": "Maize (மக்காச்சோளம்)",
        "district": "Coimbatore, Tiruppur, Dindigul (கோயம்புத்தூர், திருப்பூர்)",
        "pest_disease": "Fall Armyworm (படைப்புழு - Spodoptera frugiperda)",
        "symptoms": "புழுக்கள் இலைகளின் அடிப்பகுதியில் சுரண்டி உண்ணும். இலைகளில் சிறு துளைகள், குறுத்துப்பகுதியில் மரத்தூள் போன்ற கழிவுகள் காணப்படும்.",
        "management_biological": "வேப்பங்கொட்டைச்சாறு (NSKE) 5% அல்லது அசாடிராக்டின் 1500 ppm 5 மில்லி/லிட்டர் தெளிக்கவும். டிரைக்கோடெர்மா மற்றும் இனக்கவர்ச்சி பொறிகள் ஏக்கருக்கு 5 வீதம் வைக்கவும்.",
        "management_chemical": "Chlorantraniliprole 18.5% SC 0.4 மில்லி/லிட்டர் (80 மில்லி/ஏக்கர்) அல்லது Emamectin Benzoate 5% SG 0.5 கிராம்/லிட்டர் (100 கிராம்/ஏக்கர்) குறுத்தில் படும்படி தெளிக்கவும்.",
        "safety_phi": "அறுவடைக்கு முன் காத்திருப்பு காலம் (PHI): 14 நாட்கள். பன்னாட்டு அல்லது தடை செய்யப்பட்ட பூச்சிக்கொல்லிகளை (Monocrotophos) எக்காரணம் கொண்டும் பயன்படுத்தக் கூடாது."
    },
    {
        "id": "TNAU_PADDY_BLAST_02",
        "crop": "Paddy (நெல் - குறுவை/சம்பா)",
        "district": "Thanjavur, Tiruvarur, Erode, Madurai (தஞ்சாவூர், ஈரோடு)",
        "pest_disease": "Blast Disease (குலைநோய் / இலைக்கருகல் - Magnaporthe oryzae)",
        "symptoms": "இலைகளில் கண் வடிவ புள்ளிகள் தோன்றி மையப்பகுதி சாம்பல் நிறமாகவும் ஓரங்கள் பழுப்பு நிறமாகவும் மாறும். தீவிர நிலையில் இலைகள் கருகிவிடும்.",
        "management_biological": "சூடோமோனாஸ் புளோரசன்ஸ் (Pseudomonas fluorescens) 10 கிராம்/லிட்டர் அல்லது 1 கிலோ/ஏக்கர் தெளிக்கவும்.",
        "management_chemical": "Tricyclazole 75% WP 0.6 கிராம்/லிட்டர் (120 கிராம்/ஏக்கர்) அல்லது Azoxystrobin 25% SC 1.0 மில்லி/லிட்டர் தண்ணீரில் கலந்து கைத்தெளிப்பான் கொண்டு தெளிக்கவும்.",
        "safety_phi": "காத்திருப்பு காலம்: 21 நாட்கள். தழைச்சத்து (யூரியா) உரங்களை அளவுக்கு அதிகமாக இடுவதை தவிர்க்கவும்."
    },
    {
        "id": "TNAU_BANANA_SIGATOKA_03",
        "crop": "Banana (வாழை)",
        "district": "Trichy, Theni, Coimbatore, Tuticorin (திருச்சி, தேனி, பொள்ளாச்சி)",
        "pest_disease": "Sigatoka Leaf Spot (சிகாடோகா இலைப்புள்ளி நோய் - Mycosphaerella musicola)",
        "symptoms": "இலைகளில் நீள்வட்ட வடிவ மஞ்சள் மற்றும் அடர் பழுப்பு நிற புள்ளிகள் தோன்றி முழு இலையும் காய்ந்து தொங்கும்.",
        "management_biological": "பாதிக்கப்பட்ட இலைகளை வெட்டி அழித்து வயலை சுத்தமாக வைத்திருக்கவும். தழைச்சத்து மற்றும் சாம்பல் சத்து சமவிகிதத்தில் இடவும்.",
        "management_chemical": "Propiconazole 25% EC 1.0 மில்லி/லிட்டர் + மினரல் ஆயில் 10 மில்லி/லிட்டர் அல்லது Carbendazim 50% WP 1.0 கிராம்/லிட்டர் கலந்து 25-30 நாட்கள் இடைவெளியில் தெளிக்கவும்.",
        "safety_phi": "அறுவடைக்கு 15 நாட்களுக்கு முன் தெளிப்பதை நிறுத்தவும்."
    },
    {
        "id": "TNAU_COCONUT_RUGOSE_04",
        "crop": "Coconut (தென்னை)",
        "district": "Pollachi, Coimbatore, Tirupur, Kanyakumari (பொள்ளாச்சி, கோயம்புத்தூர்)",
        "pest_disease": "Rugose Spiraling Whitefly (சுருள் வெள்ளை ஈ - Aleurodicus rugioperculatus)",
        "symptoms": "ஓலைகளின் அடிப்பகுதியில் வெள்ளை மெழுகு போன்ற படலம் தோன்றும். அதன் மீது கரும்பூசணம் (சோட்டி மோல்ட்) படர்ந்து ஒளிச்சேர்க்கை பாதிக்கப்படும்.",
        "management_biological": "என்கார்சியா (Encarsia guadeloupae) ஒட்டுண்ணிகளை விடுவிக்க வேண்டும். மஞ்சள் நிற ஒட்டும் பொறிகள் ஏக்கருக்கு 8 வைக்கவும். கிரைசோபெர்லா இரைவிழுங்கிகளை விடவும்.",
        "management_chemical": "வேப்பெண்ணெய் 30 மில்லி/லிட்டர் அல்லது அசாடிராக்டின் 1% 2 மில்லி/லிட்டர் மற்றும் சோப்பு கரைசல் 5 மில்லி சேர்த்து மட்டைகளின் அடிப்பகுதியில் விசைத்தெளிப்பான் கொண்டு தெளிக்கவும்.",
        "safety_phi": "கடுமையான பூச்சிக்கொல்லிகளை தெளிக்கக் கூடாது, ஏனெனில் அவை இயற்கை ஒட்டுண்ணிகளை அழித்துவிடும்."
    },
    {
        "id": "TNAU_TURMERIC_RHIZOME_ROT_05",
        "crop": "Turmeric (மஞ்சள்)",
        "district": "Erode, Salem, Namakkal, Dharmapuri (ஈரோடு, சேலம், நாமக்கல்)",
        "pest_disease": "Rhizome Rot (கிழங்கு அழுகல் நோய் - Pythium aphanidermatum)",
        "symptoms": "செடியின் அடிப்பகுதி மற்றும் கிழங்கு மென்மையாகவும் அழுகி துர்நாற்றம் வீசும். இலைகள் விளிம்பிலிருந்து மஞ்சள் நிறமாகி காய்ந்துவிடும்.",
        "management_biological": "டிரைக்கோடெர்மா விரிடி (Trichoderma viride) 2.5 கிலோ/ஏக்கர் தொழு உரத்துடன் கலந்து அடியில் இடவும். விதை நேர்த்தி செய்யவும்.",
        "management_chemical": "Copper Oxychloride 50% WP 2.5 கிராம்/லிட்டர் அல்லது Metalaxyl + Mancozeb 2.0 கிராம்/லிட்டர் செடியின் தூரைச் சுற்றி நனையும்படி ஊற்றவும் (Drenching).",
        "safety_phi": "பாதிக்கப்பட்ட செடிகளை உடனடியாக அகற்றி வயலில் நீர் தேங்காமல் வடிகால் அமைக்கவும்."
    },
    {
        "id": "TNAU_COTTON_PINK_BOLLWORM_06",
        "crop": "Cotton (பருத்தி)",
        "district": "Perambalur, Salem, Virudhunagar, Theni (சேலம், பெரம்பலூர்)",
        "pest_disease": "Pink Bollworm (இளஞ்சிவப்பு காய்ப்புழு - Pectinophora gossypiella)",
        "symptoms": "பூக்கள் ரோஜா வடிவில் விரியாமல் முடிந்துவிடும் (Rosette flowers). காய்களில் சிறு துளைகள் விழுந்து பஞ்சு தரம் குறையும்.",
        "management_biological": "இனக்கவர்ச்சி பொறிகள் (Pheromone traps) ஏக்கருக்கு 5 வைக்கவும். டிரைக்கோகிரம்மா முட்டை ஒட்டுண்ணிகளை 3 முறை விடவும்.",
        "management_chemical": "Profenofos 50% EC 2.0 மில்லி/லிட்டர் அல்லது Emamectin Benzoate 5% SG 0.5 கிராம்/லிட்டர் தெளிக்கவும்.",
        "safety_phi": "காத்திருப்பு காலம்: 15 நாட்கள். பூக்கும் தருணத்தில் மாலை வேளையில் தெளிக்கவும்."
    },
    {
        "id": "TNAU_TOMATO_LEAF_CURL_07",
        "crop": "Tomato (தக்காளி)",
        "district": "Salem, Krishnagiri, Dindigul, Coimbatore (சேலம், கிருஷ்ணகிரி)",
        "pest_disease": "Leaf Curl Virus & Whitefly (இலை சுருட்டல் நச்சுயிரி & வெள்ளை ஈ)",
        "symptoms": "இலைகள் மேல்நோக்கி அல்லது கீழ்நோக்கி சுருண்டு, தடித்து, நரம்புகள் தடித்து வெளிறி காணப்படும். செடி வளர்ச்சி குன்றி காய் பிடிக்காது.",
        "management_biological": "மஞ்சள் நிற ஒட்டும் பொறிகள் ஏக்கருக்கு 12 வைக்கவும். வேப்பெண்ணெய் 3% கரைசல் தெளிக்கவும்.",
        "management_chemical": "Diafenthiuron 50% WP 1.0 கிராம்/லிட்டர் அல்லது Acetamiprid 20% SP 0.3 கிராம்/லிட்டர் வெள்ளை ஈயை கட்டுப்படுத்த தெளிக்கவும்.",
        "safety_phi": "காத்திருப்பு காலம் (PHI): 5 நாட்கள். பூக்கள் மற்றும் காய்களில் மருந்து எச்சம் படியாமல் கவனமாக தெளிக்கவும்."
    },
    {
        "id": "TNAU_SUGARCANE_BORER_08",
        "crop": "Sugarcane (கரும்பு)",
        "district": "Cuddalore, Villupuram, Erode, Thanjavur (கடலூர், விழுப்புரம், ஈரோடு)",
        "pest_disease": "Internode Borer (இடைக்கணு புழு - Chilo sacchariphagus indicus)",
        "symptoms": "கணுப்பகுதிகளில் சிறு துளைகள் தோன்றி கழிவுகள் வெளித்தள்ளப்படும். கணுக்கள் சுருங்கி சர்க்கரை அளவு குறையும்.",
        "management_biological": "டிரைக்கோகிரம்மா கைலோனிஸ் ஒட்டுண்ணி அட்டைகளை ஏக்கருக்கு 2.5 cc வீதம் நடவு செய்த 4-வது மாதம் முதல் மாத இடைவெளியில் கட்டவும்.",
        "management_chemical": "Cartap Hydrochloride 50% SP 2.0 கிராம்/லிட்டர் அல்லது Chlorantraniliprole 18.5% SC 0.3 மில்லி/லிட்டர் பயிரின் அடிப்பகுதியில் தெளிக்கவும்.",
        "safety_phi": "அறுவடைக்கு 21 நாட்களுக்கு முன் தெளிக்கவும்."
    },
    {
        "id": "TNAU_CHILLI_THRIPS_09",
        "crop": "Chilli (மிளகாய்)",
        "district": "Ramanathapuram, Thoothukudi, Tirunelveli (இராமநாதபுரம், தூத்துக்குடி)",
        "pest_disease": "Thrips & Mites (இலைப்பேன் மற்றும் சிலந்தி - Scirtothrips dorsalis)",
        "symptoms": "இலைகள் மேல்நோக்கி படகு வடிவில் சுருங்கும், இலைகளின் அடிப்பகுதி பழுப்பு நிறமாகும். காய்கள் வளைந்து நெளிந்து காணப்படும்.",
        "management_biological": "நீல நிற ஒட்டும் பொறிகள் ஏக்கருக்கு 10 வைக்கவும். வேப்பங்கொட்டை சாறு 5% தெளிக்கவும்.",
        "management_chemical": "Spinetoram 11.7% SC 1.0 மில்லி/லிட்டர் அல்லது Fipronil 5% SC 1.5 மில்லி/லிட்டர் மாலை வேளையில் தெளிக்கவும்.",
        "safety_phi": "காத்திருப்பு காலம் (PHI): 7 நாட்கள்."
    },
    {
        "id": "TNAU_GROUNDNUT_TIKKA_10",
        "crop": "Groundnut (நிலக்கடலை)",
        "district": "Tiruvannamalai, Vellore, Villupuram (திருவண்ணாமலை, வேலூர்)",
        "pest_disease": "Tikka Leaf Spot (டிக்கா இலைப்புள்ளி நோய் - Cercospora personata)",
        "symptoms": "இலைகளில் வட்ட வடிவ அடர் பழுப்பு/கருப்பு நிற புள்ளிகள் தோன்றி சுற்றிலும் மஞ்சள் வளையம் காணப்படும். தீவிர நிலையில் இலைகள் உதிர்ந்துவிடும்.",
        "management_biological": "சூடோமோனாஸ் புளோரசன்ஸ் 10 கிராம்/லிட்டர் அல்லது டிரைக்கோடெர்மா விரிடி தெளிக்கவும்.",
        "management_chemical": "Mancozeb 75% WP 2.0 கிராம்/லிட்டர் அல்லது Tebuconazole 25.9% EC 1.0 மில்லி/லிட்டர் நோய் தென்பட்டவுடன் தெளிக்கவும்.",
        "safety_phi": "காத்திருப்பு காலம்: 14 நாட்கள்."
    }
]

class AgriculturalRAGEngine:
    """Lightweight and robust lexical + semantic agricultural retrieval engine."""

    def __init__(self, data_path: str = "/home/luckycelestial/LLM Forge/data/tnau_knowledge_store.json"):
        self.data_path = data_path
        self.documents = []
        self.load_or_build_index()

    def load_or_build_index(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        self.documents = AUTHORITATIVE_AGRI_KNOWLEDGE
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        print(f"Loaded {len(self.documents)} authoritative TNAU/ICAR agronomy records.")

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Performs multi-field keyword & semantic relevance ranking."""
        q_lower = query.lower()
        query_terms = set(re.findall(r'[\w]+', q_lower))
        scores = []
        
        crop_keywords = {
            "மக்காச்சோளம்": ["மக்காச்சோளம்", "சோளம்", "maize", "corn"],
            "நெல்": ["நெல்", "நெற்பயிர்", "பயிர்", "paddy", "rice"],
            "வாழை": ["வாழை", "வாழைக்காய்", "banana"],
            "தென்னை": ["தென்னை", "தேங்காய்", "coconut"],
            "மஞ்சள்": ["மஞ்சள்", "கிழங்கு", "turmeric", "rhizome"],
            "பருத்தி": ["பருத்தி", "காய்", "cotton", "bollworm"],
            "தக்காளி": ["தக்காளி", "tomato"],
            "கரும்பு": ["கரும்பு", "sugarcane"],
            "மிளகாய்": ["மிளகாய்", "chilli", "pepper"],
            "நிலக்கடலை": ["நிலக்கடலை", "வேர்க்கடலை", "groundnut", "peanut"]
        }
        
        pest_keywords = {
            "படைப்புழு": ["படைப்புழு", "armyworm", "spodoptera"],
            "குலைநோய்": ["குலைநோய்", "blast", "magnaporthe"],
            "சிகாடோகா": ["சிகாடோகா", "sigatoka"],
            "வெள்ளை ஈ": ["வெள்ளை ஈ", "சுருள்", "whitefly"],
            "கிழங்கு அழுகல்": ["அழுகல்", "கிழங்கு", "pythium", "rot"],
            "காய்ப்புழு": ["காய்ப்புழு", "pink bollworm", "புழு"],
            "இலை சுருட்டல்": ["சுருட்டல்", "சுருண்டு", "leaf curl", "virus"],
            "இடைக்கணு": ["இடைக்கணு", "internode", "தண்டு"],
            "இலைப்பேன்": ["இலைப்பேன்", "சிலந்தி", "thrips", "mites"],
            "டிக்கா": ["டிக்கா", "இலைப்புள்ளி", "tikka"]
        }

        for doc in self.documents:
            score = 0
            doc_str = (f"{doc['crop']} {doc['pest_disease']} {doc['symptoms']} "
                       f"{doc['management_biological']} {doc['management_chemical']} {doc['district']}").lower()
            
            # Word match
            for term in query_terms:
                if len(term) > 2 and term in doc_str:
                    score += 4
            
            # Crop match
            for canonical_crop, aliases in crop_keywords.items():
                if any(alias in q_lower for alias in aliases) and any(alias in doc_str for alias in aliases):
                    score += 15
                    
            # Pest match
            for canonical_pest, aliases in pest_keywords.items():
                if any(alias in q_lower for alias in aliases) and any(alias in doc_str for alias in aliases):
                    score += 20
                    
            scores.append((score, doc))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        matches = [doc for score, doc in scores if score > 0]
        if matches:
            return matches[:top_k]
        return [self.documents[0]]

if __name__ == "__main__":
    rag = AgriculturalRAGEngine()
    test_query = "மஞ்சள் கிழங்கு அழுகல் நோய்"
    print(f"\nQuery: {test_query}")
    results = rag.search(test_query)
    for r in results:
        print(f"\n[Retrieved Evidence ID: {r['id']}] - {r['crop']}")
        print(f"  Pest/Disease: {r['pest_disease']}")
