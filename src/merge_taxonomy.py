# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import json
import sys

import config


def main() -> int:
    intents, special = [], []
    for path in sorted(config.TAXONOMY_PARTS_DIR.glob("part-*.json")):
        with open(path, encoding="utf-8") as handle:
            part = json.load(handle)
        intents += part["intents"]
        special += part.get("special_classes", [])
    ids = [item["id"] for item in intents]
    if len(ids) != len(set(ids)):
        print("duplicate id in taxonomy")
        return 1
    taxonomy = {"version": 1, "intents": intents, "special_classes": special}
    with open(config.TAXONOMY_PATH, "w", encoding="utf-8") as handle:
        json.dump(taxonomy, handle, ensure_ascii=False, indent=1)
    print(f"taxonomy.json ready: {len(intents)} intents, {len(special)} special classes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
