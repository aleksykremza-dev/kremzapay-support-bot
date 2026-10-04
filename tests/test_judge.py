import judge
import llm


def test_grounded_prompt_contains_question_answer_and_sources(monkeypatch):
    seen = {}

    def fake(prompt, **_k):
        seen["prompt"] = prompt
        return "yes"
    monkeypatch.setattr(judge.llm, "generate", fake)
    assert judge.grounded("jak zamknąć konto?", "Napisz do nas.", ["Konto zamykasz przez formularz."]) is True
    assert "jak zamknąć konto?" in seen["prompt"]
    assert "Napisz do nas." in seen["prompt"]
    assert "Konto zamykasz przez formularz." in seen["prompt"]


def test_grounded_asks_whether_sources_answer_the_question(monkeypatch):
    seen = {}

    def fake(prompt, **_k):
        seen["prompt"] = prompt
        return "no"
    monkeypatch.setattr(judge.llm, "generate", fake)
    assert judge.grounded("q", "a", ["s"]) is False
    assert "QUESTION" in seen["prompt"]
    assert "answer the question" in seen["prompt"].lower()


def test_grounded_false_on_bad_output(monkeypatch):
    def bad(*_a, **_k):
        raise llm.LLMBadOutput("empty")
    monkeypatch.setattr(judge.llm, "generate", bad)
    assert judge.grounded("q", "a", ["s"]) is False
