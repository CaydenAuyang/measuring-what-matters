<!-- TEMPLATE: Filled by src/build_docs.py into deliverables/defense_brief.md. Edit this file, never the output.
Every result number is a token. The only numbers typed here are fixed parts of the plan or of the record:
dates and counts from spec/methodology.md and spec/fall_proposal.md (95% interval, 12-month blocks, 900 and 300
items, three downloads, six months, 0.05, the $300 budget, October 7), dates from deliverables/deviations.md
(November 17 and 18), and the prompt's last-change time and the two test-run sizes (200 and 2,000 items, from
src/codebook.py's file time and logs/api_costs.csv). calc.* tokens are worked out in src/build_docs.py from the
same results files.
No AI model, product or company is named in this file. The names are in data/public/labeling_card.md. -->
# Defense brief: Measuring What Matters

Cayden Auyang. AI drafted and I reviewed.

Read this once at breakfast. Then put it away and speak from memory.

Every number below was filled in from the results files when this brief was built. Results file generated: {{generated_utc}}. Validation status: **{{text.validation_status}}**. Bootstrap resamples: {{bootstrap_reps|comma}}.

If the status reads "provisional", the kappas come from a stand-in third AI pass. They are replaced when the blind second coder has run, and other numbers can move with them. Rebuild this file after that with `.venv/bin/python src/build_docs.py`.

## The one-minute version

**The question.** When a city's problems get worse in the official numbers, does public attention rise with them?

**What was compared.** The cities are Hong Kong, New York City and London. For eight kinds of problems, the study takes the yearly change in an official statistic and sets it next to the yearly change in two kinds of attention. The first is each problem's share of local news coverage, {{counts.news_first_month}} to {{counts.news_last_month}}, built from {{counts.articles_labeled_main_panel_total|comma}} main-panel articles labeled by an AI language model. Counting the other listed outlets, which feed one check, the model labeled {{counts.articles_labeled_all|comma}} articles. The second is each problem's share of Google search interest, {{counts.search_first_month}} to {{counts.search_last_month}}.

**The three findings.**

1. Do attention and the official numbers move together (H1)? The plan predicted a positive but weak link.
   - News: {{verdicts.h1_news_sentence}}
   - Search: {{verdicts.h1_search_sentence}}
2. Does attention react more when a problem gets worse than when it gets better (H2)? The plan predicted yes.
   - News: {{verdicts.h2_news_sentence}}
   - Search: {{verdicts.h2_search_sentence}}
3. Is Safety the category where attention and official data disagree most (H3)? The plan predicted yes in at least two of the three cities.
   - News: {{verdicts.h3_news_sentence}}
   - Search: {{verdicts.h3_search_sentence}}

**The sentence to add every time.** An AI language model did the labeling and a second AI language model did the checking. No person hand-coded any article in this run, so the check shows that two AI coders agree. It does not show that a person would agree with them.

## Terms behind the poster

**Cohen's kappa.** Kappa measures how often two coders give the same label, after removing the agreement they would reach by chance alone. A kappa of 0 means no better than chance and 1 means they always agree, and a category had to reach {{v.threshold}} in a city to be used there.

**Year-over-year change.** Each month is compared with the same month one year earlier, for the official series and for attention. That takes out the seasons, and it stops two series that both drift upward for twenty years from looking related when they are not.

**Standard deviation (SD), as used here.** A standard deviation is the typical size of a yearly change in one series. Each pair's changes are divided by their own SD, so a slope reads "when the official measure worsens by one typical step, attention moves by this many of its own typical steps," and series in different units can share one model.

**Pooled regression.** One regression uses every city and category pair together, because one pair alone has only about ten to twenty independent years. Each pair gets its own intercept, which is its own baseline, and the same total weight, so a monthly series with many points cannot drown out an annual one.

**Block bootstrap and the 95% interval.** The yearly changes are resampled {{bootstrap_reps|comma}} times in whole 12-month blocks, and the slope is recomputed each time; blocks are used because neighboring months overlap and are not independent. The 95% interval is the middle 95% of those slopes, and the rule for H1 is whether that interval sits above zero.

