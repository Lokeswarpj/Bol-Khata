"""
BolKhata - Production Multilingual Kirana NLU Engine
Engineered to eliminate false defaults and handle real-world Kirana store interactions:
- Wake-word ("BolKhata") and Voice Standby ("Stop" / "Ruko")
- Reset Today's Payments ("Reset today's payment" / "Aaj ki jama reset karo")
- Full Debt Settlement ("Ramesh cleared his debt" / "hisaab chukta kar diya" / "ಸಾಲ ತೀರಿದೆ" / "అప్పు తీరిపోయింది")
- Automatic Language Detection across Kannada, Telugu, Hindi, and English
- Itemized grocery shop talk ("Ramesh 1 packet doodh le gaya 30 rupaye likh lo")
- Multi-action compound utterances ("Ramesh ka 340 udhaar, kal 200 diya tha")
- Instant spoken corrections ("nahi, 430" / "alla, 430" / "kaadhu, 430")
- Disambiguation & Nickname recognition
"""

import re
from datetime import date
from typing import Optional, List, Tuple

from app.models import ParsedIntent, IntentType, TransactionDirection
from app.services.number_parser import extract_amounts, extract_first_amount
from app.services.date_parser import extract_date_from_text


# ═══════════════════════════════════════════════════════════════
# Comprehensive Multilingual Intent Vocabularies
# ═══════════════════════════════════════════════════════════════

# Wake-word patterns (includes common STT misrecognitions like 'kolkata', 'bolkatha', etc.)
WAKE_WORD_PATTERN = r'^(?:hey\s+|suno\s+|hello\s+|hi\s+|namaste\s+|oye\s+)?(?:bolkhata|bol\s*khata|bolkatha|bol\s*katha|kolkata|kolkatha|calcutta|gol\s*khata|call\s*khata|pol\s*khata|bhole\s*khata|बोल\s*खाता|ಬೋಲ್\s*ಖಾತಾ|బోల్\s*ఖాతా)(?:[\,\:\s]+|$)'

# Stop / Sleep patterns
STOP_COMMAND_PATTERN = r'\b(?:stop|ruko|ruk\s+ja|ruk\s+jao|bas|chup|chup\s+raho|shant|shant\s+raho|sleep|standby|band\s+karo|stop\s+listening|quiet|nillu|nillisi|saaku|aagu|aapu|chalu)\b|(?:रुको|बस|चुप|शांत|बंद\s*करो)|(?:ನಿಲ್ಲು|ಸಾಕು|ಶಾಂತವಾಗಿರು|ನಿಲ್ಲಿಸಿ)|(?:ఆగు|ఆపు|శాంతంగా\s*ఉండు|చాలు)'

# Reset payments pattern
RESET_PAYMENTS_PATTERN = r'\b(?:reset\s+(?:today(?:\'s)?\s+)?(?:payment|payments|jama|collection)|clear\s+(?:today(?:\'s)?\s+)?(?:payment|payments)|aaj\s+ki\s+jama\s+reset|aaj\s+ka\s+collection\s+reset|aaj\s+ke\s+payment\s+reset|aaj\s+ki\s+jama\s+(?:hata|clear|saaf)|jama\s+reset)\b|(?:ಇಂದಿನ\s*ಜಮಾ\s*ರದ್ದು|ಜಮಾ\s*ರೀಸೆಟ್)|(?:ఈరోజు\s*జమ\s*రీసెట్|ఈరోజు\s*పేమెంట్లు\s*రీసెట్|జమ\s*రీసెట్)'

# Debt Clearing (Full Settlement) Keywords & Phrases
CLEAR_DEBT_KEYWORDS = {
    # English
    "cleared", "clear", "settled", "settle", "paid off", "zeroed", "clearing",
    # Hindi
    "chukta", "चुक्ता", "chukti", "chuka diya", "chuka", "khatam", "खत्म",
    "saaf", "साफ", "faisla", "phaisla", "barabar", "बराबर",
    # Kannada
    "theerisi", "ತೀರಿಸಿ", "theerisiddaane", "mugisiddaane", "theerthu", "teeride", "ತೀರಿದೆ",
    # Telugu
    "theerchesadu", "తీర్చేశాడు", "theerchadu", "poorthi", "chellinchesadu", "teeripoyindi", "తీరిపోయింది",
}

CLEAR_DEBT_PHRASES = [
    r'cleared\s+(?:his|her|all|the)?\s*(?:debt|account|dues|balance|khata|dues)',
    r'cleared\s+all',
    r'has\s+cleared\s+(?:his|her|all|the)?\s*(?:debt|account|dues|balance)',
    r'(?:clear|settle)\s+(?:debt|account|dues|balance|khata)\s+(?:for|of)?',
    r'hisaab\s+(?:clear|chukta|khatam|saaf|barabar)',
    r'poora\s+(?:de\s+diya|jama\s+kar\s+diya|chukta|chukaya)',
    r'saara\s+(?:udhaar|karz)\s+(?:chukta|clear|khatam)',
    r'udhaar\s+(?:chukta|clear|khatam)',
    r'saala\s+(?:theerisi|teeride|mugiside|clear)',
    r'appu\s+(?:theerchesadu|teeripoyindi|clear)',
    r'baaki\s+(?:clear|theerindi|theerchesadu)',
]

