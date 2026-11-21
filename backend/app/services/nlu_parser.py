"""
BolKhata - Advanced Code-Mixed NLU (Natural Language Understanding) Engine
Specialized for Indian Kirana Store interactions:
- Handles compound utterances: "Ramesh ka 340 udhaar, kal 200 diya tha"
- Resolves anaphora (inherits customer name across clauses)
- Distinguishes credit (udhaar) vs payment (jama/diya)
- Parses relative dates ("kal", "parso", "aaj")
- Detects spoken corrections ("nahi, 430", "nahi 450 likho")
- Fast Q&A intent detection ("Aaj kitna udhaar gaya?", "Ramesh ka total?")
"""

import re
from datetime import date
from typing import Optional, List, Tuple

from app.models import ParsedIntent, IntentType, TransactionDirection
from app.services.number_parser import extract_amounts, extract_first_amount
from app.services.date_parser import extract_date_from_text, parse_relative_date


# ═══════════════════════════════════════════════════════════════
# Intent Keywords
# ═══════════════════════════════════════════════════════════════

CREDIT_KEYWORDS = {
    "udhaar", "udhar", "उधार", "khata", "खाता",
    "credit", "likh", "लिख", "likho", "लिखो", "likhna",
    "baaki", "बाकी", "baki",
    "dena hai", "देना है", "chahiye", "चाहिए",
    "lena", "लेना", "lena hai", "le gaya", "le gayi", "le gaye",
}

PAYMENT_KEYWORDS = {
    "diya", "दिया", "diye", "दिये", "de gaya", "de gaye",
    "jama", "जमा", "payment", "paid",
    "de diya", "दे दिया", "de diye", "दे दिये",
    "wapas", "वापस", "waapis",
    "bhara", "भरा", "bhare", "भरे",
    "mila", "मिला", "mile", "मिले",
    "aaya", "आया", "aaye", "आये",
    "received", "got",
}

QUERY_KEYWORDS = {
    "kitna", "कितना", "kitne", "कितने", "kitni", "कितनी",
    "total", "टोटल", "hisaab", "हिसाब", "hisab",
    "balance", "बैलेंस",
    "baaki", "बाकी", "baki",
    "how much", "what", "kya", "check",
}

TODAY_QUERY_KEYWORDS = {
    "aaj", "आज", "today",
    "abhi tak", "अभी तक",
    "din bhar", "दिन भर",
}

LIST_KEYWORDS = {
    "sabka", "सबका", "sab", "सब",
    "everyone", "all",
    "poora", "पूरा", "pura",
    "list", "लिस्ट",
}

CORRECTION_KEYWORDS = {
    "nahi", "नहीं", "nahin", "nhi", "no", "not",
    "galat", "गलत", "wrong",
    "correction", "sudhar", "सुधार",
    "change", "badal", "बदल", "badlo", "badal do",
    "cancel", "hatao", "हटाओ", "kat do", "kaat do",
}

REMINDER_KEYWORDS = {
    "reminder", "remind", "yaad", "yaad dilao", "bhejo",
    "message", "sms", "soochana", "suchna",
}

SKIP_WORDS = {
    "ka", "ke", "ki", "ko", "ne", "se", "me", "mein", "hai", "hain",
    "tha", "thi", "the", "wala", "wali", "wale",
    "का", "के", "की", "को", "ने", "से", "में", "है", "हैं",
    "था", "थी", "थे", "वाला", "वाली", "वाले",
    "udhaar", "udhar", "diya", "diye", "jama", "payment", "credit",
    "kitna", "kitne", "kitni", "total", "hisaab", "balance",
    "aaj", "kal", "parso", "rupees", "rupaye", "rs",
    "nahi", "nahin", "galat", "wrong",
    "bhai", "bhaiya", "ji", "sahab", "dost",
    "the", "a", "an", "is", "are", "was", "were", "has", "have",
    "and", "or", "but", "for", "of", "to", "in", "on", "aur",
}

