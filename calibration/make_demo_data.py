#!/usr/bin/env python3
"""Generate a SYNTHETIC response file for testing calibrate.py. NOT student data.

Simulated students have an ability and hold a random subset of misconceptions. On each item
a student who holds a misconception targeted by a distractor chooses it with high probability;
otherwise they answer correctly with a probability that depends on ability and the item's
hypothesized difficulty. The planted misconceptions are saved so the scoring logic can be
checked for recovery (precision / recall of flagged codes).

These numbers say nothing about real students and must never be reported as findings.
Usage: python calibration/make_demo_data.py [--n 150] [--seed 7]
"""
import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150, help="simulated students per form")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    key = defaultdict(list)
    with open(ROOT / "exports/answer_key.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key[r["form"]].append(r)
    items = {i["id"]: i for i in json.loads((ROOT / "exports/items.json").read_text())["items"]}
    codes = sorted({r[f"code_{L}"] for rows in key.values() for r in rows for L in "ABCD" if r[f"code_{L}"]})
    prevalence = {c: rng.uniform(0.05, 0.30) for c in codes}

    out_dir = ROOT / "calibration/demo"
    out_dir.mkdir(parents=True, exist_ok=True)
    planted = {}
    with open(out_dir / "responses_SYNTHETIC.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "form"] + [f"q{j}" for j in range(1, 21)])
        sid = 0
        for form in ("A", "B"):
            for _ in range(a.n):
                sid += 1
                theta = rng.gauss(0, 1)
                held = {c for c in codes if rng.random() < prevalence[c]}
                planted[f"SIM{sid:04d}"] = sorted(held)
                row = []
                for k in key[form]:
                    b = {1: -1.0, 2: 0.0, 3: 1.0}[items[k["item_id"]]["difficulty"]]
                    trap = [L for L in "ABCD" if k[f"code_{L}"] in held]
                    if trap and rng.random() < 0.75:
                        row.append(rng.choice(trap))
                    elif rng.random() < 1 / (1 + math.exp(-(1.4 * (theta - b)))):
                        row.append(k["key"])
                    elif rng.random() < 0.04:
                        row.append("")
                    else:
                        row.append(rng.choice([L for L in "ABCD" if L != k["key"]]))
                w.writerow([f"SIM{sid:04d}", form] + row)
    (out_dir / "planted_SYNTHETIC.json").write_text(json.dumps(planted, indent=1))
    print(f"wrote {2 * a.n} synthetic students to {out_dir}/responses_SYNTHETIC.csv")


if __name__ == "__main__":
    main()
