"""Слой 0 каскада: точные правила (~0 мс). Срабатывают до всех моделей."""
import re

# Явная просьба позвать человека -> немедленный handoff без классификации.
HUMAN_PATTERNS = [
    # PL: konsultant / człowiek / operator / doradca / agent (и без диакритики)
    r"(chce|chcę|prosze|proszę|potrzebuje|potrzebuję|daj(cie)?|połącz|polacz|przełącz|przelacz)"
    r".{0,40}(konsultant|człowiek|czlowiek|operator|doradc|agent)",
    r"\b(konsultant|człowiek|czlowiek|operator)\w*\s*[!?.]*\s*$",
    # EN: talk/speak/connect ... human/person/agent/operator/someone real
    r"(talk|speak|connect|transfer|get)\s?(me)?\s?(to|with)?.{0,20}"
    r"(human|real person|live (person|agent)|agent|operator|someone)",
    r"\b(human|operator)\s*[!?.]*\s*$",
    r"(nie chce|nie chcę|don.?t want).{0,25}(bot|robot|maszyn|machine|ai)",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in HUMAN_PATTERNS]


def check(text):
    """Вердикт слоя 0: dict при срабатывании правила, None -> передать слою 1."""
    for pattern in COMPILED:
        if pattern.search(text):
            return {"action": "handoff", "reason": "explicit_human_request", "layer": 0}
    return None


if __name__ == "__main__":
    samples = [
        "chcę rozmawiać z konsultantem",
        "daj czlowieka!!",
        "connect me to a real person please",
        "operator",
        "I don't want a bot, get me someone",
        "jak zrobić zwrot płatności?",       # НЕ должно сработать
        "gdzie jest mój przelew do operatora sieci",  # ловушка: «operator» в другом смысле
    ]
    for s in samples:
        verdict = check(s)
        print(f"{'HANDOFF' if verdict else 'дальше '} | {s}")