**Adjusted p-values (Benjamini-Hochberg).** With {{text.pairs_tested}} separate pair tests, a few would look convincing by luck alone. The adjustment scales each p-value up by how many tests were run and where it ranks, which holds the expected share of false alarms among the pairs that pass to 5% or less; {{text.pairs_adjusted_p_below_05}} of the {{text.pairs_tested}} pairs had an adjusted p below 0.05.

**Attention share.** Attention is one category's share of a city's local news coverage, or of its search interest, in a month, and never a raw count. Shares cancel out the growth in how many outlets the news database tracks, but they also move together, so a spike in one topic pushes every other share down.

**Main panel of outlets.** The main panel is the fixed list of outlets that the news database recorded steadily in every year from 2015: {{counts.outlets_main_panel.hk}} in Hong Kong, {{counts.outlets_main_panel.nyc}} in New York City and {{counts.outlets_main_panel.london}} in London. The list is fixed so that an outlet joining or leaving cannot shift the shares, and each outlet counts equally so the largest one cannot dominate.

**Matched-panel change.** A city's yearly change in news attention is each outlet's own change from a year earlier, averaged across the outlets present in both years. That keeps the comparison like for like when an outlet has no articles in a month or is left out of some years.

**Permutation test.** For the lead and lag results, the attention series is slid along the calendar by a random amount many times, and each time the strongest correlation across lags of up to 12 months either way is recorded. The p-value is the share of those shifted series that did at least as well as the real one, and this part of the study is exploratory with no prediction attached.

## The two charts on the poster

1. **The answer chart.** Each dot is a pooled slope: how many of its own typical steps attention moves when an official measure worsens by one typical step. The pale bar is the 95% interval. The dark line marked "no link" is zero. Search: {{main.search.h1.est}} ({{main.search.h1.ci_low}} to {{main.search.h1.ci_high}}), H1 {{verdicts.h1_search}}. News: {{main.news.h1.est}} ({{main.news.h1.ci_low}} to {{main.news.h1.ci_high}}), H1 {{verdicts.h1_news}}.
2. **The case-study chart.** The dark line is the yearly change in the official measure and the orange line is the yearly change in that category's share of news, both in their own typical steps, with worse at the top. The shaded band is the stretch where they moved in opposite directions: {{text.case_city}} {{text.case_category}}, {{case_study.start}} to {{case_study.end}}, with the official measure {{case_study.official_direction}} and attention {{case_study.attention_direction}} for {{case_study.months}} months.

**About the answer title.** The title's wording is picked by a rule in `src/poster_board.py` from the two H1 verdicts, and `poster/board_manifest.json` records which rule fired. The analysis calls a slope under 0.3 weak. If the slopes above are under it, say "follow, weakly" out loud. Without 2020 to 2022 the news slope is {{checks.without_covid.news.h1.est}} ({{checks.without_covid.news.h1.ci_low}} to {{checks.without_covid.news.h1.ci_high}}) and the search slope is {{checks.without_covid.search.h1.est}} ({{checks.without_covid.search.h1.ci_low}} to {{checks.without_covid.search.h1.ci_high}}).

**Results that are not on the poster.** Have these ready.

- Validation: {{calc.validation.checks_passed}} of {{calc.validation.checks_total}} category checks reached kappa {{v.threshold}}. Overall kappa was {{v.cities.hk.overall_kappa}} in Hong Kong, {{v.cities.nyc.overall_kappa}} in New York City and {{v.cities.london.overall_kappa}} in London.
- H2: for news the slopes were {{main.news.h2.worse.est}} when worsening and {{main.news.h2.better.est}} when improving (H2 {{verdicts.h2_news}}), and for search {{main.search.h2.worse.est}} and {{main.search.h2.better.est}} (H2 {{verdicts.h2_search}}).
- H3: Safety had the largest gap in {{h3.safety_rank.news.cities_where_safety_is_largest}} of {{counts.cities}} cities for news (H3 {{verdicts.h3_news}}) and in {{h3.safety_rank.search.cities_where_safety_is_largest}} of {{counts.cities}} for search (H3 {{verdicts.h3_search}}).

