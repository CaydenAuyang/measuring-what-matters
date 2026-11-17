<!--
TEMPLATE for the research paper. Build with:  .venv/bin/python src/build_paper.py
Every number, table and verdict is a token in double curly braces, filled at build time. Do not type result numbers here.
Token sources: results.json (no prefix), v. cmp. idx. hc. run. (see src/fill_template.py), and off. paper. (see src/build_paper.py).
Places that need a person or a last interpretive pass are marked with comments that start "FINAL PASS".
Layout comments read by src/md_to_docx.py: pagebreak, wide-pages, normal-pages.
-->

# Measuring What Matters: When a City's Problems Get Worse, Does Public Attention Follow?

**Cayden Auyang**, Pomfret School

Mentors: Mr. Qua and Mr. Lake. Independent study, fall 2026.

*Draft filled from the results file generated at {{generated_utc}} (UTC). Validation status: {{text.validation_status}}.*

## Abstract

<!-- FINAL PASS: Abstract. Once the final numbers exist (final second coder, second search download, full bootstrap), rewrite the three verdict sentences as plain prose in one direction, keep every number as a token, and keep the last two sentences about AI-only validation and narrow intervals. Remove the italic "Draft filled from" line above if it is no longer wanted. Target about 200 words. -->

Civic technology often treats news coverage and online activity as evidence of how a city is doing. This study tests that assumption for Hong Kong, New York City and London. Following a plan registered before any outcome data were pulled, it compares official statistics for eight problem categories with two measures of public attention: each category's share of local news coverage in GDELT ({{counts.news_first_month}} to {{counts.news_last_month}}) and its share of Google search interest ({{counts.search_first_month}} to {{counts.search_last_month}}). Every series is turned into yearly changes, and all city and category pairs are pooled in one model per source. An AI agent ran the study in one unattended session. An AI language model labeled {{counts.articles_labeled_main_panel_total|comma}} sampled articles from the main outlet panels, and a second AI language model checked the labels. The pooled slope of attention change on official change, in standard deviations, was {{main.news.h1.est}} for news (95% interval {{main.news.h1.ci_low}} to {{main.news.h1.ci_high}}) and {{main.search.h1.est}} for search ({{main.search.h1.ci_low}} to {{main.search.h1.ci_high}}). Verdict on H1, a positive but weak link: {{verdicts.h1_news}} for news, {{verdicts.h1_search}} for search. Verdict on H2, a stronger reaction to worsening than to improving: {{verdicts.h2_news}} for news, {{verdicts.h2_search}} for search. Verdict on H3, Safety showing the largest gap: {{verdicts.h3_news}} for news, {{verdicts.h3_search}} for search. No person checked the labels. In a test on unrelated made-up series, {{synthetic_tests.false_positive_check.intervals_that_wrongly_excluded_zero}} of {{synthetic_tests.false_positive_check.trials}} intervals wrongly excluded zero, so the intervals reported here are likely too narrow.

## 1. Introduction

Governments measure a city's problems with official statistics: crime counts, unemployment rates, rents, pollution readings, hospital waiting times. Journalists and residents register the same problems another way, through what local news covers and what people search for. I run OurCityHealth, a civic intelligence platform that scores cities from news coverage. The platform rests on an assumption I share with most of the civic technology field: that news and online discussion say something real about how a city is doing. I had never tested it. This study asks whether public attention to a problem moves with the official measure of that problem, and what it means when the two disagree.

Earlier work gives reasons to expect a loose link. Funkhouser (1973) compared 1960s news coverage with statistics on the same issues and found that coverage tracked real-world conditions poorly. Behr and Iyengar (1985) found that real conditions shaped public concern partly through how much television covered them. Soroka (2006) found that UK coverage and opinion responded more strongly to negative economic changes than to equal positive ones. Downs (1972) argued that attention to a problem fades even while the problem continues. Crime is the best-known gap. In 23 of 27 Gallup surveys since 1993, at least 60% of US adults said crime was rising nationally, while it fell over most of that period (Gramlich, 2024).

Other work shaped how attention is measured here. D'Amuri and Marcucci (2017) found that searches for jobs tracked official US unemployment closely. Mellon (2014) found that search data measured issue salience well for some issues, such as the economy, and poorly for others, so the search terms here were fixed in advance and weak categories are reported as weak. Gilardi, Alizadeh and Kubli (2023) found that a language model labeled political text more accurately than crowd workers on most of their tasks, though accuracy varied by task, which is why the plan checks the labels before the analysis. Hammond and Weidmann (2014) found that machine-coded locations in GDELT's event data are unreliable below the country level, so news is selected by local outlet first. Landis and Koch (1977) supply the agreement threshold: a Cohen's kappa of 0.61 or higher, which they call substantial agreement.

Official statistics are the benchmark in this study. They are also measurements with their own blind spots. Recorded crime, for example, counts only what is reported and recorded. So the study treats official data and public attention as two imperfect measures of the same problems. Where they disagree, the cause is classified, and neither side is assumed to be right.

The design was fixed in a methodology document dated October 7, 2026, and posted publicly on November 17, 2026, before any outcome data were pulled. The plan expected six weeks of work, with hand-coding by me and by a classmate. Instead, an AI agent ran every stage in one unattended session on November 17 and 18, 2026, and a second AI language model took the place of the human coders (Section 4). The paper reports four pre-registered tests. Everything else is labeled as description, a check, or exploratory.

## 2. Research questions and hypotheses

The questions and hypotheses come from the pre-registered methodology.

1. **Can scattered informal signal be turned into a defensible monthly measure of attention?** The plan's rule: a category is analyzed in a city only if the AI labels behind it agree with a second coder at a Cohen's kappa of 0.61 or higher. The plan named my hand-coding as that second coder. In this run it was another AI language model (Section 4).
2. **Does attention move with the official measure of the same problem?**
   - **H1.** Year-over-year changes in news attention correlate positively with changes in the matching official indicator, but weakly.
   - **H2.** Attention reacts more to a problem getting worse than to it getting better.
   - **Exploratory.** Whether news or search moves first, reported for each category without a prediction.
3. **Where do official data and attention stay disconnected, and why?**
   - **H3.** Safety shows the largest gap between attention and official data, measured as the share of months in which the two move in opposite directions, in at least two of the three cities.
   - Following Downs (1972), long stretches where a problem stays bad while coverage drops are expected and are reported.

The plan tests H1 and H2 with one pooled model each, run for news and for search: four main tests. Results for the 48 city, category and source pairs are description, with p-values adjusted by the Benjamini-Hochberg method. The four categories with no official statistic (Governance, Culture, Technology, Community) are described and are not tested.

## 3. Data and methods

This section describes the method as it was carried out. Section 8 lists every difference from the plan.

### 3.1 Cities

Hong Kong, New York City and London have similar populations, roughly 7.5 to 9 million each, and very different political and media systems. The comparison runs inside each city: attention to a problem against that city's own official measure. The cities' problems are never compared with each other. The plan made Hong Kong the pilot. The run compressed all stages into one session.

### 3.2 Codebook

Every article gets one label: the main problem it describes, or "not a civic problem." The twelve categories are OurCityHealth's dimensions, rewritten with boundaries. Eight are compared with official data. Four have no official statistic.

**Table 1.** The codebook, as pre-registered.

