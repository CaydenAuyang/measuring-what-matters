<!--
GENERATED FILE. Built by src/build_paper.py from src/templates/paper.template.md and the results file generated at 2026-11-18T09:25:44Z (UTC).
Edit the template and rebuild. Changes made here are lost at the next build.
-->

# Measuring What Matters: When a City's Problems Get Worse, Does Public Attention Follow?

Cayden Auyang. AI drafted and I reviewed.

Pomfret School. Mentors: Mr. Qua and Mr. Lake. Independent study, fall 2026.

## Abstract

<!-- PROSE ASSUMES: verdicts.h1_news=supported; verdicts.h1_search=supported; verdicts.h2_news=not supported; verdicts.h2_search=not supported; verdicts.h3_news=not supported; verdicts.h3_search=not supported; paper.without_covid_news_reading=includes zero; paper.without_covid_search_reading=sits above zero; paper.h1_strengths=weak and weak; run.relabeled=yes -->

Civic technology often treats news coverage and online activity as evidence of how a city is doing. This study tests that assumption for Hong Kong, New York City and London. Following a plan registered before any outcome data were pulled, it compares official statistics for eight problem categories with two measures of public attention: each category's share of local news coverage in GDELT (2015-02 to 2026-10) and its share of Google search interest (2004-01 to 2026-10). Yearly changes are pooled in one model per source. An AI language model labeled 286,155 sampled articles from the main outlet panels, and a second, independent AI language model validated a sample of 827 of them. Attention moved with the official measures, but weakly. For each standard deviation an official measure worsened, news attention rose 0.07 standard deviations (95% interval 0.02 to 0.10) and search attention rose 0.26 (0.19 to 0.42). The first hypothesis, a positive but weak link, was supported for both sources. The news result rests on the pandemic years: without 2020 to 2022 its slope was 0.02 (-0.05 to 0.06), an interval that includes zero. The search result held without those years. The second hypothesis, a stronger reaction to worsening than to improving, was not supported for either source. The third, that Safety shows the largest gap between attention and official data, was not supported: Safety had the largest gap in 1 of 3 cities for news and in 0 for search. In a test on unrelated made-up series, 7 of 40 intervals wrongly excluded zero, so the intervals reported here are likely too narrow.

## 1. Introduction

Governments measure a city's problems with official statistics: crime counts, unemployment rates, rents, pollution readings, hospital waiting times. Journalists and residents register the same problems another way, through what local news covers and what people search for. I run OurCityHealth, a civic intelligence platform that scores cities from news coverage. The platform rests on an assumption I share with most of the civic technology field: that news and online discussion say something real about how a city is doing. I had never tested it. This study asks whether public attention to a problem moves with the official measure of that problem, and what it means when the two disagree.

Earlier work gives reasons to expect a loose link. Funkhouser (1973) compared 1960s news coverage with statistics on the same issues and found that coverage tracked real-world conditions poorly. Behr and Iyengar (1985) found that real conditions shaped public concern partly through how much television covered them. Soroka (2006) found that UK coverage and opinion responded more strongly to negative economic changes than to equal positive ones. Downs (1972) argued that attention to a problem fades even while the problem continues. Crime is the best-known gap. In 23 of 27 Gallup surveys since 1993, at least 60% of US adults said crime was rising nationally, while it fell over most of that period (Gramlich, 2024).

Other work shaped how attention is measured here. D'Amuri and Marcucci (2017) found that searches for jobs tracked official US unemployment closely. Mellon (2014) found that search data measured issue salience well for some issues, such as the economy, and poorly for others, so the search terms here were fixed in advance. Gilardi, Alizadeh and Kubli (2023) found that a language model labeled political text more accurately than crowd workers on most of their tasks, though accuracy varied by task, so the plan checks the labels first. Hammond and Weidmann (2014) found that machine-coded locations in GDELT's event data are unreliable below the country level, so news is selected by local outlet. Landis and Koch (1977) supply the agreement threshold: a Cohen's kappa of 0.61 or higher, which they call substantial agreement.

Official statistics are the benchmark in this study. They are also measurements with their own blind spots. Recorded crime, for example, counts only what is reported and recorded. So the study treats official data and public attention as two imperfect measures of the same problems. Where they disagree, the cause is classified, and neither side is assumed to be right.

The design was fixed in a methodology document dated October 7, 2026, and posted publicly on November 17, 2026, before any outcome data were pulled. Label validation used a second, independent AI language model as the second coder (Section 4). The paper reports four pre-registered tests. Everything else is labeled as description, a check, or exploratory.

## 2. Research questions and hypotheses

These come from the pre-registered methodology.

1. **Can scattered informal signal be turned into a defensible monthly measure of attention?** The plan's rule: a category is analyzed in a city only if the AI labels behind it agree with a second coder at a Cohen's kappa of 0.61 or higher. In this study the second coder is an independent AI language model from a different model family (Section 4).
2. **Does attention move with the official measure of the same problem?**
   - **H1.** Year-over-year changes in news attention correlate positively with changes in the matching official indicator, but weakly.
   - **H2.** Attention reacts more to a problem getting worse than to it getting better.
   - **Exploratory.** Whether news or search moves first, reported for each category without a prediction.
3. **Where do official data and attention stay disconnected, and why?**
   - **H3.** Safety shows the largest gap between attention and official data, measured as the share of months in which the two move in opposite directions, in at least two of the three cities.
   - Following Downs (1972), long stretches where a problem stays bad while coverage drops are expected and are reported.

The plan tests H1 and H2 with one pooled model each, run for news and for search: four main tests. Results for the 48 city, category and source pairs are description, with p-values adjusted by the Benjamini-Hochberg method. The four categories with no official statistic (Governance, Culture, Technology, Community) are described and are not tested.

## 3. Data and methods

This section describes the method as it was carried out. Section 8 lists the differences from the plan.

### 3.1 Cities

Hong Kong, New York City and London have similar populations, roughly 7.5 to 9 million each, and very different political and media systems. The comparison runs inside each city: attention to a problem against that city's own official measure. The cities' problems are never compared with each other.

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

Table 1 is the first wording. The one revision the plan allows reworded seven lines after validation (Section 4.3), and the labeling card gives both wordings.

Four pre-registered tie-break rules complete the codebook. They cover items with several topics, protests, immigration, and tone, which is labeled separately as negative, neutral or positive. The labeling card gives them word for word.

### 3.3 Official indicators

Each compared category has a main indicator and a backup in each city, all from official bodies. The plan lists 24 main indicators and 23 backups. The run built 23 main indicators and 22 backups. Missing main indicators: London Health. Each series was built by script from the publisher's open files. Each series is used at its own frequency, and nothing is interpolated. Table 2 shows what each main series covers.

**Table 2.** The main official indicators as built. The coverage column gives the first and last period with a value.

| City | Category | Main indicator as built | Frequency | Coverage obtained | Values | Status |
| :-- | :-- | :-- | :-- | :-- | --: | :-- |
| Hong Kong | Safety | Overall reported crime, annual total | Annual | 2001 to 2025 | 25 | built |
| Hong Kong | Economy | Unemployment rate, seasonally adjusted, 3-month moving average | Monthly | 1985-03 to 2026-10 | 436 | built |
| Hong Kong | Housing | Private domestic rental index, all classes (1999 = 100) | Monthly | 1993-01 to 2026-09 | 405 | built |
| Hong Kong | Transport | Fatal and serious road traffic accidents | Monthly | 2013-01 to 2026-08 | 164 | built, with gaps or a later start than planned |
| Hong Kong | Environment | NO2 and PM10 (respirable suspended particulates), monthly mean across general stations running since 2005 | Monthly | 2000-01 to 2026-05 | 634 (2 components) | built |
| Hong Kong | Health | Median waiting time for stable new specialist outpatient cases, mean over cluster and specialty pairs | Quarterly | 2018-Q3 to 2026-Q3 | 33 | built, with gaps or a later start than planned |
| Hong Kong | Education | Share of day-school HKDSE candidates with core subjects at 3322 or better (332A from 2024) | Annual | 2012 to 2025 | 14 | built |
| Hong Kong | Cost of Living | Composite CPI excluding the housing section (Oct 2019 to Sep 2020 = 100) | Monthly | 2004-10 to 2026-09 | 264 | built, with gaps or a later start than planned |
| New York City | Safety | Felony complaints, NYPD, by report month | Monthly | 2006-01 to 2026-09 | 249 | built |
| New York City | Economy | Unemployment rate, seasonally adjusted, New York City | Monthly | 1976-01 to 2026-09 | 608 | built |
| New York City | Housing | People in DHS shelters, monthly average of the daily census | Monthly | 1983-06 to 2026-10 | 502 | built |
| New York City | Transport | Subway weekday terminal on-time performance, system-wide | Monthly | 2009-06 to 2026-10 | 207 | built |
| New York City | Environment | PM2.5, monthly mean of daily readings across the five boroughs | Monthly | 1999-08 to 2026-05 | 318 | built |
| New York City | Health | Deaths from all causes occurring in New York City, by month | Monthly | 2020-01 to 2026-10 | 82 | built, with gaps or a later start than planned |
| New York City | Education | Four-year graduation rate as of June, NYC public schools | Annual | 2005 to 2025 | 21 | built |
| New York City | Cost of Living | CPI all items less shelter, New York metro area | Monthly | 1975-12 to 2026-10 | 594 | built |
| London | Safety | Recorded crime, all offences, Metropolitan Police | Monthly | 2010-04 to 2026-10 | 199 | built |
| London | Economy | Unemployment rate, London, aged 16 and over, seasonally adjusted (ONS YCNI) | Monthly | 1992-05 to 2026-09 | 413 | built |
| London | Housing | Private rents index, London (ONS PIPR, with IPHRP joined on before 2015) | Monthly | 2005-01 to 2026-09 | 261 | built |
| London | Transport | Killed or seriously injured road casualties, London, severity-adjusted (DfT) | Monthly | 2004-01 to 2025-12 | 264 | built |
| London | Environment | Nitrogen dioxide, mean of Marylebone Road and Bloomsbury (London Air Quality Network) | Monthly | 2004-01 to 2026-05 | 239 | built, with gaps or a later start than planned |
| London | Health | Waiting list: share waiting under 18 weeks, London region (NHS England RTT) | | none | 0 | missing |
| London | Education | Attainment 8 average score, London region, state-funded schools (DfE) | Annual | 2016 to 2026 | 11 | built |
| London | Cost of Living | CPI 12-month rate, all items, UK (ONS D7G7) | Monthly | 1989-01 to 2026-09 | 453 | built |

