import ingest

ARTICLE = """---
title: Jak zrobić zwrot płatności
category: refunds
id: refund-how
---

Zwrot robisz w panelu, w zakładce Płatności.

Kwota wraca na kartę klienta w ciągu kilku dni roboczych.

---
Ten artykuł jest częścią dokumentacji.
"""


def test_main_without_kb_prints_instruction_and_returns_2(tmp_path, capsys):
    code = ingest.main(tmp_path / "missing")
    out = capsys.readouterr().out.strip()
    assert code == 2
    assert out == ingest.NO_KB_MESSAGE
    assert "Własna dokumentacja" in out


def test_main_with_empty_kb_dir_returns_2(tmp_path, capsys):
    (tmp_path / "refunds").mkdir()
    assert ingest.main(tmp_path) == 2
    assert capsys.readouterr().out.count("\n") == 1


def test_parse_article_reads_frontmatter_and_body(tmp_path):
    path = tmp_path / "refund-how.md"
    path.write_text(ARTICLE, encoding="utf-8")
    meta, body = ingest.parse_article(path)
    assert meta == {"title": "Jak zrobić zwrot płatności", "category": "refunds", "id": "refund-how"}
    assert body.startswith("Zwrot robisz w panelu")
    assert "częścią dokumentacji" not in body


def test_split_chunks_respects_paragraphs(monkeypatch):
    monkeypatch.setattr(ingest.config, "CHUNK_SIZE", 40)
    body = "a" * 30 + "\n\n" + "b" * 30 + "\n\n" + "c" * 5
    chunks = ingest.split_chunks(body)
    assert chunks == ["a" * 30, "b" * 30 + "\n\n" + "c" * 5]


def test_find_articles_only_one_level_of_categories(tmp_path):
    (tmp_path / "refunds").mkdir()
    (tmp_path / "refunds" / "a.md").write_text(ARTICLE, encoding="utf-8")
    (tmp_path / "loose.md").write_text(ARTICLE, encoding="utf-8")
    found = ingest.find_articles(tmp_path)
    assert [p.name for p in found] == ["a.md"]