# Credit (Udhaar / Debt addition) Keywords
CREDIT_KEYWORDS = {
    # Hindi
    "udhaar", "udhar", "उधार", "khata", "खाता", "likh", "लिख", "likho", "लिखो", "likhna",
    "likhle", "likhlo", "baaki", "बाकी", "baki", "le gaya", "le gaye", "dena hai", "liya",
    "samaan liya", "kharida", "chahiye", "li", "di",
    # Kannada
    "saala", "ಸಾಲ", "baaki", "ಬಾಕಿ", "bare", "ಬರೆ", "bareyiri", "ಬರೆಯಿರಿ",
    "khaate", "ಖಾತೆ", "uddhaara", "ಉದ್ದಾರ", "thagondiddaane", "kodabeku",
    # Telugu
    "appu", "అప్పు", "baaki", "బాకీ", "raayi", "రాయ్", "raayandi", "రాయండి",
    "khata", "ఖాతా", "theesukunnadu", "ivvaali",
    # English
    "credit", "due", "loan", "borrowed", "took", "write", "bill", "bought",
}

# Payment (Jama / Money received) Keywords
PAYMENT_KEYWORDS = {
    # Hindi
    "diya", "दिया", "diye", "दिये", "de gaya", "jama", "जमा", "wapas", "वापस",
    "aaya", "aaye", "bhara", "vasool", "वसूूल", "vasooli", "mila", "मिला", "de diya",
    "chuka diya", "bhugtan",
    # Kannada
    "kottiddaane", "ಕೊಟ್ಟಿದ್ದಾನೆ", "kotta", "ಕೊಟ್ಟ", "jama", "ಜಮಾ", "paavati", "ಪಾವತಿ",
    "bandide", "ಬಂದಿದೆ", "sandaaya",
    # Telugu
    "icchaadu", "ఇచ్చాడు", "kattaadu", "కట్టాడు", "jama", "జమ", "chellinchaadu",
    "చెల్లించాడు", "vachindi", "వచ్చింది",
    # English
    "paid", "payment", "received", "deposited", "returned", "gave",
}

# Query Keywords
QUERY_KEYWORDS = {
    # Hindi
    "kitna", "कितना", "total", "टोटल", "hisaab", "हिसाब", "balance", "बैलेंस", "baaki", "बाकी",
    # Kannada
    "ottu", "ಒಟ್ಟು", "eshtu", "ಎಷ್ಟು", "lekka", "ಲೆಕ್ಕ",
    # Telugu
    "mottam", "మొత్తం", "entha", "ఎంత", "lekka", "లెక్క",
    # English
    "total", "balance", "how", "much", "what", "owe", "owes", "due", "dues", "account", "show", "tell",
}

TODAY_QUERY_KEYWORDS = {
    "aaj", "आज", "today", "today's", "abhi tak", "ivattu", "ಇವತ್ತು", "eeroju", "ఈరోజు",
    "dukaan", "store", "shop", "overall", "all",
}

LIST_KEYWORDS = {
    "sabka", "सबका", "sab", "ellaradu", "ಎಲ್ಲರದ್ದು", "andaridi", "అందరిదీ", "everyone", "all",
}

CORRECTION_KEYWORDS = {
    # Hindi
    "nahi", "नहीं", "nahin", "nhi", "galat", "गलत", "sudhar", "सुधार", "badlo", "बदलो",
    # Kannada
    "alla", "ಅಲ್ಲ", "tappu", "ತಪ್ಪು", "badalayisu", "ಬದಲಾಯಿಸು",
    # Telugu
    "kaadhu", "కాదు", "thappu", "తప్పు", "maarchu", "మార్చు",
    # English
    "no", "wrong", "change", "cancel", "sorry", "actually", "mistake",
}

