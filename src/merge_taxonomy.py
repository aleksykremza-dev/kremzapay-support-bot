"""Merge: combines three taxonomy parts into a single data/taxonomy.json."""
# [TAXONOMY] Merge taxonomy parts
import json

PARTS = [
    "data/taxonomy/part-a.json",
    "data/taxonomy/part-b.json",
    "data/taxonomy/part-c.json",
]

intents = []
special = []
for path in PARTS:
    part = json.load(open(path, encoding="utf-8"))
    intents += part["intents"]
    special += part.get("special_classes", [])

ids = [i["id"] for i in intents]
assert len(ids) == len(set(ids)), "duplicate id in taxonomy!"

taxonomy = {"version": 1, "intents": intents, "special_classes": special}
json.dump(taxonomy, open("data/taxonomy.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"taxonomy.json ready: {len(intents)} intents, {len(special)} special classes, version 1")
