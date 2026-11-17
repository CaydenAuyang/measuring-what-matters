#!/bin/zsh
# The official validation step: the blind second coder (Gemini, after its daily quota resets at about 03:07 Eastern)
# labels the three validation sets from the real headlines and opening lines, re-labels 50 items in a fresh
# request, and the agreement is scored. Safe to run again: finished items are skipped.
# Usage: ./src/final_validation.sh [model]
cd "$(dirname "$0")/.."
PY=.venv/bin/python
MODEL=${1:-gemini-3.5-flash-lite}
for c in hk nyc london; do
  $PY -W ignore src/coder2_gemini.py --city $c --model $MODEL --role coder2 --rpm 5 || { echo "second coder stopped on $c (exit $?)"; exit 2; }
done
$PY -W ignore src/consistency_checks.py > /dev/null      # writes the 50-item re-label input if missing
$PY -W ignore src/coder2_gemini.py --city mixed --model $MODEL --role relabel --input data/interim/validation/relabel50_input.jsonl --output data/interim/validation/relabel50_labels.csv --rpm 5 || exit 2
$PY -W ignore src/consistency_checks.py | head -30
$PY -W ignore src/validation_score.py --role coder2 --status final
$PY - <<'PYEOF'
import json
s = json.load(open("data/public/validation_summary.json"))
for c, b in s["cities"].items():
    print(c, "failed first test:", b["failed_first_test"])
PYEOF
