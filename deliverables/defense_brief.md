<!-- Built by src/build_docs.py from src/templates/defense_brief.template.md. Edit the template, then rebuild. -->
# Defense brief: Measuring What Matters

Cayden Auyang. AI drafted and I reviewed.

Read this once at breakfast. Then put it away and speak from memory.

Every number below was filled in from the results files when this brief was built. Results file generated: 2026-11-18T08:21:14Z. Validation status: **final**. Bootstrap resamples: 2,000.

If the status reads "provisional", the kappas come from a stand-in third AI pass. They are replaced when the blind second coder has run, and other numbers can move with them. Rebuild this file after that with `.venv/bin/python src/build_docs.py`.

## The one-minute version

**The question.** When a city's problems get worse in the official numbers, does public attention rise with them?

**What was compared.** The cities are Hong Kong, New York City and London. For eight kinds of problems, the study takes the yearly change in an official statistic and sets it next to the yearly change in two kinds of attention. The first is each problem's share of local news coverage, 2015-02 to 2026-10, built from 286,155 main-panel articles labeled by an AI language model. Counting the other listed outlets, which feed one check, the model labeled 429,082 articles. The second is each problem's share of Google search interest, 2004-01 to 2026-10.

**The three findings.**

1. Do attention and the official numbers move together (H1)? The plan predicted a positive but weak link.
   - News: For news coverage, attention rose 0.07 standard deviations for each standard deviation the official measure worsened (95% interval 0.02 to 0.10, 19 city and category pairs, about 185 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for news coverage.
   - Search: For search interest, attention rose 0.26 standard deviations for each standard deviation the official measure worsened (95% interval 0.19 to 0.42, 18 city and category pairs, about 336 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for search interest.
2. Does attention react more when a problem gets worse than when it gets better (H2)? The plan predicted yes.
   - News: For news coverage, the reaction to worsening and to improving could not be told apart. The slope was 0.06 when the problem worsened and 0.10 when it improved. The difference was -0.05 (95% interval -0.14 to 0.12). The interval includes zero, so H2 is not supported for news coverage.
   - Search: For search interest, the reaction to worsening and to improving could not be told apart. The slope was 0.37 when the problem worsened and 0.17 when it improved. The difference was 0.20 (95% interval -0.10 to 0.47). The interval includes zero, so H2 is not supported for search interest.
3. Is Safety the category where attention and official data disagree most (H3)? The plan predicted yes in at least two of the three cities.
   - News: For news coverage, Safety showed the largest gap in 1 of 3 cities. Hong Kong: Safety ranked 1 of 5 (70% of periods moved in opposite directions; the largest was Safety at 70%). New York City: Safety ranked 4 of 8 (45% of periods moved in opposite directions; the largest was Education at 67%). London: Safety ranked 6 of 6 (35% of periods moved in opposite directions; the largest was Housing at 58%). H3 predicted the largest gap in at least two cities, so it is not supported.
   - Search: For search interest, Safety showed the largest gap in 0 of 3 cities. Hong Kong: Safety could not be tested. New York City: Safety ranked 4 of 7 (41% of periods moved in opposite directions; the largest was Environment at 47%). London: Safety ranked 4 of 6 (41% of periods moved in opposite directions; the largest was Environment at 52%). H3 predicted the largest gap in at least two cities, so it is not supported.

**The sentence to add every time.** An AI language model did the labeling and a second AI language model did the checking. No person hand-coded any article in this run, so the check shows that two AI coders agree. It does not show that a person would agree with them.

## Terms behind the poster

**Cohen's kappa.** Kappa measures how often two coders give the same label, after removing the agreement they would reach by chance alone. A kappa of 0 means no better than chance and 1 means they always agree, and a category had to reach 0.61 in a city to be used there.

**Year-over-year change.** Each month is compared with the same month one year earlier, for the official series and for attention. That takes out the seasons, and it stops two series that both drift upward for twenty years from looking related when they are not.

**Standard deviation (SD), as used here.** A standard deviation is the typical size of a yearly change in one series. Each pair's changes are divided by their own SD, so a slope reads "when the official measure worsens by one typical step, attention moves by this many of its own typical steps," and series in different units can share one model.

**Pooled regression.** One regression uses every city and category pair together, because one pair alone has only about ten to twenty independent years. Each pair gets its own intercept, which is its own baseline, and the same total weight, so a monthly series with many points cannot drown out an annual one.

**Block bootstrap and the 95% interval.** The yearly changes are resampled 2,000 times in whole 12-month blocks, and the slope is recomputed each time; blocks are used because neighboring months overlap and are not independent. The 95% interval is the middle 95% of those slopes, and the rule for H1 is whether that interval sits above zero.

**Adjusted p-values (Benjamini-Hochberg).** With 37 separate pair tests, a few would look convincing by luck alone. The adjustment scales each p-value up by how many tests were run and where it ranks, which holds the expected share of false alarms among the pairs that pass to 5% or less; 11 of the 37 pairs had an adjusted p below 0.05.

**Attention share.** Attention is one category's share of a city's local news coverage, or of its search interest, in a month, and never a raw count. Shares cancel out the growth in how many outlets the news database tracks, but they also move together, so a spike in one topic pushes every other share down.

**Main panel of outlets.** The main panel is the fixed list of outlets that the news database recorded steadily in every year from 2015: 3 in Hong Kong, 3 in New York City and 15 in London. The list is fixed so that an outlet joining or leaving cannot shift the shares, and each outlet counts equally so the largest one cannot dominate.

**Matched-panel change.** A city's yearly change in news attention is each outlet's own change from a year earlier, averaged across the outlets present in both years. That keeps the comparison like for like when an outlet has no articles in a month or is left out of some years.

**Permutation test.** For the lead and lag results, the attention series is slid along the calendar by a random amount many times, and each time the strongest correlation across lags of up to 12 months either way is recorded. The p-value is the share of those shifted series that did at least as well as the real one, and this part of the study is exploratory with no prediction attached.

## The two charts on the poster

1. **The answer chart.** Each dot is a pooled slope: how many of its own typical steps attention moves when an official measure worsens by one typical step. The pale bar is the 95% interval. The dark line marked "no link" is zero. Search: 0.26 (0.19 to 0.42), H1 supported. News: 0.07 (0.02 to 0.10), H1 supported.
2. **The case-study chart.** The dark line is the yearly change in the official measure and the orange line is the yearly change in that category's share of news, both in their own typical steps, with worse at the top. The shaded band is the stretch where they moved in opposite directions: Hong Kong Economy, 2022-05 to 2023-06, with the official measure improving and attention rising for 14 months.

**About the answer title.** The title's wording is picked by a rule in `src/poster_board.py` from the two H1 verdicts, and `poster/board_manifest.json` records which rule fired. The analysis calls a slope under 0.3 weak. If the slopes above are under it, say "follow, weakly" out loud. Without 2020 to 2022 the news slope is 0.02 (-0.04 to 0.06) and the search slope is 0.26 (0.17 to 0.40).

**Results that are not on the poster.** Have these ready.

- Validation: 23 of 36 category checks reached kappa 0.61. Overall kappa was 0.65 in Hong Kong, 0.76 in New York City and 0.71 in London.
- H2: for news the slopes were 0.06 when worsening and 0.10 when improving (H2 not supported), and for search 0.37 and 0.17 (H2 not supported).
- H3: Safety had the largest gap in 1 of 3 cities for news (H3 not supported) and in 0 of 3 for search (H3 not supported).

Two things to know before someone asks.

**About the case study.**

- How it was picked: longest run of opposite movement in the news series with a proposed cause other than unclear.
- Proposed cause: the two measure different parts of the problem.
- Evidence recorded for that cause: The unemployment rate fell through this period. A seeded sample of ten Economy stories from the period is about weak consumer spending, calls to reopen the border, rising interest rates and people leaving the city. The category covers business conditions as a whole. The indicator covers jobs only.
- Proposed by: AI, after reading a seeded sample of the period's coverage; for Cayden to confirm.
- [CAYDEN TO CONFIRM: the proposed cause for the case study]

**About the H3 shares.** Two unrelated series would move in opposite directions about half the time. A cell near 50% means no visible relationship. Only a cell well above 50% means the two pulled against each other.

## The numbers on the poster and where they come from

`results.json` is `data/public/results.json`. `validation_summary.json` is `data/public/validation_summary.json`.

| On the poster | Value now | File and field |
| :-- | :-- | :-- |
| "3 cities" | 3 | `results.json -> counts.cities` |
| "429k news articles sorted by topic" | 429,082 | `results.json -> counts.articles_labeled_all`, rounded to thousands. This counts the main panels and the check lists. The main panels alone hold 286,155. |
| "Official data series" | 23 | `results.json -> counts.official_series_main` (main indicators; with backups there are 45) |
| "Years of search data" | 274 months | `results.json -> counts.search_months`, divided by 12 and rounded down |
| "Local news outlets" | 21 | `results.json -> counts.outlets_main_panel_total` (the main panels; 68 outlets are listed in all) |
| "Months of news" | 141 (2015-02 to 2026-10) | `results.json -> counts.news_months` |
| Search downloads per request (not on the poster) | 2 | `results.json -> counts.search_downloads_per_request` |
| The kappa bar (not on the poster) | 0.61 | `validation_summary.json -> threshold` |
| Category checks that reached the bar | 23 of 36 | `validation_summary.json -> cities.*.kept`, counted over the twelve categories in each city |
| Overall kappa, Hong Kong | 0.65 | `validation_summary.json -> cities.hk.overall_kappa` |
| Overall kappa, New York City | 0.76 | `validation_summary.json -> cities.nyc.overall_kappa` |
| Overall kappa, London | 0.71 | `validation_summary.json -> cities.london.overall_kappa` |
| H1 slope, news | 0.07 | `results.json -> main.news.h1.est` |
| H1 95% interval, news | 0.02 to 0.10 | `results.json -> main.news.h1.ci_low`, `ci_high` |
| H1 bootstrap p, news | p = 0.009 | `results.json -> main.news.h1.p_text` (from `p_boot`) |
| Pairs in the news model | 19 | `results.json -> main.news.h1.n_pairs` |
| H1 slope, search | 0.26 | `results.json -> main.search.h1.est` |
| H1 95% interval, search | 0.19 to 0.42 | `results.json -> main.search.h1.ci_low`, `ci_high` |
| H1 bootstrap p, search | p < 0.001 | `results.json -> main.search.h1.p_text` (from `p_boot`) |
| Pairs in the search model | 18 | `results.json -> main.search.h1.n_pairs` |
| H2 news, slope when worsening | 0.06 | `results.json -> main.news.h2.worse.est` |
| H2 news, slope when improving | 0.10 | `results.json -> main.news.h2.better.est` |
| H2 news, difference (95% interval) | -0.05 (-0.14 to 0.12) | `results.json -> main.news.h2.diff` |
| H2 search, slope when worsening | 0.37 | `results.json -> main.search.h2.worse.est` |
| H2 search, slope when improving | 0.17 | `results.json -> main.search.h2.better.est` |
| H2 search, difference (95% interval) | 0.20 (-0.10 to 0.47) | `results.json -> main.search.h2.diff` |
| H3 news, cities where Safety had the largest gap | 1 of 3 | `results.json -> h3.safety_rank.news.cities_where_safety_is_largest` |
| H3 search, cities where Safety had the largest gap | 0 of 3 | `results.json -> h3.safety_rank.search.cities_where_safety_is_largest` |
| H3 news, Safety's rank in Hong Kong | 1 of 5 | `results.json -> h3.safety_rank.news.by_city.hk` |
| H3 news, Safety's rank in New York City | 4 of 8 | `results.json -> h3.safety_rank.news.by_city.nyc` |
| H3 news, Safety's rank in London | 6 of 6 | `results.json -> h3.safety_rank.news.by_city.london` |
| Case study, length | 14 months | `results.json -> case_study.months` |
| Case study, dates | 2022-05 to 2023-06 | `results.json -> case_study.start`, `end` |

Notes on this table.

- A bootstrap p cannot go below one divided by the number of resamples plus one. With 2,000 resamples, a p at that floor means "none of the resampled slopes crossed zero," and it is printed as "p < 0.001".
- The count of category checks covers the twelve categories in each of the three cities. "Not a civic problem" is scored and shown, but it is not a category the rule can drop, so it is not in the count.
- In the Safety rank rows, rank 1 means the largest gap in that city. "[not available]" in a rank row means Safety could not be tested there.
- The "What surprised me" piece carries the four sentences you wrote on November 18, word for word (`src/poster_board.py`, `SURPRISED`). They are not rebuilt from the results. The first says search follows the official numbers far more closely than news: the slopes behind it are 0.26 for search and 0.07 for news, both weak by the analysis's own cutoff, and the two models pool different pairs and years. If a rebuild changes those numbers, reread your sentences.
- Rows from the H1 p-values down are not printed on the poster. They are here for questions.

## Fifteen questions a teacher is likely to ask

### Who actually did what?

An AI agent ran the whole study in one unattended session on November 17 and 18, 2026. It pulled the data, labeled the articles, ran the validation and the statistics, and drafted the documents, including this brief. The research question, the codebook, the indicators and the tests are in the methodology dated October 7, 2026, which was posted publicly before any outcome data were pulled. While the run was going I sent it instructions about which model should do the labeling, and those are in `deliverables/deviations.md`, section 2. No person hand-coded any article in this run.

[CAYDEN TO CONFIRM: your own role in the question, the codebook, the design and the interpretation]

### Why didn't you hand-code the articles?

The plan said I would hand-code about 900 items, and that agreement with my labels would decide which categories count. The study was compressed into one overnight run, and for that run I replaced my hand-coding with a second AI language model from a different company, which did not see the first labels. That is the first change listed in `deliverables/deviations.md`. It means the check shows that two AI coders agree, and it does not show that either one matches a human reader. The run left me a 50-item file, `deliverables/optional_hand_check_50.csv`, so I can code a sample by hand and compute my own kappa against both.

[CAYDEN TO CONFIRM: why the study was compressed into one run]

### How do you know the AI is right?

I can't show that it is right, and the poster does not say it is. What I can show is agreement: a second AI language model from a different company read the real headline and opening lines of a sample of articles without seeing the first labels, and overall kappa was 0.65 in Hong Kong, 0.76 in New York City and 0.71 in London. Any category under 0.61 in a city was dropped there. A separate check on 2020 and later articles found that labels made from the words in the web address matched labels made from the real stored headline at kappa 0.80, 0.79 and 0.84 in the same order. Two models can share a blind spot, so until a person codes a sample I call this consistency between AI coders and nothing stronger.

Three scoring rules need saying out loud. The run set all three after it had seen provisional scores from a third AI pass and before the official second coder ran.

- The 0.61 rule counts only the validation items that stay in the main series. In Hong Kong that is 228 of 299 items.
- Where no page could be read and the article was from 2020 on, the second coder read the real stored headline alone: 130 items in Hong Kong, 1 in New York City and 16 in London. One site challenged automated requests, so the run stopped using it and did not fetch its pages from anywhere else.
- The weights match the labeled sample by category and the attention index by outlet.

The table "Kappa under other scoring rules" at the end of this brief shows which categories fall under the bar with the plan as written and with each rule. If someone asks, say which categories the plan as written would have dropped. With the categories that rule keeps, the pooled news slope was 0.08 (0.03 to 0.11) across 16 pairs, against 0.07 (0.02 to 0.10) across 19 in the main model. No Hong Kong article from before 2020 is in the scored set, so the second coder never checked Hong Kong's labels for 2015 to 2019. The blind second coder ran on November 18 after its daily quota reset and labeled 898 validation items. It re-labeled 50 items in a fresh request.

### What does a kappa of 0.61 mean, and why were some categories dropped?

Kappa is agreement beyond chance: 0 is what random labeling would give and 1 is perfect agreement, so 0.61 is a bit more than halfway from chance to perfect. It is the bottom of the range that Landis and Koch (1977) call substantial agreement. That cutoff is a convention, and it was fixed in the plan before any labels existed. The rule was that a category under the bar in a city gets one revision of its wording and a fresh sample, and if it still falls short it is dropped for that city. Dropping a category costs pairs, and it keeps the least consistent labels out of the results.

- Hong Kong, dropped: Housing, Transport, Cost of Living, Culture, Technology and Community. Of the eight categories compared with official data: Housing, Transport and Cost of Living.
- New York City, dropped: Culture and Community. Of the eight compared: none.
- London, dropped: Cost of Living, Governance, Culture, Technology and Community. Of the eight compared: Cost of Living.

Whether a revision was tried for a category, and what it scored, is in `data/public/validation_report.md`.

### Why do Hong Kong's early years rest on one outlet?

The news database stores real headlines only from 2020, so in every year the AI reads the headline words inside each article's web address plus the database's topic tags. Some Hong Kong outlets use number-only addresses, which leaves the tags alone. The plan said to test tag-only labels against real-headline labels on 2020 and later articles, and to leave those outlets out of 2015 to 2019 if the kappa fell under 0.61. Rule applied: yes. Theme-tag-only labels agreed with real-headline labels at kappa 0.42, below 0.61. HK China News Agency and Oriental Daily, whose addresses were number-only before 2020, are left out of 2015 to 2019. Hong Kong's news series for those years rests on the South China Morning Post alone.

One row in the checks table, marked exploratory, puts every main-panel outlet back into every year. The pooled news slope there was 0.07 (0.01 to 0.10), against 0.07 (0.02 to 0.10) in the main model.

### Why did the labeling model change during the run?

The run began labeling with an AI language model through a key that turned out to be on its provider's free tier, and it hit the daily request cap partway through the Hong Kong articles. A second model on the same key was started as a stopgap. I then sent the run an instruction to switch to a model from a different provider on a paid key, to relabel everything from zero so that one model labeled every article, and to keep the first provider's model as the blind second coder. The prompt has not changed since 2026-11-17T21:00:35Z. Two test runs, of 200 and 2,000 Hong Kong items, used it before the full run. No label from the two earlier models is used in any result. Before the full run the new model was compared with a larger model from the same provider on 300 items: kappa 0.81, under a rule I set of 0.75 or higher to stay with the smaller one.

The model names and the full history are in `data/public/labeling_card.md`.

### Why did you pre-register, and why on November 17?

Pre-registering means posting the plan with a timestamp before any outcome data exist, so the hypotheses and the tests cannot be adjusted after seeing which way the results go. The plan was to post it in October on the Open Science Framework, and that step was meant to follow mentor approval. It was posted on GitHub on November 17, 2026, with copies of the plan saved by the Internet Archive, and the first query that returned outcome data ran after that. The commit is `e8d5f32`, tag `prereg-v1`, time 2026-11-17T20:31:07Z, and the record is `deliverables/preregistration.md`. So it came later than planned and on a different site, and it still came before the data.

[CAYDEN TO CONFIRM: why the pre-registration moved from October to November 17]

[CAYDEN TO CONFIRM: date of mentor approval, if any]

### Why three cities?

Hong Kong, New York City and London are close in population and very different in politics and media. The study compares how attention behaves inside each city and never ranks one city's problems against another's, which keeps those differences from tilting the result. Three cities also give more city and category pairs for the pooled test: 19 for news and 18 for search. The plan named Hong Kong as the pilot, but in this run all three cities ran in the same night, so there was no separate pilot.

### Isn't official data the truth?

No, and the plan says so in its first section: official statistics are the benchmark here, and they have blind spots of their own. Recorded crime counts only what gets reported and recorded, and a shelter count moves with policy as well as need. So when attention and an official number disagree, the study lists the period and gives a proposed cause, and "the official measure changed how it counts" is one of the allowed causes. The run listed 77 such periods of six months or more, and 4 of them were put down to a change in how the official series counts. Those causes were proposed by AI, and I still have to review them.

### Why are the news slope and the search slope different?

The pooled slope was 0.07 for news and 0.26 for search, and the study did not test why they differ, so I can only list reasons. They cover different years (search starts in 2004-01, news in 2015-02), different places (search covers all of Hong Kong, the New York media market and all of England) and different pairs (19 for news, 18 for search). They are also built differently: search uses term sets fixed in advance, and news uses AI labels on a small panel of outlets. Noise in either measure pulls its slope toward zero, so the noisier one will tend to show the smaller slope. The search numbers are also less settled than the plan intended: it called for three downloads on three different days, and the count so far is 2, from one night.

### What do the intervals tell you, and what don't they?

A 95% interval is the range the slope stays in when the years are reshuffled in 12-month blocks 2,000 times. It says how much the answer depends on which years happen to be in the sample. It says nothing about cause, and it leaves out errors in the labels, the outlet lists and the choice of indicators. The run also tried the method on made-up series with no link between them: the interval wrongly excluded zero in 7 of 40 trials, which is 18%, where an honest 95% interval would do that about 5% of the time. If the first rate is the higher one, my intervals are too narrow for slow-moving series, and an interval that only just clears zero should be called borderline.

Setup of that test: 8 unrelated pairs of 120 months each, both series with month-to-month persistence 0.8, 12-month blocks. With that few trials the rate is itself rough. The checks table also has an exploratory row with 24-month blocks.

### What would change your mind?

A human-coded sample that disagrees with the AI labels would change it first, because every news number rests on those labels. Next are the checks that the results hold: backup indicators, leaving out 2020 to 2022, leaving out every marked break, and lining official data up by release date. For news, the H1 interval stayed above zero in 9 of the 14 checks that ran (the ones where it did not: Without 2020 to 2022; Without 2020 to 2022 and every other marked break month; Official series aligned by release date; Description: Hong Kong pairs only, periods before 2021 (several major outlets closed in 2021); Description: Hong Kong pairs only, periods from 2021 on). For search it stayed above zero in 5 of 5 (the ones where it did not: none).

If a result holds in the main model and fails one of those checks, say so before anyone asks, and name the check.

### What is the biggest weakness?

No person has checked the labels. Two AI coders agreeing is weaker than the hand-coded check the plan promised, and every news result depends on those labels. After that, the whole study ran in one night, so the search downloads could not be spread over three different days as planned (downloads per request so far: 2). London Health has no official series, because the source blocked automated collection, so that pair was never tested. The full list is in `deliverables/deviations.md`.

Also look at the row "Without 2020 to 2022" in the checks table. For news, the interval in that row includes zero (slope 0.02, -0.04 to 0.06). For search it is above zero (slope 0.26, 0.17 to 0.40). If either one includes zero, that link depends on the COVID years, and that belongs in this answer.

### What would you do next with more time?

The first job is the human check: code the 50-item file by hand, then a larger sample, and compute my kappa against both AI coders. Then I would take the search downloads the plan called for on different days, and find a route to the London Health series that was blocked. I would also read coverage from each listed disconnection and confirm or change its proposed cause. After that the plan is to revise the paper for the Journal of Emerging Investigators and publish the dataset.

### How much did it cost?

BigQuery billed 3.29 terabytes across 43 queries, which is about $20.57. Language-model fees for the first coder came to $27.25 in all, for 429,082 labeled items plus the tests, which works out to about $0.06 per 1,000 articles. The second coder ran on its provider's free tier, logged as $0.00. The official statistics and the search data were free downloads. My proposal budgeted under $300 for queries and AI labeling.

## The exact sentence to use when someone asks who coded the articles

"An AI language model labeled every article in the study. A second AI language model from a different company checked a sample without seeing the first labels. No person hand-coded any article in this run, so the agreement score shows that two AI coders agree, and it does not show that either matches a human reader."

## Lines only Cayden can fill in

These are facts the run could not know. Fill them in before you present, in your own words.

- [CAYDEN TO CONFIRM: your own role in the question, the codebook, the design and the interpretation]
- [CAYDEN TO CONFIRM: date of mentor approval, if any] This one also appears in `deliverables/deviations.md` (row 1.3) and `deliverables/preregistration.md`.
- [CAYDEN TO CONFIRM: why the study was compressed into one run]
- [CAYDEN TO CONFIRM: why the pre-registration moved from October to November 17]
- [CAYDEN TO CONFIRM: what these results mean for OurCityHealth] The paper's Discussion has a first draft of this paragraph (`paper/paper.md`, Section 6).
- [CAYDEN TO CONFIRM: license for the dataset] In `data/public/README.md` and the data card.
- [CAYDEN TO CONFIRM: the proposed cause for the case study] Every other proposed cause in the disconnection table is also marked "for Cayden to confirm."

To find every open line in the project: `grep -rn "CAYDEN TO" deliverables poster paper data/public MORNING.md`

## Tables behind the charts

Keep these open while you rehearse. Slopes are in standard deviations, with 95% intervals in parentheses.

**Main models (H1 and H2)**

| Source | H1 slope (95% interval) | p | Pairs | Periods | Independent pair-years | Slope when worsening | Slope when improving | Difference (95% interval) |
| :-- | :-- | --: | --: | --: | --: | :-- | :-- | :-- |
| News | 0.07 (0.02 to 0.10) | 0.009 | 19 | 1,739 | 185 | 0.06 (0.01 to 0.10) | 0.10 (-0.05 to 0.18) | -0.05 (-0.14 to 0.12) |
| Search | 0.26 (0.19 to 0.42) | < 0.001 | 18 | 3,980 | 336 | 0.37 (0.22 to 0.59) | 0.17 (0.08 to 0.39) | 0.20 (-0.10 to 0.47) |

**H1 by category**

Each row pools at most three cities, so read these as description. The main tests are the pooled rows above.

| Category | News slope (95% interval) | Cities | Search slope (95% interval) | Cities |
| :-- | :-- | --: | :-- | --: |
| Safety | 0.05 (-0.15 to 0.18) | 3 | 0.27 (0.14 to 0.36) | 2 |
| Economy | 0.08 (0.03 to 0.13) | 3 | 0.58 (0.36 to 0.70) | 3 |
| Housing | 0.02 (-0.05 to 0.05) | 2 | 0.05 (-0.10 to 0.23) | 3 |
| Transport | 0.13 (-0.00 to 0.25) | 2 | 0.22 (0.06 to 0.46) | 2 |
| Environment | 0.13 (0.03 to 0.25) | 3 | 0.41 (0.05 to 0.90) | 3 |
| Health | 0.45 (-0.44 to 0.50) | 2 | -0.06 (-0.31 to 0.08) | 2 |
| Education | -0.22 (-0.78 to 0.19) | 3 | not tested | 0 |
| Cost of Living | 0.10 (-0.11 to 0.22) | 1 | 0.59 (0.43 to 0.74) | 3 |

**H1 by city**

| City | News slope (95% interval) | Pairs | Search slope (95% interval) | Pairs |
| :-- | :-- | --: | :-- | --: |
| Hong Kong | -0.05 (-0.38 to 0.10) | 5 | 0.23 (0.08 to 0.36) | 5 |
| New York City | 0.08 (0.03 to 0.11) | 8 | 0.31 (0.20 to 0.62) | 7 |
| London | 0.10 (0.00 to 0.24) | 6 | 0.18 (0.08 to 0.26) | 6 |

**Checks that the results hold**

| Check | News H1 slope (95% interval) | News pairs | News worse minus better | Search H1 slope (95% interval) | Search pairs | Search worse minus better |
| :-- | :-- | --: | :-- | :-- | --: | :-- |
| Main model | 0.07 (0.02 to 0.10) | 19 | -0.05 (-0.14 to 0.12) | 0.26 (0.19 to 0.42) | 18 | 0.20 (-0.10 to 0.47) |
| Backup indicators in place of the main ones | 0.13 (0.07 to 0.21) | 19 | 0.02 (-0.16 to 0.21) | 0.28 (0.17 to 0.37) | 17 | -0.15 (-0.44 to 0.10) |
| Without 2020 to 2022 | 0.02 (-0.04 to 0.06) | 19 | 0.05 (-0.14 to 0.22) | 0.26 (0.17 to 0.40) | 18 | 0.03 (-0.35 to 0.42) |
| Without 2020 to 2022 and every other marked break month | 0.03 (-0.06 to 0.15) | 19 | 0.08 (-0.19 to 0.42) | 0.24 (0.17 to 0.31) | 18 | 0.04 (-0.21 to 0.21) |
| Official series aligned by release date | 0.02 (-0.00 to 0.06) | 19 | 0.04 (-0.05 to 0.13) | 0.18 (0.11 to 0.31) | 18 | 0.23 (-0.05 to 0.45) |
| All listed outlets in place of the fixed panel | 0.10 (0.01 to 0.14) | 19 | -0.12 (-0.25 to 0.13) | not run |  |  |
| Negative-tone share in place of all coverage | 0.09 (0.02 to 0.13) | 19 | -0.10 (-0.22 to 0.16) | not run |  |  |
| Hong Kong without HK China News Agency | 0.07 (0.01 to 0.10) | 19 | -0.05 (-0.14 to 0.12) | not run |  |  |
| London without the seven borough papers that jumped in volume | 0.06 (0.00 to 0.09) | 19 | -0.04 (-0.14 to 0.12) | not run |  |  |
| Categories kept or dropped by the validation rule as the plan words it (every validation item, weights by category only) | 0.08 (0.03 to 0.11) | 16 | -0.09 (-0.19 to 0.07) | not run |  |  |
| Description: Hong Kong pairs only, periods before 2021 (several major outlets closed in 2021) | -0.23 (-1.08 to 0.27) | 5 | 1.21 (-2.32 to 2.54) | not run |  |  |
| Description: Hong Kong pairs only, periods from 2021 on | 0.02 (-0.31 to 0.20) | 5 | 0.39 (-0.66 to 0.64) | not run |  |  |
| Exploratory: every main-panel outlet in every year (no outlets left out of 2015 to 2019) | 0.07 (0.01 to 0.10) | 19 | -0.05 (-0.14 to 0.11) | not run |  |  |
| Exploratory: Hong Kong from articles with headline words in the address only (no theme-tag-only labels in any year) | 0.07 (0.02 to 0.10) | 19 | -0.06 (-0.16 to 0.10) | not run |  |  |
| Exploratory: bootstrap with 24-month blocks (wider intervals if changes are persistent) | 0.07 (0.03 to 0.10) | 19 | -0.05 (-0.11 to 0.11) | 0.26 (0.19 to 0.45) | 18 | 0.20 (-0.10 to 0.42) |

**H3: share of periods moving in opposite directions, news**

| Category | Hong Kong | New York City | London |
| :-- | --: | --: | --: |
| Safety | 70% (10 years) | 45% (128 months) | 35% (129 months) |
| Economy | 59% (114 months) | 43% (118 months) | 42% (125 months) |
| Housing | not tested | 53% (129 months) | 58% (128 months) |
| Transport | not tested | 40% (129 months) | 43% (119 months) |
| Environment | 47% (123 months) | 38% (124 months) | 51% (85 months) |
| Health | 59% (29 quarters) | 41% (70 months) | not tested |
| Education | 56% (9 years) | 67% (9 years) | 40% (10 years) |
| Cost of Living | not tested | 45% (104 months) | not tested |

**H3: share of periods moving in opposite directions, search**

| Category | Hong Kong | New York City | London |
| :-- | --: | --: | --: |
| Safety | not tested | 41% (234 months) | 41% (187 months) |
| Economy | 39% (233 months) | 28% (247 months) | 40% (253 months) |
| Housing | 48% (257 months) | 45% (256 months) | 46% (237 months) |
| Transport | not tested | 36% (191 months) | 49% (252 months) |
| Environment | 39% (256 months) | 47% (247 months) | 52% (206 months) |
| Health | 52% (29 quarters) | 43% (70 months) | not tested |
| Education | not tested | not tested | not tested |
| Cost of Living | 45% (240 months) | 41% (257 months) | 35% (258 months) |

**Disconnections of six months or more, by proposed cause**

| Proposed cause (by AI, for Cayden to confirm) | Disconnections of six months or more |
| :-- | --: |
| unclear | 36 |
| attention followed a news cycle rather than conditions | 25 |
| a real event drew coverage the indicator does not capture | 8 |
| the two measure different parts of the problem | 4 |
| the official measure changed how it counts | 4 |

**Kappa by category and city**

| Category | Hong Kong | New York City | London |
| :-- | --: | --: | --: |
| Safety | 0.72 kept | 0.80 kept | 0.83 kept |
| Economy | 0.65 kept | 0.77 kept | 0.64 kept |
| Housing | 0.46 dropped | 0.98 kept | 0.81 kept |
| Transport | 0.36 dropped | 0.82 kept | 0.80 kept |
| Environment | 0.79 kept | 0.65 kept | 0.61 kept |
| Health | 0.76 kept | 0.86 kept | 0.81 kept |
| Education | 0.82 kept | 0.74 kept | 0.88 kept |
| Cost of Living | 0.44 dropped | 0.67 kept | 0.41 dropped |
| Governance | 0.73 kept | 0.77 kept | 0.52 dropped |
| Culture | 0.18 dropped | 0.20 dropped | 0.20 dropped |
| Technology | 0.11 dropped | 0.68 kept | 0.45 dropped |
| Community | 0.36 dropped | 0.46 dropped | 0.34 dropped |
| Not a civic problem | 0.62 | 0.72 | 0.75 |
| **Overall** | **0.65** | **0.76** | **0.71** |
| Items | 228 | 300 | 299 |
| Not about the city (weighted) | 15% | 8% | 9% |

**Kappa under other scoring rules**

This shows which categories fall below the bar under the plan as written and under each scoring rule the run added.

| City | Rule | Items | Overall kappa | Categories below 0.61 |
| :-- | :-- | --: | --: | :-- |
| Hong Kong | Every validation item, weights by category only (the plan as written) | 299 | 0.56 | Safety, Economy, Housing, Transport, Cost of Living, Governance, Culture, Technology and Community |
| Hong Kong | Items that remain in the main series, weights by category only | 228 | 0.64 | Housing, Transport, Cost of Living, Culture, Technology and Community |
| Hong Kong | Items that remain in the main series, weights by category and outlet (the rule used) | 228 | 0.65 | Housing, Transport, Cost of Living, Culture, Technology and Community |
| New York City | Every validation item, weights by category only (the plan as written) | 300 | 0.76 | Culture and Community |
| New York City | Items that remain in the main series, weights by category only | 300 | 0.76 | Culture and Community |
| New York City | Items that remain in the main series, weights by category and outlet (the rule used) | 300 | 0.76 | Culture and Community |
| London | Every validation item, weights by category only (the plan as written) | 299 | 0.72 | Environment, Cost of Living, Governance, Culture, Technology and Community |
| London | Items that remain in the main series, weights by category only | 299 | 0.72 | Environment, Cost of Living, Governance, Culture, Technology and Community |
| London | Items that remain in the main series, weights by category and outlet (the rule used) | 299 | 0.71 | Cost of Living, Governance, Culture, Technology and Community |

**Counts**

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
