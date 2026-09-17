import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

raw_groq = """🌾 **உழவன் சகாயக் வேளாண் AI (TNAU & ICAR வழிகாட்டுதல்)**

📍 **மண்டலம்**: Coimbatore, Tiruppur, Dindigul (கோயம்புத்தூர், திருப்பூர், திண்டுக்கல்)

🌽 **பயிர் & பிரச்சனை**: மக்காச்சோளம் — படைப்புழு (Fall Armyworm - Spodoptera frugiperda)

வணக்கம் விவசாயி அண்ணா! உங்கள் மக்காச்சோளப் பயிரில் படைப்புழு தாக்குதல் காணப்பட்டால் கவலைப்பட வேண்டாம். உடனடியாக கீழ்கண்ட மேலாண்மை முறைகளை மேற்கொள்ளவும்.

📋 **முக்கிய அறிகுறிகள் & கண்டறிதல்**:
- இலைகளில் சல்லடை போன்ற துளைகள் மற்றும் புழுவின் கழிவுகள் காணப்படுதல்
- குருத்து பகுதியில் புழு தீவிரமாக சேதப்படுத்துதல்

💡 **உடனடி மேலாண்மை & மருந்து அளவுகள் (CIBRC அங்கீகரிக்கப்பட்டது)**:
1. **Spinetoram 11.7% SC**: ஒரு லிட்டர் தண்ணீருக்கு **0.5 மில்லி** கலந்து தெளிக்கவும்.
2. அல்லது **Chlorantraniliprole 18.5% SC**: ஒரு லிட்டர் தண்ணீருக்கு **0.4 மில்லி** கலந்து தெளிக்கவும்.
3. ஆரம்ப நிலையில் வேப்பங்கொட்டைச் சாறு **5%** தெளிக்கலாம்.

⏳ **பாதுகாப்பு & காத்திருப்பு காலம் (PHI)**:
மருந்து தெளித்த பிறகு குறைந்தபட்சம் **14 நாட்கள்** அறுவடை செய்யக்கூடாது. மருந்து தெளிக்கும்போது பாதுகாப்பு கவசங்களை அணியவும்.
"""

def extract_concise_spoken_ta(text: str) -> str:
    s = text
    # 1. Strip Markdown
    s = re.sub(r'[*#_`~]', '', s)
    s = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', s)
    s = re.sub(r'^\s*[-•\d+\.]+\s*', '', s, flags=re.MULTILINE)
    s = re.sub(r'\|[^\n]+\|', ' ', s)

    # 2. Strip emojis
    s = re.sub(r'[\U00010000-\U0010ffff]', '', s)
    s = re.sub(r'[\u2600-\u27bf\u2300-\u23ff\u2b50\u200d\ufe0f⛔🛡️✅⚠️💡📌🌾📍⏳🌽📋🧑‍🌾🌱🌿🧪]', '', s)
    s = re.sub(r'\([A-Za-z\s\-\.\,\/]+\)', '', s)

    # Clean UI section headers into spoken Tamil cues
    s = re.sub(r'உழவன் சகாயக் வேளாண் AI.*?\n', '', s)
    s = re.sub(r'மண்டலம்:[^\n]+\n', '', s)
    s = re.sub(r'பயிர் & பிரச்சனை:\s*', 'பயிர் மற்றும் பிரச்சனை: ', s)
    s = re.sub(r'முக்கிய அறிகுறிகள் & கண்டறிதல்:\s*', 'முக்கிய அறிகுறிகள்: ', s)
    s = re.sub(r'உடனடி மேலாண்மை & மருந்து அளவுகள்.*?:', 'பரிந்துரைக்கப்பட்ட மேலாண்மை மற்றும் மருந்து அளவுகள்: ', s)
    s = re.sub(r'பாதுகாப்பு & காத்திருப்பு காலம்.*?:\s*', 'பாதுகாப்பு மற்றும் அறுவடைக்கு முன் காத்திருப்பு காலம்: ', s)
    s = re.sub(r'CIBRC சட்டப்பூர்வ பாதுகாப்பு எச்சரிக்கை', 'சட்டப்பூர்வ பாதுகாப்பு எச்சரிக்கை', s)
    s = re.sub(r'பாதுகாப்பான மாற்றுப் பரிந்துரை:\s*', 'பாதுகாப்பான மாற்றுப் பரிந்துரை: ', s)

    lines = [l.strip() for l in s.split('\n') if l.strip()]
    
    # Categorize lines
    topic_lines = []
    symptom_lines = []
    treatment_lines = []
    safety_lines = []
    other_lines = []

    for l in lines:
        cl = re.sub(r'^[.\s:]+', '', l).strip()
        if not cl:
            continue
        if 'வணக்கம் விவசாயி அண்ணா' in cl:
            continue
        if any(k in cl for k in ['பயிர் மற்றும் பிரச்சனை', 'பாதுகாப்பு எச்சரிக்கை', 'சட்டப்பூர்வ']):
            topic_lines.append(cl)
        elif any(k in cl for k in ['முக்கிய அறிகுறிகள்', 'அறிகுறிகள்', 'துளைகள்', 'புழு', 'சேதம்', 'இலைகளில்']):
            symptom_lines.append(cl)
        elif any(k in cl for k in ['Spinetoram', 'Chlorantraniliprole', 'வேப்பங்கொட்டை', 'மில்லி', 'கிராம்', 'தெளிக்கவும்', 'மருந்து']):
            treatment_lines.append(cl)
        elif any(k in cl for k in ['காத்திருப்பு காலம்', 'நாட்கள்', 'பாதுகாப்பு', 'கவசம்']):
            safety_lines.append(cl)
        else:
            other_lines.append(cl)

    # Assemble concise voice response
    selected = []
    if topic_lines:
        selected.append(topic_lines[0])
    if symptom_lines:
        selected.extend(symptom_lines[:2])
    if treatment_lines:
        selected.extend(treatment_lines[:2])
    if safety_lines:
        selected.append(safety_lines[0])

    if not selected:
        selected = lines[:4]

    res = '. '.join(selected)
    res = re.sub(r'\.+', '.', res)
    res = re.sub(r'\s+', ' ', res).strip()
    return res

spoken = extract_concise_spoken_ta(raw_groq)
print("Concise Spoken Response:")
print(spoken)
print(f"Length: {len(spoken)}")
