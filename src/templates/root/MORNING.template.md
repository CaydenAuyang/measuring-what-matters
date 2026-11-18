# Morning note for Cayden

Built {{generated_utc}} UTC. Validation: **{{text.validation_status}}**.

## 1. Print first

1. `poster/print_me.pdf`: US Letter, landscape, 100%, one side.
2. `poster/layout_map.pdf`: where pages A1 to D4 go on the board.
3. `deliverables/defense_brief.md`: read it before the showcase.

## 2. What finished

Pre-registration (public before any outcome data). {{run.items_labeled_total|comma}} articles labeled by one AI model. {{counts.official_series_total}} official series. Google Trends, {{counts.search_downloads_per_request}} downloads per request. AI validation of about 300 articles per city. All pre-registered tests, poster kit, dataset, paper draft, framework, source inventory v2, deviations, AI-use log. `./src/run_all.sh` rebuilds everything. Spent about ${{run.bigquery_cost_usd}} on BigQuery and ${{run.anthropic_cost_usd}} on the paid model key.

## 3. What failed or was cut (details: `deliverables/deviations.md`)

{{run.morning_failures}}

## 4. The three results

1. **H1, attention follows official change.** News: {{verdicts.h1_news}}, slope {{main.news.h1.est|2f}} ({{main.news.h1.ci_low|2f}} to {{main.news.h1.ci_high|2f}}). Search: {{verdicts.h1_search}}, {{main.search.h1.est|2f}} ({{main.search.h1.ci_low|2f}} to {{main.search.h1.ci_high|2f}}). Without 2020 to 2022 the news slope is {{checks.without_covid.news.h1.est|2f}} ({{checks.without_covid.news.h1.ci_low|2f}} to {{checks.without_covid.news.h1.ci_high|2f}}). Say that out loud.
2. **H2, attention reacts more to worsening.** News: {{verdicts.h2_news}}. Search: {{verdicts.h2_search}}.
3. **H3, Safety has the biggest gap.** News: {{verdicts.h3_news}}. Safety was largest in {{h3.safety_rank.news.cities_where_safety_is_largest}} of {{counts.cities}} cities.

Dropped for low agreement between the AI coders. Hong Kong: {{text.dropped_hk}}. New York: {{text.dropped_nyc}}. London: {{text.dropped_london}}.

## 5. Lines only you can fill in

- Poster card D2: `[CAYDEN TO WRITE, 2 sentences]`.
- Every `[CAYDEN TO CONFIRM: ...]` line: your role, mentor approval date, dataset license, what the results mean for OurCityHealth. The defense brief lists them.
- The "What Cayden changed" column of `deliverables/ai_use_log.md`.
- AI proposed the causes of disconnections and the named events. Confirm or change them.
- Optional: label `deliverables/optional_hand_check_50.csv`, then run `src/score_hand_check.py`.

## 6. The exact sentence for who coded the articles

"An AI language model labeled every article in the study. A second AI language model from a different company checked a sample without seeing the first labels. No person hand-coded any article in this run, so the agreement score shows that two AI coders agree, and it does not show that either matches a human reader."
