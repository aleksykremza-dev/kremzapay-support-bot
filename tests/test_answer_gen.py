from types import SimpleNamespace

import answer_gen
import llm


def _hit(article_id, title, text, score=0.9):
    return SimpleNamespace(score=score, payload={"id": article_id, "title": title, "text": text})


def _retry_setup(monkeypatch, category_hits, base_hits, replies):
    calls = {"search": [], "llm": []}
    monkeypatch.setattr(answer_gen.taxonomy, "intent_definition", lambda: {"refund_how": "Refund steps."})
    monkeypatch.setattr(answer_gen.taxonomy, "intent_category", lambda: {"refund_how": "refunds"})

    def fake_search(question, category=None):
        calls["search"].append((question, category))
        return category_hits if category else base_hits

    def fake_llm(prompt, **_k):
        calls["llm"].append(prompt)
        return replies[len(calls["llm"]) - 1]
    monkeypatch.setattr(answer_gen, "search", fake_search)
    monkeypatch.setattr(answer_gen.llm, "generate", fake_llm)
    return calls


def test_build_prompt_contains_all_chunks_and_source_rule():
    hits = [_hit("refund-how", "Zwrot", "Zwrot robisz w panelu."),
            _hit("refund-time", "Czas zwrotu", "Kilka dni roboczych.")]
    prompt = answer_gen._build_prompt("jak zrobić zwrot?", hits, "pl")
    assert "Zwrot robisz w panelu." in prompt
    assert "Kilka dni roboczych." in prompt
    assert "Źródło: <id>" in prompt
    assert "Always answer in Polish" in prompt
    assert "NO_ANSWER" in prompt
    assert prompt.rstrip().endswith("ANSWER (in Polish):")


def test_is_no_answer_detects_marker():
    assert answer_gen.is_no_answer("NO_ANSWER")
    assert answer_gen.is_no_answer("  no_answer.\nŹródło: a")
    assert not answer_gen.is_no_answer("Zwrot robisz w panelu.\nŹródło: refund-how")


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


def test_generate_reads_source_at_end_of_last_paragraph(monkeypatch):
    hits = [_hit("refund-how", "Zwrot", "text refund"), _hit("payout-schedule", "Wypłata", "text payout")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate",
                        lambda *a, **k: "Pierwszy akapit.\n\nWypłata idzie co tydzień. Źródło: payout-schedule")
    assert answer_gen.generate("q", intent=None, language="pl")["chunks"] == ["text payout"]


def test_generate_reads_english_source_at_end_of_paragraph(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer here. Source: b")
    assert answer_gen.generate("q", intent=None, language="en")["chunks"] == ["text b"]


def test_generate_ignores_source_word_inside_earlier_paragraph(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate",
                        lambda *a, **k: "Check the field Source: b in the panel.\n\nAnswer end.")
    assert answer_gen.generate("q", intent=None, language="en")["chunks"] == ["text a", "text b"]


def test_no_retry_when_category_hits_answer(monkeypatch):
    calls = _retry_setup(monkeypatch, [_hit("refund-create", "Zwrot", "text c")],
                         [_hit("other", "Other", "text o")], ["Zwrot w panelu.\nŹródło: refund-create"])
    result = answer_gen.generate("jak zrobić zwrot?", intent="refund_how", language="pl")
    assert calls["search"] == [("jak zrobić zwrot?. Refund steps.", "refunds")]
    assert len(calls["llm"]) == 1
    assert result["chunks"] == ["text c"]


def test_retry_whole_base_when_category_hits_below_threshold(monkeypatch):
    calls = _retry_setup(monkeypatch, [_hit("refund-create", "Zwrot", "text c", score=0.3)],
                         [_hit("fee-when-charged", "Prowizja", "text f")], ["Prowizja.\nŹródło: fee-when-charged"])
    result = answer_gen.generate("kiedy prowizja?", intent="refund_how", language="pl")
    assert calls["search"] == [("kiedy prowizja?. Refund steps.", "refunds"), ("kiedy prowizja?", None)]
    assert len(calls["llm"]) == 1
    assert "text f" in calls["llm"][0]
    assert result["sources"] == ["fee-when-charged : Prowizja"]


def test_retry_whole_base_after_no_answer(monkeypatch):
    calls = _retry_setup(monkeypatch, [_hit("refund-create", "Zwrot", "text c")],
                         [_hit("fee-when-charged", "Prowizja", "text f")],
                         ["NO_ANSWER", "Prowizja.\nŹródło: fee-when-charged"])
    result = answer_gen.generate("kiedy prowizja?", intent="refund_how", language="pl")
    assert calls["search"] == [("kiedy prowizja?. Refund steps.", "refunds"), ("kiedy prowizja?", None)]
    assert len(calls["llm"]) == 2
    assert result["answer"] == "Prowizja.\nŹródło: fee-when-charged"
    assert result["chunks"] == ["text f"]


def test_only_one_retry_when_no_answer_twice(monkeypatch):
    calls = _retry_setup(monkeypatch, [_hit("refund-create", "Zwrot", "text c")],
                         [_hit("fee-when-charged", "Prowizja", "text f")], ["NO_ANSWER", "NO_ANSWER", "extra"])
    result = answer_gen.generate("q", intent="refund_how", language="pl")
    assert len(calls["search"]) == 2
    assert len(calls["llm"]) == 2
    assert answer_gen.is_no_answer(result["answer"])


def test_no_second_retry_after_low_score_retry(monkeypatch):
    calls = _retry_setup(monkeypatch, [_hit("refund-create", "Zwrot", "text c", score=0.3)],
                         [_hit("fee-when-charged", "Prowizja", "text f")], ["NO_ANSWER", "extra"])
    result = answer_gen.generate("q", intent="refund_how", language="pl")
    assert len(calls["search"]) == 2
    assert len(calls["llm"]) == 1
    assert answer_gen.is_no_answer(result["answer"])


def test_no_retry_without_category(monkeypatch):
    calls = _retry_setup(monkeypatch, [], [_hit("a", "A", "text a")], ["NO_ANSWER", "extra"])
    result = answer_gen.generate("q", intent=None, language="en")
    assert calls["search"] == [("q", None)]
    assert len(calls["llm"]) == 1
    assert answer_gen.is_no_answer(result["answer"])
