#!/usr/bin/env python3
"""Export the item bank to machine-readable files.

Writes:
  exports/items.json        full bank, catalog and strands in one file
  exports/items.csv         one row per item
  exports/options.csv       one row per item option (with misconception code for distractors)
  exports/answer_key.csv    form, position, item, key, and the code behind each wrong option
                            (this is what calibration/calibrate.py reads)
Usage: python code/02_export.py
"""
import csv
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "exports"


def load():
    bank = yaml.safe_load((ROOT / "items/items.yaml").read_text())["items"]
    catalog = yaml.safe_load((ROOT / "items/misconceptions.yaml").read_text())
    strands = yaml.safe_load((ROOT / "items/strands.yaml").read_text())
    stats = json.loads((ROOT / "docs/stats.json").read_text())
    return bank, catalog, strands, stats


def main():
    bank, catalog, strands, stats = load()
    OUT.mkdir(exist_ok=True)
    meta = json.loads((ROOT / "AUTHORS.json").read_text())
    (OUT / "items.json").write_text(json.dumps({
        "title": "AlgebraDx Open Diagnostic Item Bank",
        "version": stats["version"],
        "license": "CC-BY-4.0",
        "authors": [a["name"] for a in meta["authors"]],
        "strands": strands, "misconceptions": catalog, "items": bank,
        "forms": {"A": stats["form_A"], "B": stats["form_B"]},
    }, indent=2, ensure_ascii=False))

    with open(OUT / "items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "strand", "strand_name", "skill", "ccss", "naep_focus",
                    "difficulty_hypothesized", "stem", "A", "B", "C", "D", "key", "teaching_move"])
        for it in bank:
            w.writerow([it["id"], it["strand"], strands[it["strand"]]["name"], it["skill"],
                        ";".join(it["ccss"]), it["naep_focus"], it["difficulty"], it["stem"],
                        *(it["options"][L]["text"] for L in "ABCD"), it["key"], it["teaching_move"]])

    with open(OUT / "options.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "option", "text", "is_key", "misconception_code",
                    "misconception_name", "reveals"])
        for it in bank:
            for L in "ABCD":
                d = it["distractors"].get(L)
                w.writerow([it["id"], L, it["options"][L]["text"], int(L == it["key"]),
                            d["code"] if d else "", catalog[d["code"]]["name"] if d else "",
                            d["reveals"] if d else ""])

    by_id = {i["id"]: i for i in bank}
    with open(OUT / "answer_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["form", "position", "item_id", "strand", "key", "code_A", "code_B", "code_C", "code_D"])
        for form in ("A", "B"):
            for pos, iid in enumerate(stats[f"form_{form}"], 1):
                it = by_id[iid]
                w.writerow([form, pos, iid, it["strand"], it["key"],
                            *(it["distractors"].get(L, {}).get("code", "") for L in "ABCD")])
    print("exports written:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