Two things to know before someone asks.

**About the case study.**

- How it was picked: {{case_study.selection_rule}}.
- Proposed cause: {{case_study.proposed_cause}}.
- Evidence recorded for that cause: {{case_study.evidence}}
- Proposed by: {{case_study.proposed_by}}.
- [CAYDEN TO CONFIRM: the proposed cause for the case study]

**About the H3 shares.** Two unrelated series would move in opposite directions about half the time. A cell near 50% means no visible relationship. Only a cell well above 50% means the two pulled against each other.

## The numbers on the poster and where they come from

`results.json` is `data/public/results.json`. `validation_summary.json` is `data/public/validation_summary.json`.

| On the poster | Value now | File and field |
| :-- | :-- | :-- |
| "3 cities" | {{counts.cities}} | `results.json -> counts.cities` |
| "429k news articles sorted by topic" | {{counts.articles_labeled_all|comma}} | `results.json -> counts.articles_labeled_all`, rounded to thousands. This counts the main panels and the check lists. The main panels alone hold {{counts.articles_labeled_main_panel_total|comma}}. |
| "Official data series" | {{counts.official_series_main}} | `results.json -> counts.official_series_main` (main indicators; with backups there are {{counts.official_series_total}}) |
| "Years of search data" | {{counts.search_months}} months | `results.json -> counts.search_months`, divided by 12 and rounded down |
| "Local news outlets" | {{counts.outlets_main_panel_total}} | `results.json -> counts.outlets_main_panel_total` (the main panels; {{counts.outlets_listed_total}} outlets are listed in all) |
| "Months of news" | {{counts.news_months}} ({{counts.news_first_month}} to {{counts.news_last_month}}) | `results.json -> counts.news_months` |
| Search downloads per request (not on the poster) | {{counts.search_downloads_per_request}} | `results.json -> counts.search_downloads_per_request` |
| The kappa bar (not on the poster) | {{v.threshold}} | `validation_summary.json -> threshold` |
| Category checks that reached the bar | {{calc.validation.checks_passed}} of {{calc.validation.checks_total}} | `validation_summary.json -> cities.*.kept`, counted over the twelve categories in each city |
| Overall kappa, Hong Kong | {{v.cities.hk.overall_kappa}} | `validation_summary.json -> cities.hk.overall_kappa` |
| Overall kappa, New York City | {{v.cities.nyc.overall_kappa}} | `validation_summary.json -> cities.nyc.overall_kappa` |
| Overall kappa, London | {{v.cities.london.overall_kappa}} | `validation_summary.json -> cities.london.overall_kappa` |
| H1 slope, news | {{main.news.h1.est}} | `results.json -> main.news.h1.est` |
| H1 95% interval, news | {{main.news.h1.ci_low}} to {{main.news.h1.ci_high}} | `results.json -> main.news.h1.ci_low`, `ci_high` |
| H1 bootstrap p, news | {{main.news.h1.p_text}} | `results.json -> main.news.h1.p_text` (from `p_boot`) |
| Pairs in the news model | {{main.news.h1.n_pairs}} | `results.json -> main.news.h1.n_pairs` |
| H1 slope, search | {{main.search.h1.est}} | `results.json -> main.search.h1.est` |
| H1 95% interval, search | {{main.search.h1.ci_low}} to {{main.search.h1.ci_high}} | `results.json -> main.search.h1.ci_low`, `ci_high` |
| H1 bootstrap p, search | {{main.search.h1.p_text}} | `results.json -> main.search.h1.p_text` (from `p_boot`) |
| Pairs in the search model | {{main.search.h1.n_pairs}} | `results.json -> main.search.h1.n_pairs` |
| H2 news, slope when worsening | {{main.news.h2.worse.est}} | `results.json -> main.news.h2.worse.est` |
| H2 news, slope when improving | {{main.news.h2.better.est}} | `results.json -> main.news.h2.better.est` |
| H2 news, difference (95% interval) | {{main.news.h2.diff.est}} ({{main.news.h2.diff.ci_low}} to {{main.news.h2.diff.ci_high}}) | `results.json -> main.news.h2.diff` |
| H2 search, slope when worsening | {{main.search.h2.worse.est}} | `results.json -> main.search.h2.worse.est` |
| H2 search, slope when improving | {{main.search.h2.better.est}} | `results.json -> main.search.h2.better.est` |
| H2 search, difference (95% interval) | {{main.search.h2.diff.est}} ({{main.search.h2.diff.ci_low}} to {{main.search.h2.diff.ci_high}}) | `results.json -> main.search.h2.diff` |
| H3 news, cities where Safety had the largest gap | {{h3.safety_rank.news.cities_where_safety_is_largest}} of {{counts.cities}} | `results.json -> h3.safety_rank.news.cities_where_safety_is_largest` |
| H3 search, cities where Safety had the largest gap | {{h3.safety_rank.search.cities_where_safety_is_largest}} of {{counts.cities}} | `results.json -> h3.safety_rank.search.cities_where_safety_is_largest` |
| H3 news, Safety's rank in Hong Kong | {{h3.safety_rank.news.by_city.hk.safety_rank}} of {{h3.safety_rank.news.by_city.hk.of}} | `results.json -> h3.safety_rank.news.by_city.hk` |
| H3 news, Safety's rank in New York City | {{h3.safety_rank.news.by_city.nyc.safety_rank}} of {{h3.safety_rank.news.by_city.nyc.of}} | `results.json -> h3.safety_rank.news.by_city.nyc` |
| H3 news, Safety's rank in London | {{h3.safety_rank.news.by_city.london.safety_rank}} of {{h3.safety_rank.news.by_city.london.of}} | `results.json -> h3.safety_rank.news.by_city.london` |
| Case study, length | {{case_study.months}} months | `results.json -> case_study.months` |
| Case study, dates | {{case_study.start}} to {{case_study.end}} | `results.json -> case_study.start`, `end` |

