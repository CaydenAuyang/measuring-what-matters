# Measuring What Matters

**When a city's problems get worse, does public attention follow?**

A fall 2026 independent study by Cayden Auyang at Pomfret School. It compares official statistics with local news coverage and Google search interest for Hong Kong, New York City and London.

*This page was built from the results file generated at {{generated_utc}} (UTC). Validation status: {{text.validation_status}}.*

## Read this first

An AI agent ran every stage of this study in one unattended session on November 17 and 18, 2026. An AI language model labeled the news articles. A second AI language model from a different model family checked a sample of the labels. No person hand-coded any article, and no person reviewed the numbers before they were posted here. `deliverables/deviations.md` lists every difference from the plan. `deliverables/ai_use_log.md` says what AI did.

## The pre-registration

The `spec/` folder holds the plan for the study:

- `spec/methodology.md`: research questions, hypotheses, codebook, indicators, analysis plan, and Appendices A (outlet lists), B (search terms) and C (indicator direction and transformation).
- `spec/source_inventory.md`: the sources and their known limits.
- `spec/fall_proposal.md`: the original course proposal.

These files were posted here on **November 17, 2026** (commit `e8d5f32`, tag `prereg-v1`), before any outcome data were collected. Outcome data means what articles said, what any official indicator's values are, and what Google Trends shows. The only data pulled before that commit were the outlet and headline counts described in the methodology's feasibility check and Appendix A. The files in `spec/` have not been edited since. `deliverables/preregistration.md` records when and where the plan was posted and archived.

The plan was written for posting on the Open Science Framework in October. It was posted here, later than planned, and that change is recorded as a deviation.

## What was found

The plan has four main tests: H1 and H2, each for news and for search. Slopes are in standard deviations of attention change per standard deviation of official change.

| Hypothesis | News | Search |
| :-- | :-- | :-- |
| H1: attention rises when the official measure worsens, weakly | {{verdicts.h1_news}}, slope {{main.news.h1.est|2f}} ({{main.news.h1.ci_low|2f}} to {{main.news.h1.ci_high|2f}}) | {{verdicts.h1_search}}, slope {{main.search.h1.est|2f}} ({{main.search.h1.ci_low|2f}} to {{main.search.h1.ci_high|2f}}) |
| H1 without 2020 to 2022 | slope {{checks.without_covid.news.h1.est|2f}} ({{checks.without_covid.news.h1.ci_low|2f}} to {{checks.without_covid.news.h1.ci_high|2f}}) | slope {{checks.without_covid.search.h1.est|2f}} ({{checks.without_covid.search.h1.ci_low|2f}} to {{checks.without_covid.search.h1.ci_high|2f}}) |
| H2: attention reacts more to worsening than to improving | {{verdicts.h2_news}} | {{verdicts.h2_search}} |
| H3: Safety shows the largest gap in at least two of three cities | {{verdicts.h3_news}} | {{verdicts.h3_search}} |

The intervals are 95% intervals from a block bootstrap. In a test on unrelated made-up series, {{synthetic_tests.false_positive_check.intervals_that_wrongly_excluded_zero}} of {{synthetic_tests.false_positive_check.trials}} intervals wrongly excluded zero, so these intervals are likely too narrow. The paper (`paper/paper.md`) has the full results and limits.

## Where things are

| Path | What it holds |
| :-- | :-- |
| `spec/` | The pre-registered plan. |
| `data/public/` | The dataset: monthly attention shares, official series, yearly changes, every reported number (`results.json`), the validation report, the data card, the labeling card and the codebook. Start with `data/public/README.md`. |
| `paper/` | The paper draft (`paper.md` and `paper.docx`). |
| `poster/` | The poster kit (`print_me.pdf` and `layout_map.pdf`). |
| `deliverables/` | Deviations from the plan, the AI-use log, the pre-registration record, the defense brief, the civic signal framework and source inventory v2. |
| `src/` | All of the code. |
| `logs/` | The decisions log, the run log and the BigQuery cost log. |

## Rebuilding the results

`./src/run_all.sh` rebuilds every result from the saved raw files and the saved model outputs. It downloads nothing and calls no model. The raw files and the article-level sample are not in this repository, because article-level text is not published. The code that fetched and labeled them is in `src/`.
