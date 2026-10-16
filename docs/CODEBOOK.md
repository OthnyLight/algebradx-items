# Codebook

## items/items.yaml → exports/items.csv (one row per item)

| Field | Definition |
|---|---|
| `item_id` / `id` | Strand prefix + 2-digit number (e.g., EQ03). Stable across versions; a retired item's ID is never reused. |
| `strand` | One of EQ, VAR, DIST, LIN, NUM, LINF, FUNC, MOD (see `items/strands.yaml`). |
| `strand_name` | Human-readable strand name. |
| `skill` | The skill the item diagnoses, in one line. |
| `ccss` | Common Core State Standards for Mathematics codes the item assesses (semicolon-separated in CSV). |
| `naep_focus` | Plain-language description of the NAEP 2026 Algebra focus. Formal objective IDs are in `docs/NAEP_ALIGNMENT.csv`. |
| `difficulty` / `difficulty_hypothesized` | Author's hypothesis: 1 easy, 2 medium, 3 hard. Replace with local p-values after calibration. |
| `stem` | Question text. Hyphen-minus is printed as a true minus sign in PDFs. |
| `A`–`D` / `options.X.text` | Option text as shown to students. |
| `options.X.math` | Machine-checkable form used by the validator (Python syntax with exact fractions); `null` means hand-reviewed. |
| `key` | Correct option letter. |
| `distractors.X.code` | Misconception code for wrong option X (see the catalog). |
| `distractors.X.reveals` | Item-specific description of what choosing X suggests. |
| `teaching_move` | Item-level summary of the recommended teaching move. |
| `check` | Validation rule (type and parameters); see the header of `items.yaml`. |

## exports/options.csv (one row per option)

`item_id, option, text, is_key (1/0), misconception_code, misconception_name, reveals`. The key row has blank code fields.

## exports/answer_key.csv (one row per form position)

`form (A/B), position (1–20), item_id, strand, key, code_A … code_D`. The code columns are blank for the key. This is the input to `calibration/calibrate.py`.

## items/misconceptions.yaml (one entry per code)

`name`, `strand` (home strand; codes can appear in other strands), `reveals`, `move` (teaching move), `probe` (confirmation question), `refs` (keys into `docs/REFERENCES.md`).

## Forms

Form A: items 1–2 of every strand, plus item 3 of EQ, DIST, NUM and FUNC. Form B: items 4–5 of every strand, plus item 3 of VAR, LIN, LINF and MOD. Item order within a form follows the strand order. Lists are in `docs/stats.json`.

## calibration outputs (produced by schools, never collected by the project)

| File | Fields |
|---|---|
| `item_stats.csv` | `p_value` (proportion correct), `discrimination_rpb` (item vs. rest-of-form point-biserial), `omit_rate`, `pick_A–D` (choice rates), `rpb_A–D` (distractor vs. rest score; should be negative), `flags` |
| `student_profiles.csv` | `score`, `strand_*` subscores, `codes_chosen` (code×count), `codes_flagged` (codes chosen on ≥ 2 items) |
| `class_misconceptions.csv` | `code`, `name`, `students_flagged`, `pct_students`, `times_chosen`, `teaching_move` |
| `form_summary.txt` | n, mean, SD, KR-20, SEM, with reading notes |
