import importlib.util
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "tools" / "check_style.py"
spec = importlib.util.spec_from_file_location("check_style", TOOL)
check_style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_style)

DASH = chr(0x2014)
HEADER = "# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.\n"


@pytest.fixture
def tree(tmp_path):
    for name in ("src", "tools", "tests/live"):
        (tmp_path / name).mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text(HEADER + "VALUE = 1\n", encoding="utf-8")
    (tmp_path / "tools" / "tool.py").write_text(HEADER + "def run():\n    return 1\n", encoding="utf-8")
    (tmp_path / "tests" / "test_app.py").write_text("def test_value():\n    assert True\n", encoding="utf-8")
    (tmp_path / "tests" / "live" / "probe.py").write_text(HEADER + "URL = 'x'\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Bot\n\nOpis - bez długich kresek.\n", encoding="utf-8")
    (tmp_path / "Makefile").write_text("test:\n\tpytest\n", encoding="utf-8")
    return tmp_path


def test_clean_tree_is_green(tree, capsys):
    assert check_style.main(tree) == 0
    assert "STYLE_EXIT=0" in capsys.readouterr().out


@pytest.mark.parametrize("path, text, check", [
    ("src/app.py", "VALUE = 1\n", "copyright"),
    ("src/app.py", HEADER + "# note\nVALUE = 1\n", "comments"),
    ("tests/test_app.py", "def test_value():\n    # why\n    assert True\n", "comments"),
    ("README.md", f"# Bot\n\nOpis {DASH} z kreską.\n", "em dash"),
    ("CHANGELOG.md", f"## 1.0.0 {DASH} data\n", "em dash"),
    ("tools/tool.py", HEADER + "def run():\n    \"\"\"Run it.\"\"\"\n    return 1\n", "docstrings"),
    ("src/app.py", HEADER + "PHASE = '" + "Sta" + "ge 2'\n", "stage"),
])
def test_each_defect_turns_gate_red(tree, capsys, path, text, check):
    (tree / path).write_text(text, encoding="utf-8")
    assert check_style.main(tree) == 1
    out = capsys.readouterr().out
    assert f"RED {check}" in out
    assert "STYLE_EXIT=1" in out
