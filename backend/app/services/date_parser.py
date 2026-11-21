"""
BolKhata - Multilingual Relative Date Parser
Handles relative date expressions in Hindi, Kannada, Telugu, and English.
"kal" / "ninne" / "ninna" -> yesterday
"aaj" / "ivattu" / "eeroju" -> today
"parso" / "monne" -> day before yesterday
"""

from datetime import date, timedelta
from typing import Optional
import re

# Past dates (used for "diya tha" / "kottiddaane" / "icchaadu")
PAST_DATES = {
    # Hindi
    "aaj": 0, "आज": 0,
    "kal": -1, "कल": -1,
    "parso": -2, "परसो": -2, "parson": -2,
    # Kannada
    "ivattu": 0, "ಇವತ್ತು": 0, "eegale": 0,
    "ninne": -1, "ನಿನ್ನೆ": -1,
    "monne": -2, "ಮೊನ್ನೆ": -2,
    # Telugu
    "eeroju": 0, "ఈరోజు": 0, "ippude": 0,
    "ninna": -1, "నిన్న": -1,
    "monna": -2, "మొన్న": -2,
    # English
    "today": 0,
    "yesterday": -1,
    "day before yesterday": -2,
}

# Future dates
FUTURE_DATES = {
    "aaj": 0, "आज": 0, "ivattu": 0, "ಇವತ್ತು": 0, "eeroju": 0, "ఈరోజు": 0,
    "kal": 1, "कल": 1, "naale": 1, "ನಾಳೆ": 1, "repu": 1, "రేపు": 1,
    "parso": 2, "परसो": 2, "naadiddu": 2, "ನಾಡಿದ್ದು": 2, "ellundi": 2, "ఎల్లుండి": 2,
    "today": 0, "tomorrow": 1, "day after tomorrow": 2,
}

PAST_CONTEXT_WORDS = {
    "tha", "thi", "the", "diya", "diye", "aaya", "aayi", "aaye", "gaya", "mila", "paid", "gave",
    "था", "थी", "थे", "दिया", "दिये", "आया", "आयी",
    # Kannada
    "kottiddaane", "kotta", "bandide", "aagide", "ಕೊಟ್ಟಿದ್ದಾನೆ", "ಕೊಟ್ಟ", "ಬಂದಿದೆ",
    # Telugu
    "icchaadu", "iccharu", "vachindi", "ayyindi", "ఇచ్చాడు", "ఇచ్చారు", "వచ్చింది",
}

FUTURE_CONTEXT_WORDS = {
    "dena", "denge", "dega", "aayega", "will", "going",
    "देना", "देंगे", "देगा", "आएगा",
    # Kannada
    "kodabekagide", "koduttaare", "baruttaare", "ಕೊಡಬೇಕಾಗಿದೆ", "ಕೊಡುತ್ತಾರೆ",
    # Telugu
    "ivvaali", "istaaru", "vastaaru", "ఇవ్వాలి", "ఇస్తారు", "వస్తారు",
}


def _detect_tense(text: str) -> str:
    text_lower = text.lower()
    tokens = set(re.findall(r'[\w\u0900-\u097F\u0C80-\u0CFF\u0C00-\u0C7F]+', text_lower))
    past_score = len(tokens & PAST_CONTEXT_WORDS)
    future_score = len(tokens & FUTURE_CONTEXT_WORDS)
    return "future" if future_score > past_score else "past"


def parse_relative_date(text: str, context_tense: str = "auto") -> Optional[date]:
    text_lower = text.lower().strip()
    if context_tense == "auto":
        context_tense = _detect_tense(text_lower)

    lookup = PAST_DATES if context_tense == "past" else FUTURE_DATES
    today = date.today()

    for phrase, offset in sorted(lookup.items(), key=lambda x: -len(x[0])):
        if phrase in text_lower:
            return today + timedelta(days=offset)

    return None


def extract_date_from_text(text: str) -> date:
    res = parse_relative_date(text)
    return res if res is not None else date.today()