Notes on this table.

- A bootstrap p cannot go below one divided by the number of resamples plus one. With {{bootstrap_reps|comma}} resamples, a p at that floor means "none of the resampled slopes crossed zero," and it is printed as "p < 0.001".
- The count of category checks covers the twelve categories in each of the three cities. "Not a civic problem" is scored and shown, but it is not a category the rule can drop, so it is not in the count.
- In the Safety rank rows, rank 1 means the largest gap in that city. "[not available]" in a rank row means Safety could not be tested there.
- The "What surprised me" piece carries the four sentences you wrote on November 18, word for word (`src/poster_board.py`, `SURPRISED`). They are not rebuilt from the results. The first says search follows the official numbers far more closely than news: the slopes behind it are {{main.search.h1.est}} for search and {{main.news.h1.est}} for news, both weak by the analysis's own cutoff, and the two models pool different pairs and years. If a rebuild changes those numbers, reread your sentences.
- Rows from the H1 p-values down are not printed on the poster. They are here for questions.

## Fifteen questions a teacher is likely to ask

### Who actually did what?

An AI agent ran the whole study in one unattended session on November 17 and 18, 2026. It pulled the data, labeled the articles, ran the validation and the statistics, and drafted the documents, including this brief. The research question, the codebook, the indicators and the tests are in the methodology dated October 7, 2026, which was posted publicly before any outcome data were pulled. While the run was going I sent it instructions about which model should do the labeling, and those are in `deliverables/deviations.md`, section 2. No person hand-coded any article in this run.

[CAYDEN TO CONFIRM: your own role in the question, the codebook, the design and the interpretation]

### Why didn't you hand-code the articles?

The plan said I would hand-code about 900 items, and that agreement with my labels would decide which categories count. The study was compressed into one overnight run, and for that run I replaced my hand-coding with a second AI language model from a different company, which did not see the first labels. That is the first change listed in `deliverables/deviations.md`. It means the check shows that two AI coders agree, and it does not show that either one matches a human reader. The run left me a 50-item file, `deliverables/optional_hand_check_50.csv`, so I can code a sample by hand and compute my own kappa against both.

[CAYDEN TO CONFIRM: why the study was compressed into one run]