SKIP_WORDS = {
    "ka", "ke", "ki", "ko", "ne", "se", "me", "mein", "hai", "hain", "tha", "thi", "the",
    "wala", "wali", "wale", "ge", "alli", "inda", "ige", "iddaane", "ide", "ki", "ku",
    "lo", "nundi", "valla", "undi", "andi", "and", "or", "aur", "mattu", "mari",
    "the", "a", "an", "is", "are", "was", "were", "has", "have", "his", "her",
    "packet", "kilo", "kg", "gram", "rupaye", "rupees", "rs", "debt", "account",
    "bhaiya", "ji", "babu", "sahab", "anna", "garu", "sir", "madam", "namaste", "hello", "hi",
    "how", "much", "what", "give", "show", "tell", "check", "me", "you", "does", "can", "please",
    "dukaan", "store", "shop", "total", "balance", "all", "owe", "owes",
    "aaj", "kal", "parso", "today", "yesterday", "ninne", "ninna", "ivattu", "eeroju", "abhi",
    # Filter out query question words from being captured as customer names
    "sabse", "kiska", "kisne", "kisko", "kaun", "highest", "most", "who", "kitna", "kitne",
    "yaru", "yarige", "evaru", "evariki", "collection", "cash", "message", "reminder",
    "bhejo", "send", "karo", "maadu", "cheyyi", "kaluhisi", "pampandi",
    "bolkhata", "bol", "khata", "katha", "kolkata", "kolkatha", "calcutta", "stop", "ruko", "bas", "sleep", "reset", "payments",
    # Indic script greetings & polite words
    "ನಮಸ್ಕಾರ", "ನಮಸ್ಕಾರಗಳು", "ಹೇಗಿದ್ದೀರಾ", "ಹೇಗಿದ್ದೀರಿ", "ಧನ್ಯವಾದ", "ಧನ್ಯವಾದಗಳು",
    "నమస్కారం", "నమస్కారాలు", "ఎలా", "ఉన్నారు", "బాగున్నారా", "ధన్యవాదాలు",
    "नमस्ते", "नमस्कार", "धन्यवाद", "शुक्रिया", "प्रणाम", "राधे", "राम",
}

# Conversational Chit-Chat Categories & Patterns
CHITCHAT_PATTERNS = {
    "greeting": [
        r'\b(?:namaste|namaskar|namaskara|namaskaram|hello|hi|hey|good\s+morning|good\s+afternoon|good\s+evening|shubh\s+prabhat|shubh\s+sandhya|ram\s+ram|radhe\s+radhe|pranam|salaam|kem\s+cho|vanakkam)\b',
        r'(?:ನಮಸ್ಕಾರ|ನಮಸ್ಕಾರಗಳು|ಶುಭೋದಯ)',
        r'(?:నమస్కారం|నమస్కారాలు|శుభోదయం)',
        r'(?:नमस्ते|नमस्कार|शुभ\s*प्रभात|प्रणाम)',
    ],
    "how_are_you": [
        r'\b(?:kaise\s+ho|kaise\s+hain|kya\s+haal|kaisa\s+chal\s+raha|kya\s+chal\s+raha|sab\s+theek|sab\s+badhiya|how\s+are\s+you|how\s+is\s+it\s+going|hegiddira|hegidiya|chennagiddira|hegide|ela\s+unnaru|bagunnara|ela\s+undi|whats\s+up)\b',
        r'(?:ಹೇಗಿದ್ದೀರಾ|ಹೇಗಿದ್ದೀರಿ|ಹೇಗಿದೆ|ಚೆನ್ನಾಗಿದ್ದೀರಾ)',
        r'(?:ఎలా\s*ఉన్నారు|బాగున్నారా|ఎలా\s*ఉంది)',
        r'(?:कैसे\s*हो|कैसे\s*हैं|क्या\s*हाल|सब\s*ठीक)',
    ],
    "identity": [
        r'\b(?:tum\s+kaun\s+ho|aap\s+kaun\s+ho|kaun\s+ho|who\s+are\s+you|what\s+is\s+your\s+name|tumhara\s+naam|aapka\s+naam|neevu\s+yaaru|nimma\s+hesaru|nuvvu\s+evaru|mee\s+peru|what\s+do\s+you\s+do|kya\s+karte\s+ho|bolkhata\s+kya\s+hai|what\s+is\s+bolkhata|about\s+bolkhata|who\s+made\s+you)\b',
        r'(?:ನೀವು\s*ಯಾರು|ನಿಮ್ಮ\s*ಹೆಸರು)',
        r'(?:మీరు\s*ఎవరు|నువ్వు\s*ఎవరు|మీ\s*పేరు)',
        r'(?:तुम\s*कौन\s*हो|आप\s*कौन\s*हो|आपका\s*नाम)',
    ],
    "help": [
        r'\b(?:help|can\s+you\s+help|help\s+me|what\s+can\s+you\s+do|how\s+to\s+use|how\s+do\s+you\s+work|kaise\s+use\s+kare|madad|features|commands|guide)\b',
        r'(?:ಸಹಾಯ|ಏನು\s*ಮಾಡಬಹುದು)',
        r'(?:సహాయం|ఏమి\s*చేయగలరు)',
        r'(?:मदद|क्या\s*कर\s*सकते\s*हो)',
    ],
    "safety": [
        r'\b(?:safe\s+hai|surakshit|is\s+it\s+safe|data\s+safe|secure|leak|privacy|guarantee|bhadravagiya|surakshitama)\b',
        r'(?:ಸುರಕ್ಷಿತ|ಸುರಕ್ಷಿತವೇ|ಭದ್ರವಾಗಿದೆಯೇ)',
        r'(?:సురక్షితం|సురక్షితమేనా|భద్రమేనా)',
        r'(?:सुरक्षित|सेफ)',
    ],
    "gratitude": [
        r'\b(?:dhanyawaad|dhanyawad|shukriya|thank\s+you|thanks|dhanyavada|dhanyavadagalu|dhanyavadalu|bahut\s+achha|great\s+job|shabaash)\b',
        r'(?:ಧನ್ಯವಾದ|ಧನ್ಯವಾದಗಳು|ತುಂಬಾ\s*ಧನ್ಯವಾದ)',
        r'(?:ధన్యవాదాలు|చాలా\s*థాంక్స్)',
        r'(?:धन्यवाद|शुक्रिया)',
    ],
    "smalltalk": [
        r'\b(?:theek\s+hai|accha|okay|alright|sari|sare|bheed\s+hai|garmi\s+hai|barish\s+ho\s+rahi|dhandha\s+kaisa|kaam\s+kaisa)\b',
        r'(?:ಸರಿ|ಹೌದು|ಚೆನ್ನಾಗಿದೆ)',
        r'(?:సరే|అవును|బాగుంది)',
        r'(?:ठीक\s*है|अच्छा)',
    ],
}


