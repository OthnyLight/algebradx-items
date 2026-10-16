#!/usr/bin/env python3
"""Validate the item bank: schema, misconception codes, and the mathematics of every key.

For each item this checks, with exact rational arithmetic (fractions.Fraction):
  - the keyed option is mathematically correct
  - every distractor is mathematically wrong (so no item has two right answers)
Options without machine-checkable math are listed for hand review.

Writes docs/qa_report.txt and docs/stats.json. Exit code 1 if any check fails.
Usage: python code/01_validate.py
"""
import json
import random
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RNG = random.Random(20261009)  # fixed seed: results are reproducible

# --------------------------------------------------------------------- exact evaluation
_DEC = re.compile(r"(?<!['\w.])(\d+\.\d+)(?![\w.'])")
_INT = re.compile(r"(?<!['\w.])(\d+)(?![\w.'])")


def exact(src: str) -> str:
    """Rewrite numeric literals as Fractions so '/' and '**' stay exact."""
    src = _DEC.sub(lambda m: f"Fraction('{m.group(1)}')", src)
    return _INT.sub(lambda m: f"Fraction({m.group(1)})", src)


def ev(src, env=None):
    ns = {"__builtins__": {}, "Fraction": Fraction, **HELPERS}
    ns.update(env or {})
    return eval(exact(src), ns)  # single namespace so lambdas can see helpers


def rand_q():
    while True:
        q = Fraction(RNG.randint(-40, 40), RNG.randint(1, 7))
        if q != 0:
            return q


def points(vars_, n=16):
    return [{v: rand_q() for v in vars_} for _ in range(n)]


def safe(src, env):
    try:
        return ev(src, env)
    except ZeroDivisionError:
        return None


# --------------------------------------------------------------------- helpers usable in 'assert' checks
def ident(a, b, vars_):
    pts = points(vars_, 24)
    return all(safe(a, p) == safe(b, p) for p in pts if safe(a, p) is not None)


def _int_assignments(vars_, n=400):
    return [{v: Fraction(RNG.randint(-4, 4)) for v in vars_} for _ in range(n)]


def always(a, b, vars_):
    return all(ev(a, p) == ev(b, p) for p in _int_assignments(vars_))


def never(a, b, vars_):
    return all(ev(a, p) != ev(b, p) for p in _int_assignments(vars_))


def sometimes(a, b, vars_):
    return not always(a, b, vars_) and not never(a, b, vars_)


def all_int(f):
    return all(f(Fraction(n)) for n in range(0, 41))


def all_num(f):
    vals = [Fraction(n) for n in range(-20, 21)] + [Fraction(n, 3) for n in range(-20, 21)]
    return all(f(v) for v in vals)


def is_function(pairs):
    seen = {}
    for x, y in pairs:
        if x in seen and seen[x] != y:
            return False
        seen[x] = y
    return True


def defined_at(expr, v):
    return safe(expr, {"x": Fraction(v)}) is not None


def undefined_at(expr, v):
    return not defined_at(expr, v)


HELPERS = dict(ident=ident, always=always, never=never, sometimes=sometimes,
               all_int=all_int, all_num=all_num, is_function=is_function,
               defined_at=defined_at, undefined_at=undefined_at)


# --------------------------------------------------------------------- check types
def split_eq(s):
    lhs, rhs = s.split("==")
    return f"({lhs})-({rhs})"


def linear_solution(eq, var):
    f = split_eq(eq)
    f0, f1, f2 = (ev(f, {var: Fraction(k)}) for k in (0, 1, 2))
    if f2 - 2 * f1 + f0 != 0:
        raise ValueError(f"not linear: {eq}")
    slope = f1 - f0
    if slope == 0:
        return "all" if f0 == 0 else "none"
    return -f0 / slope


def is_correct(item, letter):
    """Return True/False for options with math, None for hand-review options."""
    c = item["check"]
    opt = item["options"][letter]
    t = c["type"]
    if t == "assert":
        src = c.get("truths", {}).get(letter)
        return None if src is None else bool(ev(src))
    m = opt.get("math")
    if m is None:
        return None
    if t == "value":
        return ev(m) == ev(c["answer"], {k: Fraction(v) for k, v in c.get("at", {}).items()})
    if t == "expr":
        pts = points(c["vars"], 20)
        pairs = [(safe(m, p), safe(c["target"], p)) for p in pts]
        return all(a == b for a, b in pairs if a is not None and b is not None)
    if t == "equiv_solution":
        return linear_solution(m, c["var"]) == linear_solution(c["original"], c["var"])
    if t == "solves":
        return ev(split_eq(c["equation"]), {c["var"]: ev(m)}) == 0
    if t == "ineq":
        grid = [Fraction(n, 6) for n in range(-60, 61)] + [rand_q() for _ in range(40)]
        return all(bool(ev(m, {c["var"]: x})) == bool(ev(c["original"], {c["var"]: x})) for x in grid)
    if t == "literal":
        for p in points(c["vars"], 20):
            val = safe(m, p)
            if val is None:
                continue
            if ev(split_eq(c["equation"]), {**p, c["solve_for"]: val}) != 0:
                return False
        return True
    if t == "table":
        return all(ev(m, {c["var"]: Fraction(x)}) == y for x, y in c["points"])
    if t == "relation":
        return all(bool(ev(m, {k: Fraction(v) for k, v in s.items()})) for s in c["scenarios"])
    raise ValueError(f"unknown check type {t}")


