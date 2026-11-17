# Data card

| Field | Value |
| :-- | :-- |
| Name | Measuring What Matters: monthly attention and official series for three cities |
| Version | Built {{generated_utc}} (UTC) |
| Author | Cayden Auyang, Pomfret School. Produced by an AI agent run (Claude Code, model `claude-fable-5-2`) following his pre-registered plan. [CAYDEN TO CONFIRM: his own role in the question, codebook, design and interpretation] |
| Cities | Hong Kong, New York City, London |
| Categories | Safety, Economy, Housing, Transport, Environment, Health, Education, Cost of Living (compared with official data). Governance, Culture, Technology, Community (attention only). |
| Time span | News {{counts.news_first_month}} to {{counts.news_last_month}}. Search {{counts.search_first_month}} to {{counts.search_last_month}}. Official series from 2004 or earlier where the source allows, to 2026. |
| Unit | One row per city, category and month (attention). One row per series and period (official). |

## Sources

- **News:** GDELT Global Knowledge Graph 2.0, queried on BigQuery ({{run.bigquery_tb_billed}} TB billed in total, about ${{run.bigquery_cost_usd}}). {{counts.gdelt_rows_listed_outlets|comma}} records from {{counts.outlets_listed_total}} listed outlets. {{counts.articles_after_city_filter|comma}} articles left after the city filters and duplicate removal.
- **Search:** Google Trends, downloaded from the website as CSV files. {{counts.search_requests}} requests, {{counts.search_downloads_per_request}} download(s) of each.
- **Official statistics:** government and official bodies in each city. Addresses for every series are in `official_series_meta.json`.

## How the news shares were made

1. Outlets: a fixed main panel per city ({{counts.outlets_main_panel.hk}} in Hong Kong, {{counts.outlets_main_panel.nyc}} in New York, {{counts.outlets_main_panel.london}} borough papers in London), set before any data were pulled.
2. City filter: Hong Kong articles must carry a Hong Kong location tag. New York articles must carry a city or borough tag. London papers' national wire stories are dropped.
3. Sample: a seeded random draw of up to 333 articles per outlet per month in Hong Kong and New York and up to 66 per paper per month in London. {{run.items_sampled_total|comma}} items were sampled. {{run.items_no_input|comma}} had nothing for the model to read and were left out.
4. Labels: {{run.items_labeled_total|comma}} items were labeled by `claude-haiku-5-5` (Anthropic API), 50 items per request, with the frozen prompt in `labeling_card.md`. The model read the headline words in each article's web address plus GDELT's theme tags. Cost: about ${{run.anthropic_cost_usd}} in total, ${{run.cost_per_item_usd|raw}} per item in the cost test.
5. Shares: each category's share per outlet per month, averaged across outlets with equal weights. `neg_share` counts only articles labeled with negative tone.

## Validation

- Second coder: `gemini-3.5-flash-lite` (Google Gemini API), blind to the first coder, reading each article's real headline and opening lines from the live page or the Internet Archive.
- Third pass: `gemini-3.1-flash-lite`, same text.
- Status of the numbers below: {{text.validation_status}}.

{{tables.validation_kappa}}

- First coder against a larger model of the same family (`claude-sonnet-5-5`) on {{cmp.n}} items: kappa {{cmp.kappa_category|2f}}.
- Headline check (2020 onward, same model): labels from address words plus theme tags against labels from the real stored headline. Hong Kong items with headline words: kappa {{hc.cities.hk.with_headline_words.kappa|2f}}. Hong Kong items with theme tags alone: kappa {{hc.cities.hk.theme_tags_only.kappa|2f}}. {{hc.rule.text}}

This is agreement between AI coders. It is not a check against a human reader.

## Known limits

- Theme-tag-only labels are weak. Outlets with number-only web addresses are affected most.
- GDELT's Hong Kong coverage leans on a few outlets. The London panel is borough papers with no citywide outlet. GDELT rarely tags the Bronx.
- The South China Morning Post's site challenged automated requests, so its validation items rest on headlines alone and only from 2020.
- London has no Health series. New York's Health series starts in 2020.
- Google Trends values come from a sample of searches and change between downloads.
- Break periods (COVID, method changes, real events) are flagged, not removed.

## Files, columns and checks

See `codebook.md`. Shares in `news_attention_monthly.csv` sum to 1 across the thirteen labels for every city, month and variant.

[CAYDEN TO CONFIRM: license for the dataset]