def detect_chitchat(text: str) -> Optional[str]:
    """Identifies conversational intent topic if text is natural person small-talk."""
    text_lower = text.lower()
    for topic, patterns in CHITCHAT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                return topic
    return None


NAME_PATTERNS = [
    # "Clear debt for Ramesh", "Clear Ramesh's debt"
    r'(?:clear|settle)\s+(?:debt|account|dues)?\s*(?:for|of)?\s*([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)',
    # "Ramesh cleared his debt", "Ramesh has cleared his debt"
    r'([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:has\s+)?(?:cleared|settled|zeroed)\s+(?:his|her|all|the)?\s*(?:debt|account|dues|balance)',
    # English queries: "how much does ramesh owe", "what is ramesh balance", "show me ramesh total"
    r'(?:how\s+much\s+(?:does\s+)?|what\s+is\s+|show\s+(?:me\s+)?|check\s+|tell\s+(?:me\s+)?|give\s+(?:me\s+)?)([a-zA-Z]+)(?:\'s|\s+owe|\s+balance|\s+total|\s+account)',
    # Hyphenated descriptor names: 'Ramesh - Kirana Lane', 'Ramesh - Milk Dairy'
    r'(?:^|\s)([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:ka|ke|ki|ko|ne|ge|ku|ki)\s',
    # Name followed by took / borrowed / bought / gave / paid / le gaya / liya:
    r'(?:^|\s)([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:took|borrowed|bought|gave|paid|received|deposited|le\s+gaya|liya|diya)',
    # Name at start followed by number or amount: e.g. "Ramesh 500" or "Ramesh 340 udhaar"
    r'^([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:\d+|dedh|dhai|teen|char|paanch|one|two|three|four|five|\₹)',
    # "Ramesh cleared his debt", "Ramesh ne hisaab clear kar diya"
    r'(?:^|\s)([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:ne|cleared|settled|paid|ka|ki)\s',
    # Direct "Ramesh ka 340"
    r'(?:^|\s)([a-zA-Z]+)\s+(?:ka|ke|ki|ge|ku|ki)\s',
    # Query: "Ramesh total", "Ramesh ka total", "ramesh balance", "ramesh's balance"
    r'(?:^|\s)([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s*(?:ka|ke|ki|ge|ku|ki|\'s)?\s*(?:total|hisaab|balance|kitna|ottu|mottam|eshtu|entha|dues|account|owe|owes)',
]


