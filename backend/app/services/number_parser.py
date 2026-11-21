"""
BolKhata - Multilingual Indian Number & Currency Parser
Supports Hindi, Kannada, Telugu, English & Code-Mixed variants.
"""

import re
from typing import Optional, List, Tuple

# ═══════════════════════════════════════════════════════════════
# 1. Hindi (Devanagari & Transliterated)
# ═══════════════════════════════════════════════════════════════
HINDI_ONES = {
    "ek": 1, "एक": 1, "do": 2, "दो": 2, "teen": 3, "तीन": 3,
    "chaar": 4, "चार": 4, "char": 4, "paanch": 5, "पाँच": 5, "panch": 5, "पांच": 5,
    "chhah": 6, "छह": 6, "chhe": 6, "che": 6, "छ": 6, "saat": 7, "सात": 7,
    "aath": 8, "आठ": 8, "ath": 8, "nau": 9, "नौ": 9,
}

HINDI_TENS = {
    "das": 10, "दस": 10, "gyarah": 11, "ग्यारह": 11, "barah": 12, "बारह": 12,
    "terah": 13, "तेरह": 13, "chaudah": 14, "चौदह": 14, "pandrah": 15, "पंद्रह": 15,
    "solah": 16, "सोलह": 16, "satrah": 17, "सत्रह": 17, "attharah": 18, "अठारह": 18,
    "unees": 19, "उन्नीस": 19, "bees": 20, "बीस": 20, "ikkees": 21, "इक्कीस": 21,
    "pachchees": 25, "पच्चीस": 25, "tees": 30, "तीस": 30, "paintees": 35, "पैंतीस": 35,
    "chaalis": 40, "चालीस": 40, "chalis": 40, "taintaalis": 43, "तैंतालीस": 43,
    "pachaas": 50, "पचास": 50, "saath": 60, "साठ": 60, "sattar": 70, "सत्तर": 70,
    "assi": 80, "अस्सी": 80, "nabbe": 90, "नब्बे": 90,
}

HINDI_MULTIPLIERS = {
    "sau": 100, "सौ": 100, "so": 100,
    "hazaar": 1000, "हज़ार": 1000, "hazar": 1000, "hajar": 1000,
    "lakh": 100000, "लाख": 100000, "crore": 10000000, "करोड़": 10000000,
}

INDIC_FRACTIONS = {
    "dedh sau": 150.0, "डेढ़ सौ": 150.0,
    "dhai sau": 250.0, "ढाई सौ": 250.0,
    "sadhe teen sau": 350.0, "साढ़े तीन सौ": 350.0,
    "sadhe chaar sau": 450.0, "साढ़े चार सौ": 450.0,
    "dedh hazaar": 1500.0, "डेढ़ हज़ार": 1500.0,
    "dhai hazaar": 2500.0, "ढाई हज़ार": 2500.0,
}

# ═══════════════════════════════════════════════════════════════
# 2. Kannada (Kannada Script & Transliterated)
# ═══════════════════════════════════════════════════════════════
KANNADA_ONES = {
    "ondu": 1, "ಒಂದು": 1, "eradu": 2, "ಎರಡು": 2, "mooru": 3, "ಮೂರು": 3,
    "naalku": 4, "ನಾಲ್ಕು": 4, "nalku": 4, "aidu": 5, "ಐದು": 5,
    "aaru": 6, "ಆರು": 6, "eelu": 7, "ಏಳು": 7, "elu": 7,
    "entu": 8, "ಎಂಟು": 8, "ombattu": 9, "ಒಂಬತ್ತು": 9,
}

KANNADA_TENS = {
    "hattu": 10, "ಹತ್ತು": 10, "hannondu": 11, "ಹನ್ನೊಂದು": 11, "hanneradu": 12, "ಹನ್ನೆರಡು": 12,
    "hadimooru": 13, "ಹದಿಮೂರು": 13, "hadinaalku": 14, "ಹದಿನಾಲ್ಕು": 14, "hadinaidu": 15, "ಹದಿನೈದು": 15,
    "hadinaaru": 16, "ಹದಿನಾರು": 16, "hadineelu": 17, "ಹದಿನೇಳು": 17, "hadinentalu": 18, "ಹದಿನೆಂಟು": 18,
    "hattombattu": 19, "ಹತ್ತೊಂಬತ್ತು": 19, "ippattu": 20, "ಇಪ್ಪತ್ತು": 20,
    "muvvattu": 30, "ಮೂವತ್ತು": 30, "nalavattu": 40, "ನಲವತ್ತು": 40, "nalvattu": 40,
    "aivattu": 50, "ಐವತ್ತು": 50, "aravattu": 60, "ಅರವತ್ತು": 60, "eppattu": 70, "ಎಪ್ಪತ್ತು": 70,
    "embattu": 80, "ಎಂಬತ್ತು": 80, "tombattu": 90, "ತೊಂಬತ್ತು": 90,
}

