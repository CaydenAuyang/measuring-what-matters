#!/bin/zsh
# Commit and push the public parts of the study. Private files, raw data, interim data and anything holding
# article-level text are kept out by .gitignore.
cd "$(dirname "$0")/.."
MSG=${1:-"Results, dataset, poster kit and documents"}
git add -A .gitignore README.md src data/public deliverables paper poster logs/decisions.md logs/run_log.md logs/bigquery_costs.csv logs/morning_failures.md data/manifest.csv 2>/dev/null
# safety checks: no key material and none of the private files may be staged
if git diff --cached --name-only | grep -E "(^|/)\.env|AGENT_PROMPT|CLAUDE\.md|STATE\.md|BLOCKED\.md|setup\.sh|data/raw/|data/interim/|optional_hand_check_50|\.jsonl$|MORNING\.md" ; then
  echo "REFUSING TO COMMIT: a private file is staged"; git reset -q; exit 3
fi
if git diff --cached | grep -E "sk-ant-[A-Za-z0-9]|AIza[0-9A-Za-z_-]{30}" > /dev/null; then
  echo "REFUSING TO COMMIT: something that looks like an API key is staged"; git reset -q; exit 3
fi
git commit -q -m "$MSG" || { echo "nothing to commit"; exit 0; }
git push -q origin main && echo "pushed $(git log --oneline | head -1)"
