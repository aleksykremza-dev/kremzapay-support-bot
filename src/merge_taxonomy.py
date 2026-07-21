"""Merge: собирает три части таксономии в один data/taxonomy.json."""
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
assert len(ids) == len(set(ids)), "дубль id в таксономии!"

taxonomy = {"version": 1, "intents": intents, "special_classes": special}
json.dump(taxonomy, open("data/taxonomy.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"taxonomy.json готов: {len(intents)} интентов, {len(special)} спецкласса, версия 1")
