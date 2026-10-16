# Next steps

## v1.0.0 (released 2026-10-10)
Verified by the author. Publish via `docs/PUBLISH_GUIDE.md`.

## v1.1: deeper diagnosis per code
- **NAEP item-level alignment.** Complete `docs/NAEP_ALIGNMENT.csv`: 2026 framework objective ID per item and the NAEP Questions Tool grade 12 items compared (by ID only).
- **Follow-up mini-forms.** For the most common codes (EQ-TRANSPOSE, EXP-MULT, VAR-CONJOIN, DIST-NEG, MOD-REVERSAL, FN-NOTATION …), write 3–4 additional items each, so a teacher can confirm a flagged pattern with a 5-minute targeted check. This addresses LIMITATIONS #3.
- **Two-tier items** for selected items: a reason question after the answer ("Why did you choose that?"), which strengthens diagnosis without interviews.
- **Drawn graphs** for LINF and FUNC items (accessible SVG with alt text).

## v1.2: calibration from partner schools
- Invite 3–5 Indiana schools to run `calibrate.py` locally and share **item-level statistics only** (`item_stats.csv`).
- Pool item statistics. Revise or retire items flagged for weak discrimination or a distractor that attracts high scorers. Publish the pooled statistics as a versioned Zenodo release.

## v2.0: reach
- Spanish translation with read-aloud guidance.
- Import packages for common learning platforms (QTI export from `items.json`).
- Extend strands: systems of equations, exponential functions, quadratics beyond factoring.

## Connection to AlgebraDx
The misconception codes are the shared vocabulary between this bank and the AlgebraDx diagnostic model. When the model is released, map its skill taxonomy to these codes in one table so classroom results and model outputs speak the same language.
