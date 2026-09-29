# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import re

PATTERNS = [
    ("CARD", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[ ]?(?:[A-Z0-9][ ]?){11,30}\b")),
    ("PESEL", re.compile(r"\b\d{11}\b")),
    ("PHONE", re.compile(r"(?:\+?\d{1,3}[ -]?)?(?:\d{3}[ -]?){3}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
]


def mask(text: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    masked = text
    for kind, pattern in PATTERNS:
        def replace(match, kind=kind):
            token = f"<{kind}_{sum(1 for key in mapping if key.startswith('<' + kind)) + 1}>"
            original = match.group(0)
            mapping[token] = original.strip()
            return token + (" " if original.endswith(" ") else "")
        masked = pattern.sub(replace, masked)
    return masked, mapping
