"""
BolKhata - Advanced Code-Mixed Numeral Parser
Engineered for real-world Indian Kirana Store audio & transcripts:
- Standard digits: "340", "₹340", "Rs 340", "340.50"
- Full Hindi numbers: "teen sau chaalis" -> 340, "paanch sau" -> 500
- Colloquial English compound numbers: "three-forty" / "three forty" -> 340, "two fifty" -> 250, "twelve fifty" -> 1250, "fifteen hundred" -> 1500
- Indic colloquial Kirana terms:
    "dedh sau" -> 150, "dhai sau" -> 250, "sadhe teen sau" -> 350
    "sawa sau" -> 125, "paune do sau" -> 175
    "dedh hazaar" -> 1500, "dhai hazaar" -> 2500
- Mixed Indic-English: "3 sau 40" -> 340, "2 hazaar 500" -> 2500
"""

import re
from typing import Optional, List, Tuple

# Base single digits (Hindi Romanized & Devanagari)
HINDI_ONES = {
    "ek": 1, "एक": 1,
    "do": 2, "दो": 2,
    "teen": 3, "तीन": 3,
    "chaar": 4, "चार": 4, "char": 4,
    "paanch": 5, "पाँच": 5, "panch": 5, "पांच": 5,
    "chhah": 6, "छह": 6, "chhe": 6, "che": 6, "छ": 6,
    "saat": 7, "सात": 7,
    "aath": 8, "आठ": 8, "ath": 8,
    "nau": 9, "नौ": 9,
}

