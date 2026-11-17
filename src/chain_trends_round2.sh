#!/bin/zsh
# Waits until just after local midnight, takes Google Trends download round 2, rebuilds the search shares, then rebuilds everything.
cd "$(dirname "$0")/.."
T=$(date -j -f "%Y-%m-%d %H:%M:%S" "2026-11-18 00:03:00" +%s)
until [ $(date +%s) -ge $T ]; do sleep 30; done
echo "round 2 starting $(date)"
bash src/trends/download_round.sh > logs/trends_round2.out 2>&1; echo "download exit $?"
.venv/bin/python -I src/trends/build_trends.py >> logs/trends_round2.out 2>&1; echo "build exit $?"
ls data/raw/trends/*.csv | grep -v manifest | wc -l
./src/run_all.sh > logs/run_all_after_trends.out 2>&1; echo "run_all exit $?"
grep -E "^(news|search) H1|PASSED|FAILED" logs/run_all_after_trends.out | cut -c1-200
echo "round 2 chain finished $(date)"
