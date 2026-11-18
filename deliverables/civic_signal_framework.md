<!-- Built by src/build_docs.py from src/templates/civic_signal_framework.template.md. Edit the template, then rebuild. -->
# Civic Signal Framework

Cayden Auyang. AI drafted and I reviewed.

How to compare a city's official statistics with public attention, step by step.

## Who this is for and what it gives you

This guide is for a journalist, a city staffer or a civic technologist who has official statistics for a city and wants to know how far local news coverage and search interest track them.

It gives you a method in eleven steps. At the end you have a monthly measure of how much attention each problem gets, a test of whether that attention moves with the official numbers, and a dated list of the periods when the two pulled apart.

It does not tell you which measure is right. Official statistics are a benchmark with blind spots of their own. Attention shows how much a problem is discussed, which is different from what people think should be done about it.

The method comes from one study of Hong Kong, New York City and London. Its main results:

- News: For news coverage, attention rose 0.07 standard deviations for each standard deviation the official measure worsened (95% interval 0.02 to 0.10, 19 city and category pairs, about 185 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for news coverage.
- Search: For search interest, attention rose 0.26 standard deviations for each standard deviation the official measure worsened (95% interval 0.19 to 0.42, 18 city and category pairs, about 336 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for search interest.

Every recommendation in this guide points to a number from that study. Where the study did not settle something, the guide says so.

Read the limits before you rely on it. In the study an AI agent ran the whole pipeline in one unattended session. An AI language model labeled the articles and a second AI language model checked a sample. No person hand-coded any article. Validation status when this file was built: **final**. If that reads "provisional", the agreement numbers below come from a stand-in third AI pass and will be replaced.

What you need: someone who can write SQL and Python, a cloud account that can query the GDELT news database in BigQuery, and an API key for a language model. In dollars, the study spent about $20.57 on news database queries and $27.25 on labeling. It cannot tell you how long the work takes a person, because nobody did it by hand. The proposal behind the study budgeted 60 to 70 hours for one student over a term.

## The eleven steps

### Step 1. Choose categories and write their boundaries

**Do.** List the problems you care about. For each one, write a line on what it covers and a line on what goes elsewhere, for example "rent goes under Housing, other prices go under Cost of Living." Add tie-break rules for stories that touch two categories, and a label for "not a civic problem." Mark which categories have an official statistic and which do not.

**What it produced in this study.** Twelve categories, eight of them compared with official data. The codebook is in `spec/methodology.md`. The table under Step 6 shows which categories two AI coders could apply consistently.

**What it cost here.** No data cost. The proposal budgeted about 12 hours for the methodology and the source inventory together.

**What can go wrong.** A category with a soft edge fails validation later and has to be dropped. The categories dropped in this study:

- Hong Kong: Housing, Transport, Cost of Living, Culture, Technology and Community
- New York City: Culture and Community
- London: Cost of Living, Governance, Culture, Technology and Community

Look at that list before you copy the codebook, and tighten those boundaries first.

### Step 2. Pick official indicators, with a backup for each

**Do.** For every category choose one main indicator and one backup, both from a government or other official body, at the city level where one exists. Before you look at any values, write down which direction is worse and how the yearly change is computed: percent for counts, points for rates, and the change in the 12-month rate for prices. Use each series at its own frequency. Never fill a gap. Keep a table of every known break, such as a change in how something is counted.

**What it produced in this study.** 45 main and backup series (23 main, the rest backups) holding 11,948 values, built from 465 saved raw files. The dataset file also holds 2 extra series that no test uses. Having backups let the study rerun the main test on different indicators. With backups in place of the main indicators, the pooled news slope was 0.13 (0.07 to 0.21), against 0.07 in the main model. The search slope was 0.28 (0.17 to 0.37), against 0.26.

**What it cost here.** No fees. Every series was a public download. The proposal budgeted about 22 hours for assembling the official data and building the attention pipeline together.

**What can go wrong.**

- A source blocks automated collection. London's Health series and its backup were both lost that way, so that pair was never tested.
- A series is shorter than its documentation says. Several here start years later than planned. They are listed in `deliverables/deviations.md`, section 4.
- Two files are joined and the level jumps at the seam. Mark the join as a break.
- A definition changes. Fraud left London's recorded crime count partway through the period, and those months had to be marked.
- A category has only annual data. Education was annual in all three cities, which leaves about ten points per pair.

### Step 3. Build a fixed outlet panel and a city filter

**Do.** List every local, general-news outlet you can find. Count each one's records by month in the news database before you read any content. Keep in the main panel only the outlets recorded steadily in every year. This study required articles in at least three-quarters of the months of every year and at least 30 a month. Give every outlet equal weight. Then write a filter that keeps only articles about the city, and remove duplicates.

**What it produced in this study.** 68 outlets listed and 21 in the main panels: 3 in Hong Kong, 3 in New York City and 15 in London. 6,363,992 records were pulled for the listed outlets, and 2,466,900 were left after the city filters and duplicate removal. In the validation sample, the share of articles the second coder judged not really about the city was 15% in Hong Kong, 8% in New York City and 9% in London.

**What it cost here.** 3.29 terabytes billed across 43 queries, about $20.57. Nearly all of it was the yearly extracts of the news database (`logs/bigquery_costs.csv`).

**What can go wrong.**

- **Location tags fail for New York.** The database tags most New York stories with the state. This study counted an article only if it carried a city-level tag for New York City, a borough or a borough's county. It still under-counts the Bronx, which is rarely tagged.
- **Wire copy in London.** Borough papers carry national wire stories under national-news addresses. Those addresses were dropped, and a story that ran in several sister papers in one month was counted once.
- **Number-only addresses.** The AI reads headline words from the web address. An outlet whose addresses are only numbers leaves it with topic tags alone. In the headline check for Hong Kong, labels made with headline words reached kappa 0.80. For the outlets without them: Theme-tag-only labels agreed with real-headline labels at kappa 0.42, below 0.61. HK China News Agency and Oriental Daily, whose addresses were number-only before 2020, are left out of 2015 to 2019. Hong Kong's news series for those years rests on the South China Morning Post alone.
- **One outlet dominates.** Without equal weights, the outlet with the most articles sets the city's shares.
- **The panel is narrow.** Outlets that survive a steady-in-every-year rule are not a cross-section of the press. Hong Kong's panel is mainstream and pro-establishment. London's is borough papers with no citywide outlet.
- **A query without the partition filter.** Filter the news table on its partition date and do a dry run first. In the methodology's feasibility check, the same one-week query scanned 0.77 GB with the filter and 781 GB without it.

### Step 4. Pre-register

**Do.** Before you pull any outcome data, post the plan where a third party timestamps it. Include the hypotheses, the codebook, the outlet lists, the search terms, each indicator's direction and transformation, the tests and the thresholds. Counting articles per outlet is fine before this point. Reading what the articles say is not. Start a deviations file on the first day.

**What it produced in this study.** A public commit (`e8d5f32`, tag `prereg-v1`, 2026-11-17T20:31:07Z) with copies of the plan saved by the Internet Archive, and `deliverables/deviations.md`, which lists every departure from the plan.

**What it cost here.** Nothing.

**What can go wrong.** On the night of the run the archive service returned an error for the repository page, so the plan files themselves were archived and checked by hash. The outcome of the retries is in `deliverables/preregistration.md`. The pre-registration also came in November, where the plan said October. It still came before the first query that returned outcome data.

### Step 5. Sample and label with an AI language model

**Do.** Draw a seeded random sample each month, with the same cap for every outlet. Label in rounds, each round adding the same number of articles per outlet and month, so the sample stays even if the run stops early. Put the codebook into the prompt word for word and freeze the prompt before labeling. Use one model for every article. Label a small batch first to measure the real cost per item. Save the model's exact identifier and the prompt in a labeling card.

**What it produced in this study.** 435,201 items were sampled, and 429,082 were labeled when this file was built. 6,117 had no headline words and no topic tags, so the model had nothing to read and they were left out. 286,155 of the labeled articles are from the main panels, and the main attention index is built from those, less the Hong Kong outlet-years that the headline check leaves out (Step 3). The rest are from the other listed outlets and feed one check. Labeling round reached: round 6 of 6, the full planned sample.

**What it cost here.** About $0.06 per 1,000 items, or $6.27 per 100,000, measured on the first batch. Fees for the first coder came to $27.25 in all, against a cap of $100.00. Each request held 50 items from one city (`data/public/labeling_card.md`). The largest request was 23,856 input tokens in the cost test and 26,830 in the full run.

**What can go wrong.**

- **The free-tier trap.** The first key turned out to be on its provider's free tier, with a daily request cap. Labeling stopped partway through the first city. Everything was then relabeled with a model from a different provider, so that one model labeled every article. Check the key's daily limits before you start, and run the cost test on the key you will really use.
- **Request size.** Keep each request far below the model's input limit, and keep one city per request.
- **Thin inputs.** The model sees web-address words and topic tags. It never sees the article. That is why Step 6 exists.
- **Tone needs its own check.** In a comparison with a larger model on 300 items, kappa was 0.81 for category and 0.63 for tone. Compare the two before you build anything on tone.

### Step 6. Validate with a second independent coder and a threshold

**Do.** Draw a validation set for each city. The plan here was about 300 items, at least 20 per category, spread across years and outlets. Have a second coder label it without seeing the first labels, reading more than the first coder did: the real headline and the opening lines. Weight the results back to the full sample and compute Cohen's kappa per category. Fix the threshold in advance. Record whether each article is really about the city. The second coder should be a person if you can manage it.

**What it produced in this study.** Items scored: 228 in Hong Kong, 300 in New York City and 299 in London. In Hong Kong 71 more items were coded and left out of the score, because their outlet-years are not in the main series. Overall kappa was 0.65, 0.76 and 0.71 in the same order. 23 of 36 category checks (twelve categories in each city) reached the threshold of 0.61.

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

The first coder was also compared with a larger model on the same inputs: kappa 0.81 on 300 items.

<!-- FINAL PASS: the two tokens on the next line resolve only after the second-coder step writes its consistency results. If they still read "[not available]" at the end of the run, delete the line. -->
Two more consistency checks: a third AI pass against the second coder gave kappa 0.76, and the second coder against itself on a fresh request gave kappa 0.80.

**What it cost here.** 4,751 article pages were tried and 3,210 were fetched (68%). The second coder ran on its provider's free tier, logged as $0.00, so this study cannot tell you what a paid second coder costs.

**What can go wrong.**

- **Pages you cannot fetch.** Old links die and some sites block automated requests. This study replaced an item it could not fetch with the next one from the same category in a fixed random order. That tilts the set toward outlets and years that are still online. Where no page could be read and the article was from 2020 on, the second coder read the stored headline alone (130 items in Hong Kong, 1 in New York City, 16 in London). One outlet's site challenged automated requests, so the run stopped using it. No Hong Kong article from before 2020 ended up in the scored set.
- **Scoring rules set late.** In this study three scoring rules (which items count, what to read when no page loads, and how to weight) were set after provisional scores had been seen and before the official second coder ran. Write those rules down before any score exists.
- **Two AI coders can share a blind spot.** Their agreement shows the labels are consistent. Only a person coding a sample can show the labels match a human reader.
- **Few items per category.** With about 20 items, one category's kappa has a wide interval. The intervals are in `data/public/validation_report.md`.
- **When a category fails.** Revise its wording once, label a fresh sample and test again. If it still falls short, drop it for that city and report it. Do not lower the threshold after seeing the result. Of the eight compared categories, this study dropped: Hong Kong: Housing, Transport and Cost of Living. New York City: none. London: Cost of Living.

### Step 7. Add search data with an anchor term and fixed term sets

**Do.** Write one fixed set of search terms per category, in the languages residents search in, before you look at any search data. Leave out names of people, places and programs. Put one anchor set in every request and divide every other set by it, which puts separate requests on one scale. Then turn the sets into shares. Download each request on three different days and average them. Decide in advance when a set is too sparse to test. Here the rule was zero in more than 10% of months.

**What it produced in this study.** 36 term sets in 9 requests, covering 274 months from 2004-01 to 2026-10. Downloads per request when this file was built: 2. 18 city and category pairs could be tested for search.

**What it cost here.** No fees. 18 files were downloaded through a browser.

**What can go wrong.**

- **Tiny sets.** Search values are whole numbers scaled to the busiest month in the request. A set that reads "under 1" in most months carries no signal, and its share only follows the anchor.
- **The platform changes its own collection.** The charts mark the dates. Treat them as breaks.
- **Geography is wider than the city.** Here it was the New York media market and all of England.
- **Shares move together.** One topic's spike lowers every other share that month.
- **Too few downloads.** Search results are drawn from a sample of searches. One download cannot show how much that sampling moves the numbers.

### Step 8. Compare yearly changes, not levels, on a matched panel

**Do.** Compare each period with the same period a year earlier, for the official series and for attention. Divide each pair's changes by their own standard deviation, computed outside the marked breaks. Match the attention window to the indicator's frequency. For news, compute each outlet's own yearly change and average across the outlets present in both years.

**What it produced in this study.** 1,739 matched periods across 19 news pairs, which is about 185 independent pair-years. For search: 3,980 periods across 18 pairs, about 336 independent pair-years. The file is `data/public/yearly_changes.csv`.

**What it cost here.** Computer time only.

**What can go wrong.**

- **Levels fool you.** Two series that both drift for twenty years correlate even when they are unrelated.
- **A changing panel fakes a jump.** When outlets are left out of some years, as the headline-check rule did in Hong Kong, their return looks like a jump in every category unless changes are computed outlet by outlet.
- **Monthly points overlap.** Each monthly yearly-change shares eleven months with its neighbor. The count of periods overstates how much independent information there is, so report independent pair-years next to it.

### Step 9. Run the pooled test, then the checks that the results hold

**Do.** Fit one regression across all pairs, with a separate intercept for each pair and equal weight per pair. Get intervals from a block bootstrap with 12-month blocks. To test asymmetry, split the official change into worsening and improving. Report single pairs as description, with adjusted p-values. Test the code on made-up series before it touches real data. Then rerun the main test under each check you registered.

**What it produced in this study.**

| Source | H1 slope (95% interval) | p | Pairs | Periods | Independent pair-years | Slope when worsening | Slope when improving | Difference (95% interval) |
| :-- | :-- | --: | --: | --: | --: | :-- | :-- | :-- |
| News | 0.07 (0.02 to 0.10) | 0.009 | 19 | 1,739 | 185 | 0.06 (0.01 to 0.10) | 0.10 (-0.05 to 0.18) | -0.05 (-0.14 to 0.12) |
| Search | 0.26 (0.19 to 0.42) | < 0.001 | 18 | 3,980 | 336 | 0.37 (0.22 to 0.59) | 0.17 (0.08 to 0.39) | 0.20 (-0.10 to 0.47) |

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

For news, the H1 interval stayed above zero in 9 of the 14 checks that ran (the ones where it did not: Without 2020 to 2022; Without 2020 to 2022 and every other marked break month; Official series aligned by release date; Description: Hong Kong pairs only, periods before 2021 (several major outlets closed in 2021); Description: Hong Kong pairs only, periods from 2021 on). For search it stayed above zero in 5 of 5 (the ones where it did not: none). News checks with no result: none.

At the level of single pairs, 11 of 37 had a Benjamini-Hochberg adjusted p below 0.05, and 11 could not be tested.

**What it cost here.** Computer time only, with 2,000 bootstrap resamples.

**What can go wrong.**

- **Intervals that are too narrow.** On made-up series with no link between them, the interval wrongly excluded zero in 7 of 40 trials (18%). An honest 95% interval would do that about 5% of the time. If the first rate is the higher one, call any interval that only just clears zero borderline.
- **One period carries the result.** Rerun the test without the unusual years. Without 2020 to 2022, the news interval includes zero and the search interval is above zero.
- **Many small tests.** Some single pairs pass by luck. Adjust the p-values and count pairs after the adjustment.
- **A check that did not run.** Treat it as missing evidence, and say which one.

### Step 10. List the disconnections and classify their causes

**Do.** For each pair, compute the share of periods in which attention and the official measure moved in opposite directions. List every stretch of six months or more. Give each one a cause from a short fixed list: the official measure changed how it counts, a real event drew coverage the indicator does not capture, attention followed a news cycle, the two measure different parts of the problem, or unclear. Read coverage from the period before you choose.

**What it produced in this study.** 77 stretches, 23 in news and 54 in search.

| Proposed cause (by AI, for Cayden to confirm) | Disconnections of six months or more |
| :-- | --: |
| unclear | 36 |
| attention followed a news cycle rather than conditions | 25 |
| a real event drew coverage the indicator does not capture | 8 |
| the two measure different parts of the problem | 4 |
| the official measure changed how it counts | 4 |

The longest news case with a named cause was Hong Kong Economy, 2022-05 to 2023-06: the official measure was improving while attention was rising for 14 months. Proposed cause: the two measure different parts of the problem. Proposed by: AI, after reading a seeded sample of the period's coverage; for Cayden to confirm.

**What it cost here.** Computer time. Confirming the causes is a person's time, and in this study that time has not been spent yet. Every cause is marked as proposed by AI, for Cayden to confirm.

**What can go wrong.**

- **Reading too much into a share near half.** Two unrelated series move in opposite directions about half the time. A share near 50% means no visible relationship.
- **Forcing a cause.** "Unclear" is an allowed answer. Here it was given to 36 of 77 stretches.
- **Presenting a proposed cause as a finding.** Keep the "proposed" label until someone has read the coverage and the series notes.

### Step 11. Publish the data and the deviations

**Do.** Publish the monthly shares, the official series, the yearly changes, the results file, the code, the labeling card, the validation report and the deviations list. Publish no article text. Make every document take its numbers from the results file, so nothing is retyped.

**What it produced in this study.** A public repository, https://github.com/CaydenAuyang/measuring-what-matters, with the result files in `data/public/` and the list of departures from the plan in `deliverables/deviations.md`. This guide is filled from those files by `src/build_docs.py`.

**What it cost here.** Nothing.

**What can go wrong.** A number typed by hand drifts away from the results. An API key gets committed with the code. A deviation is left out because it is awkward. List it anyway.

## When to trust attention over official data, and the reverse

Each row starts from a question you might face, gives what this study found, and then says what to do. Where a result could have gone either way, the advice covers both outcomes, so read the verdict word first. Slopes are in standard deviations.

| Your question | What this study found | What to do |
| :-- | :-- | :-- |
| News coverage of a problem is rising. Did the problem get worse? | H1 for news: **supported**. For news coverage, attention rose 0.07 standard deviations for each standard deviation the official measure worsened (95% interval 0.02 to 0.10, 19 city and category pairs, about 185 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for news coverage. Without 2020 to 2022, the interval includes zero. | If "supported", treat rising coverage as a hint, no stronger than the link described, and go check the official number. If the interval without 2020 to 2022 includes zero, the study shows the link only when the pandemic years are in, so do not count on it in ordinary years. If "not supported" or "failed", do not read coverage changes as evidence about conditions. |
| Searches about a problem are rising. Did the problem get worse? | H1 for search: **supported**. For search interest, attention rose 0.26 standard deviations for each standard deviation the official measure worsened (95% interval 0.19 to 0.42, 18 city and category pairs, about 336 independent pair-years). That is a weak link, and the interval excludes zero, so H1 is supported for search interest. Without 2020 to 2022, the interval is above zero. | Apply the same rule as for news. Keep in mind that search covers an area wider than the city, and that the downloads per request here numbered 2, from one night, where the plan said three on different days. |
| Which categories does attention track? | News interval above zero: Environment and Economy. News interval includes zero: Health, Transport, Cost of Living, Safety, Housing and Education. Search interval above zero: Cost of Living, Economy, Environment, Safety and Transport. Search interval includes zero: Housing and Health. Not tested for search: Education. | Use attention as a signal only in a category whose interval is above zero for that source. For the others this study gives no support. Each category rests on at most three cities, so treat the list as a lead to test in your own city. |
| Attention to a problem has gone quiet. Did the problem get better? | H2 for news: **not supported**. H2 for search: **not supported**. In 29 of 77 listed disconnections, the official measure was worsening while attention's share fell. | Do not take quiet as improvement without checking the official number. If H2 is "supported", attention reacts less to improvement than to worsening, so quiet is even weaker evidence. If "not supported", this study cannot say attention treats good and bad news differently, so do not assume it does. |
| Is crime coverage the least reliable signal? | H3 for news: **not supported**. For news coverage, Safety showed the largest gap in 1 of 3 cities. Hong Kong: Safety ranked 1 of 5 (70% of periods moved in opposite directions; the largest was Safety at 70%). New York City: Safety ranked 4 of 8 (45% of periods moved in opposite directions; the largest was Education at 67%). London: Safety ranked 6 of 6 (35% of periods moved in opposite directions; the largest was Housing at 58%). H3 predicted the largest gap in at least two cities, so it is not supported. H3 for search: **not supported**. | If "supported", be most careful with Safety. If "not supported", do not single Safety out. Look up each category in the H3 tables below and check the same thing in your own city. |
| When is the news signal unusable, so the official number is all I have? | Categories that failed the agreement test: Hong Kong: Housing, Transport, Cost of Living, Culture, Technology and Community. New York City: Culture and Community. London: Cost of Living, Governance, Culture, Technology and Community. Tag-only labels in the headline check: kappa 0.42 against a bar of 0.61. | Do not build a news signal for a category that fails validation in your city, or from outlets whose addresses carry no headline words. Use the official indicator alone there, and say that attention could not check it. |
| When should I doubt the official number? | 4 of 77 listed disconnections were put down to a change in how the official series counts, and 4 to the indicator and the coverage measuring different parts of the problem. These causes were proposed by AI and are not yet confirmed. With every marked break month removed, the news interval includes zero and the search interval is above zero. | Before you trust an official change, read the series notes for a counting change in that window. If there is one, treat the change as unmeasured and look at the backup indicator. If the indicator covers one slice of the category, expect attention to move with the other slices too. |
| Can attention warn me before the official number moves? | Exploratory only, with no prediction made. 14 of 31 monthly pairs had a permutation p below 0.05 at their best lag. With official data lined up by release date, the news interval includes zero and the search interval is above zero. | Do not use attention as an early warning on this evidence. The lags differ by category (table below). Use them to pick categories worth a proper test. |
| Does the amount of coverage show which problem is worst right now? | Rank correlation between how far each official indicator sits from its 2015 to 2019 average and how much news coverage its category gets: 0.24 in Hong Kong, 0.04 in New York City and -0.36 in London. | A value near 1 would mean the most-covered problems are the ones furthest from normal. If these values are near zero or negative, do not rank problems by how much coverage they get. Each city has at most eight categories, so the values are rough. |

**H1 by category.** Each row pools at most three cities.

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

**Share of periods moving in opposite directions, news.**

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

**Share of periods moving in opposite directions, search.**

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

**Lead and lag by category (exploratory).** A negative lag means attention moved before the official measure. A positive lag means it moved after.

| Category | News: lag where the mean r is furthest from zero | Mean r at that lag | Search: lag where the mean r is furthest from zero | Mean r at that lag |
| :-- | --: | --: | --: | --: |
| Safety | 0 months | 0.39 | -1 month | 0.43 |
| Economy | -1 month | 0.42 | -1 month | 0.51 |
| Housing | +12 months | -0.28 | -10 months | 0.25 |
| Transport | +10 months | 0.25 | +3 months | 0.25 |
| Environment | 0 months | 0.14 | 0 months | 0.23 |
| Health | 0 months | 0.61 | -2 months | 0.47 |
| Education | not tested |  | not tested |  |
| Cost of Living | +3 months | 0.21 | -1 month | 0.58 |

## One-page checklist

Before any data

- [ ] Categories written with a "covers" line and a "goes elsewhere" line, plus tie-break rules.
- [ ] One main and one backup official indicator per category, with direction and yearly-change rule written down.
- [ ] Known breaks listed for every series.
- [ ] Outlet list built from counts only. Main panel rule and city filter written.
- [ ] Search term sets fixed. Anchor set chosen. Sparse rule fixed.
- [ ] Hypotheses, tests, kappa threshold and checks written down.
- [ ] Plan posted with a third-party timestamp. Deviations file started.

Collecting

- [ ] Every news query filters on the partition date and gets a dry run.
- [ ] Seeded sample, equal per outlet per month.
- [ ] API key limits checked. Cost measured on a small batch.
- [ ] Prompt frozen. One model for every item. Labeling card saved.
- [ ] Search downloaded on three different days.
- [ ] Raw files saved with hashes.

Validating

- [ ] Validation set drawn for each city, with enough items in every category.
- [ ] Second coder blind to the first labels and reading the real headline and opening lines. A person if possible.
- [ ] Kappa per category. A failing category revised once, then dropped.
- [ ] "About the city?" recorded for every validation item.
- [ ] Outlets with number-only addresses tested separately.

Analyzing

- [ ] Yearly changes, standardized per pair, with a matched panel for news.
- [ ] Code tested on made-up series.
- [ ] Pooled test with pair intercepts, equal weights and a block bootstrap.
- [ ] Every registered check run. Any check that did not run is reported.
- [ ] Disconnections of six months or more listed, each given a cause after reading coverage.

Publishing

- [ ] Data, code, labeling card, validation report and deviations published. No article text.
- [ ] Every number in every document filled from the results file.
- [ ] Limits stated: who coded, what was dropped, what was not checked.

## Minimum viable version: one city, three categories

This is the smallest version that still tests something.

- **Categories.** Pick three with a monthly official indicator. Start from the categories whose interval sat above zero in this study (news: Environment and Economy; search: Cost of Living, Economy, Environment, Safety and Transport), as long as they also passed in the kappa table under Step 6. Avoid a category with only annual data.
- **Outlets.** At least three steady local outlets whose web addresses carry headline words.
- **Sample.** Up to 1,000 articles a month, split equally across outlets.
- **Validation.** About 300 items, and code them yourself. That gives you the human check this study lacks.
- **Search.** One request holds an anchor set plus up to four others, so three categories fit in one request. Download it on three different days.
- **Analysis.** You will have three pairs. Run the pooled test and the checks, and expect wide intervals: this study had 19 news pairs and its news interval still ran from 0.02 to 0.10. Report the result as description. Skip lead and lag, and skip the comparison of gaps across categories, which needs more than three.

Rough cost, from this study's own numbers:

| Item | How it is worked out | Rough cost |
| :-- | :-- | --: |
| Labeling | Up to 1,000 articles a month for 141 months is 141,000 items, at this study's measured cost per item | $8.84 |
| News database queries | The yearly extracts read the same columns of the whole table however many cities you keep, so one city costs about what three did (3.29 terabytes) | $20.57 |
| Second coder | Free tier in this study, or your own time if you hand-code | not measured |
| Official statistics and search data | Public downloads | no fee |
| **Total** | Labeling plus queries | **about $29.41** |

Fewer years cost less on both paid lines. Prices change, so measure your own cost per item on a small batch first (Step 5).

## Limits of the framework

- **Two AI coders are not a human check.** In this study an AI language model labeled every article and a second AI language model checked a sample. Their agreement shows the labels are consistent. It does not show that a person would agree. The study's plan called for hand-coding, and that step was replaced.
- **Official data are a benchmark, not truth.** Recorded crime counts only what is reported and recorded. Survey rates weaken when fewer people respond. When attention and an official number disagree, either one can be wrong.
- **Attention is volume.** It shows how much a problem is discussed. It does not show what people think should be done.
- **Moving together is not cause.** The tests show whether two series change together. The causes given for disconnections are proposals.
- **The news panels are narrow.** They hold the outlets a database happened to record steadily. In Hong Kong that means a mainstream, pro-establishment panel, and in London it means borough papers.
- **Search covers a wider area than the city.** Downloads per request here: 2, from one night, where the plan said three on different days.
- **The intervals may be too narrow.** See the made-up-series test under Step 9.
- **One run, three cities.** The whole study ran in one night, on three large cities with long-running local press. A smaller city, or one with few steady outlets, may behave differently. Treat each recommendation above as a starting hypothesis to test in your own city.