# --------------------------------------------------------------------- main
def main():
    bank = yaml.safe_load((ROOT / "items/items.yaml").read_text())["items"]
    catalog = yaml.safe_load((ROOT / "items/misconceptions.yaml").read_text())
    refs_md = (ROOT / "docs/REFERENCES.md").read_text() if (ROOT / "docs/REFERENCES.md").exists() else ""

    errors, manual, lines = [], [], []
    ids = Counter(i["id"] for i in bank)
    for k, n in ids.items():
        if n > 1:
            errors.append(f"duplicate id {k}")

    mech_pass = mech_total = 0
    codes_used = Counter()
    for it in bank:
        iid = it["id"]
        letters = sorted(it["options"])
        if letters != ["A", "B", "C", "D"]:
            errors.append(f"{iid}: options must be A-D")
        key = it["key"]
        if key not in letters:
            errors.append(f"{iid}: key {key} not an option")
        if sorted(it["distractors"]) != sorted(set(letters) - {key}):
            errors.append(f"{iid}: distractor rationales must cover exactly the non-key options")
        for L, d in it["distractors"].items():
            codes_used[d["code"]] += 1
            if d["code"] not in catalog:
                errors.append(f"{iid}{L}: unknown misconception code {d['code']}")
        for f in ("skill", "ccss", "naep_focus", "difficulty", "stem", "teaching_move"):
            if not it.get(f):
                errors.append(f"{iid}: missing {f}")

        # mathematics
        results = {}
        for L in letters:
            try:
                r = is_correct(it, L)
            except Exception as e:  # noqa: BLE001
                errors.append(f"{iid}{L}: check raised {type(e).__name__}: {e}")
                r = "ERR"
            results[L] = r
            if r is None:
                manual.append(f"{iid}{L}{' (KEY)' if L == key else ''}: {it['options'][L]['text']}")
                continue
            if r == "ERR":
                continue
            mech_total += 1
            expected = (L == key)
            if r == expected:
                mech_pass += 1
            else:
                errors.append(f"{iid}{L}: {'key is NOT correct' if expected else 'distractor is ALSO correct'}")
        lines.append(f"{iid:7s} key={key} " + " ".join(
            f"{L}:{'ok' if (r is not None and r != 'ERR' and r == (L == key)) else ('hand' if r is None else 'FAIL')}"
            for L, r in results.items()))

    # catalog integrity
    unused = sorted(set(catalog) - set(codes_used))
    for code, c in catalog.items():
        for r in c.get("refs", []):
            if refs_md and f"[{r}]" not in refs_md:
                errors.append(f"catalog {code}: reference key {r} missing from docs/REFERENCES.md")

    strands = Counter(i["strand"] for i in bank)
    diff = Counter(i["difficulty"] for i in bank)
    keys = Counter(i["key"] for i in bank)
    ccss = sorted({c for i in bank for c in i["ccss"]})
    strand_order = ["EQ", "VAR", "DIST", "LIN", "NUM", "LINF", "FUNC", "MOD"]
    form_a, form_b = forms(bank, strand_order)

    stats = {
        "version": "1.0.0",
        "n_items": len(bank),
        "n_strands": len(strands),
        "items_per_strand": {s: strands[s] for s in strand_order},
        "difficulty_counts": {str(k): diff[k] for k in sorted(diff)},
        "key_balance": {k: keys[k] for k in "ABCD"},
        "n_distractors": sum(len(i["distractors"]) for i in bank),
        "n_misconception_codes_catalog": len(catalog),
        "n_misconception_codes_used": len(codes_used),
        "codes_unused": unused,
        "most_used_codes": codes_used.most_common(5),
        "n_ccss_codes": len(ccss),
        "ccss_codes": ccss,
        "mechanical_checks_total": mech_total,
        "mechanical_checks_passed": mech_pass,
        "n_options_hand_review": len(manual),
        "form_A": form_a,
        "form_B": form_b,
        "n_items_form": len(form_a),
        "errors": len(errors),
    }
    (ROOT / "docs/stats.json").write_text(json.dumps(stats, indent=2))

    rep = ["AlgebraDx Item Bank: QA report", "=" * 40,
           f"Items: {len(bank)}   Strands: {dict(stats['items_per_strand'])}",
           f"Difficulty (hypothesized): {stats['difficulty_counts']}",
           f"Key balance: {stats['key_balance']}",
           f"Distractors: {stats['n_distractors']}   Misconception codes used: {len(codes_used)} of {len(catalog)}",
           f"Unused catalog codes: {unused or 'none'}",
           f"CCSS codes referenced: {len(ccss)}",
           "",
           f"Mechanical checks (key correct / distractor wrong): {mech_pass} of {mech_total} passed",
           f"Options needing hand review (no machine-checkable math): {len(manual)}",
           "", "Per-item results (ok = verified, hand = author must check, FAIL = error)", "-" * 40,
           *lines, "", "Hand-review list", "-" * 40, *manual, "",
           f"Form A ({len(form_a)} items): {' '.join(form_a)}",
           f"Form B ({len(form_b)} items): {' '.join(form_b)}", "",
           "ERRORS" if errors else "No errors.", *errors]
    (ROOT / "docs/qa_report.txt").write_text("\n".join(rep) + "\n")
    print("\n".join(rep[:12]))
    print(f"errors: {len(errors)}")
    for e in errors:
        print("  ", e)
    sys.exit(1 if errors else 0)


def forms(bank, strand_order):
    """Two parallel 20-item forms: items 1-2 of every strand on A, 4-5 on B,
    item 3 alternating by strand so each form gets 20."""
    a, b = [], []
    for si, s in enumerate(strand_order):
        its = [i["id"] for i in bank if i["strand"] == s]
        a += its[:2]
        b += its[3:5]
        (a if si % 2 == 0 else b).append(its[2])
    return a, b


if __name__ == "__main__":
    main()
