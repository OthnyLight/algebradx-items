# Build spec: AlgebraDx Open Diagnostic Item Bank (P3)

```
PROJECT:        AlgebraDx Open Diagnostic Item Bank, v1.0.
                Archetypes: open dataset / benchmark-style item bank (primary),
                technical report (teacher guide), analysis-free practitioner
                article, presentation package (NCTM session).

QUESTION:       Which specific algebra-readiness misconceptions does a grade 9-12
                student hold, and what should the teacher do about each one on Monday?

SOURCES:        No student data. No copied items. Every item is original.
                - NAEP 2026 Mathematics Framework, Algebra content area (NAGB),
                  https://www.nagb.gov/naep/mathematics/naep-math-assessment-framework.html
                  used for subtopic alignment only.
                - NAEP Questions Tool released grade 12 items
                  (https://www.nationsreportcard.gov/nqt/), referenced by item ID only
                  for an alignment check; no NAEP text is reproduced. NAGB policy
                  (adopted 2002-05-18) says released items are to be widely
                  distributed, but it does not state a license, so we don't copy them.
                - TIMSS items: NOT used. IEA terms require prior notice for use in
                  assessments or learning materials (timss.bc.edu/Copyright/,
                  accessed 2026-10-09).
                - Common Core State Standards for Mathematics, High School Algebra
                  and Functions, plus grade 6-8 Expressions & Equations (standard
                  codes only).
                - Published misconception research (see docs/REFERENCES.md), cited
                  for the distractor rationales.

UNIT:           Item (stem + 4 options). Each distractor is coded to one
                misconception from a controlled catalog.

MEASURES:       Per item: strand, skill, CCSS codes, NAEP subtopic, hypothesized
                difficulty (1-3), key, per-distractor misconception code + what it
                reveals, teaching move. Per bank: counts by strand/difficulty,
                misconception coverage. Mechanical check that the key is correct and
                every distractor is wrong (exact rational arithmetic / random-point
                identity testing).
                Calibration (done by schools on their own students, never by us):
                p-value, corrected point-biserial, distractor selection rates,
                misconception profile per student, KR-20 for the form.

OUTPUTS:        items/items.yaml               source of truth (40 items)
                items/misconceptions.yaml      catalog with teaching moves
                exports/items.csv, items.json  machine-readable
                exports/teacher_guide.pdf      item-by-item diagnosis + moves
                exports/student_form_A.pdf, student_form_B.pdf  printable forms
                exports/answer_key.csv         key + misconception map for scoring
                calibration/calibrate.py       schools score & calibrate locally
                calibration/response_template.csv, CALIBRATION_GUIDE.md
                docs/qa_report.txt, docs/stats.json
                article/practitioner_article.docx   (MTLT-style)
                session/NCTM_session_kit.md + session slides outline

VENUES:         GitHub release -> Zenodo DOI (dataset) -> practitioner article
                (NCTM Mathematics Teacher: Learning and Teaching PK-12) -> NCTM
                session (2027 Orlando if the window is open, otherwise the
                2028 Annual or a Spring Conference) and Indiana Council of
                Teachers of Mathematics.

VERIFY POINTS:  1. Authorship: items were drafted with AI assistance from the
                   misconception literature; the author must rewrite/approve every
                   item before the bank can be called his. The README and article
                   disclose this.
                2. Every key and every distractor rationale (mechanically checked
                   for correctness, but the diagnosis is a judgment).
                3. Every teaching move.
                4. NAEP alignment worksheet: author fills released-item IDs.
                5. Every reference in docs/REFERENCES.md checked against the source.
                6. NCTM call dates and limits confirmed on nctm.org.

LICENSE:        Items, guides, article: CC BY 4.0 (author chose attribution over CC0).
                Code: MIT.

ASSUMPTIONS:    Grades 9-12 "readiness" = the prerequisite and early-algebra
                ideas that predict success in Algebra I/II, not the full HS
                curriculum. 8 strands x 5 items = 40 items for v1.0. Multiple-choice
                only (distractors are the diagnostic instrument). Two parallel
                20-item forms (A/B) for pre/post use.
```