KANNADA_MULTIPLIERS = {
    "nooru": 100, "ನೂರು": 100, "noora": 100, "ನೂರ": 100,
    "saavira": 1000, "ಸಾವಿರ": 1000, "savira": 1000,
    "laksha": 100000, "ಲಕ್ಷ": 100000, "koti": 10000000, "ಕೋಟಿ": 10000000,
}

# ═══════════════════════════════════════════════════════════════
# 3. Telugu (Telugu Script & Transliterated)
# ═══════════════════════════════════════════════════════════════
TELUGU_ONES = {
    "okati": 1, "ఒకటి": 1, "rendu": 2, "రెండు": 2, "moodu": 3, "మూడు": 3,
    "naalugu": 4, "నాలుగు": 4, "nalugu": 4, "aidu": 5, "ఐదు": 5,
    "aaru": 6, "ఆరు": 6, "eedu": 7, "ఏడు": 7, "yedu": 7,
    "enimidi": 8, "ఎనిమిది": 8, "tommidi": 9, "తొమ్మిది": 9,
}

TELUGU_TENS = {
    "padi": 10, "పది": 10, "padakondu": 11, "పదకొండు": 11, "pennandu": 12, "పన్నెండు": 12,
    "padamoodu": 13, "పదమూడు": 13, "padanaalugu": 14, "పద్నాలుగు": 14, "padihenu": 15, "పదిహేను": 15,
    "padahaaru": 16, "పదహారు": 16, "padihedu": 17, "పదిహేడు": 17, "paddhenimidi": 18, "పద్దెనిమిది": 18,
    "pandommidi": 19, "పంతొమ్మిది": 19, "iravai": 20, "ఇరవై": 20,
    "muppai": 30, "ముప్పై": 30, "nalabhai": 40, "నలభై": 40, "nalbhai": 40,
    "yaabhai": 50, "యాభై": 50, "aravai": 60, "అరవై": 60, "debbai": 70, "డెబ్బై": 70,
    "enabhai": 80, "ఎనభై": 80, "tombhai": 90, "తొంభై": 90,
}

TELUGU_MULTIPLIERS = {
    "vanda": 100, "వంద": 100, "vandalu": 100, "వందలు": 100, "vandala": 100, "వందల": 100,
    "veyyi": 1000, "వెయ్యి": 1000, "vela": 1000, "వేల": 1000,
    "laksha": 100000, "లక్ష": 100000, "koti": 10000000, "కోటి": 10000000,
}

# ═══════════════════════════════════════════════════════════════
# 4. English (Standard & Indian Code-Mixed)
# ═══════════════════════════════════════════════════════════════
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

# Combined Vocabularies
ALL_ONES = {**HINDI_ONES, **KANNADA_ONES, **TELUGU_ONES, **ENGLISH_ONES}
ALL_TENS = {**HINDI_TENS, **KANNADA_TENS, **TELUGU_TENS, **ENGLISH_TEENS, **ENGLISH_TENS}
ALL_MULTIPLIERS = {**HINDI_MULTIPLIERS, **KANNADA_MULTIPLIERS, **TELUGU_MULTIPLIERS, **ENGLISH_MULTIPLIERS}


def _try_compound_english(tokens: List[str]) -> Optional[Tuple[float, int]]:
    """e.g. 'three forty' -> 340, 'three forty five' -> 345, 'fifteen hundred' -> 1500"""
    if len(tokens) < 2:
        return None

    t0, t1 = tokens[0], tokens[1]
    val0 = ALL_ONES.get(t0) or ALL_TENS.get(t0)

    # single digit / teen + "hundred" / "nooru" / "vanda" / "sau"
    if val0 is not None and t1 in ("hundred", "sau", "so", "nooru", "noora", "vanda", "vandalu", "vandala"):
        base = val0 * 100
        if len(tokens) >= 3:
            t2 = tokens[2]
            val2 = ALL_TENS.get(t2) or ALL_ONES.get(t2)
            if val2 is not None:
                if len(tokens) >= 4 and t2 in ENGLISH_TENS and tokens[3] in ALL_ONES:
                    return (base + val2 + ALL_ONES[tokens[3]], 4)
                return (base + val2, 3)
        return (base, 2)

    # "three forty" -> 340
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

    # "twelve fifty" -> 1250
    if val0 is not None and 11 <= val0 <= 19:
        val1 = ALL_TENS.get(t1)
        if val1 is not None and 10 <= val1 <= 99:
            return (val0 * 100 + val1, 2)

    return None


