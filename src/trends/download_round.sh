#!/bin/bash
# One round of Google Trends downloads: 9 requests (3 cities x requests A, B, C).
#
#   bash src/trends/download_round.sh              # all 9
#   bash src/trends/download_round.sh hk_A nyc_C   # only the ones named
#
# Each request is one call to the Ego lite browser (src/trends/download_round.mjs),
# in the one task Space "mwm-trends" (id saved in data/interim/trends/taskspace.txt).
# Between requests it waits 20 to 40 seconds.
# It stops the whole round at the first captcha, 429, consent wall, chart error or timeout.
# Exit codes: 0 = round finished, 2 = stopped because Google blocked or the page did not load,
#             3 = finished but at least one request failed its page check or had no data.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EGO="/Users/caydenauyang/.local/bin/ego-browser"
MJS="$ROOT/src/trends/download_round.mjs"
LOGDIR="$ROOT/data/interim/trends/round_logs"
mkdir -p "$LOGDIR" "$ROOT/data/raw/trends"
ROUND_ID="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LOGDIR/round_${ROUND_ID}.log"

ALL="hk_A hk_B hk_C nyc_A nyc_B nyc_C london_A london_B london_C"
if [ "$#" -gt 0 ]; then TODO="$*"; else TODO="$ALL"; fi

echo "round $ROUND_ID: $TODO" | tee -a "$LOG"
first=1
soft_fail=0
for pair in $TODO; do
  city="${pair%_*}"
  req="${pair#*_}"
  case " $ALL " in *" $pair "*) ;; *) echo "unknown request: $pair" | tee -a "$LOG"; exit 1;; esac
  if [ "$first" -eq 0 ]; then
    pause=$((20 + RANDOM % 21))
    echo "waiting ${pause}s" | tee -a "$LOG"
    sleep "$pause"
  fi
  first=0
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) start $pair" | tee -a "$LOG"
  out="$( { printf 'const MWM = { root: "%s", city: "%s", request: "%s" };\n' "$ROOT" "$city" "$req"; cat "$MJS"; } | "$EGO" nodejs 2>&1 )"
  echo "$out" | tail -n 6 | tee -a "$LOG"
  status="$(echo "$out" | grep -o 'MWM_STATUS=[a-z_]*' | tail -n 1 | cut -d= -f2)"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $pair status=${status:-none}" | tee -a "$LOG"
  case "${status:-none}" in
    ok) ;;
    no_data|check_failed) soft_fail=1 ;;
    *)
      echo "STOPPED at $pair (status=${status:-none}). Not trying the remaining requests this round." | tee -a "$LOG"
      echo "See data/interim/trends/page_checks.md and $LOG" | tee -a "$LOG"
      exit 2
      ;;
  esac
done
echo "round $ROUND_ID finished" | tee -a "$LOG"
if [ "$soft_fail" -eq 1 ]; then exit 3; fi
exit 0