Three differences from the plan matter most (Tables 15 and 16). London Health is missing, because the publisher's pages answered automated requests with a browser challenge and the run stopped there. New York Health uses deaths from all causes from an open CDC file whose first month is 2020-01. Hong Kong Health and Hong Kong Transport start later than planned.

Every series is turned into a change from the same period a year earlier, in which a positive number means the problem got worse (Appendix C of the methodology). Counts, pollution levels and waiting times change in percent, computed as 100 times the natural log of the ratio. Rates, shares and scores change in points. For prices and rents, the 12-month rate is computed first and its yearly change is measured in points. Indicators that are better when higher have their sign reversed. Every break in the plan's breaks table is marked in the data, along with breaks the run found in the sources.

### 3.4 News attention from GDELT

News attention comes from GDELT's Global Knowledge Graph (GDELT Project, 2026), which records each online article's source, places, themes and tone from February 2015.

**Outlets.** The outlet lists were fixed in Appendix A of the methodology. The main series uses a fixed panel of outlets that GDELT recorded steadily in every year from 2015, so an outlet joining or leaving cannot shift the shares. The panel has 3 outlets in Hong Kong (the South China Morning Post's Hong Kong section, Oriental Daily and HK China News Agency), 3 in New York (Daily News, NBC New York and Gothamist) and 15 borough papers in London. The full lists hold 68 outlets and serve as a check.

**Filters and duplicates.** Articles pass a city filter based on GDELT's location tags (Hong Kong and New York) or on the web address (London). Duplicates are removed by web address, and a London story that runs in several papers in one month counts once. Table 17 gives the exact readings.

**Sample.** The pre-registered sample is up to 333 articles per outlet per month in Hong Kong and New York and up to 66 per paper in London, drawn with a fixed seed. Articles were labeled in rounds that add the same number for every outlet and month, and only complete rounds are used. Rounds reached: round 6 of 6, the full planned sample. Table 3 gives the counts. Its count of official series leaves out 2 extra series that no test uses.

**Table 3.** What the study rests on.

| What | Count |
| :-- | --: |
| Cities | 3 |
| Outlets in the main panels | 21 |
| Outlets on the full lists | 68 |
| GDELT records pulled for the listed outlets | 6,363,992 |
| Articles left after the city filters and duplicate removal | 2,466,900 |
| Articles labeled, main panels | 286,155 |
| Articles labeled, main panels and check lists | 429,081 |
| Months of news | 141 (2015-02 to 2026-10) |
| Official series (main and backup) | 45 |
| Official values | 11,948 |
| Months of search data | 274 (2004-01 to 2026-10) |
| Search downloads per request | 2 |

**What the model reads.** GDELT stores headlines only from 2020. So that every year is labeled from the same inputs, an AI language model reads the outlet name, any headline words in the article's web address, and the first 30 GDELT theme tags. It never sees the article text. For an outlet with number-only addresses it reads theme tags alone. Of 435,201 sampled items, 6,117 had neither headline words nor theme tags and are left out.

**Labeling.** The prompt holds the codebook and the tie-break rules word for word, plus a description of the inputs and examples of items that are not a civic problem. The first prompt was fixed at 2026-11-17T21:00:35Z and labeled every article once. After the validation retest on November 18, seven category lines were reworded once (Section 4.3) and every article was labeled again with the revised prompt. The results use the second set of labels. Two test runs, of 200 and 2,000 Hong Kong items, used the first prompt before the full run (labeling card, `data/public/labeling_card.md`).

**Index.** For each outlet and month, a category's share is its labeled articles divided by all labeled articles from that outlet, including those labeled not a civic problem. A city's attention share is the average of its outlets' shares, each outlet weighted equally. Shares cancel out the growth in GDELT's source list and the difference in size between cities. The negative-tone share, used in one check, counts only articles labeled negative.

### 3.5 Search attention from Google Trends

Search attention comes from Google Trends (Google, 2026). Each category has one fixed set of search terms per city, listed in Appendix B of the methodology, in Traditional Chinese plus some English for Hong Kong and in English elsewhere. No term was changed after data were seen. The geography is Hong Kong as a whole, the New York media market, and England for London.

Trends scales each request from 0 to 100, so every request includes the Economy set as an anchor. Each set is divided by Economy in its own request, and a category's share is its ratio divided by the sum of the twelve ratios. The requests cover web search from 2004-01 to 2026-10. The files were downloaded from the Trends website, in a browser profile that was already signed in to a Google account (Table 17). The plan called for three downloads on different days. Each of the nine requests was downloaded 2 times: on the evening of November 17 and again after local midnight on November 18.

A set that reads zero in more than 10% of months is reported as too sparse to test. It is not replaced, and it stays in the denominator. The sparse sets were: Hong Kong, Safety, Transport, Education, Culture and Technology; New York, Education, Culture and Technology; England, Education and Technology. Google's charts note that its methods changed at the start of 2011, 2016 and 2022, and search changes in those years are marked as breaks.

### 3.6 Yearly changes and matching

The main test compares changes. Two series that both trend for twenty years will correlate even if they are unrelated. Yearly changes remove that trap, and seasonal patterns with it.

Attention is matched to each official series at that series' own frequency: the same month for a monthly series, the mean of the quarter for a quarterly one, and the mean of the year for an annual one (the September to August school year for Education). A series published as a 3-month or 12-month average is matched with attention averaged over the same window. The yearly change in attention is the share in that window minus the share a year earlier, in percentage points.

For news, the run computes this change on a matched panel (`logs/decisions.md`). Each outlet's share is compared with the same outlet a year earlier, and those changes are averaged across the outlets present in both periods. Without it, an outlet rejoining the panel would show up as a jump in every category.

A pair is tested only if it has at least 24 matched months, 8 quarters or 5 years. The analysis code set this floor. A check that leaves periods out keeps a pair that still has at least half that number. Each period is flagged if it falls in 2020 to 2022, in a marked break of the official series, or in a marked break of the attention series (Hong Kong in 2019 and 2020, and the Google note years for search).

### 3.7 The pooled model

Before pooling, each pair's official change and attention change are divided by their own standard deviation, computed from periods outside the marked breaks so that the COVID years do not set the scale. Slopes are then in standard deviations, and pairs measured in different units can be pooled.

H1 is tested with one regression of attention change on official change across all pairs, with a separate intercept for each pair. Every pair gets equal total weight, so a monthly pair with about 120 points does not swamp an annual pair with about 10. H2 uses the same model with official change split into two terms, one for periods when the problem worsened and one for periods when it improved. H2 holds if the worsening slope is larger. Each model is run for news and for search. These four models are the pre-registered main tests.

The analysis code reads the results by a fixed rule. H1 or H2 counts as supported when the whole 95% interval lies above zero, as failed when it lies below zero, and as not supported otherwise. For H2 the interval is for the difference between the two slopes. The code also calls a slope below 0.3 weak. The plan predicted a weak link and did not set that cutoff.

### 3.8 The bootstrap

Confidence intervals come from a moving-block bootstrap. Within each pair, blocks of 12 consecutive months (4 quarters, or 1 year) are drawn with replacement, and the model is refit on each resample. The interval runs from the 2.5th to the 97.5th percentile of the resampled slopes. The main models use 2,000 resamples, and the checks use 1,000. Yearly changes in monthly data overlap, so the effective sample is reported as independent pair-years: each pair's number of periods divided by the periods in a year.

Before the code touched real data, it was run on made-up series with known answers. It recovered a slope, an asymmetry and a three-month lag that were built in. One test is a warning. On unrelated made-up series with strong persistence, 7 of 40 intervals wrongly excluded zero, against an expected rate of 5% (Section 7).

### 3.9 Disconnections and checks

**Disconnection (H3).** For each pair, the share of periods in which attention and the official measure moved in opposite directions. Within each city the compared categories are ranked by that share, and H3 holds for a source if Safety ranks first in at least two cities. For monthly pairs the run also lists every stretch of six or more months in a row of opposite movement, and gives each one of the plan's five causes: a change in how the official measure counts, a real event the indicator does not capture, a news cycle, the two measuring different parts of the problem, or unclear. The run assigned causes by a fixed rule based on the marked breaks and a short list of events from the plan's breaks table. The plan also called for reading a sample of each period's coverage, and that was done for 4 of the stretches. Every cause is reported as a proposed cause.

**Checks that the results hold.** Table 13 lists them: the plan's own checks, two from its outlet notes, description rows for Hong Kong before and after the 2021 outlet closures, and 3 exploratory rows the run added. The plan's social media snapshot and optional pre-2015 news extension were cut (Section 8).

### 3.10 Pre-registration

The methodology, the outlet lists, the search terms and the indicator rules were committed to a public GitHub repository on November 17, 2026 (commit `e8d5f32`, tag `prereg-v1`, commit time 2026-11-17T20:31:07Z), before any outcome data were pulled. The Internet Archive saved copies of the raw methodology file and the source inventory, and each copy matched the local file's SHA-256 hash. The record, including what happened with the github.com repository page itself, is in `deliverables/preregistration.md`. The repository is at https://github.com/CaydenAuyang/measuring-what-matters.

## 4. Validation

### 4.1 Validation design

Two AI language models labeled the same articles independently, and their agreement decides which categories are analyzed. The kappa values in this section measure agreement between two independent AI coders.

The second coder is an AI language model from a different model family than the first. It never sees the first coder's labels. It reads each article's real headline and opening lines, taken from the live page or the Internet Archive. Where no page could be read, it reads the real headline alone (Section 4.2). It applies the same codebook and also records whether the article is really about the study city.

### 4.2 The validation set and the rules

For each city the run drew about 300 items from the main-panel sample. The draw gave each of the thirteen labels (the twelve categories and "not a civic problem") at least 20 items, and the rest followed how often the first coder used each label. Within each label the draw was spread across outlets and across three periods. If a page could not be read, the next candidate from the same category, in a fixed random order, took its place.

The threshold and the retest are the plan's. A category needs a Cohen's kappa of at least 0.61 in a city. One that falls short gets one revision of its wording, a fresh sample and one more test. If it still falls short, it is dropped for that city.

The run added three scoring rules that the plan does not spell out. All three were set after provisional scores from the third AI pass had been seen and before the official second coder ran.

1. **Which items count.** The 0.61 rule is applied to the validation items that remain in the main series after the headline-check rule (Section 4.4). In Hong Kong that is 228 of 299 items, with 71 left out. Leaving items out can take a label below 20 scored items. The counts, and kappa on all items, are in `data/public/validation_report.md`.
2. **What the second coder reads when no page can be read.** It tries the live page, then the Internet Archive. If neither can be read and the article is from 2020 on, it reads the real headline that GDELT stored, with no opening lines. Earlier items are replaced. Headline-only items in the scored set: 130 in Hong Kong, 1 in New York City and 16 in London. The South China Morning Post's site answered automated requests with a challenge page, so the run stopped using that site and did not fetch its pages from anywhere else.
3. **Weights.** Agreement is weighted on two margins: the first coder's category, in proportion to the labeled sample, and the outlet, in proportion to its weight in the attention index.

### 4.3 Agreement by category

The status of these numbers is: final (scored against `coder2`). The blind second coder ran on November 18 after its daily quota reset and labeled 898 validation items. It re-labeled 50 items in a fresh request.

**Table 4.** Cohen's kappa between the two AI coders, by category and city, with the decision for each category. The first number is from the first sample. A second number is the kappa on the fresh sample under the revised wording.

| Category | Hong Kong | New York City | London |
| :-- | --: | --: | --: |
| Safety | 0.72 kept, caution (fresh sample 0.57) | 0.80 kept | 0.83 kept |
| Economy | 0.65 kept | 0.77 kept, caution (fresh sample 0.58) | 0.64 kept |
| Housing | 0.46, retest 0.88: kept | 0.98 kept, caution (fresh sample 0.55) | 0.81 kept |
| Transport | 0.36, retest 0.62: kept | 0.82 kept | 0.80 kept |
| Environment | 0.79 kept | 0.65 kept | 0.61 kept |
| Health | 0.76 kept | 0.86 kept | 0.81 kept |
| Education | 0.82 kept, caution (fresh sample 0.58) | 0.74 kept | 0.88 kept, caution (fresh sample 0.51) |
| Cost of Living | 0.44, retest 0.33: dropped | 0.67 kept | 0.41, retest 0.25: dropped |
| Governance | 0.73 kept, caution (fresh sample 0.59) | 0.77 kept | 0.52, retest 0.69: kept |
| Culture | 0.18, retest 0.14: dropped | 0.20, retest 0.15: dropped | 0.20, retest 0.23: dropped |
| Technology | 0.11, retest 0.39: dropped | 0.68 kept, caution (fresh sample 0.50) | 0.45, retest 0.13: dropped |
| Community | 0.36, retest 0.48: dropped | 0.46, retest 0.30: dropped | 0.34, retest 0.47: dropped |
| Not a civic problem | 0.62 | 0.72 | 0.75 |
| **Overall** | **0.65** | **0.76** | **0.71** |
| Items | 228 | 300 | 299 |
| Not about the city (weighted) | 15% | 8% | 9% |

Overall kappa was 0.65 in Hong Kong (95% interval 0.56 to 0.74), 0.76 in New York City (0.69 to 0.82) and 0.71 in London (0.64 to 0.78). Kappa on tone, in the same order, was 0.51, 0.44 and 0.68. The plan sets no threshold for tone. Where a city's tone kappa is under 0.61, the negative-tone check in Table 13 is weak evidence for that city.

**The retest.** After the first test, the run reworded once the seven categories that had failed in any city (Housing, Transport, Cost of Living, Governance, Culture, Technology, Community). Both coders then labeled a fresh sample of about 300 items per city with the revised wording, and Table 4 gives both values. Passed and kept: Hong Kong: Housing (0.88), Transport (0.62). London: Governance (0.69). Every other retested category stayed under 0.61 and is dropped. A category that passed the first test stays kept, a rule the run set before the retest was scored. Of those, 7 scored under 0.61 on the fresh sample and are marked as cautions in Table 4. Each fresh-sample value rests on about 20 items per label, so single values move a lot.

Because revised categories passed, every article was labeled a second time with the revised prompt, by the same model with the same settings (429,081 items). Every news number below rests on this second set of labels. The first test, the headline check and the consistency checks were run on the first set. The two sets give the same category for these shares of articles: Hong Kong 85% (kappa 0.82), New York 89% (kappa 0.87), London 89% (kappa 0.87). As an exploratory comparison, the first labels, with failed categories dropped and no retest, gave a pooled news slope of 0.07 (0.02 to 0.10) across 19 pairs (`data/public/results_first_codebook.json`).

Dropped among the eight compared categories: Cost of Living in Hong Kong, none in New York City and Cost of Living in London. When a compared category is dropped in a city, that city's news pair for the category leaves every test. Search pairs are not affected, because search needs no labels.

No Hong Kong item from before 2020 is in the scored set. The South China Morning Post's pages could not be read, GDELT stores no headline before 2020, and the other two Hong Kong outlets are left out of 2015 to 2019 (Section 4.4). So Hong Kong's labels for 2015 to 2019 were not validated at all.

Table 4b shows which categories fall below 0.61 under each scoring rule. The first row for each city is the plan as written.

**Table 4b.** Categories below 0.61 under the plan as written and under the rules of Section 4.2 (description).

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

### 4.4 The city filter and the headline check

The second coder judged 15% of articles in Hong Kong, 8% in New York City and 9% in London to be not really about the study city (weighted).

GDELT stores real page titles from 2020 onward. For a sample of 2020 to 2026 articles, the first coder labeled each article twice: once from the stored headline alone, and once from the inputs used for every year. For items with headline words in the address, the two sets of labels agreed at kappa 0.80 in Hong Kong, 0.79 in New York City and 0.84 in London. For Hong Kong items with theme tags alone (1,026 items), kappa was 0.42. The other two cities had too few such items to test.

The plan set a rule for this case. If theme-tag-only labels fall below 0.61, the outlets with number-only addresses are left out of 2015 to 2019. The outcome recorded by the run: Theme-tag-only labels agreed with real-headline labels at kappa 0.42, below 0.61. HK China News Agency and Oriental Daily, whose addresses were number-only before 2020, are left out of 2015 to 2019. Hong Kong's news series for those years rests on the South China Morning Post alone.

Some London borough papers had number-only addresses for part of 2015 and 2016 and were kept (Table 17), so their labels for those months rest on theme tags alone.

### 4.5 Consistency checks

Three consistency checks were run. First, the first coder was compared with a larger model from the same family on 300 items with the same inputs: kappa 0.81 on category and 0.63 on tone. Second, a third AI pass by a different model read the same headlines and opening lines as the second coder. On 150 items its kappa was 0.76 against the second coder and 0.64 against the first. Third, the second coder labeled 50 of the same items again in a fresh request: kappa 0.80.

A file of 50 validation items with a blank label column (`deliverables/optional_hand_check_50.csv`) is included so that a reader can code a sample by hand and compare.

## 5. Results

Every number in this section comes from `data/public/results.json`, generated at 2026-11-18T09:25:44Z (UTC). Table 5 holds the four pre-registered tests.

**Table 5.** The pooled models (the pre-registered main tests). Slopes are in standard deviations of attention change per standard deviation of official change. A positive slope means attention rose when the official measure worsened.

| Source | H1 slope (95% interval) | p | Pairs | Periods | Independent pair-years | Slope when worsening | Slope when improving | Difference (95% interval) |
| :-- | :-- | --: | --: | --: | --: | :-- | :-- | :-- |
| News | 0.07 (0.02 to 0.10) | 0.006 | 21 | 1,994 | 206 | 0.05 (0.01 to 0.10) | 0.10 (-0.04 to 0.17) | -0.05 (-0.14 to 0.11) |
| Search | 0.26 (0.19 to 0.42) | < 0.001 | 18 | 3,980 | 336 | 0.37 (0.22 to 0.59) | 0.17 (0.08 to 0.39) | 0.20 (-0.10 to 0.47) |

### 5.1 H1: does attention move with the official measure?

For news coverage, attention rose 0.07 standard deviations for each standard deviation the official measure worsened (95% interval 0.02 to 0.10, 21 city and category pairs, about 206 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for news coverage.

For search interest, attention rose 0.26 standard deviations for each standard deviation the official measure worsened (95% interval 0.19 to 0.42, 18 city and category pairs, about 336 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for search interest.

Section 5.6 reruns both models without 2020 to 2022, and each verdict should be read with that row.

The two models pool different pairs over different years, so their slopes are not directly comparable. Tables 6 and 7 fit the same model within each category and within each city. They are description. Each row rests on a few pairs, and no row is a test of H1.

**Table 6.** The H1 slope within each category (description).

| Category | News slope (95% interval) | Cities | Search slope (95% interval) | Cities |
| :-- | :-- | --: | :-- | --: |
| Safety | 0.06 (-0.09 to 0.17) | 3 | 0.27 (0.14 to 0.36) | 2 |
| Economy | 0.07 (0.01 to 0.11) | 3 | 0.58 (0.36 to 0.70) | 3 |
| Housing | 0.03 (-0.03 to 0.06) | 3 | 0.05 (-0.10 to 0.23) | 3 |
| Transport | 0.08 (-0.03 to 0.19) | 3 | 0.22 (0.06 to 0.46) | 2 |
| Environment | 0.17 (0.07 to 0.29) | 3 | 0.41 (0.05 to 0.90) | 3 |
| Health | 0.46 (-0.43 to 0.50) | 2 | -0.06 (-0.31 to 0.08) | 2 |
| Education | -0.25 (-0.85 to 0.25) | 3 | not tested | 0 |
| Cost of Living | 0.08 (-0.11 to 0.19) | 1 | 0.59 (0.43 to 0.74) | 3 |

**Table 7.** The H1 slope within each city (description).

| City | News slope (95% interval) | Pairs | Search slope (95% interval) | Pairs |
| :-- | :-- | --: | :-- | --: |
| Hong Kong | -0.04 (-0.26 to 0.08) | 7 | 0.23 (0.08 to 0.36) | 5 |
| New York City | 0.08 (0.03 to 0.11) | 8 | 0.31 (0.20 to 0.62) | 7 |
| London | 0.11 (-0.01 to 0.26) | 6 | 0.18 (0.08 to 0.26) | 6 |

The plan said Hong Kong results would be reported by outlet group. Table 7b gives each Hong Kong outlet's category shares. It is description.

**Table 7b.** Hong Kong: category shares by outlet and period (description).

| Category | South China Morning Post 2015 to 2019 | South China Morning Post 2020 to 2026 | Oriental Daily 2020 to 2026 | HK China News Agency 2020 to 2026 |
| :-- | --: | --: | --: | --: |
| Safety | 15.5% | 15.1% | 6.3% | 5.5% |
| Economy | 8.7% | 11.7% | 25.1% | 12.4% |
| Housing | 3.4% | 3.1% | 5.9% | 0.5% |
| Transport | 5.7% | 3.1% | 3.7% | 4.0% |
| Environment | 5.6% | 5.6% | 4.3% | 5.2% |
| Health | 6.8% | 16.6% | 15.6% | 19.6% |
| Education | 4.3% | 5.6% | 1.7% | 4.6% |
| Cost of Living | 0.5% | 0.9% | 1.0% | 0.7% |
| Governance | 32.3% | 24.4% | 12.4% | 37.6% |
| Culture | 1.5% | 1.2% | 0.3% | 0.0% |
| Technology | 0.9% | 1.1% | 0.5% | 1.6% |
| Community | 1.9% | 1.1% | 0.3% | 0.5% |
| Not a civic problem | 13.0% | 10.5% | 22.8% | 7.9% |

### 5.2 H2: does attention react more to worsening?

For news coverage, the reaction to worsening and to improving could not be told apart. The slope was 0.05 when the problem worsened and 0.10 when it improved. The difference was -0.05 (95% interval -0.14 to 0.11). The interval includes zero, so H2 is not supported for news coverage.

For search interest, the reaction to worsening and to improving could not be told apart. The slope was 0.37 when the problem worsened and 0.17 when it improved. The difference was 0.20 (95% interval -0.10 to 0.47). The interval includes zero, so H2 is not supported for search interest.

### 5.3 Lead and lag (exploratory)

The plan made no prediction here. Table 8 gives, for each category, the lag at which the correlation between attention change and official change, averaged across cities, was largest in size. A positive lag means attention moved after the official measure. A lag at either end of the range should be read with caution. Of 33 monthly pairs, 16 had a p-value below 0.05 for their largest correlation, with no adjustment for the number of pairs. The p-value comes from a permutation test that shifts the attention series in time.

**Table 8.** Lead and lag between attention and the official measure, by category (exploratory).

| Category | News: lag where the mean r is furthest from zero | Mean r at that lag | Search: lag where the mean r is furthest from zero | Mean r at that lag |
| :-- | --: | --: | --: | --: |
| Safety | 0 months | 0.42 | -1 month | 0.43 |
| Economy | -1 month | 0.37 | -1 month | 0.51 |
| Housing | +12 months | -0.19 | -10 months | 0.25 |
| Transport | -12 months | -0.16 | +3 months | 0.25 |
| Environment | -12 months | -0.19 | 0 months | 0.23 |
| Health | 0 months | 0.59 | -2 months | 0.47 |
| Education | not tested |  | not tested |  |
| Cost of Living | +3 months | 0.18 | -1 month | 0.58 |

Table 9 compares news with search. A positive lag means news moved after search. The table covers all twelve categories, including sparse search sets and news categories dropped in validation.

**Table 9.** Lead and lag between news and search, by category (exploratory).

| Category | Lag where the mean r is furthest from zero | Mean r at that lag | Mean r at lag 0 | Cities |
| :-- | --: | --: | --: | --: |
| Safety | +6 months | 0.23 | 0.18 | 3 |
| Economy | 0 months | 0.28 | 0.28 | 3 |
| Housing | -2 months | 0.14 | 0.09 | 3 |
| Transport | -1 month | 0.32 | 0.27 | 3 |
| Environment | +3 months | 0.16 | 0.02 | 3 |
| Health | -11 months | -0.23 | 0.08 | 3 |
| Education | +3 months | -0.20 | -0.10 | 3 |
| Cost of Living | -3 months | 0.25 | 0.18 | 3 |
| Governance | 0 months | 0.33 | 0.33 | 3 |
| Culture | +12 months | -0.10 | 0.07 | 3 |
| Technology | 0 months | 0.34 | 0.34 | 3 |
| Community | -6 months | -0.18 | 0.03 | 3 |

### 5.4 H3: where do the two disconnect?

For news coverage, Safety showed the largest gap in 1 of 3 cities. Hong Kong: Safety ranked 1 of 7 (70% of periods moved in opposite directions; the largest was Safety at 70%). New York City: Safety ranked 4 of 8 (45% of periods moved in opposite directions; the largest was Education at 67%). London: Safety ranked 6 of 6 (34% of periods moved in opposite directions; the largest was Housing at 59%). H3 predicted the largest gap in at least two cities, so it is not supported.

For search interest, Safety showed the largest gap in 0 of 3 cities. Hong Kong: Safety could not be tested. New York City: Safety ranked 4 of 7 (41% of periods moved in opposite directions; the largest was Environment at 47%). London: Safety ranked 4 of 6 (41% of periods moved in opposite directions; the largest was Environment at 52%). H3 predicted the largest gap in at least two cities, so it is not supported.

Tables 10 and 11 give the share for every pair, with the number of periods in parentheses. A period in which either series did not change has no direction and is left out, so some counts here are smaller than the period counts in Appendix Table A1. Annual pairs rest on about ten periods, so one year moves their share a long way.

**Table 10.** Share of periods in which news attention and the official measure moved in opposite directions.

| Category | Hong Kong | New York City | London |
| :-- | --: | --: | --: |
| Safety | 70% (10 years) | 45% (128 months) | 34% (129 months) |
| Economy | 59% (114 months) | 47% (118 months) | 44% (125 months) |
| Housing | 37% (126 months) | 56% (129 months) | 59% (128 months) |
| Transport | 54% (125 months) | 34% (129 months) | 43% (119 months) |
| Environment | 46% (123 months) | 41% (124 months) | 48% (85 months) |
| Health | 59% (29 quarters) | 44% (70 months) | not tested |
| Education | 56% (9 years) | 67% (9 years) | 40% (10 years) |
| Cost of Living | not tested | 42% (91 months) | not tested |

**Table 11.** Share of periods in which search attention and the official measure moved in opposite directions.

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

**Disconnections.** The run found 78 stretches of six or more months of opposite movement: 24 in news and 54 in search. Table 12 counts them by cause, and Appendix Table A4 lists the twenty longest. Each stretch has a proposed cause: 4 from reading a seeded sample of that period's stories, and 74 by rule alone. The stretches labeled as attention following a news cycle are the pattern Downs (1972) expected: the official measure kept worsening while the category's share of attention fell.

**Table 12.** Disconnections of six months or more, by proposed cause.

| Proposed cause | Disconnections of six months or more |
| :-- | --: |
| unclear | 35 |
| attention followed a news cycle rather than conditions | 25 |
| a real event drew coverage the indicator does not capture | 11 |
| the official measure changed how it counts | 4 |
| the two measure different parts of the problem | 3 |

**Case study.** The longest news disconnection with a proposed cause other than unclear was in Hong Kong, in the Economy category, from 2022-05 to 2023-06 (14 months). Over those months the official measure was improving, with a mean yearly change of -1.63 standard deviations (worse is positive). The category's share of news attention was rising, with a mean yearly change of 1.41 standard deviations. Proposed cause: the two measure different parts of the problem.

> Evidence recorded by the run: The unemployment rate fell through this period. A seeded sample of ten Economy stories from the period is about weak consumer spending, calls to reopen the border, rising interest rates and people leaving the city. The category covers business conditions as a whole. The indicator covers jobs only.


### 5.5 The 48 pairs (description)

Of the 48 city, category and source pairs, 39 could be tested and 9 could not. A pair is left out when its official series is missing, its search set is too sparse, its news category was dropped in validation, or it has too few matched periods. After the Benjamini-Hochberg adjustment, 14 pairs had an adjusted p-value below 0.05 for the correlation between attention change and official change. Each p-value comes from the block bootstrap. Appendix Table A1 gives every pair.

### 5.6 Checks that the results hold

Table 13 reruns the H1 model and the H2 difference under each check. "Not run" means the check does not apply to that source or could not be computed. One row keeps and drops categories by the validation rule as the plan words it (Table 4b): the news slope there was 0.08 (0.02 to 0.11) across 16 pairs. A check agrees with the main result when its slope has the same sign and its interval sits on the same side of zero. Appendix Tables A2 and A3 add p-values and sample sizes.

Without 2020 to 2022, the news slope was 0.02 (-0.05 to 0.06), an interval that includes zero. The search slope was 0.26 (0.17 to 0.40), an interval that sits above zero. With every other marked break month also left out, the news interval includes zero and the search interval sits above zero. Where one of these includes zero and the main interval does not, that source's H1 verdict rests on the COVID years.

**Table 13.** Checks that the results hold.

| Check | News H1 slope (95% interval) | News pairs | News worse minus better | Search H1 slope (95% interval) | Search pairs | Search worse minus better |
| :-- | :-- | --: | :-- | :-- | --: | :-- |
| Main model | 0.07 (0.02 to 0.10) | 21 | -0.05 (-0.14 to 0.11) | 0.26 (0.19 to 0.42) | 18 | 0.20 (-0.10 to 0.47) |
| Backup indicators in place of the main ones | 0.13 (0.06 to 0.20) | 21 | 0.02 (-0.17 to 0.20) | 0.28 (0.17 to 0.37) | 17 | -0.15 (-0.44 to 0.10) |
| Without 2020 to 2022 | 0.02 (-0.05 to 0.06) | 21 | 0.02 (-0.16 to 0.22) | 0.26 (0.17 to 0.40) | 18 | 0.03 (-0.35 to 0.42) |
| Without 2020 to 2022 and every other marked break month | 0.06 (-0.03 to 0.16) | 21 | 0.04 (-0.19 to 0.40) | 0.24 (0.17 to 0.31) | 18 | 0.04 (-0.21 to 0.21) |
| Official series aligned by release date | 0.02 (-0.01 to 0.06) | 21 | 0.05 (-0.04 to 0.15) | 0.18 (0.11 to 0.31) | 18 | 0.23 (-0.05 to 0.45) |
| All listed outlets in place of the fixed panel | 0.08 (0.01 to 0.12) | 21 | -0.09 (-0.22 to 0.16) | not run |  |  |
| Negative-tone share in place of all coverage | 0.09 (0.03 to 0.13) | 21 | -0.11 (-0.22 to 0.13) | not run |  |  |
| Hong Kong without HK China News Agency | 0.07 (0.01 to 0.10) | 21 | -0.05 (-0.14 to 0.12) | not run |  |  |
| London without the seven borough papers that jumped in volume | 0.06 (-0.00 to 0.09) | 21 | -0.05 (-0.13 to 0.12) | not run |  |  |
| Categories kept or dropped by the validation rule as the plan words it (every validation item, weights by category only) | 0.08 (0.02 to 0.11) | 16 | -0.09 (-0.19 to 0.07) | not run |  |  |
| Description: Hong Kong pairs only, periods before 2021 (several major outlets closed in 2021) | -0.20 (-0.68 to 0.12) | 7 | 0.84 (-1.28 to 1.52) | not run |  |  |
| Description: Hong Kong pairs only, periods from 2021 on | 0.04 (-0.15 to 0.20) | 7 | 0.24 (-0.31 to 0.44) | not run |  |  |
| Exploratory: every main-panel outlet in every year (no outlets left out of 2015 to 2019) | 0.07 (0.02 to 0.09) | 21 | -0.05 (-0.14 to 0.11) | not run |  |  |
| Exploratory: Hong Kong from articles with headline words in the address only (no theme-tag-only labels in any year) | 0.07 (0.02 to 0.10) | 21 | -0.06 (-0.15 to 0.10) | not run |  |  |
| Exploratory: bootstrap with 24-month blocks (wider intervals if changes are persistent) | 0.07 (0.03 to 0.09) | 21 | -0.05 (-0.10 to 0.10) | 0.26 (0.19 to 0.45) | 18 | 0.20 (-0.10 to 0.42) |

### 5.7 Current-year ranking (description)

For each city, the eight compared categories are ranked twice: by how far the official indicator now sits from its own 2015 to 2019 average, and by the category's share of news over the latest twelve months. The Spearman rank correlation between the two orderings was 0.21 in Hong Kong, 0.04 in New York City and -0.32 in London, across 8, 7 and 7 categories. The rankings are in Appendix Tables A5 to A7. The distance is in units of each series' spread over 2015 to 2019. Some series barely moved in those years, which makes their distances very large, so the rank correlations are rough. A category dropped in validation still shows an unvalidated news share.

### 5.8 The four signal-only categories (description)

Table 14 gives each signal-only category's mean share of local news in 2015 to 2019 and in 2023 to 2026, with its peak month. The plan called for naming the major events behind the peaks. The last column holds notes written for some rows after reading a seeded sample of the peak month's headlines. A blank cell means no note was written. A category dropped in validation for a city still appears in the table, and its row is not validated.

**Table 14.** Signal-only categories: share of local news (description).

| City | Category | Agreement check | Mean share 2015 to 2019 | Mean share 2023 to 2026 | Peak month | Share in peak month | What the peak month's coverage was about (from a seeded sample) |
| :-- | :-- | :-- | --: | --: | :-- | --: | :-- |
| Hong Kong | Governance | kept | 32.3% | 22.7% | 2019-06 | 52.7% | the extradition bill protests |
| Hong Kong | Culture | dropped: shown for completeness only | 1.5% | 0.6% | 2017-01 | 4.5% |  |
| Hong Kong | Technology | dropped: shown for completeness only | 0.9% | 1.4% | 2018-11 | 3.3% |  |
| Hong Kong | Community | dropped: shown for completeness only | 1.9% | 0.7% | 2019-05 | 6.0% |  |
| New York City | Governance | kept | 21.0% | 26.4% | 2025-06 | 43.2% | the Democratic primary for mayor |
| New York City | Culture | dropped: shown for completeness only | 0.9% | 0.7% | 2018-04 | 3.7% |  |
| New York City | Technology | kept | 0.4% | 0.3% | 2019-07 | 3.9% | the July 2019 power blackout in Manhattan |
| New York City | Community | dropped: shown for completeness only | 1.8% | 1.6% | 2015-11 | 5.4% |  |
| London | Governance | kept | 9.5% | 5.3% | 2015-04 | 28.0% | the 2015 general election campaign |
| London | Culture | dropped: shown for completeness only | 1.5% | 1.5% | 2026-03 | 3.6% |  |
| London | Technology | dropped: shown for completeness only | 0.2% | 0.4% | 2017-05 | 1.4% |  |
| London | Community | dropped: shown for completeness only | 3.8% | 1.9% | 2020-06 | 9.4% |  |


## 6. Discussion

**What was found.** Attention followed the official measures a little. A worsening of one standard deviation in an official measure went with a rise of 0.07 standard deviations in news attention and 0.26 in search attention. Both intervals exclude zero, so H1 is supported for both sources. Both slopes are weak, so most of the movement in attention comes from something else. H2 is not supported for either source: the reaction to worsening and the reaction to improving could not be told apart. H3 is not supported: Safety had the largest gap in 1 of 3 cities for news and in 0 for search. Not supported means this design could not tell the result from zero. It does not show that there is no difference.

**The COVID years.** Without 2020 to 2022 the news slope is 0.02 (-0.05 to 0.06), an interval that includes zero. Those years carry the pooled news result. The search slope without them is 0.26 (0.17 to 0.40), so the search verdict does not depend on them. The news interval also includes zero in these rows of Table 13: official series aligned by release date; london without the seven borough papers that jumped in volume. No other row of Table 13 moves the search interval to the other side of zero.

**A news-based score.** OurCityHealth scores cities from news coverage. On these results, a change in a category's share of coverage says little about a change in the official measure of the same problem: the pooled link is weak, and outside the pandemic years it could not be told from zero. A news-based score measures attention. Whether it can stand in for conditions has to be read category by category (Table 6 and Appendix Table A1), and only for categories that passed validation in that city.

**What this means for OurCityHealth.** These results change how I will build the platform in three ways. First, news-based scores will be presented as measures of attention, shown beside official indicators and not in place of them. Second, search interest followed official change more closely than news did, so I plan to add it as a signal. Third, the platform will score a category in a city only where the labels pass validation, and it will flag the periods where attention and official data move apart, because those gaps carry information of their own.

**How far to trust any verdict.** Every verdict rests on labels validated by agreement between two AI coders and on intervals that are likely too narrow (Section 7). The lower end of the news interval, 0.02, is close to zero, so I treat the news verdict as provisional. A hand-coded sample is the natural next step.

## 7. Limitations

The plan stated these limitations, and they still hold.

- **Official statistics are a benchmark with blind spots.** Where the two disagree, the official measure may be the one that is wrong.
- **The news panels are narrow.** Hong Kong's main panel is mainstream and pro-establishment. London's is borough papers, with no citywide outlet. Machine-coded GDELT locations are unreliable below the country level (Hammond and Weidmann, 2014).
- **Early labels rest on thin inputs:** web-address headlines and theme tags.
- **Search geography is wider than the city** in New York (the media market) and in London (England).
- **Prices are not city-level.** New York's cover the metro area. London's inflation is UK-wide and includes some rent.
- **Attention is volume.** It shows how much a problem is discussed, and it does not show what people think should be done about it.
- **The study does not test causes.** Its explanations of disagreements are judgments.

The analysis added these.

- **Some kept categories missed the bar on the retest sample.** 7 kept categories scored under 0.61 on the fresh sample under the revised wording (Table 4). That sample is the only test of the revised labels, and it has about 20 items per label.
- **Three scoring rules were set during validation,** after provisional scores had been seen and before the official second coder ran (Section 4.2 and Table 4b).
- **Theme-tag-only labels are weak.** In the headline check they agreed with real-headline labels at kappa 0.42. The plan's rule removes the affected outlets from 2015 to 2019 only. HK China News Agency has number-only addresses in every year, and Oriental Daily had them through 2020 and for part of 2021, so theme-tag-only labels remain in the Hong Kong main series from 2020 on. Two rows of Table 13 check this.
- **Hong Kong's labels for 2015 to 2019 were not validated.** No Hong Kong item from before 2020 is in the scored validation set (Section 4.3).
- **Search data rest on two downloads per request,** taken on consecutive days, against the three planned. Downloads taken close together mostly repeat the same sample of searches. Several search sets also read "<1" in most months and carry little signal.
- **Some official series are missing or short.** Missing: London Health. New York Health's first month is 2020-01, so its yearly changes fall in or just after the COVID years.
- **The intervals are likely too narrow.** On unrelated made-up series the bootstrap wrongly excluded zero in 7 of 40 trials (Section 3.8). An interval that only just excludes zero should not be read as firm.
- **Disconnection causes are a first pass.** Of 78 causes, 74 come from a fixed rule alone.

## 8. Deviations from the pre-registered plan

The plan is the methodology posted on November 17, 2026 (commit `e8d5f32`, tag `prereg-v1`). Tables 15 to 17 list the places where the study did something different. `deliverables/deviations.md` holds the full list with more detail.

The main change is the second coder: an independent AI language model in place of hand-coding, with further AI passes as consistency checks. Table 15 gives the changes decided before data collection (rows 1.1 to 1.4), the changes made during the analysis after the first labeling key hit a daily cap (2.1 to 2.5), and the changes forced by what the run found (3.1 to 3.5).

**Table 15.** Deviations in sections 1 to 3 of `deliverables/deviations.md`.

| # | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| 1.1 | I was to hand-code about 900 items. Agreement between the AI labels and that hand-coding was to decide which categories are analyzed. | A second AI language model from a different model family codes the same validation set blind, from the real headline and opening lines, or from the real headline alone where no page could be read. The sample design, kappa, the 0.61 threshold, one revision and the drop rule are as written. Three scoring rules were added (Table 17). | My design decision for this study. Kappa here measures agreement between two AI coders. |
| 1.2 | A classmate was to label 150 of the same items. I was to re-label 50 items two weeks later. | A third AI pass by a different model codes the same items. The second coder re-labels 50 items in a fresh request. | Same reason. |
| 1.3 | Pre-registration on the Open Science Framework in October, after the mentors approve the plan. | Pre-registration on GitHub and the Internet Archive on November 17, 2026, before any outcome data. | Posted before any outcome data were pulled. |
| 1.4 | Each Trends request is downloaded on three different days and averaged. | Two downloads per request, taken on consecutive days. | Two downloads were available at the time of analysis. |
| 2.1 | The first coder is a small model from the provider first chosen. | The first coder is a small model from a different provider. Every item was labeled by this one model. Items the earlier model had labeled were relabeled. | The first provider's key hit a daily cap (3.1). My instruction during the run. |
| 2.2 | The second coder is a model from a different family than the first. | Still true. The second coder is a model from the provider first chosen for labeling, run blind after its daily quota reset. The third pass is a different model from that provider. | My instruction during the run. |
| 2.3 | Model and prompt are frozen before the full run. | The same prompt was used for two test runs and for the full run, and it did not change between them (Section 3.4). The first prompt was fixed before the full run and did not change during it. After validation, the one revision the plan allows changed seven category lines, and every article was labeled again with the revised prompt. The model changed before the full run (2.1). The first 2,000 items were labeled first to measure cost: $0.13, or $0.06 per 1,000 items. The projected cost of the full sample was under the cap of $100, so the sample was not shrunk. | My instruction: measure the real cost per item first. |
| 2.4 | Not in the plan. | The first coder was compared with a larger model from the same family on 300 of those items. Kappa was 0.81 on category and 0.63 on tone. The rule set beforehand was to keep the smaller model at 0.75 or higher. The run kept the smaller model. | My instruction during the run. |
| 2.5 | Not in the plan. | Every request stayed under 100,000 tokens. The largest was 23,856 input tokens in the cost test and 26,830 in the full run. All labeling used normal requests. No batch job was submitted, so nothing was billed twice. | My instructions during the run. |
| 3.1 | Bulk labeling through the first provider's key, with a $100 budget. | That key was on a free tier with a daily request cap. One model reached its cap partway through the Hong Kong sample. A replacement was started and then stopped when the instruction in 2.1 arrived. Neither set of labels is used in any index. Both are kept as cross-model comparisons. | Found in the throughput test. Paid access was not turned on, because that would have changed my cloud settings. |
| 3.2 | The Internet Archive saves the repository page and the raw methodology file. | The raw methodology and the source inventory were saved and checked against their SHA-256. The proposal and the README were also saved. The repository page returned an error on the first tries. The outcome of the retries is in `deliverables/preregistration.md`. | An Archive error for github.com pages. |
| 3.3 | London Health: share of the waiting list waiting under 18 weeks, with A&E four-hour performance as the backup. | Both are missing. London Health has no official series, so that pair is not tested. | The NHS England statistics pages returned a browser challenge. The rules for this run say to stop when a site blocks collection. No open-portal copy was found. |
| 3.4 | New York Health: deaths of city residents by month from CDC WONDER, from 1999. | Deaths from all causes occurring in New York City, from the CDC's open provisional file, from 2020-01. | CDC WONDER requires accepting a data-use agreement on a web form, which the run does not do. |
| 3.5 | The model reads the same inputs for every outlet. | True, but 6,117 of 435,201 sampled items had no headline words and no theme tags. They could not be labeled and are left out of the shares. | GDELT recorded no themes for them. |

**Official indicators.** Table 16 lists each official series that differs from the methodology's tables. Notes on every series are in `data/public/official_series_meta.json` and in `deliverables/source_inventory_v2.md`.

**Table 16.** Official indicators: differences from the methodology's tables.

| Series | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| Hong Kong Health, main | Specialist outpatient waiting time from 2013, all specialties from 2015. | Starts 2018-Q3. | The data.gov.hk archive of the Hospital Authority file is the only machine-readable history. |
| Hong Kong Transport, main | Fatal and serious road accidents from 2003. | Starts 2013-01. | The earlier figures are only in PDF digests, which were not extracted. |
| Hong Kong Cost of Living, main | Composite CPI without the housing section, from 1981. | Starts 2004-10. Built from the table that holds the section indices, with the published housing weights for four base periods. | The planned table has no section indices. The oldest weights were not found. |
| Hong Kong Economy, main | Break for the change in seasonal adjustment marked at 2008. | Marked at January to December 2007. | The statistics office revised the series back to the period ending January 2007, so those are the comparisons that mix methods. |
| Hong Kong Environment, main | Hourly NO2 and PM10 averaged by month. | The publisher's own station monthly averages for 11 general stations. Ends 2026-05. | The export provides monthly averages. |
| Hong Kong Safety, main | Annual from 2001, monthly for 2022 to 2024. | Annual, 2001 to 2025. The monthly file for 2022 to 2024 was not found. Two years come from an Internet Archive copy of the police workbook. | Source pages moved. |
| Hong Kong Education, main | Share of day-school candidates meeting the entrance requirement, from 2012. | 2012 to 2025, core subjects only. The first year was read from a scanned PDF and checked against the counts. The 2026 file was not at the usual address. | Source format. |
| Hong Kong backups | Public rental waiting time (quarterly), MTR delays of 8 minutes or more (annual from 2008), very hot days, teacher wastage. | Waiting time 2014-Q1 to 2026-Q2 with some quarters missing. MTR delays 2008 to 2024 with some years missing. Very hot days annual. Teacher wastage 2018 to 2026, as the mean of primary and secondary. | Assembled from dated official pages and Legislative Council papers. |
| New York Education, main | Four-year graduation rate. | The June rate, classes of 2005 to 2025. | No August rate is published for the earliest classes. |
| New York Transport, main | Subway on-time performance from 2009. | Starts 2009-06, weekday trains, with two months missing. Two files are joined at 2015 and agree closely where they overlap. | Source coverage. |
| New York Housing, main | DHS shelter census, with the Coalition for the Homeless series before 2013. | Three files joined. The Coalition total runs above the DHS figure at the join, which is marked as a break. Coalition months with no total are left out. | Source coverage. |
| New York Environment | PM2.5 from 1999, air quality index from 1989. | Both from 1999, ending 2026-05. A few thin months are dropped. Before 2025 most days rest on two or three of the five boroughs. | EPA file coverage. |
| New York Economy, backup | Nonfarm jobs from 1950. | From 1990-01. | The open series starts there. |
| New York prices | Break for the 2018 area redraw. | Marked for 2018. The analysis extends it through 2019, because the change in a 12-month rate looks back two years. | Follows from the transformation in Appendix C. |
| London Safety, main | Recorded crime from 2008. | Starts 2010-04. A break was added at February 2013, when fraud left the count. | No file with the older categories exists. |
| London Housing, main | Older rent index joined to the current one at 2015. | Joined at January 2015. The months around the join are marked as a break. | The two indices differ where both exist. |
| London Transport, main | Severity-adjusted killed or seriously injured, from 1979. | 2004-01 to 2025-12. | Adjusted figures do not exist for earlier years. |
| London Environment, main | NO2 at Marylebone Road and Bloomsbury. | Some months are empty, nearly all because Bloomsbury has no readings, including a long stretch from late 2023 to early 2025. Ends 2026-05. A month with one site missing is left empty and is not filled. | Missing readings in the network's data service. |
| London Education, main | Attainment 8 from 2015/16. | School years ending 2016 to 2026. The first three years come from a London Datastore workbook of DfE figures. The latest year is provisional. | Source coverage. |
| London backups | Temporary accommodation, Underground lost customer hours, PM2.5 at the same sites, absence rate. | Temporary accommodation has some empty quarters. Lost customer hours run 2011-05 to 2020-02. PM2.5 uses a different instrument code at Marylebone Road and runs 2009-05 to 2021-04. The absence rate lacks one school year. | Source coverage. |
| London Cost of Living, backup | None exists. | None. | As the methodology says. |
| Later first periods | Hong Kong Economy from 1981, Hong Kong Environment from 1990, London Environment from 1992. | First periods as built: 1985-03, 2000-01 and 2004-01. | The statistics office's open file and the publisher's monthly averages start later than the plan's tables say. The London files were fetched from the year the search data begin. |

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
| Sample for the check with all listed outlets | The same budget of 1,000 a month split equally over every listed outlet. Labeled: the full check sample (41 articles per outlet per month in Hong Kong, 50 in New York and 41 in London). |
| Theme tags sent to the model | The first 30 different tags in order of first appearance. |
| Poster | The showcase poster is eight pieces on a 710 by 550 mm board, built to a design I supplied during the run, and not the 18 to 24 letter-size pages first aimed for. This does not affect the paper. |
| Which validation items the 0.61 rule uses | Items that remain in the main series after the headline-check rule. Kappa on every validation item is in the validation report. Set after provisional scores from the third AI pass had been seen and before the official second coder ran. |
| Validation text when no page can be read | The live page, then the Internet Archive. If neither can be read and the article is from 2020 on, the second coder reads the real headline that GDELT stored, headline only. Earlier items are replaced. One site challenged automated requests, so the run stopped using it and did not fetch its pages from anywhere else. Set at the same point as the rule above. |
| Validation weights | Two margins: the first coder's category, in proportion to the labeled sample, and the outlet, in proportion to its weight in the attention index. Set at the same point as the rule above. |
| Browser used for Google Trends | The browser profile was already signed in to a Google account. The run did not sign in. Google Trends is open to visitors who are not signed in. Whether a signed-out visitor gets the same numbers was not tested. |
| London papers with number-only addresses | Some London papers had number-only addresses for part of 2015 and 2016. The headline-check rule is written for outlets, and these papers have headline words in every later year, so they were kept. |
| Minimum periods inside a check | A check that leaves periods out keeps a pair that still has at least half the minimum number of periods. |
| p-values | From the bootstrap: twice the smaller share of resampled slopes on either side of zero. |
| Release-date check | Each official series is shifted by its approximate publication lag in whole months. |
| Causes of disconnections | Proposed by a fixed rule from the marked breaks and a short list of named events. For some stretches a seeded sample of that period's headlines was also read. |
| Events at attention peaks | For some rows of Table 14 a seeded sample of the peak month's headlines was read, and the note says what the coverage was about. |
| Current-year ranking | Each main indicator's mean over its latest 12 months, or its latest value for a quarterly or annual series, is compared with its own 2015 to 2019 mean, in 2015 to 2019 standard deviations. Price indices use the 12-month rate. |
| Effective sample size | Matched periods divided by the periods in a year, summed over pairs. |
| Checks added by the run | The rows labeled exploratory in Table 13. |

**Outcomes and items cut.** Section 6 of `deliverables/deviations.md` lists the outcomes that changed what is analyzed. Two parts of the plan were cut: the social media snapshot and the optional pre-2015 news extension, which need API keys, logins or a subscription that the run did not have.

## 9. AI-use disclosure

I used AI tools throughout this study, under my direction and following the methodology I wrote. AI tools collected the official statistics, queried GDELT, downloaded the Google Trends files, drew the news sample and wrote the analysis code. An AI language model labeled every sampled article, and a second AI language model from a different model family validated a sample of those labels. AI tools also produced the figures and tables and drafted this paper, which I reviewed. The exact model names, settings and prompts are in the labeling card (`data/public/labeling_card.md`) and in the AI-use log that goes with this paper.

The research question, the twelve-category codebook, the choice of cities and official indicators, the design of the attention index and the hypotheses are mine, set out in the methodology document of October 7, 2026. I directed the analysis, made the decisions recorded in Section 8, and reviewed the results and the interpretation in this paper.

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

| City | Category | Source | Official indicator | Frequency | Periods | r (95% interval) | p | Adjusted p | Opposite directions |
| :-- | :-- | :-- | :-- | :-- | --: | :-- | --: | --: | --: |
| Hong Kong | Safety | News | Overall reported crime, annual total | A | 10 | -0.14 (-0.73 to 0.38) | 0.458 | 0.576 | 70% |
| Hong Kong | Economy | News | Unemployment rate, seasonally adjusted, 3-month moving average | M | 127 | 0.11 (-0.44 to 0.48) | 0.586 | 0.693 | 59% |
| Hong Kong | Housing | News | Private domestic rental index, all classes (1999 = 100) | M | 128 | 0.35 (0.12 to 0.54) | 0.002 | 0.007 | 37% |
| Hong Kong | Transport | News | Fatal and serious road traffic accidents | M | 127 | -0.13 (-0.40 to 0.19) | 0.282 | 0.419 | 54% |
| Hong Kong | Environment | News | NO2 and PM10 (respirable suspended particulates), monthly mean across general stations running since 2005 | M | 124 | 0.02 (-0.11 to 0.12) | 0.856 | 0.902 | 46% |
| Hong Kong | Health | News | Median waiting time for stable new specialist outpatient cases, mean over cluster and specialty pairs | Q | 29 | -0.25 (-0.83 to 0.35) | 0.336 | 0.452 | 59% |
| Hong Kong | Education | News | Share of day-school HKDSE candidates with core subjects at 3322 or better (332A from 2024) | A | 9 | -0.12 (-0.75 to 0.43) | 0.564 | 0.687 | 56% |
| Hong Kong | Cost of Living | News |  | | | not tested: dropped: agreement between the two AI coders below 0.61 | | | |
| New York City | Safety | News | Felony complaints, NYPD, by report month | M | 128 | 0.38 (0.04 to 0.59) | 0.032 | 0.078 | 45% |
| New York City | Economy | News | Unemployment rate, seasonally adjusted, New York City | M | 127 | 0.35 (-0.17 to 0.54) | 0.156 | 0.277 | 47% |
| New York City | Housing | News | People in DHS shelters, monthly average of the daily census | M | 129 | 0.20 (-0.19 to 0.39) | 0.242 | 0.378 | 56% |
| New York City | Transport | News | Subway weekday terminal on-time performance, system-wide | M | 129 | 0.36 (0.15 to 0.59) | < 0.001 | 0.004 | 34% |
| New York City | Environment | News | PM2.5, monthly mean of daily readings across the five boroughs | M | 124 | 0.33 (0.17 to 0.50) | < 0.001 | 0.004 | 41% |
| New York City | Health | News | Deaths from all causes occurring in New York City, by month | M | 70 | 0.59 (0.04 to 0.62) | 0.008 | 0.024 | 44% |
| New York City | Education | News | Four-year graduation rate as of June, NYC public schools | A | 9 | -0.30 (-0.76 to 0.46) | 0.210 | 0.354 | 67% |
| New York City | Cost of Living | News | CPI all items less shelter, New York metro area | M | 127 | 0.09 (-0.07 to 0.27) | 0.218 | 0.354 | 42% |
| London | Safety | News | Recorded crime, all offences, Metropolitan Police | M | 129 | 0.45 (0.27 to 0.62) | < 0.001 | 0.004 | 34% |
| London | Economy | News | Unemployment rate, London, aged 16 and over, seasonally adjusted (ONS YCNI) | M | 126 | 0.44 (0.09 to 0.61) | 0.024 | 0.062 | 44% |
| London | Housing | News | Private rents index, London (ONS PIPR, with IPHRP joined on before 2015) | M | 128 | -0.18 (-0.49 to 0.17) | 0.350 | 0.455 | 59% |
| London | Transport | News | Killed or seriously injured road casualties, London, severity-adjusted (DfT) | M | 119 | 0.17 (-0.13 to 0.52) | 0.290 | 0.419 | 43% |
| London | Environment | News | Nitrogen dioxide, mean of Marylebone Road and Bloomsbury (London Air Quality Network) | M | 85 | 0.18 (-0.05 to 0.47) | 0.122 | 0.227 | 48% |
| London | Health | News |  | | | not tested: no official series | | | |
| London | Education | News | Attainment 8 average score, London region, state-funded schools (DfE) | A | 10 | -0.14 (-0.77 to 0.79) | 0.720 | 0.780 | 40% |
| London | Cost of Living | News |  | | | not tested: dropped: agreement between the two AI coders below 0.61 | | | |
| Hong Kong | Safety | Search |  | | | not tested: search set too sparse to test (zero in more than 10% of months) | | | |
| Hong Kong | Economy | Search | Unemployment rate, seasonally adjusted, 3-month moving average | M | 260 | 0.57 (0.30 to 0.74) | < 0.001 | 0.004 | 39% |
| Hong Kong | Housing | Search | Private domestic rental index, all classes (1999 = 100) | M | 261 | 0.15 (-0.05 to 0.27) | 0.090 | 0.195 | 48% |
| Hong Kong | Transport | Search |  | | | not tested: search set too sparse to test (zero in more than 10% of months) | | | |
| Hong Kong | Environment | Search | NO2 and PM10 (respirable suspended particulates), monthly mean across general stations running since 2005 | M | 257 | 0.18 (0.10 to 0.33) | < 0.001 | 0.004 | 39% |
| Hong Kong | Health | Search | Median waiting time for stable new specialist outpatient cases, mean over cluster and specialty pairs | Q | 29 | -0.30 (-0.76 to 0.08) | 0.108 | 0.222 | 52% |
| Hong Kong | Education | Search |  | | | not tested: search set too sparse to test (zero in more than 10% of months) | | | |
| Hong Kong | Cost of Living | Search | Composite CPI excluding the housing section (Oct 2019 to Sep 2020 = 100) | M | 240 | 0.51 (0.14 to 0.71) | 0.004 | 0.013 | 45% |
| New York City | Safety | Search | Felony complaints, NYPD, by report month | M | 237 | 0.49 (0.24 to 0.66) | < 0.001 | 0.004 | 41% |
| New York City | Economy | Search | Unemployment rate, seasonally adjusted, New York City | M | 260 | 0.83 (0.56 to 0.90) | < 0.001 | 0.004 | 28% |
| New York City | Housing | Search | People in DHS shelters, monthly average of the daily census | M | 260 | -0.00 (-0.27 to 0.29) | 0.976 | 0.992 | 45% |
| New York City | Transport | Search | Subway weekday terminal on-time performance, system-wide | M | 193 | 0.38 (0.07 to 0.67) | 0.014 | 0.039 | 36% |
| New York City | Environment | Search | PM2.5, monthly mean of daily readings across the five boroughs | M | 251 | 0.48 (0.14 to 0.66) | < 0.001 | 0.004 | 47% |
| New York City | Health | Search | Deaths from all causes occurring in New York City, by month | M | 70 | -0.06 (-0.13 to 0.55) | 0.694 | 0.773 | 43% |
| New York City | Education | Search |  | | | not tested: search set too sparse to test (zero in more than 10% of months) | | | |
| New York City | Cost of Living | Search | CPI all items less shelter, New York metro area | M | 260 | 0.61 (0.42 to 0.73) | < 0.001 | 0.004 | 41% |
| London | Safety | Search | Recorded crime, all offences, Metropolitan Police | M | 187 | 0.31 (-0.04 to 0.54) | 0.114 | 0.222 | 41% |
| London | Economy | Search | Unemployment rate, London, aged 16 and over, seasonally adjusted (ONS YCNI) | M | 259 | 0.06 (-0.20 to 0.32) | 0.662 | 0.759 | 40% |
| London | Housing | Search | Private rents index, London (ONS PIPR, with IPHRP joined on before 2015) | M | 237 | 0.11 (-0.12 to 0.30) | 0.324 | 0.451 | 46% |
| London | Transport | Search | Killed or seriously injured road casualties, London, severity-adjusted (DfT) | M | 252 | 0.10 (-0.01 to 0.20) | 0.080 | 0.184 | 49% |
| London | Environment | Search | Nitrogen dioxide, mean of Marylebone Road and Bloomsbury (London Air Quality Network) | M | 206 | 0.02 (-0.13 to 0.12) | 0.992 | 0.992 | 52% |
| London | Health | Search |  | | | not tested: no official series | | | |
| London | Education | Search |  | | | not tested: search set too sparse to test (zero in more than 10% of months) | | | |
| London | Cost of Living | Search | CPI 12-month rate, all items, UK (ONS D7G7) | M | 261 | 0.61 (0.36 to 0.81) | < 0.001 | 0.004 | 35% |

**Table A2.** Checks that the results hold, news models, with p-values and sample sizes.

| Check | H1 slope (95% interval) | p | Pairs | Periods | Independent pair-years | Slope when worsening | Slope when improving | Difference (95% interval) |
| :-- | :-- | --: | --: | --: | --: | :-- | :-- | :-- |
| Main model | 0.07 (0.02 to 0.10) | 0.006 | 21 | 1,994 | 206 | 0.05 (0.01 to 0.10) | 0.10 (-0.04 to 0.17) | -0.05 (-0.14 to 0.11) |
| Backup indicators in place of the main ones | 0.13 (0.06 to 0.20) | < 0.001 | 21 | 1,524 | 186 | 0.13 (0.02 to 0.26) | 0.11 (0.02 to 0.21) | 0.02 (-0.17 to 0.20) |
| Without 2020 to 2022 | 0.02 (-0.05 to 0.06) | 0.414 | 21 | 1,413 | 144 | 0.02 (-0.08 to 0.08) | -0.00 (-0.16 to 0.12) | 0.02 (-0.16 to 0.22) |
| Without 2020 to 2022 and every other marked break month | 0.06 (-0.03 to 0.16) | 0.228 | 21 | 1,203 | 120 | 0.08 (-0.06 to 0.31) | 0.04 (-0.14 to 0.18) | 0.04 (-0.19 to 0.40) |
| Official series aligned by release date | 0.02 (-0.01 to 0.06) | 0.086 | 21 | 2,019 | 208 | 0.04 (0.01 to 0.09) | -0.01 (-0.08 to 0.07) | 0.05 (-0.04 to 0.15) |
| All listed outlets in place of the fixed panel | 0.08 (0.01 to 0.12) | 0.030 | 21 | 1,994 | 206 | 0.05 (0.00 to 0.11) | 0.15 (-0.08 to 0.26) | -0.09 (-0.22 to 0.16) |
| Negative-tone share in place of all coverage | 0.09 (0.03 to 0.13) | 0.002 | 21 | 1,994 | 206 | 0.06 (0.00 to 0.12) | 0.16 (-0.03 to 0.27) | -0.11 (-0.22 to 0.13) |
| Hong Kong without HK China News Agency | 0.07 (0.01 to 0.10) | 0.010 | 21 | 1,994 | 206 | 0.05 (0.01 to 0.10) | 0.10 (-0.05 to 0.17) | -0.05 (-0.14 to 0.12) |
| London without the seven borough papers that jumped in volume | 0.06 (-0.00 to 0.09) | 0.052 | 21 | 1,994 | 206 | 0.05 (-0.01 to 0.09) | 0.09 (-0.06 to 0.16) | -0.05 (-0.13 to 0.12) |
| Categories kept or dropped by the validation rule as the plan words it (every validation item, weights by category only) | 0.08 (0.02 to 0.11) | 0.004 | 16 | 1,517 | 157 | 0.05 (0.00 to 0.09) | 0.14 (-0.01 to 0.23) | -0.09 (-0.19 to 0.07) |
| Description: Hong Kong pairs only, periods before 2021 (several major outlets closed in 2021) | -0.20 (-0.68 to 0.12) | 0.296 | 7 | 249 | 30 | 0.16 (-1.32 to 0.57) | -0.68 (-1.16 to 0.24) | 0.84 (-1.28 to 1.52) |
| Description: Hong Kong pairs only, periods from 2021 on | 0.04 (-0.15 to 0.20) | 0.722 | 7 | 305 | 38 | 0.13 (-0.29 to 0.27) | -0.11 (-0.30 to 0.18) | 0.24 (-0.31 to 0.44) |
| Exploratory: every main-panel outlet in every year (no outlets left out of 2015 to 2019) | 0.07 (0.02 to 0.09) | 0.012 | 21 | 1,994 | 206 | 0.05 (0.01 to 0.09) | 0.10 (-0.04 to 0.17) | -0.05 (-0.14 to 0.11) |
| Exploratory: Hong Kong from articles with headline words in the address only (no theme-tag-only labels in any year) | 0.07 (0.02 to 0.10) | 0.004 | 21 | 1,994 | 206 | 0.05 (0.01 to 0.10) | 0.11 (-0.03 to 0.18) | -0.06 (-0.15 to 0.10) |
| Exploratory: bootstrap with 24-month blocks (wider intervals if changes are persistent) | 0.07 (0.03 to 0.09) | 0.002 | 21 | 1,994 | 206 | 0.05 (0.03 to 0.10) | 0.10 (-0.02 to 0.15) | -0.05 (-0.10 to 0.10) |

**Table A3.** Checks that the results hold, search models, with p-values and sample sizes.

| Check | H1 slope (95% interval) | p | Pairs | Periods | Independent pair-years | Slope when worsening | Slope when improving | Difference (95% interval) |
| :-- | :-- | --: | --: | --: | --: | :-- | :-- | :-- |
| Main model | 0.26 (0.19 to 0.42) | < 0.001 | 18 | 3,980 | 336 | 0.37 (0.22 to 0.59) | 0.17 (0.08 to 0.39) | 0.20 (-0.10 to 0.47) |
| Backup indicators in place of the main ones | 0.28 (0.17 to 0.37) | < 0.001 | 17 | 2,987 | 302 | 0.21 (-0.01 to 0.37) | 0.36 (0.23 to 0.49) | -0.15 (-0.44 to 0.10) |
| Without 2020 to 2022 | 0.26 (0.17 to 0.40) | < 0.001 | 18 | 3,375 | 284 | 0.27 (0.10 to 0.58) | 0.24 (0.07 to 0.50) | 0.03 (-0.35 to 0.42) |
| Without 2020 to 2022 and every other marked break month | 0.24 (0.17 to 0.31) | < 0.001 | 18 | 2,739 | 231 | 0.26 (0.13 to 0.36) | 0.22 (0.11 to 0.37) | 0.04 (-0.21 to 0.21) |
| Official series aligned by release date | 0.18 (0.11 to 0.31) | < 0.001 | 18 | 3,989 | 337 | 0.30 (0.15 to 0.47) | 0.07 (-0.01 to 0.25) | 0.23 (-0.05 to 0.45) |
| Exploratory: bootstrap with 24-month blocks (wider intervals if changes are persistent) | 0.26 (0.19 to 0.45) | < 0.001 | 18 | 3,980 | 336 | 0.37 (0.21 to 0.59) | 0.17 (0.09 to 0.40) | 0.20 (-0.10 to 0.42) |

**Table A4.** The twenty longest disconnections. Every cause is a proposed cause.

| City | Category | Source | From | To | Months | Official measure | Attention | Proposed cause | Evidence |
| :-- | :-- | :-- | :-- | :-- | --: | :-- | :-- | :-- | :-- |
| New York City | Housing | Search | 2008-10 | 2010-01 | 16 | worsening | falling | attention followed a news cycle rather than conditions | the indicator kept worsening while attention's share fell (Downs's issue-attention cycle); no marked break or event overlaps |
| New York City | Housing | Search | 2021-03 | 2022-06 | 16 | improving | rising | a real event drew coverage the indicator does not capture | COVID-19 distorts nearly every series |
| London | Economy | Search | 2007-02 | 2008-04 | 15 | improving | rising | unclear | no marked break or named event overlaps this period |
| Hong Kong | Economy | News | 2022-05 | 2023-06 | 14 | improving | rising | the two measure different parts of the problem | The unemployment rate fell through this period. A seeded sample of ten Economy stories from the period is about weak consumer spending, calls to reopen the border, rising interest rates and people leaving the city. The category covers business conditions as a whole. The indicator covers jobs only. |
| London | Economy | News | 2018-01 | 2019-02 | 14 | improving | rising | unclear | no marked break or named event overlaps this period |
| London | Housing | Search | 2019-03 | 2020-04 | 14 | worsening | falling | attention followed a news cycle rather than conditions | attention share fell while the indicator worsened; the period overlaps: COVID-19 distorts nearly every series (a spike elsewhere lowers every other share) |
| London | Housing | News | 2023-08 | 2024-07 | 12 | worsening | falling | the two measure different parts of the problem | Private rents rose faster through this period. A seeded sample of ten Housing stories from the borough papers is about council repairs, planning rules and house prices. None of the ten is about rents. |
| New York City | Safety | Search | 2010-02 | 2011-01 | 12 | improving | rising | unclear | no marked break or named event overlaps this period |
| London | Safety | Search | 2013-03 | 2014-02 | 12 | improving | rising | the official measure changed how it counts | at least half of these months fall in a counting break marked in the official series: fraud offences moved from police forces to Action Fraud; the source note says March 2013 and the counts fall in February 2013 (found tonight; not in the methodology's breaks table) |
| London | Economy | Search | 2012-07 | 2013-06 | 12 | improving | rising | unclear | no marked break or named event overlaps this period |
| Hong Kong | Cost of Living | Search | 2020-06 | 2021-04 | 11 | improving | rising | a real event drew coverage the indicator does not capture | COVID-19 distorts nearly every series |
| New York City | Safety | Search | 2014-06 | 2015-04 | 11 | improving | rising | unclear | no marked break or named event overlaps this period |
| New York City | Cost of Living | Search | 2014-11 | 2015-09 | 11 | improving | rising | unclear | no marked break or named event overlaps this period |
| London | Economy | Search | 2009-05 | 2010-03 | 11 | worsening | falling | attention followed a news cycle rather than conditions | the indicator kept worsening while attention's share fell (Downs's issue-attention cycle); no marked break or event overlaps |
| Hong Kong | Cost of Living | Search | 2019-06 | 2020-03 | 10 | worsening | falling | attention followed a news cycle rather than conditions | attention share fell while the indicator worsened; the period overlaps: COVID-19 distorts nearly every series (a spike elsewhere lowers every other share) |
| London | Housing | Search | 2010-01 | 2010-10 | 10 | improving | rising | unclear | no marked break or named event overlaps this period |
| London | Cost of Living | Search | 2014-10 | 2015-07 | 10 | improving | rising | unclear | no marked break or named event overlaps this period |
| Hong Kong | Economy | News | 2025-10 | 2026-06 | 9 | worsening | falling | attention followed a news cycle rather than conditions | the indicator kept worsening while attention's share fell (Downs's issue-attention cycle); no marked break or event overlaps |
| Hong Kong | Environment | News | 2024-08 | 2025-04 | 9 | worsening | falling | the two measure different parts of the problem | NO2 and PM10 rose while Environment's share of coverage fell. A seeded sample of eight Environment stories is about typhoons, storms, recycling rules and water quality. None of the eight is about air pollution, which is what the indicator tracks. |
| Hong Kong | Housing | Search | 2020-06 | 2021-02 | 9 | improving | rising | a real event drew coverage the indicator does not capture | COVID-19 distorts nearly every series |

**Table A5.** Current-year ranking, Hong Kong (description).

| Category | Official: distance from its 2015 to 2019 average (SD, worse is positive) | Baseline periods in 2015 to 2019 | Official rank | News share, latest 12 months | Attention rank |
| :-- | --: | --: | --: | --: | --: |
| Safety | 6.31 (short or very flat baseline: read with care) | 5 | 1 | 10.2% | 2 |
| Economy | 2.81 | 60 | 2 | 20.1% | 1 |
| Cost of Living | 0.13 | 60 | 3 | 1.3% | 8 |
| Housing | 0.12 | 60 | 4 | 3.7% | 7 |
| Environment | -1.19 | 60 | 5 | 5.5% | 4 |
| Education | -3.35 (short or very flat baseline: read with care) | 5 | 6 | 4.3% | 6 |
| Transport | -4.23 | 60 | 7 | 4.8% | 5 |
| Health | -10.45 (short or very flat baseline: read with care) | 6 | 8 | 5.9% | 3 |

**Table A6.** Current-year ranking, New York City (description).

| Category | Official: distance from its 2015 to 2019 average (SD, worse is positive) | Baseline periods in 2015 to 2019 | Official rank | News share, latest 12 months | Attention rank |
| :-- | --: | --: | --: | --: | --: |
| Housing | 19.29 (short or very flat baseline: read with care) | 60 | 1 | 4.4% | 4 |
| Safety | 3.10 | 60 | 2 | 24.6% | 1 |
| Cost of Living | 2.46 | 60 | 3 | 0.7% | 8 |
| Economy | 1.14 | 60 | 4 | 2.2% | 7 |
| Environment | 0.69 | 60 | 5 | 6.0% | 3 |
| Transport | -2.01 | 60 | 6 | 10.3% | 2 |
| Education | -2.89 (short or very flat baseline: read with care) | 5 | 7 | 3.2% | 5 |
| Health | n/a | n/a | n/a | 3.1% | 6 |

**Table A7.** Current-year ranking, London (description).

| Category | Official: distance from its 2015 to 2019 average (SD, worse is positive) | Baseline periods in 2015 to 2019 | Official rank | News share, latest 12 months | Attention rank |
| :-- | --: | --: | --: | --: | --: |
| Economy | 2.22 | 60 | 1 | 3.4% | 7 |
| Cost of Living | 1.46 | 60 | 2 | 1.0% | 8 |
| Safety | 1.25 | 60 | 3 | 18.2% | 1 |
| Housing | 0.22 | 60 | 4 | 4.2% | 4 |
| Transport | 0.19 | 60 | 5 | 8.8% | 2 |
| Education | -0.55 (short or very flat baseline: read with care) | 4 | 6 | 3.8% | 6 |
| Environment | -3.58 | 60 | 7 | 4.1% | 5 |
| Health | n/a | n/a | n/a | 4.4% | 3 |
