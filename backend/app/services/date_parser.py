"""
BolKhata - Relative Date Parser
Handles Hindi/English relative date expressions.
"kal" → yesterday or tomorrow, "parso" → day before/after yesterday/tomorrow.
"""

from datetime import date, timedelta
from typing import Optional
import re


# ═══════════════════════════════════════════════════════════════
# Hindi/English relative date mappings
# ═══════════════════════════════════════════════════════════════

# Past-tense date words (used with "diya tha", "aaya tha")
PAST_DATES = {
    # Hindi
    "aaj": 0, "आज": 0,
    "kal": -1, "कल": -1,  # Yesterday (past context)
    "parso": -2, "परसो": -2, "parson": -2,
    "narso": -3, "नरसो": -3,
    "pichle hafte": -7,
    "pichle week": -7,
    
    # English
    "today": 0,
    "yesterday": -1,
    "day before yesterday": -2,
    "day before": -2,
    "last week": -7,
}

# Future-tense date words (used with "dena hai", "dega")
FUTURE_DATES = {
    "aaj": 0, "आज": 0,
    "kal": 1, "कल": 1,  # Tomorrow (future context)
    "parso": 2, "परसो": 2, "parson": 2,
    "narso": 3, "नरसो": 3,
    
    "today": 0,
    "tomorrow": 1,
    "day after tomorrow": 2,
    "day after": 2,
    "next week": 7,
}

# Past-context keywords (help determine if "kal" = yesterday or tomorrow)
PAST_CONTEXT_WORDS = {
    "tha", "thi", "the", "diya", "diye", "aaya", "aayi", "aaye",
    "kiya", "kiye", "gaya", "gayi", "gaye", "mila", "mili", "mile",
    "paid", "gave", "came", "did", "was", "were",
    "था", "थी", "थे", "दिया", "दिये", "आया", "आयी", "आये",
    "किया", "किये", "गया", "गयी", "गये", "मिला", "मिली", "मिले",
}

# Future-context keywords
FUTURE_CONTEXT_WORDS = {
    "dena", "denge", "dega", "degi", "aayega", "aayegi", "karega", "karegi",
    "will", "gonna", "going", "should", "must",
    "देना", "देंगे", "देगा", "देगी", "आएगा", "आएगी", "करेगा", "करेगी",
}


def _detect_tense(text: str) -> str:
    """Detect whether the sentence is past or future tense."""
    text_lower = text.lower()
    tokens = set(text_lower.split())
    
    past_score = len(tokens & PAST_CONTEXT_WORDS)
    future_score = len(tokens & FUTURE_CONTEXT_WORDS)
    
    if past_score > future_score:
        return "past"
    elif future_score > past_score:
        return "future"
    else:
        # Default to past (most common for ledger entries: "kal 200 diya tha")
        return "past"


def parse_relative_date(text: str, context_tense: str = "auto") -> Optional[date]:
    """
    Parse a relative date expression from text.
    
    Args:
        text: The input text containing a date reference
        context_tense: "past", "future", or "auto" (auto-detect from surrounding words)
    
    Returns:
        Resolved date, or None if no date reference found.
    
    Examples:
        "kal 200 diya tha" → yesterday
        "kal dena hai" → tomorrow
        "parso" (past context) → day before yesterday
    """
    text_lower = text.lower().strip()
    
    # Determine tense context
    if context_tense == "auto":
        context_tense = _detect_tense(text_lower)
    
    date_lookup = PAST_DATES if context_tense == "past" else FUTURE_DATES
    today = date.today()
    
    # Check for multi-word date expressions first (longest match)
    for phrase, offset in sorted(date_lookup.items(), key=lambda x: -len(x[0])):
        if phrase in text_lower:
            return today + timedelta(days=offset)
    
    return None


def extract_date_from_text(text: str) -> date:
    """
    Extract date from text, defaulting to today if no date reference found.
    
    This is the main function used by the NLU parser.
    """
    result = parse_relative_date(text)
    return result if result is not None else date.today()


# ═══════════════════════════════════════════════════════════════
# Quick test
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    today = date.today()
    test_cases = [
        ("Ramesh ne kal 200 diya tha", today - timedelta(days=1)),
        ("aaj ka hisaab", today),
        ("parso dena hai", today + timedelta(days=2)),
        ("Ramesh ka 340 udhaar", today),  # No date = today
    ]
    
    print("Date Parser Tests:")
    print("=" * 60)
    for text, expected in test_cases:
        result = extract_date_from_text(text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{text}' → {result} (expected {expected})")
