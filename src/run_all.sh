#!/bin/zsh
# Measuring What Matters: rebuild every result from the saved raw data and saved model outputs, with one command.
# It does not download anything, call any language model, or run any BigQuery query.
# Usage: ./src/run_all.sh
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python
echo "== 1. Tests of the analysis code on made-up series"
$PY -W ignore src/test_synthetic.py | tail -1
echo "== 2. Official indicators from saved raw files"
for c in hk nyc london; do $PY -W ignore src/official/$c.py > logs/official_rebuild_$c.out 2>&1 && echo "   $c ok"; done
echo "== 3. Search attention from saved Google Trends files"
$PY -I src/trends/build_trends.py > logs/trends_rebuild.out 2>&1 && echo "   trends ok"
echo "== 4. Headline check and validation scoring"
$PY -W ignore src/headline_check.py > logs/headline_check_rebuild.out 2>&1
if [ -f data/interim/validation/hk_coder2_labels_v1.csv ] && [ -f data/interim/validation/nyc_coder2_labels_v1.csv ] && [ -f data/interim/validation/london_coder2_labels_v1.csv ]; then
  [ -f src/consistency_checks.py ] && $PY -W ignore src/consistency_checks.py > logs/consistency_rebuild.out 2>&1
  $PY -W ignore src/validation_score.py --role coder2 --status final | tail -6
else
  echo "   second coder has not run yet: scoring against the third pass (provisional)"
  $PY -W ignore src/validation_score.py --role thirdpass --status provisional | tail -6
fi
echo "== 5. News attention index"
$PY -W ignore src/build_index.py | tail -1
echo "== 6. Analysis"
$PY -W ignore src/analysis.py | tail -3
echo "== 7. Dataset package, run facts and documents"
$PY -W ignore src/package_dataset.py > logs/package_rebuild.out 2>&1
$PY -W ignore src/run_facts.py > /dev/null
$PY -W ignore src/build_public_docs.py
$PY -W ignore src/build_root_docs.py
$PY -W ignore src/build_manifest.py
[ -f deliverables/source_inventory_v2.md ] && $PY -W ignore src/patch_inventory.py
[ -f src/build_docs.py ] && $PY -W ignore src/build_docs.py
[ -f src/build_paper.py ] && $PY -W ignore src/build_paper.py | tail -2
echo "== 8. Poster"
[ -f src/poster.py ] && $PY -W ignore src/poster.py | tail -2 && $PY -W ignore src/poster_check.py | tail -2
echo "== done: $(date)"
