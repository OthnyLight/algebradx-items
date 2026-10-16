#!/usr/bin/env python3
"""Score and calibrate AlgebraDx forms on YOUR OWN students. Nothing leaves your machine.

Input: a CSV with one row per student:
    student_id, form, q1, q2, ..., q20
where form is A or B and each q is the letter the student circled (A-D), blank if omitted.
Use calibration/response_template.csv as the starting point. Use local IDs, not names.

Outputs (in --out, default ./calibration_output):
    item_stats.csv          difficulty (p), discrimination (corrected point-biserial),
                            choice rates, distractor discrimination, and review flags
    form_summary.txt        mean, SD, KR-20 reliability, SEM, and how to read them
    student_profiles.csv    score, strand subscores, misconception codes chosen, codes flagged
    class_misconceptions.csv  how many students show each misconception pattern, and the move

Standard library only. Usage:
    python calibration/calibrate.py responses.csv [--key exports/answer_key.csv] [--out DIR]
                                    [--catalog items/misconceptions.json]
"""
import argparse
import csv
import json
import math
import statistics as stats
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MIN_FLAG = 2  # a code chosen at least this many times on one form is treated as a pattern


def pearson(x, y):
    if len(x) < 3:
        return float("nan")
    mx, my = stats.fmean(x), stats.fmean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def load_key(path):
    key = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key[r["form"]].append(r)
    return key


def load_catalog():
    j = ROOT / "exports/items.json"
    if j.exists():
        return json.loads(j.read_text(encoding="utf-8"))["misconceptions"]
    return {}


