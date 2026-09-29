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


class SearchUnavailable(Exception):
    pass


_stub("knn_router", classify=_unused)
_stub("llm_classifier", classify=_unused)
_stub("search", search=_unused, ping=lambda: True, SearchUnavailable=SearchUnavailable)
