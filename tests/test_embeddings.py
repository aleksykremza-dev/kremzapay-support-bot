import embeddings


def test_e5_gets_query_and_passage_prefixes():
    name = "intfloat/multilingual-e5-large"
    assert embeddings.prefixed(name, ["a"], "query") == ["query: a"]
    assert embeddings.prefixed(name, ["a", "b"], "passage") == ["passage: a", "passage: b"]


def test_other_models_get_no_prefix():
    name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    assert embeddings.prefixed(name, ["a"], "query") == ["a"]
    assert embeddings.prefixed(name, ["a"], "passage") == ["a"]


def test_model_instance_is_shared(monkeypatch):
    created = []

    class Fake:
        def __init__(self, name):
            created.append(name)
    monkeypatch.setattr(embeddings, "TextEmbedding", Fake)
    embeddings.model.cache_clear()
    first = embeddings.model("m")
    assert embeddings.model("m") is first
    assert created == ["m"]
    embeddings.model.cache_clear()


def test_search_and_router_default_to_the_same_model():
    assert embeddings.config.EMBED_MODEL == embeddings.config.ROUTER_EMBED_MODEL