### How do you know the AI is right?

I can't show that it is right, and the poster does not say it is. What I can show is agreement: a second AI language model from a different company read the real headline and opening lines of a sample of articles without seeing the first labels, and overall kappa was {{v.cities.hk.overall_kappa}} in Hong Kong, {{v.cities.nyc.overall_kappa}} in New York City and {{v.cities.london.overall_kappa}} in London. Any category under {{v.threshold}} in a city was dropped there. A separate check on 2020 and later articles found that labels made from the words in the web address matched labels made from the real stored headline at kappa {{v.headline_check.hk.with_headline_words.kappa}}, {{v.headline_check.nyc.with_headline_words.kappa}} and {{v.headline_check.london.with_headline_words.kappa}} in the same order. Two models can share a blind spot, so until a person codes a sample I call this consistency between AI coders and nothing stronger.

Three scoring rules need saying out loud. The run set all three after it had seen provisional scores from a third AI pass and before the official second coder ran.

- The {{v.threshold}} rule counts only the validation items that stay in the main series. In Hong Kong that is {{v.cities.hk.n_items}} of {{v.cities.hk.n_items_all}} items.
- Where no page could be read and the article was from 2020 on, the second coder read the real stored headline alone: {{v.cities.hk.headline_only_items}} items in Hong Kong, {{v.cities.nyc.headline_only_items}} in New York City and {{v.cities.london.headline_only_items}} in London. One site challenged automated requests, so the run stopped using it and did not fetch its pages from anywhere else.
- The weights match the labeled sample by category and the attention index by outlet.

The table "Kappa under other scoring rules" at the end of this brief shows which categories fall under the bar with the plan as written and with each rule. If someone asks, say which categories the plan as written would have dropped. With the categories that rule keeps, the pooled news slope was {{checks.validation_rule_as_written.news.h1.est}} ({{checks.validation_rule_as_written.news.h1.ci_low}} to {{checks.validation_rule_as_written.news.h1.ci_high}}) across {{checks.validation_rule_as_written.news.h1.n_pairs}} pairs, against {{main.news.h1.est}} ({{main.news.h1.ci_low}} to {{main.news.h1.ci_high}}) across {{main.news.h1.n_pairs}} in the main model. No Hong Kong article from before 2020 is in the scored set, so the second coder never checked Hong Kong's labels for 2015 to 2019. {{run.second_coder_note}}

### What does a kappa of {{v.threshold}} mean, and why were some categories dropped?

Kappa is agreement beyond chance: 0 is what random labeling would give and 1 is perfect agreement, so {{v.threshold}} is a bit more than halfway from chance to perfect. It is the bottom of the range that Landis and Koch (1977) call substantial agreement. That cutoff is a convention, and it was fixed in the plan before any labels existed. The rule was that a category under the bar in a city gets one revision of its wording and a fresh sample, and if it still falls short it is dropped for that city. Dropping a category costs pairs, and it keeps the least consistent labels out of the results.

- Hong Kong, dropped: {{text.dropped_hk}}. Of the eight categories compared with official data: {{text.dropped_compared_hk}}.
- New York City, dropped: {{text.dropped_nyc}}. Of the eight compared: {{text.dropped_compared_nyc}}.
- London, dropped: {{text.dropped_london}}. Of the eight compared: {{text.dropped_compared_london}}.

Whether a revision was tried for a category, and what it scored, is in `data/public/validation_report.md`.

### Why do Hong Kong's early years rest on one outlet?

The news database stores real headlines only from 2020, so in every year the AI reads the headline words inside each article's web address plus the database's topic tags. Some Hong Kong outlets use number-only addresses, which leaves the tags alone. The plan said to test tag-only labels against real-headline labels on 2020 and later articles, and to leave those outlets out of 2015 to 2019 if the kappa fell under {{v.threshold}}. Rule applied: {{v.headline_check.rule.applied}}. {{v.headline_check.rule.text}}

