# Calibrating AlgebraDx on your own students

The difficulty levels printed in the teacher guide are the author's hypotheses. Real difficulty and discrimination depend on your students and your curriculum, so this kit lets a school or district calibrate the items locally. **No data is sent anywhere.** The project collects no student data.

## What you need

- Python 3.9 or newer. Nothing else is required: `calibrate.py` uses only the standard library.
- Completed paper forms (A, B, or both).
- About 30 minutes of data entry per 100 students.

## Steps

1. **Enter responses.** Copy `response_template.csv`. Put one row per student with a local ID (not a name), the form letter, and the letter each student circled for q1–q20. Leave a cell blank if the student skipped the question.
2. **Run the script** from the project folder:
   ```
   python calibration/calibrate.py my_responses.csv --out my_results
   ```
3. **Read `form_summary.txt` first.** It gives the mean, the spread and KR-20 reliability, and explains each statistic.
4. **Act on `class_misconceptions.csv`.** It lists every misconception code that two or more of a student's answers point to, how many students show it, and the teaching move. Start re-teaching with the top rows.
5. **Use `student_profiles.csv` for small groups.** It shows each student's strand subscores, every code they chose, and the codes flagged as patterns.
6. **Review `item_stats.csv` once you have about 100 students.** Look at the `flags` column for items that are very hard, very easy, weakly discriminating, or have a wrong option that attracts strong students. A flagged item is worth a second look, not automatic removal.

## Reading a single student's answers

A single wrong answer is a hypothesis about the student's thinking, not a diagnosis. On a 20-item form, only some misconception codes appear on two or more items. For those codes the script can flag a *pattern*. For the others, use the one-line **probe** question for that code (Appendix A of the teacher guide) to confirm before re-teaching.

## Sharing results back (optional)

If you want to help improve the bank, you can share **item-level statistics only** (`item_stats.csv`: p-values, discrimination and choice rates, with no student rows) by opening an issue on the project repository. Never share `student_profiles.csv` or raw responses outside your school.

## Testing the script

`make_demo_data.py` creates a **synthetic** response file in `calibration/demo/` so you can see what the outputs look like. Those numbers come from a simulation and say nothing about real students.
