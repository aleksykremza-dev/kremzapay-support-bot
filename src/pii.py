"""6.10: PII-маскер (input-rail). Работает ДО любого вызова LLM и ДО записи в лог."""
import re

PATTERNS = [
    # Номер карты: 13-19 цифр, допускаем пробелы/дефисы между четвёрками.
    ("CARD", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    # IBAN: PL + 26 цифр, или общий формат CCdd + 11-30 знаков.
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[ ]?(?:[A-Z0-9][ ]?){11,30}\b")),
    # PESEL: ровно 11 цифр подряд.
    ("PESEL", re.compile(r"\b\d{11}\b")),
    # Телефон: +48 xxx xxx xxx и похожие.
    ("PHONE", re.compile(r"(?:\+?\d{1,3}[ -]?)?(?:\d{3}[ -]?){3}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
]


def mask(text):
    """Возвращает (замаскированный текст, маппинг метка->оригинал)."""
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
        "jak zrobić zwrot płatności?",  # чистый текст — не должен измениться
    ]
    for s in samples:
        m, mp = mask(s)
        print(f"{m}\n   маппинг: {mp}\n")
