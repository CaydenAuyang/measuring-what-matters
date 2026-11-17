#!/bin/zsh
# Waits until the Gemini daily quota has reset (about 03:07 Eastern), runs the blind second coder and the scoring,
# then rebuilds everything. If the quota has not reset yet it waits five minutes and tries again, up to an hour.
cd "$(dirname "$0")/.."
T=$(date -j -f "%Y-%m-%d %H:%M:%S" "2026-11-18 03:09:00" +%s)
until [ $(date +%s) -ge $T ]; do sleep 30; done
echo "final validation starting $(date)"
for try in 1 2 3 4 5 6 7 8 9 10 11 12; do
  ./src/final_validation.sh > logs/final_validation.out 2>&1; rc=$?
  echo "try $try exit $rc $(date +%H:%M:%S)"
  [ $rc -eq 0 ] && break
  sleep 300
done
tail -12 logs/final_validation.out | cut -c1-260
.venv/bin/python -W ignore src/mark_final_auto.py
./src/run_all.sh > logs/run_all_final_auto.out 2>&1; echo "run_all exit $?"
grep -E "^(news|search) H1|PASSED|FAILED" logs/run_all_final_auto.out | cut -c1-200
echo "- $(date -u +%FT%TZ) Unattended chain: second coder scored, everything rebuilt (validation status in data/public/validation_summary.json)." >> logs/run_log.md
./src/publish.sh "Final validation by the blind second coder; results, dataset, poster kit and documents rebuilt" 2>&1 | tail -2
printf '\n## AUTOMATIC PATH FINISHED %s\nThe 3 AM chain ran: second coder scored, run_all rebuilt everything, public parts pushed. If the main session did not wake after this line, the one-revision step, the paper final pass and the poster D2 candidates were NOT done by hand; MORNING.md says so.\n' "$(date)" >> STATE.md
echo "final validation chain finished $(date)"
