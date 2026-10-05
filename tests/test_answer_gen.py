from types import SimpleNamespace

import answer_gen
import llm


def _hit(article_id, title, text, score=0.9):
    return SimpleNamespace(score=score, payload={"id": article_id, "title": title, "text": text})


def _search_setup(monkeypatch, base_hits, replies):
    calls = {"search": [], "llm": []}

    def fake_search(question):
        calls["search"].append(question)
        return base_hits

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
    assert answer_gen.generate("anything", language="en") is None


def test_generate_returns_none_on_bad_llm_output(monkeypatch):
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: [_hit("a", "A", "text")])

    def bad(*_a, **_k):
        raise llm.LLMBadOutput("empty")
    monkeypatch.setattr(answer_gen.llm, "generate", bad)
    assert answer_gen.generate("q", language="en") is None


def test_generate_packs_answer_sources_chunks(monkeypatch):
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: [_hit("a", "A", "text a")])
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer.\nSource: a")
    result = answer_gen.generate("q", language="en")
    assert result == {"answer": "Answer.\n\nSource: a", "sources": ["a : A"], "chunks": ["text a"]}


def test_generate_keeps_only_cited_chunks(monkeypatch):
    hits = [_hit("refund-how", "Zwrot", "text refund"), _hit("payout-schedule", "Wypłata", "text payout")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Odpowiedź.\n\nŹródło: payout-schedule")
    result = answer_gen.generate("q", language="pl")
    assert result["chunks"] == ["text payout"]
    assert result["sources"] == ["refund-how : Zwrot", "payout-schedule : Wypłata"]


def test_generate_uses_top_chunk_without_source_line(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer without citation.")
    assert answer_gen.generate("q", language="en")["chunks"] == ["text a"]


def test_generate_does_not_match_id_as_substring(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("ab", "AB", "text ab")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer.\nSource: ab")
    assert answer_gen.generate("q", language="en")["chunks"] == ["text ab"]


def test_generate_uses_top_chunk_when_cited_id_unknown(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer.\nSource: zzz")
    assert answer_gen.generate("q", language="en")["chunks"] == ["text a"]


def test_generate_reads_source_at_end_of_last_paragraph(monkeypatch):
    hits = [_hit("refund-how", "Zwrot", "text refund"), _hit("payout-schedule", "Wypłata", "text payout")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate",
                        lambda *a, **k: "Pierwszy akapit.\n\nWypłata idzie co tydzień. Źródło: payout-schedule")
    assert answer_gen.generate("q", language="pl")["chunks"] == ["text payout"]


def test_generate_reads_english_source_at_end_of_paragraph(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer here. Source: b")
    assert answer_gen.generate("q", language="en")["chunks"] == ["text b"]


def test_generate_ignores_source_word_inside_earlier_paragraph(monkeypatch):
    hits = [_hit("a", "A", "text a"), _hit("b", "B", "text b")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate",
                        lambda *a, **k: "Check the field Source: b in the panel.\n\nAnswer end.")
    result = answer_gen.generate("q", language="en")
    assert result["chunks"] == ["text a"]
    assert result["answer"] == "Check the field Source: b in the panel.\n\nAnswer end.\n\nSource: a"


def test_search_uses_question_over_whole_base(monkeypatch):
    calls = _search_setup(monkeypatch, [_hit("fee-when-charged", "Prowizja", "text f")],
                          ["Prowizja.\nŹródło: fee-when-charged"])
    result = answer_gen.generate("kiedy prowizja?", language="pl")
    assert calls["search"] == ["kiedy prowizja?"]
    assert len(calls["llm"]) == 1
    assert result["chunks"] == ["text f"]


def test_no_answer_is_final_without_second_search(monkeypatch):
    calls = _search_setup(monkeypatch, [_hit("fee-when-charged", "Prowizja", "text f")], ["NO_ANSWER", "extra"])
    result = answer_gen.generate("q", language="pl")
    assert calls["search"] == ["q"]
    assert len(calls["llm"]) == 1
    assert answer_gen.is_no_answer(result["answer"])


def _two_hits(monkeypatch, reply):
    hits = [_hit("team-add-user", "Zespol", "text team"), _hit("team-roles", "Role", "text roles")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: reply)
    return answer_gen.generate("q", language="pl")


def test_source_line_is_rewritten_from_valid_ids(monkeypatch):
    result = _two_hits(monkeypatch, "Dodaj osobe w Zespol.\n\nŹródło: team-roles, team-add-user")
    assert result["answer"] == "Dodaj osobe w Zespol.\n\nŹródło: team-roles, team-add-user"
    assert result["chunks"] == ["text team", "text roles"]


def test_misspelled_source_id_is_mapped_to_closest_hit(monkeypatch):
    result = _two_hits(monkeypatch, "Dodaj osobe.\n\nŹródło: team-add_usеr")
    assert result["answer"] == "Dodaj osobe.\n\nŹródło: team-add-user"
    assert result["chunks"] == ["text team"]


def test_missing_source_line_gets_top_hit(monkeypatch):
    result = _two_hits(monkeypatch, "Dodaj osobe w Zespol.")
    assert result["answer"] == "Dodaj osobe w Zespol.\n\nŹródło: team-add-user"
    assert result["chunks"] == ["text team"]


def test_wrong_label_before_valid_id_is_replaced(monkeypatch):
    result = _two_hits(monkeypatch, "Wybierz role uzytkownik. Ty: team-roles")
    assert result["answer"] == "Wybierz role uzytkownik.\n\nŹródło: team-roles"
    assert result["chunks"] == ["text roles"]


def test_unknown_source_id_falls_back_to_top_hit(monkeypatch):
    result = _two_hits(monkeypatch, "Dodaj osobe.\nŹródło: zzz-qqq")
    assert result["answer"] == "Dodaj osobe.\n\nŹródło: team-add-user"
    assert result["chunks"] == ["text team"]


def test_english_answer_gets_source_label(monkeypatch):
    hits = [_hit("a-b", "A", "text a")]
    monkeypatch.setattr(answer_gen, "search", lambda *a, **k: hits)
    monkeypatch.setattr(answer_gen.llm, "generate", lambda *a, **k: "Answer.")
    assert answer_gen.generate("q", language="en")["answer"] == "Answer.\n\nSource: a-b"


def test_no_answer_text_is_not_rewritten(monkeypatch):
    result = _two_hits(monkeypatch, "NO_ANSWER")
    assert result["answer"] == "NO_ANSWER"
