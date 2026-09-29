# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import argparse
import ast
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import config

SCAN_DIRS = ("src", "tools")
FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


def git_output(*args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=config.BASE_DIR, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def to_https_repo_url(remote: str) -> str:
    url = remote
    if url.startswith("git@"):
        host, _, path = url[len("git@"):].partition(":")
        url = f"https://{host}/{path}"
    if url.endswith(".git"):
        url = url[:-len(".git")]
    return url.rstrip("/")


def function_signature(node: ast.AST) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"


def class_signature(node: ast.ClassDef) -> str:
    bases = ", ".join(ast.unparse(base) for base in node.bases)
    return f"class {node.name}({bases})" if bases else f"class {node.name}"


def make_entry(node: ast.AST, kind: str, qualified: str, rel_file: str, signature: str,
               repo: str, commit: str) -> dict:
    return {"name": node.name, "qualified_name": qualified, "kind": kind, "file": rel_file,
            "lineno": node.lineno, "end_lineno": node.end_lineno, "signature": signature,
            "link": f"{repo}/blob/{commit}/{rel_file}#L{node.lineno}-L{node.end_lineno}"}


def collect_file(path: Path, repo: str, commit: str) -> list[dict]:
    rel_file = path.relative_to(config.BASE_DIR).as_posix()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    entries: list[dict] = []
    for node in tree.body:
        if isinstance(node, FUNCTION_NODES):
            entries.append(make_entry(node, "function", node.name, rel_file, function_signature(node), repo, commit))
        elif isinstance(node, ast.ClassDef):
            entries.append(make_entry(node, "class", node.name, rel_file, class_signature(node), repo, commit))
            entries += collect_methods(node, rel_file, repo, commit)
    return entries


def collect_methods(cls: ast.ClassDef, rel_file: str, repo: str, commit: str) -> list[dict]:
    return [make_entry(node, "method", f"{cls.name}.{node.name}", rel_file, function_signature(node), repo, commit)
            for node in cls.body if isinstance(node, FUNCTION_NODES)]


def collect_all(repo: str, commit: str) -> list[dict]:
    entries: list[dict] = []
    for dir_name in SCAN_DIRS:
        for path in sorted((config.BASE_DIR / dir_name).glob("*.py")):
            entries += collect_file(path, repo, commit)
    return entries


def print_table(entries: list[dict]) -> None:
    kind_width = max(len(entry["kind"]) for entry in entries)
    name_width = max(len(entry["qualified_name"]) for entry in entries)
    location_width = max(len(f"{entry['file']}:{entry['lineno']}-{entry['end_lineno']}") for entry in entries)
    for entry in entries:
        location = f"{entry['file']}:{entry['lineno']}-{entry['end_lineno']}"
        print(f"{entry['kind']:<{kind_width}}  {entry['qualified_name']:<{name_width}}  "
              f"{location:<{location_width}}  {entry['signature']}")


def write_codemap(report: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=config.REPORTS_DIR / "codemap.json")
    parser.add_argument("--format", choices=("json", "table"), default="json")
    args = parser.parse_args()

    commit = git_output("rev-parse", "HEAD")
    repo = to_https_repo_url(git_output("remote", "get-url", "origin"))
    entries = collect_all(repo, commit)
    report = {"generated": datetime.now().isoformat(timespec="seconds"), "repo": repo,
              "commit": commit, "entries": entries}
    write_codemap(report, args.out)

    if args.format == "table" and entries:
        print_table(entries)
    print(f"{len(entries)} entries at {commit[:8]} written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
