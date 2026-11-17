# AI-use log

Every AI tool and model used in the run of November 17 and 18, 2026, with exact versions. The last column is for Cayden.

| Date | Tool and exact model | Task | What Cayden changed |
| :-- | :-- | :-- | :-- |
| Nov 17 to 18, 2026 | Claude Code (Anthropic), main agent, model `claude-fable-5-2` | Ran the whole study from Cayden's written instructions and pre-registered plan: set up the project, posted the pre-registration, wrote all code in `src/`, pulled GDELT data on BigQuery, applied the city filters and drew the samples, ran and monitored the labeling, built the validation sets, wrote and ran the analysis, checked the outputs, wrote the deviations file, the labeling card, the data card, this log and `MORNING.md`, and edited every other document. | |
| Nov 17, 2026 | Claude Code subagents, model `claude-fable-5-2` (three agents, one per city; the Hong Kong agent used one helper agent of the same kind) | Found, downloaded and built the official indicator series for Hong Kong, New York City and London (`src/official/*.py`, `data/interim/official/`). | |
| Nov 17 to 18, 2026 | Claude Code subagent, model `claude-fable-5-2`, driving the Ego lite browser | Downloaded the Google Trends CSV files and wrote the Trends build script (`src/trends/`). | |
| Nov 17 to 18, 2026 | Claude Code subagents, model `claude-fable-5-2` | Built the poster generator and its checks (`src/poster.py`, `src/poster_check.py`). Drafted the research paper template, the defense brief, the Civic Signal Framework and the source inventory, version 2. The main agent reviewed and edited them. | |
| Nov 17, 2026 | Anthropic API, `claude-haiku-5-5` | First coder. Labeled {{run.items_labeled_total|comma}} sampled news articles with one category and one tone each, from headline words in the web address plus GDELT theme tags. Also labeled {{hc.n_items|comma}} articles from their real stored headlines for the headline check. Total cost about ${{run.anthropic_cost_usd}}. | |
| Nov 17, 2026 | Anthropic API, `claude-sonnet-5-5` | Labeled 300 of the first 2,000 items once, to check the first coder against a larger model (kappa {{cmp.kappa_category|2f}}). Not used for any result. | |
| Nov 18, 2026 | Google Gemini API, `gemini-3.5-flash-lite` (version `3.5-flash-lite-07-2026`) | Second coder. Labeled the validation sets blind, from each article's real headline and opening lines, and judged whether each article is about the city. Re-labeled 50 items in a fresh request. | |
| Nov 17, 2026 | Google Gemini API, `gemini-3.1-flash-lite` (version `3.1-flash-lite-05-2026`) | Third pass on the validation sets (the stand-in for a classmate's 150 items). | |
| Nov 17, 2026 | Google Gemini API, `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite` | Two earlier attempts at the first-coder role (10,582 and 4,422 Hong Kong items) and the tests around them. Stopped when the free tier's daily cap was reached and Cayden switched the first coder to Claude Haiku 5.5. These labels are not used in any result. | |
| 2015 to 2026 (upstream) | GDELT Global Knowledge Graph 2.0 (machine coding by the GDELT Project, not run by this study) | GDELT's own software assigned the theme tags, location tags and machine translation that the study reads. | |

Not AI, listed for completeness: Google BigQuery ({{run.bigquery_queries}} queries, {{run.bigquery_tb_billed}} TB billed), Python libraries (pandas, numpy, matplotlib, reportlab, trafilatura), the Internet Archive.

What AI did not do in this run: no person's judgment was imitated or claimed. No article was hand-coded by anyone. The research question, the codebook, the indicator choices and the analysis plan come from the pre-registered methodology. [CAYDEN TO CONFIRM: his own role in the question, codebook, design and interpretation]