| Category | Covers | Goes elsewhere | Compared with official data |
| :-- | :-- | :-- | :-- |
| Safety | Crime and personal safety | National security cases (Governance); road crashes (Transport) | Yes |
| Economy | Jobs, unemployment, wages, business conditions, poverty, inequality | Everyday prices (Cost of Living) | Yes |
| Housing | Rent, home prices, supply, living conditions, subdivided flats, homelessness | Other prices (Cost of Living) | Yes |
| Transport | Transit reliability, congestion, commuting, fares, road safety | | Yes |
| Environment | Air and water pollution, green space, climate hazards such as typhoons, floods, and heat | | Yes |
| Health | Access to care, waiting times, public health, disease, mental health, overdoses | | Yes |
| Education | School quality, access, attainment, teacher supply | | Yes |
| Cost of Living | Everyday prices other than housing: food, utilities, goods | Rent and home prices (Housing); fares (Transport) | Yes |
| Governance | Government decisions, trust in institutions, corruption, elections, national security cases | | No |
| Culture | Arts, heritage, and nightlife as civic issues, such as venue closures or funding cuts | Event listings and reviews (not a civic problem) | No |
| Technology | Digital access, outages, cyberattacks on public services, privacy | Tech industry and startup news (not a civic problem) | No |
| Community | Relations between residents: cohesion, discrimination, neighborhood life | Trust in government (Governance) | No |

Four pre-registered tie-break rules complete the codebook. They cover items with several topics, protests, immigration, and tone, which is labeled separately as negative, neutral or positive. The labeling card gives them word for word.

### 3.3 Official indicators

Each compared category has a main indicator and a backup in each city, all from official bodies. The plan lists 24 main indicators and 23 backups. The run built {{paper.main_built}} main indicators and {{paper.backup_built}} backups. Missing main indicators: {{paper.main_missing}}. An AI agent built each series by script from the publisher's open files. Each series is used at its own frequency, and nothing is interpolated. Table 2 shows what each main series covers.

**Table 2.** The main official indicators as built. The coverage column gives the first and last period with a value.

{{paper.indicator_table}}

Three differences from the plan matter most. London Health is missing because the NHS England statistics pages returned a browser challenge, and the rules for this run say to stop when a site blocks collection. New York Health uses deaths from all causes from an open CDC file that starts in {{off.nyc_health_main.first_period}}, because the planned source sits behind a data-use form. Hong Kong Health and Hong Kong Transport start later than planned.

Every series is turned into a change from the same period a year earlier, in which a positive number means the problem got worse (Appendix C of the methodology). Counts, pollution levels and waiting times change in percent, computed as 100 times the natural log of the ratio. Rates, shares and scores change in points. For prices and rents, the 12-month rate is computed first and its yearly change is measured in points. Indicators that are better when higher have their sign reversed. Every break in the plan's breaks table is marked in the data, along with breaks the run found in the sources.

### 3.4 News attention from GDELT

News attention comes from GDELT's Global Knowledge Graph (GDELT Project, 2026), which records each online article's source, places, themes and tone from February 2015. The run queried the partitioned BigQuery table, filtered every query on the partition date, and billed {{run.bigquery_tb_billed}} terabytes in total.