HINDI_TENS = {
    "das": 10, "दस": 10,
    "gyarah": 11, "ग्यारह": 11, "gyara": 11,
    "barah": 12, "बारह": 12, "bara": 12,
    "terah": 13, "तेरह": 13, "tera": 13,
    "chaudah": 14, "चौदह": 14, "chauda": 14,
    "pandrah": 15, "पंद्रह": 15, "pandra": 15,
    "solah": 16, "सोलह": 16, "sola": 16,
    "satrah": 17, "सत्रह": 17, "satra": 17,
    "attharah": 18, "अठारह": 18, "atharah": 18, "athara": 18,
    "unees": 19, "उन्नीस": 19, "unis": 19,
    "bees": 20, "बीस": 20, "bis": 20,
    "ikkees": 21, "इक्कीस": 21,
    "baaees": 22, "बाईस": 22, "baais": 22,
    "teis": 23, "तेईस": 23, "tayis": 23,
    "chaubees": 24, "चौबीस": 24,
    "pachchees": 25, "पच्चीस": 25, "pachees": 25, "pachis": 25,
    "chhabbees": 26, "छब्बीस": 26, "chabbis": 26,
    "sattaees": 27, "सत्ताईस": 27, "satais": 27,
    "atthaees": 28, "अट्ठाईस": 28, "athais": 28,
    "untees": 29, "उनतीस": 29, "untis": 29,
    "tees": 30, "तीस": 30, "tis": 30,
    "ikattees": 31, "इकतीस": 31, "iktis": 31,
    "battees": 32, "बत्तीस": 32, "battis": 32,
    "taintees": 33, "तैंतीस": 33, "tentis": 33,
    "chauntees": 34, "चौंतीस": 34, "chautis": 34,
    "paintees": 35, "पैंतीस": 35, "pentis": 35,
    "chhattees": 36, "छत्तीस": 36, "chattis": 36,
    "saintees": 37, "सैंतीस": 37, "sentis": 37,
    "adtees": 38, "अड़तीस": 38, "adtis": 38,
    "untaalees": 39, "उनतालीस": 39, "untalis": 39,
    "chaalis": 40, "चालीस": 40, "chalis": 40,
    "iktaalis": 41, "इकतालीस": 41, "iktalis": 41,
    "bayaalis": 42, "बयालीस": 42, "bayalis": 42,
    "taintaalis": 43, "तैंतालीस": 43, "tentalis": 43,
    "chawaalis": 44, "चवालीस": 44, "chawalis": 44,
    "paintaalis": 45, "पैंतालीस": 45, "pentalis": 45,
    "chhiyaalis": 46, "छियालीस": 46, "chiyalis": 46,
    "saintaalis": 47, "सैंतालीस": 47, "sentalis": 47,
    "adtaalis": 48, "अड़तालीस": 48, "adtalis": 48,
    "unchaas": 49, "उनचास": 49, "unchas": 49,
    "pachaas": 50, "पचास": 50, "pachas": 50,
    "ikaavan": 51, "इक्यावन": 51, "ikyavan": 51,
    "baawan": 52, "बावन": 52, "bawan": 52,
    "tirpan": 53, "तिरपन": 53,
    "chauvan": 54, "चौवन": 54,
    "pachpan": 55, "पचपन": 55,
    "chhappan": 56, "छप्पन": 56,
    "sattaavan": 57, "सत्तावन": 57, "satavan": 57,
    "atthaavan": 58, "अट्ठावन": 58, "athavan": 58,
    "unsath": 59, "उनसठ": 59,
    "saath": 60, "साठ": 60, "sath": 60,
    "iksath": 61, "इकसठ": 61,
    "baasath": 62, "बासठ": 62,
    "tirsath": 63, "तिरसठ": 63,
    "chausath": 64, "चौंसठ": 64,
    "painsath": 65, "पैंसठ": 65,
    "chhiyaasath": 66, "छियासठ": 66,
    "sadsath": 67, "सड़सठ": 67,
    "adsath": 68, "अड़सठ": 68,
    "unhattar": 69, "उनहत्तर": 69,
    "sattar": 70, "सत्तर": 70,
    "ikattar": 71, "इकहत्तर": 71,
    "bahattar": 72, "बहत्तर": 72,
    "tihattar": 73, "तिहत्तर": 73,
    "chauhattar": 74, "चौहत्तर": 74,
    "pachhattar": 75, "पचहत्तर": 75, "pachattar": 75,
    "chhihattar": 76, "छिहत्तर": 76,
    "sathattar": 77, "सतहत्तर": 77,
    "athhattar": 78, "अठहत्तर": 78,
    "unasi": 79, "उनासी": 79, "unasi": 79,
    "assi": 80, "अस्सी": 80, "asi": 80,
    "ikasi": 81, "इक्यासी": 81,
    "bayasi": 82, "बयासी": 82,
    "tirasi": 83, "तिरासी": 83,
    "chaurasi": 84, "चौरासी": 84,
    "pachasi": 85, "पचासी": 85,
    "chhiasi": 86, "छियासी": 86,
    "sattasi": 87, "सतासी": 87,
    "atthasi": 88, "अठासी": 88,
    "nawaasi": 89, "नवासी": 89, "nawasi": 89,
    "nabbe": 90, "नब्बे": 90, "nabe": 90,
    "ikaanbe": 91, "इक्यानबे": 91,
    "baanbe": 92, "बानबे": 92,
    "tiranbe": 93, "तिरानबे": 93,
    "chauranbe": 94, "चौरानबे": 94,
    "pachanbe": 95, "पचानबे": 95,
    "chhiyanbe": 96, "छियानबे": 96,
    "sattanbe": 97, "सत्तानबे": 97,
    "atthanbe": 98, "अट्ठानबे": 98,
    "ninyaanbe": 99, "निन्यानबे": 99, "ninyanbe": 99,
}

HINDI_MULTIPLIERS = {
    "sau": 100, "सौ": 100, "so": 100,
    "hazaar": 1000, "हज़ार": 1000, "hazar": 1000, "hajar": 1000, "हजार": 1000,
    "lakh": 100000, "लाख": 100000, "lac": 100000, "lacs": 100000,
    "crore": 10000000, "करोड़": 10000000, "karor": 10000000,
}

