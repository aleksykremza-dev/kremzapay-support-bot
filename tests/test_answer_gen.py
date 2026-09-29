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