def detect_language(text: str) -> str:
    """Accurately detects Kannada, Telugu, Hindi, or English."""
    # 1. Unicode Script Detection (100% accurate for native scripts)
    if re.search(r'[\u0C80-\u0CFF]', text):
        return "kn-IN"
    if re.search(r'[\u0C00-\u0C7F]', text):
        return "te-IN"
    if re.search(r'[\u0900-\u097F]', text):
        return "hi-IN"

    # 2. Vocabulary Frequency Scoring for Romanized Speech
    text_lower = text.lower()
    tokens = set(re.findall(r'\b\w+\b', text_lower))

    kn_vocab = {
        "saala", "kottiddaane", "kotta", "ivattu", "ninne", "mooru", "eradu",
        "nooru", "eshtu", "ottu", "alla", "bare", "ge", "namaskara", "hegiddira",
        "hegidiya", "chennagiddira", "yaaru", "dhanyavada", "sari", "nimma",
        "angadi", "grahakaru", "grahaka", "haalu", "akki", "bele", "sakkare",
        "hecchu", "kadime", "kaluhisi", "kodabeku", "thagondiddaane", "teeride",
        "theerisi", "nillu", "saaku"
    }
    te_vocab = {
        "appu", "icchaadu", "eeroju", "ninna", "moodu", "rendu", "vanda",
        "entha", "mottam", "kaadhu", "raayi", "ki", "namaskaram", "ela",
        "unnaru", "bagunnara", "evaru", "dhanyavadalu", "sare", "meeru",
        "dukanam", "customerlu", "paalu", "biyyam", "panchadara", "ekkuva",
        "thakkuva", "pampandi", "theerchesadu", "ivvaali", "theesukunnadu",
        "teeripoyindi", "aagu", "aapu"
    }
    hi_vocab = {
        "udhaar", "diya", "diye", "hisaab", "chukta", "kitna", "kitne", "aaj", "kal", "teen",
        "sau", "chaalis", "nahi", "likh", "likho", "jama", "namaste", "kaise", "haal",
        "kaun", "dhanyawaad", "shukriya", "bhaiya", "theek", "aapka", "surakshit",
        "kya", "ye", "yeh", "hai", "hain", "kaisa", "chahiye", "batao", "bataiye", "bata",
        "samaan", "liya", "kharida", "becha", "paise", "rupaye", "doodh", "chawal",
        "cheeni", "chini", "tel", "sabun", "chai", "atta", "daal", "sabse", "zyada",
        "jyada", "bada", "grahak", "dukaan", "bhejo", "kiska", "kisne", "vasool", "vasooli",
        "ruko", "bas", "chup", "shant"
    }

    en_vocab = {
        "cleared", "debt", "credit", "paid", "total", "balance", "yesterday",
        "today", "three", "forty", "hello", "hi", "how", "you", "who", "safe",
        "thanks", "thank", "good", "morning", "what", "is", "are", "does", "do",
        "can", "help", "owe", "owes", "due", "dues", "tell", "show", "give", "me",
        "much", "why", "where", "name", "customer", "customers", "account", "please", "my",
        "your", "store", "shop", "khata", "ledger", "bolkhata", "secure", "about",
        "sale", "sales", "check", "no", "yes", "all", "everyone", "send", "reminder",
        "collect", "collected", "highest", "most", "groceries", "milk", "rice", "sugar",
        "stop", "sleep", "standby", "reset"
    }

    kn_score = len(tokens & kn_vocab)
    te_score = len(tokens & te_vocab)
    hi_score = len(tokens & hi_vocab)
    en_score = len(tokens & en_vocab)

    if kn_score > te_score and kn_score > hi_score and kn_score > en_score:
        return "kn-IN"
    if te_score > kn_score and te_score > hi_score and te_score > en_score:
        return "te-IN"
    if en_score > hi_score and en_score > kn_score and en_score > te_score:
        return "en-IN"
    if hi_score > 0:
        return "hi-IN"
    if en_score > 0:
        return "en-IN"

    return "en-IN"


def _tokenize_clause(text: str) -> set:
    return set(re.findall(r'[\w\u0900-\u097F\u0C80-\u0CFF\u0C00-\u0C7F]+', text.lower()))


def _has_name(text: str) -> bool:
    for word in text.split():
        if word[0:1].isupper() and word.lower() not in SKIP_WORDS:
            return True
    return False


def _extract_customer_name(text: str) -> Optional[str]:
    # 1. Regex patterns
    for pattern in NAME_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            cand = m.group(1).strip()
            if cand.lower() not in SKIP_WORDS:
                return cand.title()

    # 2. Capitalized tokens
    words = text.split()
    for i, w in enumerate(words):
        clean = re.sub(r'[^a-zA-Z\u0900-\u097F\u0C80-\u0CFF\u0C00-\u0C7F]', '', w)
        if clean and clean[0].isupper() and clean.lower() not in SKIP_WORDS:
            # Check for hyphenated or descriptor names like "Ramesh - Kirana"
            if i + 2 < len(words) and words[i+1] in ("-", "–") and words[i+2][0].isupper():
                return f"{clean} - {words[i+2].title()}"
            return clean.title()

    # 3. Indic Scripts
    indic_words = re.findall(r'[\u0900-\u097F\u0C80-\u0CFF\u0C00-\u0C7F]+', text)
    for iw in indic_words:
        if iw not in SKIP_WORDS and len(iw) > 2:
            return iw

    return None