One row in the checks table, marked exploratory, puts every main-panel outlet back into every year. The pooled news slope there was {{checks.exploratory_all_main_outlets_every_year.news.h1.est}} ({{checks.exploratory_all_main_outlets_every_year.news.h1.ci_low}} to {{checks.exploratory_all_main_outlets_every_year.news.h1.ci_high}}), against {{main.news.h1.est}} ({{main.news.h1.ci_low}} to {{main.news.h1.ci_high}}) in the main model.

### Why did the labeling model change during the run?

The run began labeling with an AI language model through a key that turned out to be on its provider's free tier, and it hit the daily request cap partway through the Hong Kong articles. A second model on the same key was started as a stopgap. I then sent the run an instruction to switch to a model from a different provider on a paid key, to relabel everything from zero so that one model labeled every article, and to keep the first provider's model as the blind second coder. The prompt has not changed since 2026-11-17T21:00:35Z. Two test runs, of 200 and 2,000 Hong Kong items, used it before the full run. No label from the two earlier models is used in any result. Before the full run the new model was compared with a larger model from the same provider on {{cmp.n}} items: kappa {{cmp.kappa_category}}, under a rule I set of {{cmp.threshold}} or higher to stay with the smaller one.

The model names and the full history are in `data/public/labeling_card.md`.

### Why did you pre-register, and why on November 17?

Pre-registering means posting the plan with a timestamp before any outcome data exist, so the hypotheses and the tests cannot be adjusted after seeing which way the results go. The plan was to post it in October on the Open Science Framework, and that step was meant to follow mentor approval. It was posted on GitHub on November 17, 2026, with copies of the plan saved by the Internet Archive, and the first query that returned outcome data ran after that. The commit is `{{run.prereg_commit}}`, tag `{{run.prereg_tag}}`, time {{run.prereg_utc}}, and the record is `deliverables/preregistration.md`. So it came later than planned and on a different site, and it still came before the data.

[CAYDEN TO CONFIRM: why the pre-registration moved from October to November 17]

[CAYDEN TO CONFIRM: date of mentor approval, if any]

### Why three cities?

Hong Kong, New York City and London are close in population and very different in politics and media. The study compares how attention behaves inside each city and never ranks one city's problems against another's, which keeps those differences from tilting the result. Three cities also give more city and category pairs for the pooled test: {{main.news.h1.n_pairs}} for news and {{main.search.h1.n_pairs}} for search. The plan named Hong Kong as the pilot, but in this run all three cities ran in the same night, so there was no separate pilot.

### Isn't official data the truth?

No, and the plan says so in its first section: official statistics are the benchmark here, and they have blind spots of their own. Recorded crime counts only what gets reported and recorded, and a shelter count moves with policy as well as need. So when attention and an official number disagree, the study lists the period and gives a proposed cause, and "the official measure changed how it counts" is one of the allowed causes. The run listed {{text.runs_total}} such periods of six months or more, and {{calc.runs.counting_change}} of them were put down to a change in how the official series counts. Those causes were proposed by AI, and I still have to review them.

### Why are the news slope and the search slope different?

The pooled slope was {{main.news.h1.est}} for news and {{main.search.h1.est}} for search, and the study did not test why they differ, so I can only list reasons. They cover different years (search starts in {{counts.search_first_month}}, news in {{counts.news_first_month}}), different places (search covers all of Hong Kong, the New York media market and all of England) and different pairs ({{main.news.h1.n_pairs}} for news, {{main.search.h1.n_pairs}} for search). They are also built differently: search uses term sets fixed in advance, and news uses AI labels on a small panel of outlets. Noise in either measure pulls its slope toward zero, so the noisier one will tend to show the smaller slope. The search numbers are also less settled than the plan intended: it called for three downloads on three different days, and the count so far is {{counts.search_downloads_per_request}}, from one night.

### What do the intervals tell you, and what don't they?

A 95% interval is the range the slope stays in when the years are reshuffled in 12-month blocks {{bootstrap_reps|comma}} times. It says how much the answer depends on which years happen to be in the sample. It says nothing about cause, and it leaves out errors in the labels, the outlet lists and the choice of indicators. The run also tried the method on made-up series with no link between them: the interval wrongly excluded zero in {{synthetic_tests.false_positive_check.intervals_that_wrongly_excluded_zero}} of {{synthetic_tests.false_positive_check.trials}} trials, which is {{synthetic_tests.false_positive_check.rate|pct}}, where an honest 95% interval would do that about {{synthetic_tests.false_positive_check.nominal_rate|pct}} of the time. If the first rate is the higher one, my intervals are too narrow for slow-moving series, and an interval that only just clears zero should be called borderline.