def fmt(x, nd=3):
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def analyze(rows, form, key_rows, catalog, out):
    n_items = len(key_rows)
    resp = [[(r.get(f"q{j}") or "").strip().upper()[:1] for j in range(1, n_items + 1)] for r in rows]
    scored = [[int(a == k["key"]) for a, k in zip(rr, key_rows)] for rr in resp]
    totals = [sum(s) for s in scored]
    n = len(rows)

    item_out = []
    for j, k in enumerate(key_rows):
        col = [s[j] for s in scored]
        rest = [t - c for t, c in zip(totals, col)]
        p = stats.fmean(col) if n else float("nan")
        rpb = pearson(col, rest)
        picks = Counter(rr[j] for rr in resp)
        rec = {"form": form, "position": j + 1, "item_id": k["item_id"], "strand": k["strand"],
               "key": k["key"], "n": n, "p_value": p, "discrimination_rpb": rpb,
               "omit_rate": picks[""] / n if n else float("nan")}
        flags = []
        for L in "ABCD":
            rate = picks[L] / n if n else float("nan")
            rec[f"pick_{L}"] = rate
            if L != k["key"]:
                chose = [int(rr[j] == L) for rr in resp]
                d_rpb = pearson(chose, rest)
                rec[f"rpb_{L}"] = d_rpb
                if n >= 30 and rate < 0.03:
                    flags.append(f"{L} rarely chosen (<3%): consider revising")
                if not math.isnan(d_rpb) and d_rpb > 0.05:
                    flags.append(f"{L} attracts higher scorers: check key and wording")
            else:
                rec[f"rpb_{L}"] = float("nan")
        if not math.isnan(p):
            if p < 0.20:
                flags.append("very hard (p<.20)")
            if p > 0.95:
                flags.append("very easy (p>.95)")
        if not math.isnan(rpb) and rpb < 0.15:
            flags.append("weak discrimination (r<.15)")
        if n < 100:
            flags.append(f"small sample (n={n}); treat values as provisional")
        rec["flags"] = "; ".join(flags)
        item_out.append(rec)

    # reliability
    var_t = stats.pvariance(totals) if n > 1 else float("nan")
    pq = sum(stats.fmean([s[j] for s in scored]) * (1 - stats.fmean([s[j] for s in scored]))
             for j in range(n_items)) if n else float("nan")
    kr20 = (n_items / (n_items - 1)) * (1 - pq / var_t) if n > 1 and var_t > 0 else float("nan")
    sd = math.sqrt(var_t) if n > 1 else float("nan")
    sem = sd * math.sqrt(1 - kr20) if not math.isnan(kr20) and kr20 < 1 else float("nan")

    # student profiles
    strands = sorted({k["strand"] for k in key_rows})
    profiles, class_codes = [], defaultdict(set)
    code_sel = Counter()
    for r, rr, s in zip(rows, resp, scored):
        codes = Counter()
        for a, k in zip(rr, key_rows):
            if a and a != k["key"] and k.get(f"code_{a}"):
                codes[k[f"code_{a}"]] += 1
        code_sel.update(codes)
        flagged = sorted(c for c, v in codes.items() if v >= MIN_FLAG)
        for c in flagged:
            class_codes[c].add(r["student_id"])
        sub = {st: f"{sum(x for x, k in zip(s, key_rows) if k['strand'] == st)}/"
                   f"{sum(1 for k in key_rows if k['strand'] == st)}" for st in strands}
        profiles.append({"student_id": r["student_id"], "form": form, "score": sum(s),
                         "max": n_items, **{f"strand_{st}": v for st, v in sub.items()},
                         "codes_chosen": "; ".join(f"{c}x{v}" for c, v in codes.most_common()),
                         "codes_flagged": "; ".join(flagged)})

    out.mkdir(parents=True, exist_ok=True)
    return item_out, profiles, class_codes, code_sel, {
        "form": form, "n": n, "items": n_items, "mean": stats.fmean(totals) if n else float("nan"),
        "sd": sd, "kr20": kr20, "sem": sem}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("responses")
    ap.add_argument("--key", default=str(ROOT / "exports/answer_key.csv"))
    ap.add_argument("--out", default="calibration_output")
    a = ap.parse_args()
    out = Path(a.out)
    key = load_key(a.key)
    catalog = load_catalog()
    with open(a.responses, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    by_form = defaultdict(list)
    for r in rows:
        by_form[(r.get("form") or "").strip().upper()].append(r)

    all_items, all_prof, summaries = [], [], []
    class_codes, code_sel = defaultdict(set), Counter()
    for form, rs in sorted(by_form.items()):
        if form not in key:
            print(f"skipping {len(rs)} rows with unknown form '{form}'")
            continue
        it, pr, cc, cs, sm = analyze(rs, form, key[form], catalog, out)
        all_items += it
        all_prof += pr
        summaries.append(sm)
        for c, ids in cc.items():
            class_codes[c] |= ids
        code_sel.update(cs)

    fields = ["form", "position", "item_id", "strand", "key", "n", "p_value", "discrimination_rpb",
              "omit_rate", "pick_A", "pick_B", "pick_C", "pick_D", "rpb_A", "rpb_B", "rpb_C", "rpb_D", "flags"]
    with open(out / "item_stats.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_items:
            w.writerow({k: (fmt(v) if isinstance(v, float) else v) for k, v in r.items()})

    pf = list(dict.fromkeys(k for p in all_prof for k in p))
    with open(out / "student_profiles.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=pf)
        w.writeheader()
        w.writerows(all_prof)

    n_students = len(all_prof)
    with open(out / "class_misconceptions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["code", "name", "students_flagged", "pct_students", "times_chosen", "teaching_move"])
        for c, ids in sorted(class_codes.items(), key=lambda kv: -len(kv[1])):
            w.writerow([c, catalog.get(c, {}).get("name", ""), len(ids),
                        fmt(len(ids) / n_students, 2) if n_students else "", code_sel[c],
                        catalog.get(c, {}).get("move", "")])

    lines = ["AlgebraDx calibration summary", "=" * 34, ""]
    for s in summaries:
        lines += [f"Form {s['form']}: n = {s['n']}, items = {s['items']}",
                  f"  mean score = {fmt(s['mean'], 2)}   SD = {fmt(s['sd'], 2)}",
                  f"  KR-20 reliability = {fmt(s['kr20'], 2)}   SEM = {fmt(s['sem'], 2)} points", ""]
    lines += ["How to read this",
              "- p_value: share of students answering correctly (difficulty; higher = easier).",
              "- discrimination_rpb: correlation of the item with the rest of the form. Above .30 is good,",
              "  .15-.30 acceptable, below .15 means the item is not separating stronger and weaker students.",
              "- rpb_A..D for wrong options should be negative. A positive value means stronger students",
              "  are choosing a wrong answer: re-read the item, the key, and the wording.",
              "- KR-20 near .70 or above is typical for a 20-item classroom diagnostic. The form is built to",
              "  diagnose misconceptions, so use subscores and codes, not only the total.",
              "- With fewer than about 100 students, treat every value as provisional.",
              "",
              "Privacy: this script runs locally and writes only to the output folder. Use local IDs,",
              "not student names, and keep outputs under your school's data policy."]
    (out / "form_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:3 + 4 * len(summaries)]))
    print(f"wrote {out}/item_stats.csv, student_profiles.csv, class_misconceptions.csv, form_summary.txt")


if __name__ == "__main__":
    main()
