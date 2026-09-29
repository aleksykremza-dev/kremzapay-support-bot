# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import re

INJECTION = [
    r"ignore (\w+ ){0,3}(instructions|rules|prompt)",
    r"system prompt|developer mode|jailbreak|\bdan mode\b|jesteś teraz|act as if",
    r"zignoruj (\w+ ){0,3}(instrukcje|zasady|polecenia)",
    r"(wypisz|pokaż|poka[zż]|show|reveal|print).{0,25}(prompt|instrukcj|instructions)",
    r"tryb (dewelopera|deweloperski|developer)",
]
FRAUD = [
    r"stolen (card|credit)|charge .{0,30}without .{0,15}(permission|consent)",
    r"kradzion\w+ kart|skradzion\w+ kart",
    r"(obej[śs][ćc]|omin[ąa][ćc]|bypass).{0,25}(kyc|weryfikacj|verification)",
    r"launder|prani\w+ (pieni|brudnych)",
]
COMPETITORS = [
    r"\b(payu|stripe|przelewy ?24|p24|tpay|paypal|adyen|dotpay|paynow|klarna|revolut)\b",
]
TAX = [
    r"\b(pit|cit)\b.{0,30}(rozlicz|zezna|deklarac)|rozlicz\w*.{0,20}\b(pit|cit)\b",
    r"\bkpir\b|urz[ąa]d skarbowy|\bzus\b|jednoosobow\w+ dzialalno",
    r"(personal|own|prywatn\w+).{0,20}(visa|mastercard|card|kart).{0,30}(dispute|bank|spor)",
]
HUMAN = [
    r"(chce|chcę|prosze|proszę|potrzebuje|potrzebuję|daj(cie)?|połącz|polacz|przełącz|przelacz)"
    r".{0,40}(konsultant|człowiek|czlowiek|operator|doradc|agent)",
    r"\b(konsultant|człowiek|czlowiek|operator)\w*\s*[!?.]*\s*$",
    r"(talk|speak|connect|transfer|get)\s?(me)?\s?(to|with)?.{0,20}"
    r"(human|real person|live (person|agent)|agent|operator|someone)",
    r"\b(human|operator)\s*[!?.]*\s*$",
    r"(nie chce|nie chcę|don.?t want).{0,25}(bot|robot|maszyn|machine|ai)",
]

GUARDS = [
    ("unsafe_refuse", "injection", [re.compile(p, re.I) for p in INJECTION]),
    ("unsafe_refuse", "fraud_request", [re.compile(p, re.I) for p in FRAUD]),
    ("redirect", "competitor_product", [re.compile(p, re.I) for p in COMPETITORS]),
    ("redirect", "tax_accounting", [re.compile(p, re.I) for p in TAX]),
    ("handoff", "explicit_human_request", [re.compile(p, re.I) for p in HUMAN]),
]


def check(text: str) -> dict | None:
    for action, reason, patterns in GUARDS:
        for pattern in patterns:
            if pattern.search(text):
                return {"action": action, "reason": reason, "layer": 0}
    return None
