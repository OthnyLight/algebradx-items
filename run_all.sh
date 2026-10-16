#!/usr/bin/env sh
# Rebuild everything from items/*.yaml. Add --final only after the author's verification.
set -e
python code/01_validate.py
python code/02_export.py
python code/03_print.py "$@"
python calibration/make_demo_data.py
python calibration/calibrate.py calibration/demo/responses_SYNTHETIC.csv --out calibration/demo/output
python code/04_design_check.py
node code/05_article.js "$@"
