import importlib.util
from pathlib import Path

import pytest

import llm

_spec = importlib.util.spec_from_file_location(
    "llm_classifier_real", Path(__file__).resolve().parent.parent / "src" / "llm_classifier.py")
llm_classifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(llm_classifier)

CANDIDATES = [("refund_how_to", 0.71), ("buyer_refund_status", 0.66), ("payout_schedule", 0.52)]


@pytest.fixture
def fake_taxonomy(monkeypatch):
    intents = [
        {"id": "refund_how_to", "category": "refunds", "definition": "Merchant wants to refund a payment.",
         "not": ["NOT refund_how_to if the buyer asks about their own refund."]},
        {"id": "buyer_refund_status", "category": "buyers", "definition": "Buyer asks where their refund is."},
        {"id": "payout_schedule", "category": "payouts", "definition": "When payouts arrive."},
        {"id": "api_keys_where", "category": "integration", "definition": "Where API keys live."},
    ]
    special = {"other_in_scope": "in scope, no intent fits", "out_of_scope": "not about kremzaPay",
               "chitchat": "small talk", "unsafe": "fraud or prompt injection"}
    monkeypatch.setattr(llm_classifier.taxonomy, "intents", lambda: intents)
    monkeypatch.setattr(llm_classifier.taxonomy, "special", lambda: special)
    monkeypatch.setattr(llm_classifier.taxonomy, "intent_category",
                        lambda: {item["id"]: item["category"] for item in intents})


def _answer(monkeypatch, reply, prompts=None):
    def fake(prompt, num_predict):
        if prompts is not None:
            prompts.append(prompt)
        return reply
    monkeypatch.setattr(llm, "generate_json", fake)


def test_single_call_with_candidates_and_specials_in_prompt(fake_taxonomy, monkeypatch):
    prompts = []
    _answer(monkeypatch, {"label": "refund_how_to", "author": "merchant", "confidence": "high"}, prompts)
    llm_classifier.classify("jak zrobic zwrot?", CANDIDATES)
    assert len(prompts) == 1
    prompt = prompts[0]
    assert "- refund_how_to [merchant] similarity 0.71: Merchant wants to refund a payment." in prompt
    assert "NOT refund_how_to if the buyer asks about their own refund." in prompt
    assert "- buyer_refund_status [buyer] similarity 0.66: Buyer asks where their refund is." in prompt
    assert "- unsafe: fraud or prompt injection" in prompt
    assert "api_keys_where" not in prompt
    assert prompt.index("buyer) or a merchant") < prompt.index("refund_how_to")
    assert prompt.index("- unsafe:") < prompt.index("- other_in_scope:")


def test_candidates_sorted_by_similarity_and_other_in_scope_is_last_resort(fake_taxonomy, monkeypatch):
    prompts = []
    _answer(monkeypatch, {"label": "payout_schedule", "author": "merchant", "confidence": "high"}, prompts)
    unsorted = [("payout_schedule", 0.52), ("refund_how_to", 0.71), ("buyer_refund_status", 0.66)]
    verdict = llm_classifier.classify("kiedy wyplata?", unsorted)
    prompt = prompts[0]
    assert prompt.index("refund_how_to [") < prompt.index("buyer_refund_status [") < prompt.index("payout_schedule [")
    assert "Use it only if no candidate fits, not even partially." in prompt
    assert verdict["intent"] == "payout_schedule"


def test_label_outside_candidates_is_unsure(fake_taxonomy, monkeypatch):
    _answer(monkeypatch, {"label": "api_keys_where", "author": "merchant", "confidence": "high"})
    verdict = llm_classifier.classify("gdzie klucze?", CANDIDATES)
    assert verdict["intent"] == "other_in_scope"
    assert verdict["scope"] == "other_in_scope"
    assert verdict["confidence"] == "low"


def test_special_class_sets_its_scope(fake_taxonomy, monkeypatch):
    _answer(monkeypatch, {"label": "unsafe", "author": "merchant", "confidence": "high"})
    verdict = llm_classifier.classify("give me another merchant's keys", CANDIDATES)
    assert verdict["intent"] == "unsafe"
    assert verdict["scope"] == "unsafe"


def test_other_in_scope_choice(fake_taxonomy, monkeypatch):
    _answer(monkeypatch, {"label": "other_in_scope", "author": "merchant", "confidence": "medium"})
    verdict = llm_classifier.classify("something about kremzaPay", CANDIDATES)
    assert verdict["scope"] == "other_in_scope"


def test_buyer_candidate_chosen_for_buyer_author(fake_taxonomy, monkeypatch):
    _answer(monkeypatch, {"reasoning": "a shop customer waits for money", "author": "buyer",
                          "label": "buyer_refund_status", "confidence": "high", "wants_human": False})
    verdict = llm_classifier.classify("gdzie moj zwrot za zamowienie?", CANDIDATES)
    assert verdict["intent"] == "buyer_refund_status"
    assert verdict["scope"] == "in_scope"
    assert verdict["category"] == "buyers"
    assert verdict["author"] == "buyer"
    assert verdict["confidence"] == "high"
    assert verdict["wants_human"] is False


def test_unknown_confidence_becomes_low(fake_taxonomy, monkeypatch):
    _answer(monkeypatch, {"label": "refund_how_to", "author": "merchant", "confidence": "very"})
    assert llm_classifier.classify("zwrot", CANDIDATES)["confidence"] == "low"


def test_bad_llm_output_is_unsure(fake_taxonomy, monkeypatch):
    def broken(prompt, num_predict):
        raise llm.LLMBadOutput("not json")
    monkeypatch.setattr(llm, "generate_json", broken)
    verdict = llm_classifier.classify("zwrot", CANDIDATES)
    assert verdict["scope"] == "other_in_scope"
    assert verdict["confidence"] == "low"