# Special Indian Kirana expressions
INDIC_FRACTION_AMOUNTS = {
    "dedh sau": 150.0, "डेढ़ सौ": 150.0, "derd sau": 150.0, "derh sau": 150.0,
    "dhai sau": 250.0, "ढाई सौ": 250.0, "dhai so": 250.0,
    "sadhe teen sau": 350.0, "साढ़े तीन सौ": 350.0,
    "sadhe chaar sau": 450.0, "साढ़े चार सौ": 450.0,
    "sadhe paanch sau": 550.0, "साढ़े पाँच सौ": 550.0,
    "sawa sau": 125.0, "सवा सौ": 125.0,
    "paune do sau": 175.0, "पौने दो सौ": 175.0,
    "paune teen sau": 275.0, "पौने तीन सौ": 275.0,
    "dedh hazaar": 1500.0, "डेढ़ हज़ार": 1500.0, "dedh hazar": 1500.0,
    "dhai hazaar": 2500.0, "ढाई हज़ार": 2500.0, "dhai hazar": 2500.0,
}

# English numbers
ENGLISH_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
}

ENGLISH_TEENS = {
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19,
}

ENGLISH_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

ENGLISH_MULTIPLIERS = {
    "hundred": 100, "thousand": 1000, "lakh": 100000, "lakhs": 100000,
    "crore": 10000000, "crores": 10000000,
}

ALL_ONES = {**HINDI_ONES, **ENGLISH_ONES}
ALL_TENS = {**HINDI_TENS, **ENGLISH_TEENS, **ENGLISH_TENS}
ALL_MULTIPLIERS = {**HINDI_MULTIPLIERS, **ENGLISH_MULTIPLIERS}


def _clean_token(tok: str) -> str:
    return tok.strip().lower()


def _try_compound_english_number(tokens: List[str]) -> Optional[Tuple[float, int]]:
    """
    Handles expressions like:
    - "three forty" -> 340 (3 * 100 + 40)
    - "three forty five" -> 345 (3 * 100 + 45)
    - "twelve fifty" -> 1250 (12 * 100 + 50)
    - "fifteen hundred" -> 1500 (15 * 100)
    - "twenty five hundred" -> 2500 (25 * 100)
    - "twenty five fifty" -> 2550 (25 * 100 + 50)
    Returns (amount, tokens_consumed) if matched, else None.
    """
    if len(tokens) < 2:
        return None

    t0, t1 = tokens[0], tokens[1]
    
    # Pattern A: single digit / teen (1-19) + "hundred" -> e.g. "fifteen hundred" = 1500
    val0 = ALL_ONES.get(t0) or ALL_TENS.get(t0)
    if val0 is not None and t1 in ("hundred", "sau", "so"):
        base = val0 * 100
        # Check if 3rd and 4th token follow, e.g. "fifteen hundred fifty" -> 1550
        if len(tokens) >= 3:
            t2 = tokens[2]
            val2 = ALL_TENS.get(t2) or ALL_ONES.get(t2)
            if val2 is not None:
                if len(tokens) >= 4 and t2 in ENGLISH_TENS and tokens[3] in ALL_ONES:
                    return (base + val2 + ALL_ONES[tokens[3]], 4)
                return (base + val2, 3)
        return (base, 2)

    # Pattern B: Single digit (1-9) + Tens (20-99) without the word "hundred"
    # E.g.: "three forty" -> 340, "two fifty" -> 250, "one twenty" -> 120
    # Also handles "three forty five" -> 345
    if val0 is not None and 1 <= val0 <= 9:
        val1 = ALL_TENS.get(t1)
        if val1 is not None and 10 <= val1 <= 99:
            base = val0 * 100 + val1
            if len(tokens) >= 3 and t1 in ENGLISH_TENS:
                t2 = tokens[2]
                val2 = ALL_ONES.get(t2)
                if val2 is not None and 1 <= val2 <= 9:
                    return (base + val2, 3)
            return (base, 2)

    # Pattern C: Teen (11-19) + Tens (20-99), e.g. "twelve fifty" -> 1250
    if val0 is not None and 11 <= val0 <= 19:
        val1 = ALL_TENS.get(t1)
        if val1 is not None and 10 <= val1 <= 99:
            base = val0 * 100 + val1
            return (base, 2)

    return None


