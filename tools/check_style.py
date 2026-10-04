# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import ast
import re
import sys
from pathlib import Path

COPYRIGHT = "Copyright (c) 2026 Oleksii Kremza"
EM_DASH = chr(0x2014)
PHASE_WORD = re.compile(r"Stage ?[0-9]|ST[A]GE")
COMMENT = re.compile(r"^\s*#")
CODE_GLOBS = ("src/*.py", "tools/*.py", "tests/*.py", "tests/live/*.py")
COPYRIGHT_GLOBS = ("src/*.py", "tools/*.py", "tests/live/*.py")
TEXT_DIRS = ("src", "tools", "tests")
TEXT_FILES = ("README.md", "Makefile", "CHANGELOG.md")


def _files(root: Path, globs: tuple[str, ...]) -> list[Path]:
    return sorted(path for pattern in globs for path in root.glob(pattern))


def _text_files(root: Path) -> list[Path]:
    found = [path for name in TEXT_DIRS for path in sorted((root / name).rglob("*"))
             if path.is_file() and "__pycache__" not in path.parts]
    return found + [root / name for name in TEXT_FILES if (root / name).is_file()]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def missing_copyright(root: Path) -> list[str]:
    return [str(path.relative_to(root)) for path in _files(root, COPYRIGHT_GLOBS) if COPYRIGHT not in _read(path)]


def comments(root: Path) -> list[str]:
    return [f"{path.relative_to(root)}:{number}: {line.strip()}"
            for path in _files(root, CODE_GLOBS)
            for number, line in enumerate(_read(path).splitlines(), 1)
            if COMMENT.match(line) and COPYRIGHT not in line]


def em_dashes(root: Path) -> list[str]:
    return [f"{path.relative_to(root)}:{number}"
            for path in _text_files(root)
            for number, line in enumerate(_read(path).splitlines(), 1) if EM_DASH in line]


def docstrings(root: Path) -> list[str]:
    found = []
    for path in _files(root, CODE_GLOBS):
        tree = ast.parse(_read(path))
        nodes = [tree] + [node for node in ast.walk(tree)
                          if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        found += [f"{path.relative_to(root)}:{getattr(node, 'lineno', 1)} {getattr(node, 'name', '<module>')}"
                  for node in nodes if ast.get_docstring(node) is not None]
    return found


def stage_words(root: Path) -> list[str]:
    return [f"{path.relative_to(root)}:{number}"
            for path in _text_files(root) if path.name not in TEXT_FILES
            for number, line in enumerate(_read(path).splitlines(), 1) if PHASE_WORD.search(line)]


CHECKS = (("copyright", missing_copyright), ("comments", comments), ("em dash", em_dashes),
          ("docstrings", docstrings), ("stage", stage_words))


def main(root: Path) -> int:
    failed = False
    for name, check in CHECKS:
        problems = check(root)
        print(f"{'RED' if problems else 'green'} {name}")
        for problem in problems[:10]:
            print(f"  {problem}")
        failed = failed or bool(problems)
    print(f"STYLE_EXIT={int(failed)}")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent))
