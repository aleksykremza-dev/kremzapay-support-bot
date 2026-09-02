"""PII masker (input-rail). Runs BEFORE any LLM call and BEFORE writing to logs."""
# [PII] Input rail: PII masking before LLM and logs
import re

PATTERNS = [
    # Card number: 13-19 digits, allow spaces/hyphens between groups of four.
    ("CARD", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    # IBAN: PL + 26 digits, or the general format CCdd + 11-30 characters.
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[ ]?(?:[A-Z0-9][ ]?){11,30}\b")),
    # PESEL: exactly 11 consecutive digits.
    ("PESEL", re.compile(r"\b\d{11}\b")),
    # Phone: +48 xxx xxx xxx and similar.
    ("PHONE", re.compile(r"(?:\+?\d{1,3}[ -]?)?(?:\d{3}[ -]?){3}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
]


def mask(text):
    """Returns (masked text, mapping token->original)."""
    mapping = {}
    masked = text
    for kind, pattern in PATTERNS:
        def _sub(match, kind=kind):
            token = f"<{kind}_{sum(1 for k in mapping if k.startswith('<'+kind))+1}>"
            original = match.group(0)
            mapping[token] = original.strip()
            return token + (" " if original.endswith(" ") else "")
        masked = pattern.sub(_sub, masked)
    return masked, mapping


if __name__ == "__main__":
    samples = [
        "moja karta 4111 1111 1111 1111 zostala obciazona dwa razy",
        "wyplata na PL61109010140000071219812874 nie doszla",
        "mój pesel 90010112345, sprawdźcie konto",
        "call me at +48 601 123 456 or mail jan.kowalski@firma.pl",
        "jak zrobić zwrot płatności?",  # clean text — should not change
    ]
    for s in samples:
        m, mp = mask(s)
        print(f"{m}\n   mapping: {mp}\n")