def parse_spoken_number(text: str) -> Optional[float]:
    """
    Parse any spoken code-mixed Indian or English numeral into a float.
    """
    if not text:
        return None

    # Pre-clean string
    cleaned = text.lower().replace("-", " ").replace("–", " ").strip()

    # Check for direct digit string
    digit_match = re.match(r'^(?:₹|rs\.?\s*)?(\d+(?:,\d{3})*(?:\.\d+)?)$', cleaned)
    if digit_match:
        try:
            return float(digit_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # Check for exact Indic fraction amounts ("dedh sau", "dhai sau", etc.)
    for phrase, val in INDIC_FRACTION_AMOUNTS.items():
        if phrase in cleaned:
            return val

    tokens = [_clean_token(t) for t in cleaned.split() if t.strip()]
    if not tokens:
        return None

    # Try colloquial compound English first (e.g. "three forty" -> 340)
    compound_res = _try_compound_english_number(tokens)
    if compound_res is not None:
        return compound_res[0]

    # Standard hierarchical parser for multi-word numerals
    total = 0.0
    current = 0.0
    found_any = False

    i = 0
    while i < len(tokens):
        t = tokens[i]

        # 1. Pure digit token (e.g. "3" in "3 sau 40")
        if re.match(r'^\d+(\.\d+)?$', t):
            val = float(t)
            current += val
            found_any = True
            i += 1
            continue

        # 2. Multiplier token (sau, hundred, hazaar, thousand, lakh)
        if t in ALL_MULTIPLIERS:
            mult = ALL_MULTIPLIERS[t]
            if current == 0:
                current = 1.0
            
            if mult >= 1000:
                total += current * mult
                current = 0.0
            else:
                current *= mult
            found_any = True
            i += 1
            continue

        # 3. Base number words
        val = ALL_ONES.get(t) or ALL_TENS.get(t)
        if val is not None:
            # Check if this token starts a compound like "three forty" within a larger phrase
            comp = _try_compound_english_number(tokens[i:])
            if comp is not None:
                current += comp[0]
                i += comp[1]
                found_any = True
                continue
            
            current += val
            found_any = True
            i += 1
            continue

        # Non-number token encountered
        i += 1

    final_val = total + current
    return final_val if found_any else None


def extract_amounts(text: str) -> List[Tuple[float, str]]:
    """
    Extract all distinct numeric amounts from text, preserving order.
    Returns list of (amount_float, original_substring).
    """
    results: List[Tuple[float, str]] = []
    text_lower = text.lower().replace("-", " ")

    # 1. Extract standard digits (e.g. ₹340, 340, 200.50)
    digit_pattern = r'(?:₹|rs\.?\s*)?(\b\d+(?:,\d{3})*(?:\.\d{1,2})?\b)'
    for m in re.finditer(digit_pattern, text_lower):
        try:
            val = float(m.group(1).replace(",", ""))
            if 0 < val <= 50_00_000:
                results.append((val, m.group(0)))
        except ValueError:
            pass

    # 2. Check for Indic fraction phrases ("dedh sau", "dhai sau", etc.)
    for phrase, val in INDIC_FRACTION_AMOUNTS.items():
        if phrase in text_lower:
            results.append((val, phrase))

    # 3. Extract word-based number clusters
    word_vocab = set(ALL_ONES.keys()) | set(ALL_TENS.keys()) | set(ALL_MULTIPLIERS.keys())
    tokens = text_lower.split()

    i = 0
    while i < len(tokens):
        # Look for start of a number sequence
        tok = _clean_token(tokens[i])
        if tok in word_vocab or re.match(r'^\d+$', tok):
            j = i
            while j < len(tokens) and (_clean_token(tokens[j]) in word_vocab or re.match(r'^\d+$', _clean_token(tokens[j]))):
                j += 1
            phrase = " ".join(tokens[i:j])
            amt = parse_spoken_number(phrase)
            if amt is not None and 0 < amt <= 50_00_000:
                # Add if not duplicate
                if not any(abs(existing[0] - amt) < 0.01 for existing in results):
                    results.append((amt, phrase))
            i = j
        else:
            i += 1

    return results


def extract_first_amount(text: str) -> Optional[float]:
    """Returns the first detected amount in text."""
    amounts = extract_amounts(text)
    return amounts[0][0] if amounts else None
