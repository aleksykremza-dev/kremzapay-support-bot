from types import SimpleNamespace

import answer_gen
import llm


def _hit(article_id, title, text):
    return SimpleNamespace(score=0.9, payload={"id": article_id, "title": title, "text": text})


def test_build_prompt_contains_all_chunks_and_source_rule():
    hits = [_hit("refund-how", "Zwrot", "Zwrot robisz w panelu."),
            _hit("refund-time", "Czas zwrotu", "Kilka dni roboczych.")]
    prompt = answer_gen._build_prompt("jak zrobić zwrot?", hits, "pl")
    assert "Zwrot robisz w panelu." in prompt
    assert "Kilka dni roboczych." in prompt
    assert "Źródło: <id>" in prompt
    assert "Always answer in Polish" in prompt
    assert prompt.rstrip().endswith("ANSWER (in Polish):")


def test_generate_returns_none_without_hits(monkeypatch):
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: [])
    assert answer_gen.generate("anything", intent=None, language="en") is None


def test_generate_returns_none_on_bad_llm_output(monkeypatch):
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: [_hit("a", "A", "text")])

    def bad(*_a, **_k):
        raise llm.LLMBadOutput("empty")
    monkeypatch.setattr(answer_gen.llm, "generate", bad)
    assert answer_gen.generate("q", intent=None, language="en") is None


def test_generate_packs_answer_sources_chunks(monkeypatch):
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: [_hit("a", "A", "text a")])
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer.\nSource: a")
    result = answer_gen.generate("q", intent=None, language="en")
    assert result == {"answer": "Answer.\nSource: a", "sources": ["a : A"], "chunks": ["text a"]}


def test_generate_keeps_only_cited_chunks(monkeypatch):
    hits = [_hit("refund-how", "Zwrot", "text refund"), _hit("payout-schedule", "Wypłata", "text payout")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Odpowiedź.\n\nŹródło: payout-schedule")
    result = answer_gen.generate("q", intent=None, language="pl")
    assert result["chunks"] == ["text payout"]
    assert result["sources"] == ["refund-how : Zwrot", "payout-schedule : Wypłata"]


def test_generate_keeps_all_chunks_without_source_line(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer without citation.")
    assert answer_gen.generate("q", intent=None, language="en")["chunks"] == ["text a", "text b"]


def test_generate_does_not_match_id_as_substring(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("ab", "AB", "text ab")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer.\nSource: ab")
    assert answer_gen.generate("q", intent=None, language="en")["chunks"] == ["text ab"]


def test_generate_keeps_all_chunks_when_cited_id_unknown(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer.\nSource: zzz")
    assert answer_gen.generate("q", intent=None, language="en")["chunks"] == ["text a", "text b"]
