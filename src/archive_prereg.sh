#!/bin/zsh
# Retries Internet Archive saves for pre-registration pages that did not save on the first try.
# Usage: src/archive_prereg.sh   (writes logs/archive_prereg.log; stops when all are saved or after 40 tries)
cd "$(dirname "$0")/.." || exit 1
H=e8d5f32e0c64a43b752d27fb76c4f70a099cf3a6
URLS=(
  "https://github.com/CaydenAuyang/measuring-what-matters"
  "https://github.com/CaydenAuyang/measuring-what-matters/tree/prereg-v1"
  "https://raw.githubusercontent.com/CaydenAuyang/measuring-what-matters/$H/spec/fall_proposal.md"
  "https://raw.githubusercontent.com/CaydenAuyang/measuring-what-matters/$H/README.md"
)
typeset -A DONE
for try in {1..40}; do
  left=0
  for u in $URLS; do
    [ -n "${DONE[$u]}" ] && continue
    R=$(curl -s -m 170 -A "Mozilla/5.0 (research-archiver)" -o /dev/null -D - "https://web.archive.org/save/$u" | grep -iE "^(HTTP|location)" | tr -d '\r' | tr '\n' ' ')
    echo "$(date -u +%FT%TZ) try=$try $u => $R" >> logs/archive_prereg.log
    if echo "$R" | grep -q "location: https://web.archive.org/web/"; then DONE[$u]=1; else left=$((left+1)); fi
    sleep 20
  done
  [ $left -eq 0 ] && { echo "$(date -u +%FT%TZ) ALL SAVED" >> logs/archive_prereg.log; exit 0; }
  sleep 300
done
echo "$(date -u +%FT%TZ) GAVE UP with $left unsaved" >> logs/archive_prereg.log
