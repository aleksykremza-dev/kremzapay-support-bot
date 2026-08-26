"""Hermetic test setup: stub the heavy cascade dependencies.

cascade.py imports knn_router / llm_classifier / search at module level; those
pull fastembed, qdrant and the taxonomy file. Tests must run without Qdrant,
Ollama or model downloads, so lightweight stubs are installed under the same
module names BEFORE cascade is imported. Individual tests override behavior
via monkeypatch.
"""
import sys
import types


def _stub(name, **attrs):
    if name in sys.modules:
        return sys.modules[name]
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


def _unused(*_args, **_kwargs):
    raise AssertionError("stub called without an explicit override in the test")


_stub("knn_router", classify=_unused)
_stub("llm_classifier", classify=_unused)
_stub("search", search=_unused)
