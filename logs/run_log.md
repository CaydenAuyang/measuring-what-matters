# Run log (times in UTC)

- 2026-11-17T20:28Z Run started. setup.sh: all checks PASS.
- 2026-11-17T20:30Z Phase 0 done: folders, .venv (Python 3.12), caffeinate.
- 2026-11-17T20:31:07Z Phase 1: spec committed (e8d5f32). Pushed 20:31:23Z. Tag prereg-v1.
- 2026-11-17T20:32:59Z Internet Archive saved raw methodology.md (hash verified). 20:33:27Z saved source_inventory.md (hash verified).
- 2026-11-17T20:36:38Z deliverables/preregistration.md written. NO outcome data pulled before this line.
- 2026-11-17T20:44:25Z GDELT yearly extract started (12 queries, 3.07 TB estimated in total, about $19). First outcome-data query of the run.
- 2026-11-17T22:08:10Z Phase 3: full labeling with claude-haiku-5-5 under way (429,084 items). Headline check done. Provisional validation (third pass) for New York and London. Poster and source inventory delegated to subagents.
- 2026-11-17T22:16:53Z Labeling finished: 429,082 of 429,084 items labeled by claude-haiku-5-5 in 27 minutes, $26.71. All six rounds and both check rounds are complete, so the full pre-registered sample is used.
- 2026-11-17T23:25:51Z Review round done: 40 findings from an independent review subagent fixed in code, templates and records. Everything rebuilt with ./src/run_all.sh. Waiting for the midnight search download and the 3 AM second coder.
- 2026-11-18T05:15:03Z Google Trends round 2 downloaded after local midnight (9 files, 18 in total, 2 per request). Full rebuild ran clean. Search H1 slope 0.26 (0.19 to 0.42). Morning note template shortened.
- 2026-11-18T08:23:19Z Unattended chain: second coder scored, everything rebuilt (validation status in data/public/validation_summary.json).
