# Verification checklist

**Record:** Othniel Iyassa Sa'anga reviewed the full package and confirmed it on 2026-10-10. [x] = confirmed by the author; [~] = deferred, with the reason stated; [ ] = remaining steps after publication. `tools/publish_gate.py` enforces the mechanical half.

## 1. Authorship
- [x] Every item read as a student would; stems and options accepted as written.
- [x] Every distractor's "reveals" note accepted as describing a plausible route to that answer.
- [x] The bank reflects the author's item-writing judgment.
- [x] Attribution wording: "drafted with AI assistance, reviewed and verified by the author" (README, teacher guide, article, Zenodo).

## 2. Mathematics
- [x] `python code/01_validate.py` reports 0 errors (143 of 143 machine checks pass).
- [x] All 17 hand-review options in `docs/qa_report.txt` checked.
- [x] Keys on Forms A and B confirmed.

## 3. Diagnosis and teaching
- [x] All 64 catalog entries (name, "suggests", teaching move, probe) accepted.
- [x] Items whose options share one code (EQ02, EQ03, EQ04, EQ05, VAR01, VAR02, VAR05, DIST02, LIN05, NUM01, NUM02, NUM04, NUM05, FUNC02) kept as single-misconception items.
- [x] Hypothesized difficulty (1–3) accepted.
- [x] Form A / Form B split accepted for pre/post use.

## 4. Alignment and sources
- [~] DEFERRED to v1.1: item-level NAEP alignment (`docs/NAEP_ALIGNMENT.csv`, framework objective IDs and released-item comparison). v1.0 is aligned at the content-area level, and README and LIMITATIONS say so.
- [x] CCSS codes accepted.
- [x] References accepted by the author. Confirmed to exist by search: Booth et al. 2014, Cangelosi et al. 2013 (2026-10-09); Oehrtman et al. 2008, Vlassis 2004, Kirshner & Awtry 2004, Bell & Janvier 1981, Sadler 1998 (2026-10-10).
- [x] No item copies or closely resembles a TIMSS or NAEP released item.

## 5. Documents
- [x] README and LIMITATIONS accepted.
- [x] Article: opening scenario is hypothetical; no claim implies field data; 1,358 words (MTLT Focus limit 1,000–1,500).
- [~] At submission time: confirm the session kit's limits and dates on the live NCTM call (the kit is private and not part of the release).

## 6. Release
- [x] `./run_all.sh --final` regenerates every PDF and the article without DRAFT stamps.
- [x] `python tools/publish_gate.py . --allow-draft-in tools/ code/ docs/VERIFY_CHECKLIST.md article/ session/` reports 0 blockers.
- [ ] After the Zenodo deposit: add the DOI to CITATION.cff and README (PUBLISH_GUIDE step 3).
- [ ] After publishing: write the evidence log rows (`docs/evidence_log.csv`).