**Outlets.** The outlet lists were fixed in Appendix A of the methodology. The main series uses a fixed panel of outlets that GDELT recorded steadily in every year from 2015, so an outlet joining or leaving cannot shift the shares. The panel has {{counts.outlets_main_panel.hk}} outlets in Hong Kong (the South China Morning Post's Hong Kong section, Oriental Daily and HK China News Agency), {{counts.outlets_main_panel.nyc}} in New York (Daily News, NBC New York and Gothamist) and {{counts.outlets_main_panel.london}} borough papers in London. The full lists hold {{counts.outlets_listed_total}} outlets and serve as a check.

**Filters and duplicates.** Articles pass a city filter based on GDELT's location tags (Hong Kong and New York) or on the web address (London). Duplicates are removed by web address, and a London story that runs in several papers in one month counts once. Table 17 gives the exact readings.

**Sample.** The pre-registered sample is up to 333 articles per outlet per month in Hong Kong and New York and up to 66 per paper in London, drawn with a fixed seed. Articles were labeled in rounds that add the same number for every outlet and month, and only complete rounds are used. This draft uses up to {{idx.caps_hk_nyc_london.0}} articles per outlet per month in Hong Kong and New York and up to {{idx.caps_hk_nyc_london.2}} in London. Table 3 gives the counts. Its count of official series includes any extra series the run built beyond the planned indicators.

**Table 3.** What the study rests on.

{{tables.counts}}

<!-- FINAL PASS: Table 3. When this template was written, the count of official series (47) included two extra Hong Kong series the tests do not use (hk_safety_main_monthly and hk_environment_backup_monthly), while London Health main and backup are missing. The sentence above the table covers this. Drop that sentence if the count is changed to planned series only. -->

**What the model reads.** GDELT stores headlines only from 2020. So that every year is labeled from the same inputs, an AI language model reads the outlet name, any headline words in the article's web address, and the first 30 GDELT theme tags. It never sees the article text. For an outlet with number-only addresses it reads theme tags alone. Of {{run.items_sampled_total|comma}} sampled items, {{run.items_no_input|comma}} had neither headline words nor theme tags and are left out.

**Labeling.** The prompt holds the codebook and the tie-break rules word for word, plus a description of the inputs and examples of items that are not a civic problem. It was frozen before labeling began. The exact model, settings and prompt are in the labeling card (`data/public/labeling_card.md`).

**Index.** For each outlet and month, a category's share is its labeled articles divided by all labeled articles from that outlet, including those labeled not a civic problem. A city's attention share is the average of its outlets' shares, each outlet weighted equally. Shares cancel out the growth in GDELT's source list and the difference in size between cities. The negative-tone share, used in one check, counts only articles labeled negative.

### 3.5 Search attention from Google Trends

Search attention comes from Google Trends (Google, 2026). Each category has one fixed set of search terms per city, listed in Appendix B of the methodology, in Traditional Chinese plus some English for Hong Kong and in English elsewhere. No term was changed after data were seen. The geography is Hong Kong as a whole, the New York media market, and England for London.

Trends scales each request from 0 to 100, so every request includes the Economy set as an anchor. Each set is divided by Economy in its own request, and a category's share is its ratio divided by the sum of the twelve ratios. The requests cover web search from {{counts.search_first_month}} to {{counts.search_last_month}}. An AI agent downloaded the files from the Trends website. The plan called for three downloads on different days. The run took its downloads within one night. Downloads per request behind this draft: {{counts.search_downloads_per_request}}.

A set that reads zero in more than 10% of months is reported as too sparse to test. It is not replaced, and it stays in the denominator. The sparse sets were: Hong Kong, {{paper.sparse_hk}}; New York, {{paper.sparse_nyc}}; England, {{paper.sparse_london}}. Google's charts note that its methods changed at the start of 2011, 2016 and 2022, and search changes in those years are marked as breaks.

### 3.6 Yearly changes and matching

The main test compares changes. Two series that both trend for twenty years will correlate even if they are unrelated. Yearly changes remove that trap, and seasonal patterns with it.

Attention is matched to each official series at that series' own frequency: the same month for a monthly series, the mean of the quarter for a quarterly one, and the mean of the year for an annual one (the September to August school year for Education). A series published as a 3-month or 12-month average is matched with attention averaged over the same window. The yearly change in attention is the share in that window minus the share a year earlier, in percentage points.

For news, the run computes this change on a matched panel (`logs/decisions.md`). Each outlet's share is compared with the same outlet a year earlier, and those changes are averaged across the outlets present in both periods. Without it, an outlet rejoining the panel would show up as a jump in every category.

A pair is tested only if it has at least 24 matched months, 8 quarters or 5 years. The analysis code set this floor. Each period is flagged if it falls in 2020 to 2022, in a marked break of the official series, or in a marked break of the attention series (Hong Kong in 2019 and 2020, and the Google note years for search).

### 3.7 The pooled model

Before pooling, each pair's official change and attention change are divided by their own standard deviation, computed from periods outside the marked breaks so that the COVID years do not set the scale. Slopes are then in standard deviations, and pairs measured in different units can be pooled.

H1 is tested with one regression of attention change on official change across all pairs, with a separate intercept for each pair. Every pair gets equal total weight, so a monthly pair with about 120 points does not swamp an annual pair with about 10. H2 uses the same model with official change split into two terms, one for periods when the problem worsened and one for periods when it improved. H2 holds if the worsening slope is larger. Each model is run for news and for search. These four models are the pre-registered main tests.

The analysis code reads the results by a fixed rule. H1 or H2 counts as supported when the whole 95% interval lies above zero, as failed when it lies below zero, and as not supported otherwise. For H2 the interval is for the difference between the two slopes. The code also calls a slope below 0.3 weak. The plan predicted a weak link and did not set that cutoff.

### 3.8 The bootstrap

Confidence intervals come from a moving-block bootstrap. Within each pair, blocks of 12 consecutive months (4 quarters, or 1 year) are drawn with replacement, and the model is refit on each resample. The interval runs from the 2.5th to the 97.5th percentile of the resampled slopes. The main models in this draft use {{bootstrap_reps}} resamples, and the checks use {{paper.bootstrap_reps_checks}}. Yearly changes in monthly data overlap, so the effective sample is reported as independent pair-years: each pair's number of periods divided by the periods in a year.

Before the code touched real data, it was run on made-up series with known answers. It recovered a slope, an asymmetry and a three-month lag that were built in. One test is a warning. On unrelated made-up series with strong persistence, {{synthetic_tests.false_positive_check.intervals_that_wrongly_excluded_zero}} of {{synthetic_tests.false_positive_check.trials}} intervals wrongly excluded zero, against an expected rate of {{synthetic_tests.false_positive_check.nominal_rate|pct}} (Section 7).

### 3.9 Disconnections and checks

**Disconnection (H3).** For each pair, the share of periods in which attention and the official measure moved in opposite directions. Within each city the compared categories are ranked by that share, and H3 holds for a source if Safety ranks first in at least two cities. For monthly pairs the run also lists every stretch of six or more months in a row of opposite movement, and gives each one of the plan's five causes: the official measure changed how it counts, a real event drew coverage the indicator does not capture, attention followed a news cycle, the two measure different parts of the problem, or unclear. The run assigned causes by a fixed rule based on the marked breaks and a short list of events from the plan's breaks table. The plan also called for reading a sample of each period's coverage. For {{paper.runs_read_coverage}} of the stretches, an AI agent read a seeded sample of that period's stories and revised the cause where the sample pointed elsewhere. The rest have the rule alone. No person read the coverage, so every cause is labeled as proposed by AI, for Cayden to confirm.

**Checks that the results hold.** The plan lists backup indicators, the COVID years and other breaks left out, official series aligned by release date, all listed outlets, and negative-tone share. Its outlet notes add Hong Kong without HK China News Agency and London without the seven borough papers whose volume jumped. The run added two exploratory rows. The labeled sample for the check with all listed outlets was: {{paper.check_sample}}.

The plan also describes a social media snapshot and an optional pre-2015 news extension. Neither feeds any result in this paper (Section 8).

### 3.10 Pre-registration

The methodology, the outlet lists, the search terms and the indicator rules were committed to a public GitHub repository on November 17, 2026 (commit `e8d5f32`, tag `prereg-v1`, commit time {{run.prereg_utc}}), before any outcome data were pulled. The Internet Archive saved copies of the raw methodology file and the source inventory, and each copy matched the local file's SHA-256 hash. The record is in `deliverables/preregistration.md`, and the repository is at {{run.repository}}.

[CAYDEN TO CONFIRM: whether and when his mentors approved the plan]

<!-- FINAL PASS: Pre-registration. Check deliverables/preregistration.md for the final Internet Archive status of the repository page and add one sentence here if it was saved. -->

## 4. Validation

### 4.1 What was planned and what was done

The plan called for me to hand-code about 900 items, and for a classmate to code 150 of them. That did not happen in this run. Two AI language models labeled the same articles independently, and their agreement decides which categories are analyzed. This section reports agreement between two AI coders. It does not show that either coder matches a human reader. Nobody hand-coded any article.

The second coder is an AI language model from a different model family than the first. It never sees the first coder's labels. It reads each article's real headline and opening lines, taken from the live page or the Internet Archive. It applies the same codebook and also records whether the article is really about the study city.

### 4.2 The validation set and the rule

For each city the run aimed for about 300 items from the main-panel sample (Table 4 gives the number scored). Each of the thirteen labels (the twelve categories and "not a civic problem") got at least 20 items, and the rest followed how often the first coder used each label. Items were spread across outlets and across three periods. If a page could not be fetched, the next candidate from the same category, in a fixed random order, took its place. Agreement is weighted back to the full sample.

Two sites limited what the second coder could read (`logs/decisions.md`). The South China Morning Post's site blocked automated requests. For its items from 2020 onward the second coder read only the headline that GDELT stored, and its earlier items were replaced by other items. HK China News Agency's pages were gone from the live site, so Internet Archive copies were used where they exist.

The rule is the plan's. A category is analyzed in a city only if Cohen's kappa for that category is at least 0.61. A category that falls short gets one revision of its wording, a fresh sample and one more test. If it still falls short, it is dropped for that city.

### 4.3 Agreement by category

<!-- FINAL PASS: Validation. After the blind second coder has run (status "final", scored against "coder2"), delete the sentence that explains the two status words, check that all three cities appear in Table 4 and in the kept and dropped lists, and add one plain sentence on any category that was revised and retested (the detail is in data/public/validation_report.md). -->

The status of these numbers is: {{text.validation_status}}. The scoring file records the pass they were scored against as `{{v.scored_against}}`, where `coder2` is the blind second coder and `thirdpass` is a stand-in pass by a third AI model, used before the second coder had run.

**Table 4.** Cohen's kappa between the two AI coders, by category and city, with the decision for each category.

{{tables.validation_kappa}}

Overall kappa was {{v.cities.hk.overall_kappa}} in Hong Kong (95% interval {{v.cities.hk.overall_ci_low}} to {{v.cities.hk.overall_ci_high}}), {{v.cities.nyc.overall_kappa}} in New York City ({{v.cities.nyc.overall_ci_low}} to {{v.cities.nyc.overall_ci_high}}) and {{v.cities.london.overall_kappa}} in London ({{v.cities.london.overall_ci_low}} to {{v.cities.london.overall_ci_high}}). Kappa on tone, in the same order, was {{v.cities.hk.tone_kappa}}, {{v.cities.nyc.tone_kappa}} and {{v.cities.london.tone_kappa}}. The negative-tone check depends on the tone labels.

- **Hong Kong.** Kept: {{text.kept_hk}}. Dropped: {{text.dropped_hk}}. Dropped among the eight compared categories: {{text.dropped_compared_hk}}.
- **New York City.** Kept: {{text.kept_nyc}}. Dropped: {{text.dropped_nyc}}. Dropped among the eight compared categories: {{text.dropped_compared_nyc}}.
- **London.** Kept: {{text.kept_london}}. Dropped: {{text.dropped_london}}. Dropped among the eight compared categories: {{text.dropped_compared_london}}.

When a compared category is dropped in a city, that city's news pair for the category leaves every test. Search pairs are not affected, because search needs no labels.

### 4.4 The city filter and the headline check

The second coder judged the share of articles not really about the study city, weighted to the full sample, at {{v.cities.hk.not_about_city_share|pct}} in Hong Kong, {{v.cities.nyc.not_about_city_share|pct}} in New York City and {{v.cities.london.not_about_city_share|pct}} in London.

GDELT stores real page titles from 2020 onward. For a sample of 2020 to 2026 articles, the first coder labeled each article twice: once from the stored headline alone, and once from the inputs used for every year. For items with headline words in the address, the two sets of labels agreed at kappa {{v.headline_check.hk.with_headline_words.kappa}} in Hong Kong, {{v.headline_check.nyc.with_headline_words.kappa}} in New York City and {{v.headline_check.london.with_headline_words.kappa}} in London. For Hong Kong items with theme tags alone ({{hc.cities.hk.theme_tags_only.n|comma}} items), kappa was {{v.headline_check.hk.theme_tags_only.kappa}}. The other two cities had too few such items to test.

The plan set a rule for this case. If theme-tag-only labels fall below 0.61, the outlets with number-only addresses are left out of 2015 to 2019. The outcome recorded by the run: {{v.headline_check.rule.text}}

London's borough papers had number-only addresses for part of 2015 and 2016. They have headline words in every later year, so they stay in.

### 4.5 Consistency checks, and what this section does not show

Three checks stand in for the plan's second human coder and for my own re-labeling. First, the first coder was compared with a larger model from the same family on {{v.consistency.first_coder_vs_larger_model.n}} items with the same inputs: kappa {{v.consistency.first_coder_vs_larger_model.kappa}} on category and {{v.consistency.first_coder_vs_larger_model.tone_kappa}} on tone. Second, a third AI pass by a different model read the same headlines and opening lines as the second coder. On {{v.consistency.third_pass.n}} items its kappa was {{v.consistency.third_pass.kappa_vs_second}} against the second coder and {{v.consistency.third_pass.kappa_vs_first}} against the first. Third, the second coder labeled {{v.consistency.relabel.n}} of the same items again in a fresh request: kappa {{v.consistency.relabel.kappa}}.

Two AI models can agree with each other and both be wrong in the same way. A file of 50 validation items with a blank label column (`deliverables/optional_hand_check_50.csv`) was prepared so that a person can code them later. Nobody has filled it in.

## 5. Results

Every number in this section comes from `data/public/results.json`, generated at {{generated_utc}} (UTC). Table 5 holds the four pre-registered tests.

**Table 5.** The pooled models (the pre-registered main tests). Slopes are in standard deviations of attention change per standard deviation of official change. A positive slope means attention rose when the official measure worsened.

{{tables.main}}

### 5.1 H1: does attention move with the official measure?

{{verdicts.h1_news_sentence}}

{{verdicts.h1_search_sentence}}

The two models pool different pairs over different years, so their slopes are not directly comparable. Tables 6 and 7 fit the same model within each category and within each city. They are description. Each row rests on a few pairs, and no row is a test of H1.

**Table 6.** The H1 slope within each category (description).

{{tables.h1_by_category}}

**Table 7.** The H1 slope within each city (description).

{{tables.h1_by_city}}

### 5.2 H2: does attention react more to worsening?

{{verdicts.h2_news_sentence}}

{{verdicts.h2_search_sentence}}

### 5.3 Lead and lag (exploratory)

The plan made no prediction here. Table 8 gives, for each category, the lag at which the correlation between attention change and official change, averaged across cities, was largest in size. A positive lag means attention moved after the official measure. A lag at either end of the range should be read with caution. Of {{text.leadlag_pairs}} monthly pairs, {{text.leadlag_pairs_p_below_05}} had a p-value below 0.05 for their largest correlation, with no adjustment for the number of pairs. The p-value comes from a permutation test that shifts the attention series in time.

**Table 8.** Lead and lag between attention and the official measure, by category (exploratory).

{{tables.leadlag_by_category}}

Table 9 compares news with search. A positive lag means news moved after search. The table covers all twelve categories, including sparse search sets and news categories dropped in validation.

**Table 9.** Lead and lag between news and search, by category (exploratory).

{{tables.news_vs_search}}

### 5.4 H3: where do the two disconnect?

{{verdicts.h3_news_sentence}}

{{verdicts.h3_search_sentence}}

Tables 10 and 11 give the share for every pair, with the number of periods in parentheses. Annual pairs rest on about ten periods, so one year moves their share a long way.

**Table 10.** Share of periods in which news attention and the official measure moved in opposite directions.

{{tables.h3_news}}

**Table 11.** Share of periods in which search attention and the official measure moved in opposite directions.

{{tables.h3_search}}

**Disconnections.** The run found {{text.runs_total}} stretches of six or more months of opposite movement: {{text.runs_news}} in news and {{text.runs_search}} in search. Table 12 counts them by cause, and Appendix Table A4 lists the twenty longest. Every cause is proposed by AI, for Cayden to confirm: {{paper.runs_read_coverage}} after an AI agent read a seeded sample of that period's stories, and {{paper.runs_by_rule_only}} by rule alone. The stretches labeled as attention following a news cycle are the pattern Downs (1972) expected: the official measure kept worsening while the category's share of attention fell.

**Table 12.** Disconnections of six months or more, by proposed cause.

{{tables.runs_by_cause}}

**Case study.** The longest news disconnection with a proposed cause other than unclear was in {{text.case_city}}, in the {{text.case_category}} category, from {{case_study.start}} to {{case_study.end}} ({{case_study.months}} months). Over those months the official measure was {{case_study.official_direction}}, with a mean yearly change of {{case_study.mean_official_change_sd}} standard deviations (worse is positive). The category's share of {{text.case_source}} attention was {{case_study.attention_direction}}, with a mean yearly change of {{case_study.mean_attention_change_sd}} standard deviations. Proposed cause: {{case_study.proposed_cause}}. Proposed by: {{case_study.proposed_by}}.

> Evidence recorded by the run: {{case_study.evidence}}

<!-- FINAL PASS: Case study. After a person has looked at this period's coverage and the official series' documentation, replace the proposed cause and the evidence line with a confirmed account, or keep the "proposed by AI, for Cayden to confirm" label. -->

### 5.5 The 48 pairs (description)

Of the 48 city, category and source pairs, {{text.pairs_tested}} could be tested and {{text.pairs_not_tested}} could not. A pair is left out when its official series is missing, its search set is too sparse, its news category was dropped in validation, or it has too few matched periods. After the Benjamini-Hochberg adjustment, {{text.pairs_adjusted_p_below_05}} pairs had an adjusted p-value below 0.05 for the correlation between attention change and official change. Each p-value comes from the block bootstrap. Appendix Table A1 gives every pair.

### 5.6 Checks that the results hold

Table 13 reruns the H1 model and the H2 difference under each check. A cell marked "not run" means the check does not apply to that source or could not be computed. The two rows labeled exploratory were not in the plan. A check agrees with the main result when its slope has the same sign and its interval sits on the same side of zero. Where a check's interval includes zero and the main model's does not, the verdict depends on that choice. Appendix Tables A2 and A3 add p-values and sample sizes.

**Table 13.** Checks that the results hold.

{{tables.checks}}

<!-- FINAL PASS: Checks. Add one or two plain sentences saying which checks changed a verdict, if any, using the rows of Table 13. -->

### 5.7 Current-year ranking (description)

For each city, the eight compared categories are ranked twice: by how far the official indicator now sits from its own 2015 to 2019 average, and by the category's share of news over the latest twelve months. The Spearman rank correlation between the two orderings was {{text.ranking_rho_hk}} in Hong Kong, {{text.ranking_rho_nyc}} in New York City and {{text.ranking_rho_london}} in London, across {{ranking.hk.n_categories}}, {{ranking.nyc.n_categories}} and {{ranking.london.n_categories}} categories. The rankings are in Appendix Tables A5 to A7. A series with few values in 2015 to 2019 gives an unstable distance, and a category dropped in validation still shows an unvalidated news share.

<!-- FINAL PASS: Ranking. Read each ranking table for implausible distances before quoting any of them. When this template was written, ranking_block in src/analysis.py selected official rows by role == "main", which for Hong Kong Safety mixes the extra monthly series hk_safety_main_monthly with the annual totals and gives a distance near minus 11 standard deviations. Selecting by series_id (city_category_main) would fix it. -->

### 5.8 The four signal-only categories (description)

Table 14 gives each signal-only category's mean share of local news in 2015 to 2019 and in 2023 to 2026, with its peak month. The plan called for naming the major events behind the peaks. The run reports the peak months and does not name events. A category dropped in validation for a city still appears in the table, and its row is not validated.

**Table 14.** Signal-only categories: share of local news (description).

{{tables.signal_only_news}}

<!-- FINAL PASS: Signal-only categories. Name the event behind each peak month only if a person has confirmed it. -->

## 6. Discussion

<!-- FINAL PASS: Discussion. This section is neutral on purpose, because the numbers were provisional when it was written. After the final numbers exist: (1) say in plain prose what was found for H1, H2 and H3, using the verdict sentences; (2) say which checks in Table 13 changed a verdict; (3) add what the result means for OurCityHealth; (4) keep the paragraph on what the AI-only validation and the narrow intervals mean for how far to trust any verdict. Interpretation is Cayden's to write or confirm. -->

This section says what each possible outcome would mean and points to the verdicts in Section 5.

**H1.** A verdict of supported for a source means attention in that source carries some information about conditions: when the official measure worsens, attention tends to rise. A small slope would still mean that most of the movement in attention comes from something else. A verdict of not supported means this design could not tell the link from zero. It does not show that there is no link. A verdict of failed means attention moved against the official measure. The verdicts were: {{verdicts.h1_news}} for news and {{verdicts.h1_search}} for search.

**H2.** A verdict of supported means attention registers decline more than recovery, as Soroka (2006) found for UK economic news. A verdict of not supported means the two reactions could not be told apart with this sample. The verdicts were: {{verdicts.h2_news}} for news and {{verdicts.h2_search}} for search.

**H3.** A verdict of supported means crime is where attention and official counts part ways most often, in line with the survey evidence in Gramlich (2024). A verdict of not supported means another category showed the largest gap in most cities, and Tables 10 and 11 name it. The verdicts were: {{verdicts.h3_news}} for news and {{verdicts.h3_search}} for search. In both cases the measure counts direction only. It says nothing about which side is right.

**Disconnections.** Each long disconnection has more than one possible reading. The run's labels are a first pass, and they need a person who knows each city to confirm them.

**A news-based score.** OurCityHealth scores cities from news coverage. Where such a score can stand in for conditions has to be read category by category, from Table 6 and Appendix Table A1, and only for categories that passed validation in that city.

**How far to trust any verdict.** Every verdict rests on labels that no person checked and on intervals that are likely too narrow. I would treat a verdict of supported as provisional until a hand-coded sample confirms the labels.

## 7. Limitations

The first seven limitations were stated in the plan.

- **Official statistics are a benchmark with blind spots.** When attention and an official measure disagree, the official measure may be the one that is wrong.
- **The news panels are narrow.** GDELT's Hong Kong coverage leans on a few outlets, and the Hong Kong main panel is mainstream and pro-establishment. London's main panel is borough papers, with no citywide outlet. Machine-coded GDELT locations are unreliable below the country level (Hammond and Weidmann, 2014), and the plan's feasibility test found the same problem for New York.
- **Early labels rest on thin inputs.** Labels for 2015 to 2019 rest on web-address headlines and theme tags, and on theme tags alone for Hong Kong outlets with number-only addresses.
- **Search geography is wider than the city** in New York (the media market) and in London (England).
- **Prices are not city-level.** New York's price series cover the metro area. London's inflation is UK-wide and includes some rent.
- **Attention is volume.** It shows how much a problem is discussed. It does not show what people think should be done about it.
- **The study does not test causes.** It shows whether series move together and which moves first. Its explanations of disagreements are judgments.

The run added these.

- **AI did the labeling and the validation.** The kappa values in Section 4 measure agreement between two AI language models. The plan's central check, agreement with my own hand-coding, was not done.
- **Theme-tag-only labels are weak.** In the headline check they agreed with real-headline labels at kappa {{v.headline_check.hk.theme_tags_only.kappa}}. The pre-registered rule removes the affected outlets from 2015 to 2019 only. HK China News Agency uses number-only addresses in every year, so its later labels still rest on theme tags alone. Table 13 includes a check without that outlet.
- **Hong Kong 2015 to 2019 may rest on one outlet.** Whether the headline-check rule applied in this run: {{v.headline_check.rule.applied}}. Where it applied, Hong Kong's news series for those years is the South China Morning Post's Hong Kong section alone, and that outlet's items from before 2020 could not be put in the validation set.
- **The labeled sample depends on the round reached.** The plan is up to 333 articles per outlet per month in Hong Kong and New York and 66 in London. This draft uses up to {{idx.caps_hk_nyc_london.0}} and {{idx.caps_hk_nyc_london.2}}.
- **Search data come from one night.** Downloads per request in this draft: {{counts.search_downloads_per_request}}. Downloads taken close together mostly repeat the same sample of searches. Several search sets also read "<1" in most months and carry little signal.
- **Some official series are missing or short.** Missing: {{paper.main_missing}}. New York Health starts in {{off.nyc_health_main.first_period}}, so its yearly changes fall in or just after the COVID years.
- **The intervals are likely too narrow.** On unrelated made-up series the bootstrap wrongly excluded zero in {{synthetic_tests.false_positive_check.intervals_that_wrongly_excluded_zero}} of {{synthetic_tests.false_positive_check.trials}} trials (Section 3.8). An interval that only just excludes zero should not be read as firm.
- **Disconnection causes are a first pass.** Of {{text.runs_total}} causes, {{paper.runs_by_rule_only}} come from a fixed rule alone. For the rest an AI agent also read a seeded sample of stories. No person read the coverage.

## 8. Deviations from the pre-registered plan

The plan is the methodology posted on November 17, 2026 (commit `e8d5f32`, tag `prereg-v1`). Tables 15 to 17 list every place where the study did something different. `deliverables/deviations.md` holds the same list with more detail.

**Decided before the run.** The largest change is who checked the labels: a second AI language model in place of my hand-coding, and further AI passes in place of a classmate and of my own re-labeling. The pre-registration moved from the Open Science Framework in October to GitHub and the Internet Archive on November 17. The search downloads and the whole schedule were compressed into one session.

**Decided during the run.** After the first labeling key hit a daily cap, I sent new instructions by message. The first coder changed to a small model from a different provider, and every item was relabeled so that one model labels the whole sample. The provider first chosen supplied the second coder instead. The prompt never changed.

**Forced by what the run found.** London Health is missing, New York Health comes from a different CDC file, and a small share of sampled items had nothing for the model to read.

**Table 15.** Deviations in sections 1 to 3 of `deliverables/deviations.md`.

| # | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| 1.1 | I hand-code about 900 items. Agreement between the AI labels and my hand-coding decides which categories are analyzed. | A second AI language model from a different model family codes the same validation set blind, from the real headline and opening lines. The sample design, kappa, the 0.61 threshold, one revision and the drop rule are as written. | The study was compressed into one run with nobody available to hand-code. This measures agreement between two AI coders. |
| 1.2 | A classmate labels 150 of the same items. I re-label 50 items two weeks later. | A third AI pass by a different model codes the same items. The second coder re-labels 50 items in a fresh request. | Same reason. |
| 1.3 | Pre-registration on the Open Science Framework in October, after the mentors approve the plan. | Pre-registration on GitHub and the Internet Archive on November 17, 2026, before any outcome data. | Later than planned. [CAYDEN TO CONFIRM: date of mentor approval, if any] |
| 1.4 | Each Trends request is downloaded on three different days and averaged. | Downloads taken within one night. Downloads per request in this draft: {{counts.search_downloads_per_request}}. | One-night run. |
| 1.5 | Work spread over October 12 to November 20. | All stages ran in one session on November 17 and 18. | Compressed schedule. |
| 2.1 | The first coder is a small model from the provider first chosen. | The first coder is a small model from a different provider. Every item was labeled by this one model. Items the earlier model had labeled were relabeled. | The first provider's key hit a daily cap (3.1). My instruction during the run. |
| 2.2 | The second coder is a model from a different family than the first. | Still true. The second coder is a model from the provider first chosen for labeling, run blind after its daily quota reset. The third pass is a different model from that provider. | My instruction during the run. |
| 2.3 | Model and prompt are frozen before the full run. | The prompt was frozen once and never changed. The model changed before the full run (2.1). The first 2,000 items were labeled first to measure cost: {{run.first2000_cost_usd|money}}, or {{paper.cost_per_1000_items|money}} per 1,000 items. The projected cost of the full sample was under the cap of ${{run.language_model_cap_usd}}, so the sample was not shrunk. | My instruction: measure the real cost per item first. |
| 2.4 | Not in the plan. | The first coder was compared with a larger model from the same family on {{cmp.n}} of those items. Kappa was {{cmp.kappa_category}} on category and {{cmp.kappa_tone}} on tone. The rule set beforehand was to keep the smaller model at {{cmp.threshold}} or higher. The run kept the smaller model. | My instruction during the run. |
| 2.5 | Not in the plan. | Every request stayed under 100,000 tokens. The largest in the cost test was {{run.largest_request_tokens|comma}}. All labeling used normal requests. No batch job was submitted, so nothing was billed twice. | My instructions during the run. |
| 3.1 | Bulk labeling through the first provider's key, with a $100 budget. | That key was on a free tier with a daily request cap. One model reached its cap partway through the Hong Kong sample. A replacement was started and then stopped when the instruction in 2.1 arrived. Neither set of labels is used in any index. Both are kept as cross-model comparisons. | Found in the throughput test. Paid access was not turned on, because that would have changed my cloud settings. |
| 3.2 | The Internet Archive saves the repository page and the raw methodology file. | The raw methodology, source inventory, proposal and README were saved and checked against their SHA-256. The repository page returned an error on the first tries. The outcome of the retries is in `deliverables/preregistration.md`. | An Archive error for github.com pages. |
| 3.3 | London Health: share of the waiting list waiting under 18 weeks, with A&E four-hour performance as the backup. | Both are missing. London Health has no official series, so that pair is not tested. | The NHS England statistics pages returned a browser challenge. The rules for this run say to stop when a site blocks collection. No open-portal copy was found. |
| 3.4 | New York Health: deaths of city residents by month from CDC WONDER, from 1999. | Deaths from all causes occurring in New York City, from the CDC's open provisional file, from {{off.nyc_health_main.first_period}}. | CDC WONDER requires accepting a data-use agreement on a web form, which the run does not do. |
| 3.5 | The model reads the same inputs for every outlet. | True, but {{run.items_no_input|comma}} of {{run.items_sampled_total|comma}} sampled items had no headline words and no theme tags. They could not be labeled and are left out of the shares. | GDELT recorded no themes for them. |

**Official indicators.** Table 16 lists each official series that differs from the methodology's tables. Full notes are in `data/interim/official/`.

**Table 16.** Official indicators: differences from the methodology's tables.

| Series | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| Hong Kong Health, main | Specialist outpatient waiting time from 2013, all specialties from 2015. | Starts {{off.hk_health_main.first_period}}. | The data.gov.hk archive of the Hospital Authority file is the only machine-readable history. |
| Hong Kong Transport, main | Fatal and serious road accidents from 2003. | Starts {{off.hk_transport_main.first_period}}. | The earlier figures are only in PDF digests, which were not extracted. |
| Hong Kong Cost of Living, main | Composite CPI without the housing section, from 1981. | Starts {{off.hk_cost_of_living_main.first_period}}. Built from the table that holds the section indices, with the published housing weights for four base periods. | The planned table has no section indices. The oldest weights were not found. |
| Hong Kong Economy, main | Break for the change in seasonal adjustment marked at 2008. | Marked at January to December 2007. | The statistics office revised the series back to the period ending January 2007, so those are the comparisons that mix methods. |
| Hong Kong Environment, main | Hourly NO2 and PM10 averaged by month. | The publisher's own station monthly averages for 11 general stations. Ends {{off.hk_environment_main.last_period}}. | The export provides monthly averages. |
| Hong Kong Safety, main | Annual from 2001, monthly for 2022 to 2024. | Annual, {{off.hk_safety_main.first_period}} to {{off.hk_safety_main.last_period}}. The monthly file for 2022 to 2024 was not found. Two years come from an Internet Archive copy of the police workbook. | Source pages moved. |
| Hong Kong Education, main | Share of day-school candidates meeting the entrance requirement, from 2012. | {{off.hk_education_main.first_period}} to {{off.hk_education_main.last_period}}, core subjects only. The first year was read from a scanned PDF and checked against the counts. The 2026 file was not at the usual address. | Source format. |
| Hong Kong backups | Public rental waiting time (quarterly), MTR delays of 8 minutes or more (annual from 2008), very hot days, teacher wastage. | Waiting time {{off.hk_housing_backup.first_period}} to {{off.hk_housing_backup.last_period}} with some quarters missing. MTR delays {{off.hk_transport_backup.first_period}} to {{off.hk_transport_backup.last_period}} with some years missing. Very hot days annual. Teacher wastage {{off.hk_education_backup.first_period}} to {{off.hk_education_backup.last_period}}, as the mean of primary and secondary. | Assembled from dated official pages and Legislative Council papers. |
| New York Education, main | Four-year graduation rate. | The June rate, classes of {{off.nyc_education_main.first_period}} to {{off.nyc_education_main.last_period}}. | No August rate is published for the earliest classes. |
| New York Transport, main | Subway on-time performance from 2009. | Starts {{off.nyc_transport_main.first_period}}, weekday trains, with two months missing. Two files are joined at 2015 and agree closely where they overlap. | Source coverage. |
| New York Housing, main | DHS shelter census, with the Coalition for the Homeless series before 2013. | Three files joined. The Coalition total runs above the DHS figure at the join, which is marked as a break. Coalition months with no total are left out. | Source coverage. |
| New York Environment | PM2.5 from 1999, air quality index from 1989. | Both from 1999, ending {{off.nyc_environment_main.last_period}}. A few thin months are dropped. Before 2025 most days rest on two or three of the five boroughs. | EPA file coverage. |
| New York Economy, backup | Nonfarm jobs from 1950. | From {{off.nyc_economy_backup.first_period}}. | The open series starts there. |
| New York prices | Break for the 2018 area redraw. | Marked for 2018. The analysis extends it through 2019, because the change in a 12-month rate looks back two years. | Follows from the transformation in Appendix C. |
| London Safety, main | Recorded crime from 2008. | Starts {{off.london_safety_main.first_period}}. A break was added at February 2013, when fraud left the count. | No file with the older categories exists. |
| London Housing, main | Older rent index joined to the current one at 2015. | Joined at January 2015. The months around the join are marked as a break. | The two indices differ where both exist. |
| London Transport, main | Severity-adjusted killed or seriously injured, from 1979. | {{off.london_transport_main.first_period}} to {{off.london_transport_main.last_period}}. | Adjusted figures do not exist for earlier years. |
| London Environment, main | NO2 at Marylebone Road and Bloomsbury. | Some months are empty, nearly all because Bloomsbury has no readings, including a long stretch from late 2023 to early 2025. Ends {{off.london_environment_main.last_period}}. A month with one site missing is left empty and is not filled. | Missing readings in the network's data service. |
| London Education, main | Attainment 8 from 2015/16. | School years ending {{off.london_education_main.first_period}} to {{off.london_education_main.last_period}}. The first three years come from a London Datastore workbook of DfE figures. The latest year is provisional. | Source coverage. |
| London backups | Temporary accommodation, Underground lost customer hours, PM2.5 at the same sites, absence rate. | Temporary accommodation has some empty quarters. Lost customer hours run {{off.london_transport_backup.first_period}} to {{off.london_transport_backup.last_period}}. PM2.5 uses a different instrument code at Marylebone Road and runs {{off.london_environment_backup.first_period}} to {{off.london_environment_backup.last_period}}. The absence rate lacks one school year. | Source coverage. |
| London Cost of Living, backup | None exists. | None. | As the methodology says. |

**Judgment calls.** Table 17 records the reading the run took where the plan left a detail open. Three more choices sit in the analysis code and are described in Section 3: the matched panel, the minimum number of matched periods, and the rule that reads the verdicts.

**Table 17.** Judgment calls made while applying the plan.

| Topic | Reading taken |
| :-- | :-- |
| Hong Kong city filter | An article counts if GDELT gives it any location tag whose country code is Hong Kong. |
| New York city filter | An article counts if GDELT gives it a city-level tag named New York City, a borough, or a borough's county. Neighborhood tags alone do not count. GDELT rarely tags the Bronx, so Bronx stories are under-counted. |
| London national news | Addresses under the papers' national-news sections are dropped. For the Evening Standard (check list only), its UK and world news sections are dropped. |
| Pages that are not articles | Tag, author, topic and section index pages are dropped. |
| Duplicates | Addresses are compared after removing `www.`, `m.`, ports and tracking parameters. The first appearance is kept. |
| London shared stories | Headline words in the address are compared within a month. One copy is kept, chosen by the seeded random order. |
| Apple Daily and Now TV (check list) | The Taiwan edition of Apple Daily and the finance pages of now.com are left out. |
| The seven London papers that jumped | Identified from yearly counts: East London Advertiser, Hackney Gazette, Ham & High, Ilford Recorder, Islington Gazette, Kilburn Times and Romford Recorder. |
| Google Trends requests | There are 11 sets other than Economy and 12 open slots, so the third request repeats Safety. The first request's Safety is the one used. |
| Sample for the check with all listed outlets | The same budget of 1,000 a month split equally over every listed outlet: 41 per outlet per month in Hong Kong and London, 50 in New York. |
| Theme tags sent to the model | The first 30 different tags in order of first appearance. |
| Poster size | The poster board holds at most 16 letter-size pages laid flat, so the poster kit is 16 pages and not the 18 to 24 first aimed for. This does not affect the paper. |

<!-- FINAL PASS: Deviations, items cut or still open. Section 6 of deliverables/deviations.md was still pending when this template was written. Once it is complete, replace the paragraph below with its rows in prose: the labeling round reached, the validation outcome and categories dropped, the headline check and its effect on Hong Kong 2015 to 2019, the social media snapshot, and the pre-2015 news extension. Also add the items this paper already discloses if they are not there yet: disconnection causes were assigned by rule, with an AI-read sample of stories for only some stretches and no person reading any coverage, the events behind the signal-only peaks were not named, and the analysis code set the minimum number of matched periods and the verdict cutoffs. -->

**Items cut or still open.** Items cut or left open at the end of the run are listed in section 6 of `deliverables/deviations.md`, including the social media snapshot and the optional pre-2015 news extension. No result in this paper uses social media data or pre-2015 news.

## 9. AI-use disclosure

An AI agent ran the whole pipeline of this study in one unattended session on November 17 and 18, 2026. It posted the pre-registration, collected the official statistics, queried GDELT, downloaded the Google Trends files, drew the news sample and wrote the analysis code. An AI language model labeled every sampled article. A second AI language model from a different model family validated those labels, and further AI passes served as consistency checks. The agent proposed the causes of the disconnections. It made the figures and tables, and it drafted this paper. No person reviewed the labels, the data or the numbers before this draft was built. The exact model names, settings and prompts are in the labeling card (`data/public/labeling_card.md`) and in the AI-use log that goes with this paper.

The pre-registered plan states that the research question, the codebook, the indicator choices, the index design and the interpretation are mine.

[CAYDEN TO CONFIRM: his own role in the question, codebook, design and interpretation]

## References

### Studies

Behr, R. L., & Iyengar, S. (1985). Television news, real-world cues, and changes in the public agenda. *Public Opinion Quarterly, 49*(1), 38–57. https://doi.org/10.1086/268900

D'Amuri, F., & Marcucci, J. (2017). The predictive power of Google searches in forecasting US unemployment. *International Journal of Forecasting, 33*(4), 801–816. https://doi.org/10.1016/j.ijforecast.2017.03.004

Downs, A. (1972). Up and down with ecology: The "issue-attention cycle." *The Public Interest, 28*, 38–50.

Funkhouser, G. R. (1973). The issues of the sixties: An exploratory study in the dynamics of public opinion. *Public Opinion Quarterly, 37*(1), 62–75. https://doi.org/10.1086/268060

Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences, 120*(30), e2305016120. https://doi.org/10.1073/pnas.2305016120

Gramlich, J. (2024, April 24). *What the data says about crime in the U.S.* Pew Research Center. https://www.pewresearch.org/short-reads/2024/04/24/what-the-data-says-about-crime-in-the-us/

Hammond, J., & Weidmann, N. B. (2014). Using machine-coded event data for the micro-level study of political violence. *Research & Politics, 1*(2). https://doi.org/10.1177/2053168014539924

Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics, 33*(1), 159–174. https://doi.org/10.2307/2529310

Mellon, J. (2014). Internet search data and issue salience: The properties of Google Trends as a measure of issue salience. *Journal of Elections, Public Opinion and Parties, 24*(1), 45–72. https://doi.org/10.1080/17457289.2013.846346

Soroka, S. N. (2006). Good news and bad news: Asymmetric responses to economic information. *The Journal of Politics, 68*(2), 372–385. https://doi.org/10.1111/j.1468-2508.2006.00413.x

### Data sources

All data were retrieved in November 2026. A title in square brackets is a description of a data set that has no single formal title in the study's source notes.

GDELT Project. (2026). *GDELT Global Knowledge Graph 2.0* [Data set]. Queried through Google BigQuery. https://www.gdeltproject.org/data.html

Google. (2026). *Google Trends* [Data set]. https://support.google.com/trends/answer/4355213?hl=en

*Hong Kong*

Census and Statistics Department, Hong Kong. (2026). [Table 210-06101: seasonally adjusted unemployment rate and underemployment rate] [Data set]. https://www.censtatd.gov.hk/api/get.php?id=210-06101&lang=en&full_series=1

Census and Statistics Department, Hong Kong. (2026). [Tables 510-60001, 510-60001A and 510-60002: Composite Consumer Price Index, its section indices, and the Underlying Composite CPI] [Data set]. https://www.censtatd.gov.hk/api/get.php?id=510-60001&lang=en&full_series=1

Centre for Health Protection, Hong Kong. (2026). [Number of notifiable infectious diseases by month] [Data set].

Education Bureau, Hong Kong. (2026). [Teacher wastage rates, primary and secondary schools] [Data set].

Environmental Protection Department, Hong Kong. (2026). [Monthly average concentrations of nitrogen dioxide and respirable suspended particulates at general stations] [Data set]. https://cd.epic.epd.gov.hk/EPICDI/air/station/?lang=_en

Hong Kong Examinations and Assessment Authority. (2012–2025). [HKDSE examination statistics, yearly reports] [Data set]. https://www.hkeaa.edu.hk/DocLibrary/HKDSE/Exam_Report/Examination_Statistics/dseexamstat24_3.pdf

Hong Kong Observatory. (2026). *Number of Very Hot days observed at the Hong Kong Observatory* [Data set].

Hong Kong Police Force. (2026). [Overall reported crime and violent crime, annual totals] [Data set]. https://www.police.gov.hk/ppp_en/09_statistics/csc_2001_2013.html

Hospital Authority, Hong Kong. (2026). [Waiting time for stable new cases at specialist outpatient clinics] [Data set]. https://data.gov.hk/en-data/dataset/hospital-hadata-sop-waiting-time

Housing Authority and Housing Bureau, Hong Kong. (various dates). [Average waiting time for public rental housing, general applicants, as published each quarter].

Legislative Council of Hong Kong. (various dates). [MTR incidents causing delays of 8 minutes or more, from Research Office paper ISSH07/17-18 and the reply to question 13 of May 14, 2025].

Rating and Valuation Department, Hong Kong. (2026). [Private domestic rental index, all classes] [Data set]. https://www.rvd.gov.hk/doc/en/statistics/his_data_3.xls

Transport Department, Hong Kong. (2026). [Road traffic accidents by severity, monthly] [Data set]. https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/table71_eng.csv

*New York City*

Centers for Disease Control and Prevention, National Center for Health Statistics. (2026). *Provisional COVID-19 death counts by week ending date and state* [Data set]. Used in place of CDC WONDER, the source named in the plan.

Centers for Disease Control and Prevention, National Center for Health Statistics. (2026). *VSRR provisional drug overdose death counts* [Data set].

Coalition for the Homeless. (2026). *New York City homeless municipal shelter population, 1983-present* [Data set]. https://www.coalitionforthehomeless.org/

Metropolitan Transportation Authority. (2026). *MTA subway terminal on-time performance: Beginning 2015* and *MTA key performance indicators: 2008-2021* [Data sets]. https://data.ny.gov/resource/f6rf-2a3t.json

New York City Department of Education. (2026). [Citywide graduation results and daily attendance] [Data sets]. https://infohub.nyced.org/reports-and-policies/citywide-information-and-data/graduation-results

New York City Department of Homeless Services. (2026). *DHS daily report* and *DHS daily report (historical)* [Data sets]. https://data.cityofnewyork.us/resource/k46n-sa2m.json

New York City Police Department. (2026). *NYPD complaint data historic* and *NYPD complaint data current (year to date)* [Data sets]. https://data.cityofnewyork.us/resource/qgea-i56i.json

New York City Police Department. (2026). [Shooting incident data] and *Motor vehicle collisions - crashes* [Data sets]. NYC Open Data.

New York State Department of Labor. (2026). [Local area unemployment statistics, seasonally adjusted, New York City] [Data set]. https://data.ny.gov/resource/dh9m-5v4d.json

U.S. Bureau of Labor Statistics. (2026). [Consumer Price Index, New York metro area: all items less shelter, rent of primary residence, and food; total nonfarm employment, New York City] [Data sets]. Retrieved from FRED, Federal Reserve Bank of St. Louis. https://fred.stlouisfed.org/series/CUURA101SA0L2

U.S. Environmental Protection Agency. (2026). *AirData*: daily PM2.5 files and daily air quality index by county [Data sets]. https://aqs.epa.gov/aqsweb/airdata/download_files.html

*London*

Department for Education. (2026). [Key stage 4 performance, Attainment 8, London region; absence sessions by reason] [Data sets]. https://explore-education-statistics.service.gov.uk/data-catalogue/data-set/9e761bdf-fe02-4e1e-9d3d-b32dac9fa6ef

Department for Transport. (2026). *Road safety data* [Data set]. https://www.gov.uk/government/statistics/road-safety-data

Home Office. (2026). *Police recorded crime and outcomes open data tables* [Data set]. https://www.gov.uk/government/statistical-data-sets/police-recorded-crime-and-outcomes-open-data-tables

London Air Quality Network. (2026). [Hourly nitrogen dioxide and PM2.5 readings, Marylebone Road and Bloomsbury] [Data set]. https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode=MY1/SpeciesCode=NO2/StartDate=2005-01-01/EndDate=2005-01-03/Json

London Datastore. (2026). *GCSE results total and by sex* [Data set]. https://data.london.gov.uk/dataset/gcse-results-by-borough-20pd9

Metropolitan Police Service. (2026). *MPS recorded crime: Geographic breakdown* [Data set]. London Datastore. https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m

Ministry of Housing, Communities and Local Government. (2026). *Live tables on homelessness* [Data set]. https://www.gov.uk/government/statistical-data-sets/live-tables-on-homelessness

Office for National Statistics. (2026). [Unemployment rate, London, series YCNI; claimant count, London, series DPDK] [Data sets]. https://www.ons.gov.uk/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/ycni/lms

Office for National Statistics. (2026). *Price Index of Private Rents* and *Index of Private Housing Rental Prices* [Data sets]. https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/priceindexofprivaterentsukmonthlypricestatistics

Office for National Statistics. (2026). [Consumer Prices Index, annual rate, series D7G7] [Data set]. https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7g7/mm23

Transport for London. (2020). [London Underground performance reports] [Data set]. London Datastore. https://data.london.gov.uk/dataset/london-underground-performance-reports-em8qy

<!-- wide-pages -->

## Appendix

Every table in this appendix is filled from `data/public/results.json`. The tables are description or checks. None is a pre-registered test.

**Table A1.** All 48 city, category and source pairs (description). The correlation r is between yearly changes in attention and in the official measure, both in standard deviations. Frequency: M is monthly, Q is quarterly, A is annual. The adjusted p uses the Benjamini-Hochberg method across all tested pairs.

{{tables.pair_level}}

**Table A2.** Checks that the results hold, news models, with p-values and sample sizes.

{{paper.checks_news}}

**Table A3.** Checks that the results hold, search models, with p-values and sample sizes.

{{paper.checks_search}}

**Table A4.** The twenty longest disconnections. Every cause is proposed by AI, for Cayden to confirm.

{{tables.runs_top20}}

**Table A5.** Current-year ranking, Hong Kong (description).

{{tables.ranking_hk}}

**Table A6.** Current-year ranking, New York City (description).

{{tables.ranking_nyc}}

**Table A7.** Current-year ranking, London (description).

{{tables.ranking_london}}
