#!/bin/zsh
# Only used if a revised category passes its retest. Labels the whole sample again with the revised prompt
# (same model, same settings, same batch size), into a new file. Resumable: finished items are skipped.
# The swap of label files is done by src/swap_revised_labels.py after the new file has been checked.
cd "$(dirname "$0")/.."
.venv/bin/python -W ignore src/labeler_claude.py \
  --items data/interim/labels/items_ordered.parquet \
  --out data/interim/labels/labels_main_revised.jsonl \
  --system src/prompt_first_coder_revised.txt \
  --workers 40 --budget 45 \
  --task "full relabel with the revised codebook, claude-haiku-5-5" \
  --stats data/interim/labels/full_run_revised_stats.json
echo "relabel exit $?"