NAME_PATTERNS = [
    # "Ramesh Sharma ka 340 udhaar" -> Ramesh Sharma
    r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:ka|ke|ki|ko|ne)\s',
    # "Ramesh ka total" -> Ramesh
    r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:ka|ke|ki)\s+(?:total|hisaab|balance|kitna|baaki)',
    # "Ramesh ne 200 diya" -> Ramesh
    r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+ne\s',
]


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
            candidate = m.group(1).strip()
            if candidate.lower() not in SKIP_WORDS:
                return candidate.title()

    # 2. Capitalized tokens
    for w in text.split():
        clean = re.sub(r'[^a-zA-Z\u0900-\u097F]', '', w)
        if clean and clean[0].isupper() and clean.lower() not in SKIP_WORDS:
            return clean.title()

    # 3. Indic Devanagari script names
    hindi_words = re.findall(r'[\u0900-\u097F]+', text)
    for hw in hindi_words:
        if hw not in SKIP_WORDS and len(hw) > 2:
            return hw

    return None


def _tokenize_clause(text: str) -> set:
    """Extract clean words/tokens without punctuation, supporting Indic scripts."""
    return set(re.findall(r'[\w\u0900-\u097F]+', text.lower()))


def _classify_intent_clause(clause_text: str) -> IntentType:
    tokens = _tokenize_clause(clause_text)

    # Correction check
    if tokens & CORRECTION_KEYWORDS:
        return IntentType.CORRECTION

    # Query checks
    if tokens & QUERY_KEYWORDS:
        if (tokens & TODAY_QUERY_KEYWORDS) and not _has_name(clause_text):
            return IntentType.QUERY_TODAY
        if tokens & LIST_KEYWORDS:
            return IntentType.LIST_DUES
        return IntentType.QUERY_BALANCE

    # Payment
    if tokens & PAYMENT_KEYWORDS:
        return IntentType.ADD_PAYMENT

    # Credit
    if tokens & CREDIT_KEYWORDS:
        return IntentType.ADD_CREDIT

    # If amount + name exist without explicit verb, kirana default is credit
    if extract_first_amount(clause_text) is not None:
        return IntentType.ADD_CREDIT

    return IntentType.UNKNOWN


def _split_into_clauses(text: str) -> List[str]:
    """
    Split complex sentences like:
    'Ramesh ka 340 udhaar, kal 200 diya tha'
    into:
    ['Ramesh ka 340 udhaar', 'kal 200 diya tha']
    """
    # If the text is a spoken correction (e.g. 'nahi, 430'), do NOT split it
    tokens = _tokenize_clause(text)
    if tokens & CORRECTION_KEYWORDS:
        return [text.strip()]

    # Split by comma, semicolon, ' aur ', ' and '
    raw_clauses = re.split(r'[,;]|\s+aur\s+|\s+and\s+', text, flags=re.IGNORECASE)
    clauses = [c.strip() for c in raw_clauses if c.strip()]
    return clauses if clauses else [text.strip()]


def parse_clause(
    clause: str,
    default_customer: Optional[str] = None,
) -> ParsedIntent:
    """Parse a single clause, optionally inheriting customer name."""
    intent = _classify_intent_clause(clause)
    cust_name = _extract_customer_name(clause) or default_customer
    amount = extract_first_amount(clause)
    txn_date = extract_date_from_text(clause)

    direction = None
    if intent == IntentType.ADD_CREDIT:
        direction = TransactionDirection.CREDIT
    elif intent == IntentType.ADD_PAYMENT:
        direction = TransactionDirection.PAYMENT

    confidence = 0.5
    if intent != IntentType.UNKNOWN:
        confidence += 0.2
    if cust_name:
        confidence += 0.15
    if amount is not None:
        confidence += 0.15

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
    """
    Parses an entire voice utterance, which may contain single or compound actions.
    
    Example:
    'Ramesh ka 340 udhaar, kal 200 diya tha'
    -> [
        ParsedIntent(ADD_CREDIT, 'Ramesh', 340, today),
        ParsedIntent(ADD_PAYMENT, 'Ramesh', 200, yesterday)
    ]
    """
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
    """
    Backwards-compatible single intent parser.
    Returns the primary parsed intent for the utterance.
    """
    actions = parse_voice_utterance(text)
    if not actions:
        return ParsedIntent(intent=IntentType.UNKNOWN, raw_text=text)
    # Return first action as primary
    return actions[0]
