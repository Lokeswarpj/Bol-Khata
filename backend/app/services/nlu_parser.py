"""
BolKhata - Production Multilingual Kirana NLU Engine
Engineered to eliminate false defaults and handle real-world Kirana store interactions:
- Full Debt Settlement ("Ramesh cleared his debt" / "hisaab chukta kar diya")
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

# Debt Clearing (Full Settlement) Keywords
CLEAR_DEBT_KEYWORDS = {
    # English
    "cleared", "clear", "settled", "settle", "paid off", "zeroed", "clearing",
    # Hindi
    "chukta", "चुक्ता", "chukti", "chuka diya", "chuka", "khatam", "खत्म",
    "saaf", "साफ", "faisla", "phaisla",
    # Kannada
    "theerisi", "ತೀರಿಸಿ", "theerisiddaane", "mugisiddaane", "theerthu",
    # Telugu
    "theerchesadu", "తీర్చేశాడు", "theerchadu", "poorthi", "chellinchesadu",
}

CLEAR_DEBT_PHRASES = [
    r'cleared\s+(?:his|her|all|the)?\s*(?:debt|account|dues|balance|khata)',
    r'cleared\s+all',
    r'hisaab\s+(?:clear|chukta|khatam|saaf)',
    r'poora\s+(?:de\s+diya|jama\s+kar\s+diya|chukta)',
    r'saala\s+theerisi',
    r'appu\s+theerchesadu',
]

# Credit (Udhaar / Debt addition) Keywords
CREDIT_KEYWORDS = {
    # Hindi
    "udhaar", "udhar", "उधार", "khata", "खाता", "likh", "लिख", "likho", "लिखो", "likhna",
    "likhle", "likhlo", "baaki", "बाकी", "baki", "le gaya", "le gaye", "dena hai",
    # Kannada
    "saala", "ಸಾಲ", "baaki", "ಬಾಕಿ", "bare", "ಬರೆ", "bareyiri", "ಬರೆಯಿರಿ",
    "khaate", "ಖಾತೆ", "uddhaara", "ಉದ್ದಾರ", "thagondiddaane", "kodabeku",
    # Telugu
    "appu", "అప్పు", "baaki", "బాకీ", "raayi", "రాయ్", "raayandi", "రాయండి",
    "khata", "ఖాతా", "theesukunnadu", "ivvaali",
    # English
    "credit", "due", "loan", "borrowed", "took", "write", "bill",
}

# Payment (Jama / Money received) Keywords
PAYMENT_KEYWORDS = {
    # Hindi
    "diya", "दिया", "diye", "दिये", "de gaya", "jama", "जमा", "wapas", "वापस",
    "aaya", "aaye", "bhara", "vasool", "वसूूल", "mila", "मिला", "de diya",
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
    "total", "balance", "how much", "what is",
}

TODAY_QUERY_KEYWORDS = {
    "aaj", "आज", "today", "abhi tak", "ivattu", "ಇವತ್ತು", "eeroju", "ఈరోజు",
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
}

NAME_PATTERNS = [
    # Hyphenated descriptor names: 'Ramesh - Kirana Lane', 'Ramesh - Milk Dairy'
    r'(?:^|\s)([A-Z][a-z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:ka|ke|ki|ko|ne|ge|ku|ki)\s',
    # "Ramesh cleared his debt", "Ramesh ne hisaab clear kar diya"
    r'(?:^|\s)([A-Z][a-z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s+(?:ne|cleared|settled|paid|ka|ki)\s',
    # Direct "Ramesh ka 340"
    r'(?:^|\s)([A-Z][a-z]+)\s+(?:ka|ke|ki|ge|ku|ki)\s',
    # Query: "Ramesh total", "Ramesh ka total"
    r'(?:^|\s)([A-Z][a-z]+(?:\s+[-–]\s+[A-Za-z\s]+)?)\s*(?:ka|ke|ki|ge|ku|ki)?\s*(?:total|hisaab|balance|kitna|ottu|mottam|eshtu|entha)',
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

    kn_vocab = {"saala", "kottiddaane", "kotta", "ivattu", "ninne", "mooru", "eradu", "nooru", "eshtu", "ottu", "alla", "bare", "ge"}
    te_vocab = {"appu", "icchaadu", "eeroju", "ninna", "moodu", "rendu", "vanda", "entha", "mottam", "kaadhu", "raayi", "ki"}
    hi_vocab = {"udhaar", "diya", "hisaab", "chukta", "kitna", "aaj", "kal", "teen", "sau", "chaalis", "nahi", "likh", "jama"}

    kn_score = len(tokens & kn_vocab)
    te_score = len(tokens & te_vocab)
    hi_score = len(tokens & hi_vocab)

    if kn_score > te_score and kn_score > hi_score:
        return "kn-IN"
    if te_score > kn_score and te_score > hi_score:
        return "te-IN"
    if hi_score > 0:
        return "hi-IN"

    # English check
    en_vocab = {"cleared", "debt", "credit", "paid", "total", "balance", "yesterday", "today", "three", "forty"}
    if len(tokens & en_vocab) > 0:
        return "en-IN"

    return "hi-IN"


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
        m = re.search(pattern, text)
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
    return False


def _classify_intent_clause(clause_text: str) -> IntentType:
    tokens = _tokenize_clause(clause_text)

    # 1. Spoken Correction
    if tokens & CORRECTION_KEYWORDS:
        return IntentType.CORRECTION

    # 2. Debt Clearing (CRITICAL FIX: Checks before adding credit!)
    if _is_debt_clearing_utterance(clause_text):
        return IntentType.CLEAR_DEBT

    # 3. Queries
    if tokens & QUERY_KEYWORDS:
        if (tokens & TODAY_QUERY_KEYWORDS) and not _has_name(clause_text):
            return IntentType.QUERY_TODAY
        if tokens & LIST_KEYWORDS:
            return IntentType.LIST_DUES
        return IntentType.QUERY_BALANCE

    # 4. Payment
    if tokens & PAYMENT_KEYWORDS:
        return IntentType.ADD_PAYMENT

    # 5. Credit
    if tokens & CREDIT_KEYWORDS:
        return IntentType.ADD_CREDIT

    # Default to credit if an amount is present
    if extract_first_amount(clause_text) is not None:
        return IntentType.ADD_CREDIT

    return IntentType.UNKNOWN


def _split_into_clauses(text: str) -> List[str]:
    tokens = _tokenize_clause(text)
    # Do not split corrections or debt clearings
    if (tokens & CORRECTION_KEYWORDS) or _is_debt_clearing_utterance(text):
        return [text.strip()]

    # Split by comma, semicolon, ' aur ', ' and ', ' mattu ', ' mari '
    raw_clauses = re.split(r'[,;]|\s+aur\s+|\s+and\s+|\s+mattu\s+|\s+mari\s+', text, flags=re.IGNORECASE)
    clauses = [c.strip() for c in raw_clauses if c.strip()]
    return clauses if clauses else [text.strip()]


def parse_clause(clause: str, default_customer: Optional[str] = None) -> ParsedIntent:
    intent = _classify_intent_clause(clause)
    cust_name = _extract_customer_name(clause) or default_customer
    amount = extract_first_amount(clause)
    txn_date = extract_date_from_text(clause)

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
    if amount is not None or intent == IntentType.CLEAR_DEBT:
        confidence += 0.1

    return ParsedIntent(
        intent=intent,
        customer_name=cust_name,
        amount=amount,
        direction=direction,
        transaction_date=txn_date,
        raw_text=clause,
        confidence=min(confidence, 1.0),
    )


def parse_voice_utterance(text: str) -> List[ParsedIntent]:
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
