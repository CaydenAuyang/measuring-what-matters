# Measuring What Matters: public dataset

Cayden Auyang. AI drafted and I reviewed.

Monthly public attention and official statistics for Hong Kong, New York City and London. Built for the study "Measuring What Matters: when a city's problems get worse, does public attention follow?" by Cayden Auyang (Pomfret School, fall 2026).

The whole dataset was produced in one automated run on November 17 and 18, 2026. An AI agent carried out a plan that was posted publicly before any outcome data were collected (commit `e8d5f32`, tag `prereg-v1`, in the repository at https://github.com/CaydenAuyang/measuring-what-matters).

## What is here

| File | What it holds |
| :-- | :-- |
| `news_attention_monthly.csv` | Each category's share of local news coverage, by city and month, 2015-02 to 2026-10. |
| `search_attention_monthly.csv` | Each category's share of Google search interest, by city and month, 2004-01 to 2026-10. |
| `official_series.csv` | 45 official series (the main and backup indicators), at their own frequency, with break flags. The file also holds 2 extra series that no test uses (see `codebook.md`). |
| `official_series_meta.json` | One entry per official series: source addresses, how it was built, coverage, breaks, caveats. |
| `yearly_changes.csv` | The matched year-over-year changes that the analysis uses, for every city, category and source. |
| `results.json` | Every number reported in the paper and on the poster. |
| `validation_summary.json`, `validation_report.md` | Agreement between the two AI coders, by city and category. |
| `labeling_card.md` | The exact model, settings and prompt used to label the news. |
| `data_card.md` | What the dataset is, how it was made, and its limits. |
| `codebook.md` | Every column of every file. |
| `sample_sizes.csv`, `sample_sizes_by_city_month.csv` | How many articles GDELT held, how many passed the city filter, how many were sampled and labeled, for every outlet and month. |
| `outlets.csv`, `search_term_sets.json` | The pre-registered outlet lists and search terms. |
| `synthetic_test_results.json` | Tests of the analysis code on made-up series with known answers. |

There is no article-level text in this dataset. It holds monthly shares, official series, and counts.

## Counts

| What | Count |
| :-- | --: |
| Cities | 3 |
| Outlets in the main panels | 21 |
| Outlets on the full lists | 68 |
| GDELT records pulled for the listed outlets | 6,363,992 |
| Articles left after the city filters and duplicate removal | 2,466,900 |
| Articles labeled, main panels | 286,155 |
| Articles labeled, main panels and check lists | 429,082 |
| Months of news | 141 (2015-02 to 2026-10) |
| Official series (main and backup) | 45 |
| Official values | 11,948 |
| Months of search data | 274 (2004-01 to 2026-10) |
| Search downloads per request | 2 |

## How to rebuild it

`./src/run_all.sh` rebuilds every result from the saved raw files and saved model outputs. The raw files and the article-level sample are not in the public repository. The code that fetched them is in `src/`.

## Read these limits before using the data

1. An AI language model labeled every article. A second AI language model from a different family checked a sample. No person hand-coded any article. See `validation_report.md`.
2. Categories whose agreement fell below 0.61 in a city are not analyzed for that city. The shares are still in the file. Check `validation_summary.json` before using a category.
3. Hong Kong's news series for 2015 to 2019 rests on one outlet if the headline-check rule applied. See `validation_report.md`.
4. Search data cover the New York media market and England, which are wider than the two cities.
5. Official statistics are a benchmark. They are not ground truth.
6. Every change from the pre-registered plan is in `deliverables/deviations.md`.

[CAYDEN TO CONFIRM: license for the dataset]
