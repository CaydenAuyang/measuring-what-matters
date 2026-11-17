# Morning note for Cayden

Built {{generated_utc}} (UTC). Validation status: **{{text.validation_status}}**. If that word is "provisional", read section 3 first.

## 1. Print first

1. `poster/print_me.pdf`. 16 pages, US Letter, landscape. Print at 100% with no "fit to page", one side only.
2. `poster/layout_map.pdf`. One page. It shows where each piece goes: four rows of four pages, codes A1 to D4 in each page's corner.
3. `deliverables/defense_brief.md`. Read it before the showcase.

Card D2 says `[CAYDEN TO WRITE, 2 sentences]`. Write on the printed page, or edit `poster/poster_text.json` and run `.venv/bin/python src/poster.py`.

## 2. What finished

- Pre-registration: public on GitHub and the Internet Archive before any outcome data (`deliverables/preregistration.md`).
- News: {{counts.gdelt_rows_listed_outlets|comma}} GDELT records from {{counts.outlets_listed_total}} outlets, {{run.items_labeled_total|comma}} articles labeled by one AI model. Full planned sample.
- Validation: about 300 articles per city coded blind by a second AI model. Results are in `data/public/validation_report.md`.
- Official data: {{counts.official_series_total}} series for the three cities.
- Search: {{counts.search_requests}} Google Trends requests, {{counts.search_downloads_per_request}} download(s) of each.
- Analysis: the four pre-registered pooled tests, the 48 pair results, lead and lag, the disconnection list, and every check. All numbers are in `data/public/results.json`.
- Poster kit, defense brief, dataset package (`data/public/`), paper draft (`paper/paper.md`, `paper/paper.docx`), Civic Signal Framework, source inventory version 2, deviations, AI-use log.
- One command rebuilds everything from the saved files: `./src/run_all.sh`.

Money: BigQuery {{run.bigquery_tb_billed}} TB (about ${{run.bigquery_cost_usd}}, cap 8 TB). Anthropic API about ${{run.anthropic_cost_usd}} (cap $100). Gemini $0 (free tier).

## 3. What failed or was cut, and why

{{run.morning_failures}}

Every change from the plan is in `deliverables/deviations.md`.

## 4. The three results in plain words

1. **Does attention follow official change (H1)?** {{verdicts.h1_news_sentence}} {{verdicts.h1_search_sentence}}
2. **Does attention react more to worsening (H2)?** {{verdicts.h2_news_sentence}} {{verdicts.h2_search_sentence}}
3. **Is Safety the biggest gap (H3)?** {{verdicts.h3_news_sentence}}

One thing to say with result 1: without the years 2020 to 2022 the news slope is {{checks.without_covid.news.h1.est|2f}} (95% interval {{checks.without_covid.news.h1.ci_low|2f}} to {{checks.without_covid.news.h1.ci_high|2f}}).

Categories dropped because the two AI coders agreed too little. Hong Kong: {{text.dropped_hk}}. New York: {{text.dropped_nyc}}. London: {{text.dropped_london}}.

## 5. Lines only you can fill in

- Poster card D2: `[CAYDEN TO WRITE, 2 sentences]`. Two candidate sentences are printed under it.
- `[CAYDEN TO CONFIRM: his own role in the question, codebook, design and interpretation]` in the paper's AI-use disclosure, the data card and the AI-use log.
- `[CAYDEN TO CONFIRM: date of mentor approval, if any]` in `deliverables/preregistration.md` and `deliverables/deviations.md`.
- `[CAYDEN TO CONFIRM: license for the dataset]` in `data/public/README.md` and the data card.
- The "What Cayden changed" column of `deliverables/ai_use_log.md`.
- The causes of disconnections in the paper are proposed by AI. Confirm or change them.
- Optional: `deliverables/optional_hand_check_50.csv`. Label the 50 items yourself, then run `.venv/bin/python src/score_hand_check.py`.

## 6. The exact sentence to use when someone asks who coded the articles

"An AI language model labeled every article. A second AI model from a different company checked about 900 of them without seeing the first labels. No person hand-coded any article in this run, so the agreement score shows that two AI coders agree, and it does not show that either matches a human reader."
