#!/usr/bin/env python3
"""Design checks on the forms (no student data):

1. Opportunities: on each form, how many distractors carry each misconception code.
   A code with one opportunity cannot be flagged as a pattern (the profile rule needs 2 choices).
2. Simulation recovery: using the SYNTHETIC responses from calibration/make_demo_data.py,
   how well does the flagging rule recover the planted misconceptions (precision / recall)?
   This tests the scoring logic only. It is not evidence about real students.

Appends results to docs/stats.json and writes docs/design_check.txt.
Usage: python code/04_design_check.py   (after calibration/make_demo_data.py and calibrate.py)
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    key = defaultdict(list)
    with open(ROOT / "exports/answer_key.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key[r["form"]].append(r)
    # count ITEMS carrying the code, not distractors: a student picks one option per item
    opp = {form: Counter(c for r in rows for c in {r[f"code_{L}"] for L in "ABCD" if r[f"code_{L}"]})
           for form, rows in key.items()}
    flaggable = {form: sorted(c for c, n in o.items() if n >= 2) for form, o in opp.items()}

    lines = ["Design check", "=" * 30, ""]
    for form, o in sorted(opp.items()):
        lines.append(f"Form {form}: {len(o)} codes appear; {len(flaggable[form])} have >= 2 opportunities "
                     f"(flaggable as a pattern)")
        lines.append("  flaggable: " + ", ".join(f"{c}({o[c]})" for c in flaggable[form]))
        lines.append("")

    rec = {}
    planted_p = ROOT / "calibration/demo/planted_SYNTHETIC.json"
    prof_p = ROOT / "calibration/demo/output/student_profiles.csv"
    if planted_p.exists() and prof_p.exists():
        planted = json.loads(planted_p.read_text())
        tp = fp = fn = 0
        with open(prof_p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                eligible = set(flaggable[r["form"]])
                truth = set(planted[r["student_id"]]) & eligible
                got = {c for c in r["codes_flagged"].split("; ") if c}
                tp += len(got & truth)
                fp += len(got - truth)
                fn += len(truth - got)
        prec = tp / (tp + fp) if tp + fp else float("nan")
        recall = tp / (tp + fn) if tp + fn else float("nan")
        rec = {"sim_precision": round(prec, 3), "sim_recall": round(recall, 3),
               "sim_true_pos": tp, "sim_false_pos": fp, "sim_false_neg": fn}
        lines += ["Simulation recovery (SYNTHETIC data; tests scoring logic, not students)",
                  f"  among flaggable codes: precision = {prec:.2f}, recall = {recall:.2f} "
                  f"(TP {tp}, FP {fp}, FN {fn})",
                  "  Assumes a student holding a misconception picks its distractor 75% of the time;",
                  "  real-world rates are unknown until local calibration.", ""]

    stats_p = ROOT / "docs/stats.json"
    st = json.loads(stats_p.read_text())
    st.update({"flaggable_codes_A": len(flaggable["A"]), "flaggable_codes_B": len(flaggable["B"]),
               "codes_on_form_A": len(opp["A"]), "codes_on_form_B": len(opp["B"]), **rec})
    stats_p.write_text(json.dumps(st, indent=2))
    (ROOT / "docs/design_check.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