Setup of that test: {{synthetic_tests.false_positive_check.setup}}. With that few trials the rate is itself rough. The checks table also has an exploratory row with 24-month blocks.

### What would change your mind?

A human-coded sample that disagrees with the AI labels would change it first, because every news number rests on those labels. Next are the checks that the results hold: backup indicators, leaving out 2020 to 2022, leaving out every marked break, and lining official data up by release date. For news, the H1 interval stayed above zero in {{calc.news.checks_h1_above_zero}} of the {{calc.news.checks_run}} checks that ran (the ones where it did not: {{calc.news.checks_h1_not_above_zero_labels}}). For search it stayed above zero in {{calc.search.checks_h1_above_zero}} of {{calc.search.checks_run}} (the ones where it did not: {{calc.search.checks_h1_not_above_zero_labels}}).

If a result holds in the main model and fails one of those checks, say so before anyone asks, and name the check.

### What is the biggest weakness?

No person has checked the labels. Two AI coders agreeing is weaker than the hand-coded check the plan promised, and every news result depends on those labels. After that, the whole study ran in one night, so the search downloads could not be spread over three different days as planned (downloads per request so far: {{counts.search_downloads_per_request}}). London Health has no official series, because the source blocked automated collection, so that pair was never tested. The full list is in `deliverables/deviations.md`.

Also look at the row "Without 2020 to 2022" in the checks table. For news, the interval in that row {{calc.checks.without_covid.news.h1_interval}} (slope {{checks.without_covid.news.h1.est}}, {{checks.without_covid.news.h1.ci_low}} to {{checks.without_covid.news.h1.ci_high}}). For search it {{calc.checks.without_covid.search.h1_interval}} (slope {{checks.without_covid.search.h1.est}}, {{checks.without_covid.search.h1.ci_low}} to {{checks.without_covid.search.h1.ci_high}}). If either one includes zero, that link depends on the COVID years, and that belongs in this answer.

### What would you do next with more time?

The first job is the human check: code the 50-item file by hand, then a larger sample, and compute my kappa against both AI coders. Then I would take the search downloads the plan called for on different days, and find a route to the London Health series that was blocked. I would also read coverage from each listed disconnection and confirm or change its proposed cause. After that the plan is to revise the paper for the Journal of Emerging Investigators and publish the dataset.

### How much did it cost?

BigQuery billed {{run.bigquery_tb_billed}} terabytes across {{run.bigquery_queries}} queries, which is about {{run.bigquery_cost_usd|money}}. Language-model fees for the first coder came to {{run.anthropic_cost_usd|money}} in all, for {{run.items_labeled_total|comma}} labeled items plus the tests, which works out to about {{calc.cost_per_1000_items_usd|money}} per 1,000 articles. The second coder ran on its provider's free tier, logged as {{run.gemini_cost_usd|money}}. The official statistics and the search data were free downloads. My proposal budgeted under $300 for queries and AI labeling.

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

{{tables.main}}

**H1 by category**

Each row pools at most three cities, so read these as description. The main tests are the pooled rows above.

{{tables.h1_by_category}}

**H1 by city**

{{tables.h1_by_city}}

**Checks that the results hold**

{{tables.checks}}

**H3: share of periods moving in opposite directions, news**

{{tables.h3_news}}

**H3: share of periods moving in opposite directions, search**

{{tables.h3_search}}

**Disconnections of six months or more, by proposed cause**

{{tables.runs_by_cause}}

**Kappa by category and city**

{{tables.validation_kappa}}

**Kappa under other scoring rules**

This shows which categories fall below the bar under the plan as written and under each scoring rule the run added.

{{tables.validation_rule_variants}}

**Counts**

{{tables.counts}}