def parse_spoken_number(text: str) -> Optional[float]:
    """Parse any spoken numeral across Hindi, Kannada, Telugu, English."""
    if not text:
        return None

    cleaned = text.lower().replace("-", " ").replace("–", " ").strip()

    # Raw digits check
    digit_match = re.match(r'^(?:₹|rs\.?\s*)?(\d+(?:,\d{3})*(?:\.\d+)?)$', cleaned)
    if digit_match:
        try:
            return float(digit_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # Fraction phrases
    for phrase, val in INDIC_FRACTIONS.items():
        if phrase in cleaned:
            return val

    # Tokenize
    tokens = [t.strip().lower() for t in cleaned.split() if t.strip()]
    if not tokens:
        return None

    # Compound check
    comp = _try_compound_english(tokens)
    if comp is not None:
        return comp[0]

    # Hierarchical parser
    total = 0.0
    current = 0.0
    found_any = False

    i = 0
    while i < len(tokens):
        t = tokens[i]

        if re.match(r'^\d+(\.\d+)?$', t):
            current += float(t)
            found_any = True
            i += 1
            continue

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

        val = ALL_ONES.get(t) or ALL_TENS.get(t)
        if val is not None:
            comp_sub = _try_compound_english(tokens[i:])
            if comp_sub is not None:
                current += comp_sub[0]
                i += comp_sub[1]
                found_any = True
                continue
            current += val
            found_any = True
            i += 1
            continue

        i += 1

    final_val = total + current
    return final_val if found_any else None


UNIT_PATTERNS = re.compile(
    r'\b(?:packet|packets|pkt|pkts|kilo|kg|kgs|kilogram|gram|grams|gm|gms|litre|litres|liter|liters|ltr|l|'
    r'dabba|dhabba|dappe|bori|boriyan|bag|bags|pouch|pouches|piece|pieces|pc|pcs|bottle|bottles|'
    r'dozen|darjan|tin|tins|can|cans|cup|plate|patte|patti)\b',
    re.IGNORECASE
)

CURRENCY_PATTERNS = re.compile(
    r'(?:₹|rs\.?\s*|rupaye|rupayee|rupees|roopayi|roopaayi|rupai|rupaiya|rupaiye)',
    re.IGNORECASE
)


def extract_amounts(text: str) -> List[Tuple[float, str]]:
    results: List[Tuple[float, str]] = []
    text_lower = text.lower().replace("-", " ")

    # Identify numbers that are quantities of grocery items (e.g. "2 packet", "5 kilo")
    qty_matches = set()
    for qm in re.finditer(rf'(\b\d+(?:\.\d+)?\b)\s*{UNIT_PATTERNS.pattern}', text_lower):
        qty_matches.add(qm.group(1))

    # 1. Digits
    digit_pattern = r'(?:₹|rs\.?\s*)?(\b\d+(?:,\d{3})*(?:\.\d{1,2})?\b)'
    for m in re.finditer(digit_pattern, text_lower):
        try:
            raw_num_str = m.group(1).replace(",", "")
            val = float(raw_num_str)
            if 0 < val <= 50_00_000:
                # If this number was specifically qualifying a unit (e.g. "2 packet")
                # and there are other numbers or currency in the sentence, treat it as quantity
                is_unit_qty = raw_num_str in qty_matches
                is_curr_marked = bool(re.search(CURRENCY_PATTERNS, m.group(0))) or bool(re.search(rf'{raw_num_str}\s*(?:rupaye|rupees|rs|₹|roopayi)', text_lower))
                results.append((val, m.group(0), is_curr_marked, is_unit_qty))
        except ValueError:
            pass

    # 2. Fractions
    for phrase, val in INDIC_FRACTIONS.items():
        if phrase in text_lower:
            results.append((val, phrase, True, False))

    # 3. Words
    vocab = set(ALL_ONES.keys()) | set(ALL_TENS.keys()) | set(ALL_MULTIPLIERS.keys())
    tokens = text_lower.split()

    i = 0
    while i < len(tokens):
        tok = tokens[i].strip().lower()
        if tok in vocab or re.match(r'^\d+$', tok):
            j = i
            while j < len(tokens) and (tokens[j].strip().lower() in vocab or re.match(r'^\d+$', tokens[j].strip().lower())):
                j += 1
            phrase = " ".join(tokens[i:j])
            amt = parse_spoken_number(phrase)
            if amt is not None and 0 < amt <= 50_00_000:
                if not any(abs(existing[0] - amt) < 0.01 for existing in results):
                    is_curr = bool(re.search(CURRENCY_PATTERNS, phrase)) or bool(re.search(rf'{re.escape(phrase)}\s*(?:rupaye|rupees|rs|₹|roopayi)', text_lower))
                    is_qty = bool(re.search(rf'{re.escape(phrase)}\s*{UNIT_PATTERNS.pattern}', text_lower))
                    results.append((amt, phrase, is_curr, is_qty))
            i = j
        else:
            i += 1

    # Prioritize:
    # 1st: Currency-marked numbers (e.g. "60 rupaye", "₹340")
    # 2nd: Non-unit standalone numbers
    # 3rd: Unit quantities (only if no other number exists)
    if len(results) > 1:
        # Check if any currency-marked number exists
        currency_marked = [r for r in results if r[2] and not r[3]]
        if currency_marked:
            sorted_res = currency_marked
        else:
            non_units = [r for r in results if not r[3]]
            sorted_res = non_units if non_units else results
    else:
        sorted_res = results

    return [(r[0], r[1]) for r in sorted_res]


def extract_first_amount(text: str) -> Optional[float]:
    amts = extract_amounts(text)
    return amts[0][0] if amts else None