def _is_wake_command(text: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if utterance is or starts with wake-word: 'BolKhata' / 'Hey BolKhata'.
    Returns (is_wake, remaining_command_text_if_any).
    """
    m = re.match(WAKE_WORD_PATTERN, text.strip(), re.IGNORECASE)
    if m:
        remaining = text.strip()[m.end():].strip()
        return True, (remaining if remaining else None)
    return False, None


def _is_stop_command(text: str) -> bool:
    """Checks if merchant said stop/sleep/ruko/bas."""
    text_clean = text.strip().lower()
    return bool(re.search(STOP_COMMAND_PATTERN, text_clean, re.IGNORECASE))


def _is_reset_payments_query(text: str) -> bool:
    """Checks if merchant asked to reset today's payments."""
    text_clean = text.strip().lower()
    return bool(re.search(RESET_PAYMENTS_PATTERN, text_clean, re.IGNORECASE))


def _is_debt_clearing_utterance(text: str) -> bool:
    """Detect if utterance indicates complete debt settlement."""
    text_lower = text.lower()
    for phrase in CLEAR_DEBT_PHRASES:
        if re.search(phrase, text_lower):
            return True
    tokens = _tokenize_clause(text)
    # Check for combo: clear/chukta + hisaab/debt/saala/appu
    if (tokens & CLEAR_DEBT_KEYWORDS) and ({"debt", "hisaab", "saala", "appu", "baaki", "dues", "balance", "poora", "all"} & tokens):
        return True
    if "cleared" in tokens:
        return True
    # Indic script checks
    if any(k in text for k in ("ಸಾಲ ತೀರಿದೆ", "ಸಾಲ ಕ್ಲಿಯರ್", "ಅಪ್ಪು ತೀರಿపోయింది", "అప్పు తీరిపోయింది", "బాకీ క్లియర్", "उधार चुकता", "हिसाब चुकता")):
        return True
    return False


def _is_owner_registration(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detects if the shopkeeper is registering their name and store name.
    e.g. "Mera naam Niranjan hai, dukaan Sri Balaji Kirana"
         "Register my store Sri Balaji Kirana, owner Niranjan"
    """
    # 1. "mera naam <X> ... dukaan/store <Y>"
    m1 = re.search(r'(?:mera\s+naam|my\s+name\s+is|nanna\s+hesaru|naa\s+peru)\s+([a-zA-Z\s]+?)(?:\s+hai|\.|\,)?\s+(?:dukaan|dukan|shop|store|angadi|dukanam)(?:\s+ka\s+naam|\s+is|\s+hesaru|\s+peru)?\s+([a-zA-Z0-9\s]+)', text, re.IGNORECASE)
    if m1:
        owner = re.sub(r'\b(?:hai|is|ide|undi)\b', '', m1.group(1), flags=re.IGNORECASE).strip().title()
        store = m1.group(2).strip().title()
        return True, owner, store

    # 2. "dukaan <Y> ... owner/naam <X>"
    m2 = re.search(r'(?:dukaan|dukan|store|shop|angadi|dukanam)\s+(?:ka\s+naam\s+)?([a-zA-Z0-9\s]+?)(?:hai|\.|,)?\s+(?:owner|malik|mera\s+naam|owner\s+is)\s+([a-zA-Z\s]+)', text, re.IGNORECASE)
    if m2:
        owner = re.sub(r'\b(?:hai|is|ide|undi)\b', '', m2.group(2), flags=re.IGNORECASE).strip().title()
        store = m2.group(1).strip().title()
        return True, owner, store

    # 3. "register (my) store <Y> (owner) <X>"
    m3 = re.search(r'register\s+(?:my\s+)?(?:store|shop|dukaan)\s+([a-zA-Z0-9\s]+?)(?:\s+(?:owner|by|name)\s+([a-zA-Z\s]+))?$', text, re.IGNORECASE)
    if m3:
        store = m3.group(1).strip().title()
        owner = m3.group(2).strip().title() if m3.group(2) else "Store Owner"
        return True, owner, store

    return False, None, None


def _is_owner_query(text: str) -> bool:
    """Detects inquiries about the store owner's business health and overview."""
    text_lower = text.lower()
    return bool(re.search(r'\b(?:mera\s+store|mera\s+dukaan|meri\s+dukaan|my\s+store|my\s+shop|store\s+status|store\s+summary|how\s+is\s+my\s+store|business\s+status|dukaan\s+ka\s+hisaab|overall\s+dukaan|dukaan\s+summary)\b', text_lower))


def _is_top_debtor_query(text: str) -> bool:
    """Detects who owes the most money."""
    text_lower = text.lower()
    patterns = [
        r'\b(?:sabse\s+(?:jyada|zyada|bada)|highest\s+(?:debt|balance|dues)|who\s+owes\s+the\s+most|top\s+debtor|max\s+udhaar|kiska\s+sabse\s+(?:jyada|zyada))\b',
        r'(?:ಯಾರಿಗೆ\s*ಹೆಚ್ಚು\s*ಸಾಲ|ಹೆಚ್ಚು\s*ಬಾಕಿ)',
        r'(?:ఎవరికి\s*ఎక్కువ\s*అప్పు|ఎక్కువ\s*బాకీ)',
    ]
    return any(re.search(p, text_lower) for p in patterns)


def _is_customer_count_query(text: str) -> bool:
    """Detects queries about total customers count."""
    text_lower = text.lower()
    patterns = [
        r'\b(?:how\s+many\s+customers|total\s+customers|kitne\s+(?:customers|grahak|log)|count\s+of\s+customers)\b',
        r'(?:ಎಷ್ಟು\s*ಗ್ರಾಹಕರು|ಒಟ್ಟು\s*ಗ್ರಾಹಕರು)',
        r'(?:ఎంతమంది\s*కస్టమర్లు|మొత్తం\s*కస్టమర్లు)',
    ]
    return any(re.search(p, text_lower) for p in patterns)


def _is_collections_today_query(text: str) -> bool:
    """Detects queries about today's collection or payment receipts."""
    text_lower = text.lower()
    patterns = [
        r'\b(?:how\s+much\s+(?:did\s+we\s+)?collect|today(?:\'s)?\s+collection|aaj\s+kitna\s+(?:jama|collection|paisa\s+aaya|cash\s+aaya|vasool))\b',
        r'(?:ಇವತ್ತು\s*ಎಷ್ಟು\s*ಜಮಾ|ಇಂದು\s*ಎಷ್ಟು\s*ವಸೂಲಿ)',
        r'(?:ఈరోజు\s*ఎంత\s*జమ|ఈరోజు\s*ఎంత\s*వసూలు)',
    ]
    return any(re.search(p, text_lower) for p in patterns)


def _is_reminder_trigger(text: str) -> Tuple[bool, Optional[str]]:
    """Detects request to trigger polite payment reminder."""
    text_lower = text.lower()
    if "reminder" not in text_lower:
        return False, None
    m1 = re.search(r'([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:ko|ge|ki|ku)?\s*reminder', text, re.IGNORECASE)
    if m1 and m1.group(1).lower() not in SKIP_WORDS:
        return True, m1.group(1).strip().title()
    m2 = re.search(r'(?:send\s+reminder\s+to|reminder\s+to|remind)\s+([a-zA-Z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)', text, re.IGNORECASE)
    if m2 and m2.group(1).lower() not in SKIP_WORDS:
        return True, m2.group(1).strip().title()
    cust = _extract_customer_name(text)
    if cust and cust.lower() not in SKIP_WORDS:
        return True, cust
    return False, None


def _classify_intent_clause(clause_text: str) -> Tuple[IntentType, Optional[str]]:
    tokens = _tokenize_clause(clause_text)

    # 0a. Stop / Sleep Command ("Stop", "Ruko", "Bas", "Sleep")
    if _is_stop_command(clause_text):
        return IntentType.STOP_LISTENING, None

    # 0b. Wake-up Command ("BolKhata", "Hey BolKhata")
    is_wake, remaining = _is_wake_command(clause_text)
    if is_wake and not remaining:
        return IntentType.WAKE_UP, None

    # 0c. Reset Today's Payments ("Reset today's payment" / "Aaj ki jama reset karo")
    if _is_reset_payments_query(clause_text):
        return IntentType.RESET_TODAYS_PAYMENTS, None

    # 0d. Owner Registration ("Mera naam Niranjan hai, dukaan Sri Balaji Kirana")
    is_reg, owner_name, store_name = _is_owner_registration(clause_text)
    if is_reg:
        return IntentType.REGISTER_OWNER, f"{owner_name}|{store_name}"

    # 0e. Store Owner Overview Query ("Mera store kaisa chal raha hai?")
    if _is_owner_query(clause_text):
        return IntentType.QUERY_OWNER, None

    # 0f. Top Debtor Query ("Sabse zyada udhaar kiska hai?" / "Who owes the most?")
    if _is_top_debtor_query(clause_text):
        return IntentType.QUERY_TOP_DEBTOR, None

    # 0g. Customer Count Query ("Total customers kitne hain?")
    if _is_customer_count_query(clause_text):
        return IntentType.QUERY_CUSTOMERS_COUNT, None

    # 0h. Today Collections Query ("How much did we collect today?" / "Aaj kitna collection hua?")
    if _is_collections_today_query(clause_text):
        return IntentType.QUERY_COLLECTIONS_TODAY, None

    # 0i. Reminder Trigger ("Ramesh ko reminder bhejo" / "Send reminder to Ramesh")
    is_rem, rem_cust = _is_reminder_trigger(clause_text)
    if is_rem:
        return IntentType.TRIGGER_REMINDER, rem_cust

    # 1. Spoken Correction ("nahi, 430")
    if tokens & CORRECTION_KEYWORDS:
        return IntentType.CORRECTION, None

    # 2. Debt Clearing ("Ramesh cleared his debt" / "hisaab chukta ho gaya")
    if _is_debt_clearing_utterance(clause_text):
        return IntentType.CLEAR_DEBT, None

    # 3. Conversational Small-Talk & Chitchat (Greetings, How are you, Identity, Help, Safety)
    chitchat_topic = detect_chitchat(clause_text)
    if chitchat_topic and extract_first_amount(clause_text) is None:
        return IntentType.CHITCHAT, chitchat_topic

    # 4. Queries (English & Indic)
    has_query_kw = bool(tokens & QUERY_KEYWORDS)
    is_question = bool(re.search(r'\b(?:how\s+much|what\s+is|what\'s|show|tell|check|balance|total|kitna|eshtu|entha|dues|account)\b', clause_text, re.IGNORECASE))

    if has_query_kw or is_question:
        if (tokens & TODAY_QUERY_KEYWORDS) and not _extract_customer_name(clause_text):
            return IntentType.QUERY_TODAY, None
        if tokens & LIST_KEYWORDS:
            return IntentType.LIST_DUES, None
        return IntentType.QUERY_BALANCE, None

    # 5. Payment
    if tokens & PAYMENT_KEYWORDS:
        return IntentType.ADD_PAYMENT, None

    # 6. Credit
    if tokens & CREDIT_KEYWORDS:
        return IntentType.ADD_CREDIT, None

    # Default to credit if an amount is present
    if extract_first_amount(clause_text) is not None:
        return IntentType.ADD_CREDIT, None

    # Secondary chitchat fallback
    if chitchat_topic:
        return IntentType.CHITCHAT, chitchat_topic

    return IntentType.UNKNOWN, None


def _split_into_clauses(text: str) -> List[str]:
    tokens = _tokenize_clause(text)
    # Do not split corrections, debt clearings, reset payments, or owner registrations
    if (tokens & CORRECTION_KEYWORDS) or _is_debt_clearing_utterance(text) or _is_reset_payments_query(text) or _is_owner_registration(text)[0]:
        return [text.strip()]

    # Split by comma, semicolon, ' aur ', ' and ', ' mattu ', ' mari '
    raw_clauses = re.split(r'[,;]|\s+aur\s+|\s+and\s+|\s+mattu\s+|\s+mari\s+', text, flags=re.IGNORECASE)
    clauses = [c.strip() for c in raw_clauses if c.strip()]
    return clauses if clauses else [text.strip()]


def parse_clause(clause: str, default_customer: Optional[str] = None) -> ParsedIntent:
    intent, chitchat_topic = _classify_intent_clause(clause)
    cust_name = _extract_customer_name(clause) or default_customer
    amount = extract_first_amount(clause)
    txn_date = extract_date_from_text(clause)

    # In chitchat, don't accidentally capture words as customer names
    if intent in (IntentType.CHITCHAT, IntentType.STOP_LISTENING, IntentType.WAKE_UP, IntentType.RESET_TODAYS_PAYMENTS):
        cust_name = None
        amount = None
    elif intent == IntentType.TRIGGER_REMINDER:
        cust_name = chitchat_topic or cust_name
    elif intent in (IntentType.QUERY_TOP_DEBTOR, IntentType.QUERY_CUSTOMERS_COUNT, IntentType.QUERY_COLLECTIONS_TODAY, IntentType.QUERY_OWNER):
        cust_name = None
        amount = None

    direction = None
    if intent == IntentType.ADD_CREDIT:
        direction = TransactionDirection.CREDIT
    elif intent == IntentType.ADD_PAYMENT or intent == IntentType.CLEAR_DEBT:
        direction = TransactionDirection.PAYMENT

    confidence = 0.5
    if intent != IntentType.UNKNOWN:
        confidence += 0.2
    if cust_name:
        confidence += 0.2
    if amount is not None or intent in (IntentType.CLEAR_DEBT, IntentType.CHITCHAT, IntentType.RESET_TODAYS_PAYMENTS, IntentType.STOP_LISTENING, IntentType.WAKE_UP):
        confidence += 0.1

    return ParsedIntent(
        intent=intent,
        customer_name=cust_name,
        amount=amount,
        direction=direction,
        transaction_date=txn_date,
        raw_text=clause,
        confidence=min(confidence, 1.0),
        chitchat_topic=chitchat_topic,
    )


def parse_voice_utterance(text: str) -> List[ParsedIntent]:
    # Normalize common phonetic STT errors like 'kolkata' -> 'BolKhata'
    clean_text = re.sub(r'\b(?:kolkata|kolkatha|calcutta|bolkatha|bol\s*katha|gol\s*khata|call\s*khata|pol\s*khata|bhole\s*khata)\b', 'BolKhata', text.strip(), flags=re.IGNORECASE)

    # Check if prefixed with wake-word: e.g. "BolKhata, Ramesh ka 340 udhaar"
    is_wake, remainder = _is_wake_command(clean_text)
    if is_wake:
        if not remainder:
            return [ParsedIntent(intent=IntentType.WAKE_UP, raw_text=text, confidence=1.0)]
        else:
            text = remainder
    else:
        text = clean_text

    # Check for direct stop command
    if _is_stop_command(text):
        return [ParsedIntent(intent=IntentType.STOP_LISTENING, raw_text=text, confidence=1.0)]

    # Check for reset payments command
    if _is_reset_payments_query(text):
        return [ParsedIntent(intent=IntentType.RESET_TODAYS_PAYMENTS, raw_text=text, confidence=1.0)]

    clauses = _split_into_clauses(text)
    results: List[ParsedIntent] = []
    current_customer: Optional[str] = None

    for c in clauses:
        parsed = parse_clause(c, default_customer=current_customer)
        if parsed.customer_name:
            current_customer = parsed.customer_name
        results.append(parsed)

    return results


def parse_voice_command(text: str) -> ParsedIntent:
    actions = parse_voice_utterance(text)
    return actions[0] if actions else ParsedIntent(intent=IntentType.UNKNOWN, raw_text=text)
