# Morning note for Cayden

Built {{generated_utc}} (UTC). Validation status: **{{text.validation_status}}**. If that word is "provisional", read section 3 first.

## 1. Print first

1. `poster/print_me.pdf`. US Letter, landscape, one page per poster piece. Print at 100% with no "fit to page", one side only.
2. `poster/layout_map.pdf`. One page. It shows where each piece goes: four rows of four pages, codes A1 to D4 in each page's corner.
3. `deliverables/defense_brief.md`. Read it before the showcase.

Card D2 says `[CAYDEN TO WRITE, 2 sentences]`. Write on the printed page, or edit `poster/poster_text.json` and run `.venv/bin/python src/poster.py`.

## 2. What finished

- Pre-registration, public before any outcome data (`deliverables/preregistration.md`).
- News: {{run.items_labeled_total|comma}} articles from {{counts.outlets_listed_total}} outlets labeled by one AI model (the full planned sample). Search: {{counts.search_requests}} Google Trends requests, {{counts.search_downloads_per_request}} download(s) each. Official data: {{counts.official_series_total}} series.
- Validation of about 300 articles per city by a second AI model (`data/public/validation_report.md`).
- The pre-registered tests and checks that could be run (`data/public/results.json`), poster kit, defense brief, dataset (`data/public/`), paper draft (`paper/`), framework, source inventory v2, deviations, AI-use log.
- `./src/run_all.sh` rebuilds everything from the saved files.

Spent: BigQuery {{run.bigquery_tb_billed}} TB, about ${{run.bigquery_cost_usd}} (cap {{run.bigquery_cap_tb}} TB). The paid language-model key about ${{run.anthropic_cost_usd}} (cap ${{run.language_model_cap_usd}}). The free-tier key ${{run.gemini_cost_usd|0f}}.

## 3. What failed or was cut, and why

{{run.morning_failures}}

Every change from the plan is in `deliverables/deviations.md`.

## 4. The three results in plain words

1. **H1, does attention follow official change?** News: {{verdicts.h1_news}}, slope {{main.news.h1.est|2f}} ({{main.news.h1.ci_low|2f}} to {{main.news.h1.ci_high|2f}}). Search: {{verdicts.h1_search}}, slope {{main.search.h1.est|2f}} ({{main.search.h1.ci_low|2f}} to {{main.search.h1.ci_high|2f}}). Without 2020 to 2022 the news slope is {{checks.without_covid.news.h1.est|2f}} ({{checks.without_covid.news.h1.ci_low|2f}} to {{checks.without_covid.news.h1.ci_high|2f}}). Say that out loud.
2. **H2, does attention react more to worsening?** News: {{verdicts.h2_news}}. Search: {{verdicts.h2_search}}.
3. **H3, is Safety the biggest gap?** News: {{verdicts.h3_news}}. Safety had the largest gap in {{h3.safety_rank.news.cities_where_safety_is_largest}} of {{counts.cities}} cities.

Dropped for low agreement between the two AI coders. Hong Kong: {{text.dropped_hk}}. New York: {{text.dropped_nyc}}. London: {{text.dropped_london}}.

## 5. Lines only you can fill in

- Poster card D2: `[CAYDEN TO WRITE, 2 sentences]`.
- `[CAYDEN TO CONFIRM: his own role in the question, codebook, design and interpretation]`: paper, data card, AI-use log. The defense brief lists every such line.
- `[CAYDEN TO CONFIRM: date of mentor approval, if any]`: `deliverables/preregistration.md`, `deliverables/deviations.md`.
- `[CAYDEN TO CONFIRM: license for the dataset]`: `data/public/README.md`, data card.
- The "What Cayden changed" column of `deliverables/ai_use_log.md`.
- Causes of disconnections and named events are proposed by AI. Confirm or change them.
- Optional: label `deliverables/optional_hand_check_50.csv`, then run `.venv/bin/python src/score_hand_check.py`.

## 6. The exact sentence to use when someone asks who coded the articles

"An AI language model labeled every article in the study. A second AI language model from a different company checked a sample without seeing the first labels. No person hand-coded any article in this run, so the agreement score shows that two AI coders agree, and it does not show that either matches a human reader."
