# AlgebraDx Open Diagnostic Item Bank

**Status:** Released v1.0.0 (2026-10-10), verified by the author | **Maintainer:** Othniel Iyassa Sa'anga, [ORCID 0009-0002-6113-6158](https://orcid.org/0009-0002-6113-6158) | **License:** items, guides and article CC BY 4.0; code MIT

A free, openly licensed bank of original multiple-choice items that diagnose **why** a grade 9–12 student is struggling with algebra, not just whether. Each item is tagged with the skill it diagnoses. Each wrong answer is written to reveal a specific, research-documented misconception and is paired with the teaching move that addresses it. No student data is collected. Schools that adopt the items can calibrate them on their own students with the included kit, which runs locally.

This is the classroom layer of **AlgebraDx**: ready-to-use diagnostic questions a teacher can give on Monday.

## What is here

```
items/
  items.yaml             the 40 items (source of truth)
  misconceptions.yaml    64 misconception codes: what each suggests, teaching move, probe, research
  strands.yaml           the 8 strands and why each matters for readiness
exports/
  student_form_A.pdf, student_form_B.pdf   parallel 20-item printable forms
  teacher_guide.pdf      item-by-item diagnosis, teaching moves, catalog, answer keys
  items.csv, options.csv, items.json       machine-readable bank (LMS / research use)
  answer_key.csv         key + the misconception code behind every wrong option
calibration/
  calibrate.py           score and calibrate on your own students (standard library only)
  response_template.csv, CALIBRATION_GUIDE.md
  make_demo_data.py, demo/   SYNTHETIC data and outputs for testing only
docs/  BUILD_SPEC, CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, NEXT_STEPS, PUBLISH_GUIDE,
       REFERENCES, NAEP_ALIGNMENT.csv, qa_report.txt, design_check.txt, stats.json
code/  01_validate.py  02_export.py  03_print.py  04_design_check.py  05_article.js
```

## Run it

```
pip install -r requirements.txt     # PyYAML, reportlab, matplotlib (for fonts), python-docx
npm install docx                    # only for rebuilding the article
./run_all.sh                        # validate -> export -> PDFs -> demo calibration -> design check -> article
./run_all.sh --final                # release build (final, unstamped outputs)
```

Everything is regenerated from `items/*.yaml`. Edit an item there, rerun, and every form, guide, export and article number updates.

To calibrate on your own students, see `calibration/CALIBRATION_GUIDE.md`.

## Quality checks (from `docs/qa_report.txt` and `docs/stats.json`)

- 40 items, 5 in each of 8 strands. Keys balanced (10 each of A, B, C, D). Hypothesized difficulty: 15 easy, 20 medium, 5 hard.
- 120 distractors, each coded to one of 64 misconceptions. Every catalog code is used at least once.
- 143 of 143 machine-checkable options pass an exact-arithmetic check: every key is correct and no distractor is also correct. 17 verbal options are on the hand-review list.
- On a single 20-item form, 10 codes (Form A) and 9 codes (Form B) appear on two or more items and can be flagged as patterns. The rest give single-choice signals to confirm with a probe. See `docs/LIMITATIONS.md`.

## Sources and originality

All items are original. **No NAEP or TIMSS item text is reproduced.** TIMSS items are not used because IEA requires prior notice for their use in assessments or learning materials. NAEP is used only for alignment. In v1.0 each item is described against the Algebra content area of the NAEP 2026 framework; the item-by-item comparison with released grade 12 NAEP items (by ID only, in `docs/NAEP_ALIGNMENT.csv`) is scheduled for v1.1. The research basis for every misconception is in `docs/REFERENCES.md`.

**AI assistance:** Items, rationales, code and text were drafted with AI assistance (Claude, Anthropic) from the published misconception research, under the author's direction. The author reviewed and verified every item, rationale and teaching move before release (`docs/VERIFY_CHECKLIST.md`).

## Limitations

Read `docs/LIMITATIONS.md` before using or citing anything here. In short: the items are not field-tested, difficulty levels are hypotheses, and this is not a placement or grading instrument.

## Citation

See `CITATION.cff`. DOI: added after the Zenodo deposit.
