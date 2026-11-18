<!-- TEMPLATE: Filled by src/build_docs.py into deliverables/civic_signal_framework.md. Edit this file, never the output.
Every result number is a token. The only numbers typed here are fixed parts of the plan or of the record:
rules and counts from spec/methodology.md (twelve and eight categories, 300 and 20 validation items, 1,000 articles
a month, three downloads, 12-month blocks, six months, the 10% sparse rule, three-quarters of months and 30 a month,
0.77 GB and 781 GB from the feasibility check, 0.05), hours from spec/fall_proposal.md, and the request size from
data/public/labeling_card.md. calc.* tokens are worked out in src/build_docs.py from the same results files.
No AI model, product or company is named in this file. The names are in data/public/labeling_card.md. -->
# Civic Signal Framework

Cayden Auyang. AI drafted and I reviewed.

How to compare a city's official statistics with public attention, step by step.

## Who this is for and what it gives you

This guide is for a journalist, a city staffer or a civic technologist who has official statistics for a city and wants to know how far local news coverage and search interest track them.

It gives you a method in eleven steps. At the end you have a monthly measure of how much attention each problem gets, a test of whether that attention moves with the official numbers, and a dated list of the periods when the two pulled apart.

It does not tell you which measure is right. Official statistics are a benchmark with blind spots of their own. Attention shows how much a problem is discussed, which is different from what people think should be done about it.

The method comes from one study of Hong Kong, New York City and London. Its main results:

- News: {{verdicts.h1_news_sentence}}
- Search: {{verdicts.h1_search_sentence}}

Every recommendation in this guide points to a number from that study. Where the study did not settle something, the guide says so.

Read the limits before you rely on it. In the study an AI agent ran the whole pipeline in one unattended session. An AI language model labeled the articles and a second AI language model checked a sample. No person hand-coded any article. Validation status when this file was built: **{{text.validation_status}}**. If that reads "provisional", the agreement numbers below come from a stand-in third AI pass and will be replaced.

What you need: someone who can write SQL and Python, a cloud account that can query the GDELT news database in BigQuery, and an API key for a language model. In dollars, the study spent about {{run.bigquery_cost_usd|money}} on news database queries and {{run.anthropic_cost_usd|money}} on labeling. It cannot tell you how long the work takes a person, because nobody did it by hand. The proposal behind the study budgeted 60 to 70 hours for one student over a term.

## The eleven steps

### Step 1. Choose categories and write their boundaries

**Do.** List the problems you care about. For each one, write a line on what it covers and a line on what goes elsewhere, for example "rent goes under Housing, other prices go under Cost of Living." Add tie-break rules for stories that touch two categories, and a label for "not a civic problem." Mark which categories have an official statistic and which do not.

**What it produced in this study.** Twelve categories, eight of them compared with official data. The codebook is in `spec/methodology.md`. The table under Step 6 shows which categories two AI coders could apply consistently.

**What it cost here.** No data cost. The proposal budgeted about 12 hours for the methodology and the source inventory together.

**What can go wrong.** A category with a soft edge fails validation later and has to be dropped. The categories dropped in this study:

- Hong Kong: {{text.dropped_hk}}
- New York City: {{text.dropped_nyc}}
- London: {{text.dropped_london}}

Look at that list before you copy the codebook, and tighten those boundaries first.

### Step 2. Pick official indicators, with a backup for each

**Do.** For every category choose one main indicator and one backup, both from a government or other official body, at the city level where one exists. Before you look at any values, write down which direction is worse and how the yearly change is computed: percent for counts, points for rates, and the change in the 12-month rate for prices. Use each series at its own frequency. Never fill a gap. Keep a table of every known break, such as a change in how something is counted.

**What it produced in this study.** {{counts.official_series_total}} main and backup series ({{counts.official_series_main}} main, the rest backups) holding {{counts.official_values|comma}} values, built from {{run.official_raw_files|comma}} saved raw files. The dataset file also holds {{counts.official_series_extra}} extra series that no test uses. Having backups let the study rerun the main test on different indicators. With backups in place of the main indicators, the pooled news slope was {{checks.backup_indicators.news.h1.est}} ({{checks.backup_indicators.news.h1.ci_low}} to {{checks.backup_indicators.news.h1.ci_high}}), against {{main.news.h1.est}} in the main model. The search slope was {{checks.backup_indicators.search.h1.est}} ({{checks.backup_indicators.search.h1.ci_low}} to {{checks.backup_indicators.search.h1.ci_high}}), against {{main.search.h1.est}}.

**What it cost here.** No fees. Every series was a public download. The proposal budgeted about 22 hours for assembling the official data and building the attention pipeline together.

**What can go wrong.**

- A source blocks automated collection. London's Health series and its backup were both lost that way, so that pair was never tested.
- A series is shorter than its documentation says. Several here start years later than planned. They are listed in `deliverables/deviations.md`, section 4.
- Two files are joined and the level jumps at the seam. Mark the join as a break.
- A definition changes. Fraud left London's recorded crime count partway through the period, and those months had to be marked.
- A category has only annual data. Education was annual in all three cities, which leaves about ten points per pair.

### Step 3. Build a fixed outlet panel and a city filter

**Do.** List every local, general-news outlet you can find. Count each one's records by month in the news database before you read any content. Keep in the main panel only the outlets recorded steadily in every year. This study required articles in at least three-quarters of the months of every year and at least 30 a month. Give every outlet equal weight. Then write a filter that keeps only articles about the city, and remove duplicates.

**What it produced in this study.** {{counts.outlets_listed_total}} outlets listed and {{counts.outlets_main_panel_total}} in the main panels: {{counts.outlets_main_panel.hk}} in Hong Kong, {{counts.outlets_main_panel.nyc}} in New York City and {{counts.outlets_main_panel.london}} in London. {{counts.gdelt_rows_listed_outlets|comma}} records were pulled for the listed outlets, and {{counts.articles_after_city_filter|comma}} were left after the city filters and duplicate removal. In the validation sample, the share of articles the second coder judged not really about the city was {{v.cities.hk.not_about_city_share|pct}} in Hong Kong, {{v.cities.nyc.not_about_city_share|pct}} in New York City and {{v.cities.london.not_about_city_share|pct}} in London.

**What it cost here.** {{run.bigquery_tb_billed}} terabytes billed across {{run.bigquery_queries}} queries, about {{run.bigquery_cost_usd|money}}. Nearly all of it was the yearly extracts of the news database (`logs/bigquery_costs.csv`).

**What can go wrong.**

- **Location tags fail for New York.** The database tags most New York stories with the state. This study counted an article only if it carried a city-level tag for New York City, a borough or a borough's county. It still under-counts the Bronx, which is rarely tagged.
- **Wire copy in London.** Borough papers carry national wire stories under national-news addresses. Those addresses were dropped, and a story that ran in several sister papers in one month was counted once.
- **Number-only addresses.** The AI reads headline words from the web address. An outlet whose addresses are only numbers leaves it with topic tags alone. In the headline check for Hong Kong, labels made with headline words reached kappa {{v.headline_check.hk.with_headline_words.kappa}}. For the outlets without them: {{v.headline_check.rule.text}}
- **One outlet dominates.** Without equal weights, the outlet with the most articles sets the city's shares.
- **The panel is narrow.** Outlets that survive a steady-in-every-year rule are not a cross-section of the press. Hong Kong's panel is mainstream and pro-establishment. London's is borough papers with no citywide outlet.
- **A query without the partition filter.** Filter the news table on its partition date and do a dry run first. In the methodology's feasibility check, the same one-week query scanned 0.77 GB with the filter and 781 GB without it.

### Step 4. Pre-register

**Do.** Before you pull any outcome data, post the plan where a third party timestamps it. Include the hypotheses, the codebook, the outlet lists, the search terms, each indicator's direction and transformation, the tests and the thresholds. Counting articles per outlet is fine before this point. Reading what the articles say is not. Start a deviations file on the first day.

**What it produced in this study.** A public commit (`{{run.prereg_commit}}`, tag `{{run.prereg_tag}}`, {{run.prereg_utc}}) with copies of the plan saved by the Internet Archive, and `deliverables/deviations.md`, which lists every departure from the plan.

**What it cost here.** Nothing.

**What can go wrong.** On the night of the run the archive service returned an error for the repository page, so the plan files themselves were archived and checked by hash. The outcome of the retries is in `deliverables/preregistration.md`. The pre-registration also came in November, where the plan said October. It still came before the first query that returned outcome data.

### Step 5. Sample and label with an AI language model

**Do.** Draw a seeded random sample each month, with the same cap for every outlet. Label in rounds, each round adding the same number of articles per outlet and month, so the sample stays even if the run stops early. Put the codebook into the prompt word for word and freeze the prompt before labeling. Use one model for every article. Label a small batch first to measure the real cost per item. Save the model's exact identifier and the prompt in a labeling card.

**What it produced in this study.** {{run.items_sampled_total|comma}} items were sampled, and {{run.items_labeled_total|comma}} were labeled when this file was built. {{run.items_no_input|comma}} had no headline words and no topic tags, so the model had nothing to read and they were left out. {{counts.articles_labeled_main_panel_total|comma}} of the labeled articles are from the main panels, and the main attention index is built from those, less the Hong Kong outlet-years that the headline check leaves out (Step 3). The rest are from the other listed outlets and feed one check. Labeling round reached: {{text.labeling_round_label}}.

**What it cost here.** About {{calc.cost_per_1000_items_usd|money}} per 1,000 items, or {{calc.cost_per_100k_items_usd|money}} per 100,000, measured on the first batch. Fees for the first coder came to {{run.anthropic_cost_usd|money}} in all, against a cap of {{run.language_model_cap_usd|money}}. Each request held 50 items from one city (`data/public/labeling_card.md`). The largest request was {{run.largest_request_tokens|comma}} input tokens in the cost test and {{run.full_run_largest_request_tokens|comma}} in the full run.

**What can go wrong.**

- **The free-tier trap.** The first key turned out to be on its provider's free tier, with a daily request cap. Labeling stopped partway through the first city. Everything was then relabeled with a model from a different provider, so that one model labeled every article. Check the key's daily limits before you start, and run the cost test on the key you will really use.
- **Request size.** Keep each request far below the model's input limit, and keep one city per request.
- **Thin inputs.** The model sees web-address words and topic tags. It never sees the article. That is why Step 6 exists.
- **Tone needs its own check.** In a comparison with a larger model on {{cmp.n}} items, kappa was {{cmp.kappa_category}} for category and {{cmp.kappa_tone}} for tone. Compare the two before you build anything on tone.

### Step 6. Validate with a second independent coder and a threshold

**Do.** Draw a validation set for each city. The plan here was about 300 items, at least 20 per category, spread across years and outlets. Have a second coder label it without seeing the first labels, reading more than the first coder did: the real headline and the opening lines. Weight the results back to the full sample and compute Cohen's kappa per category. Fix the threshold in advance. Record whether each article is really about the city. The second coder should be a person if you can manage it.

**What it produced in this study.** Items scored: {{v.cities.hk.n_items}} in Hong Kong, {{v.cities.nyc.n_items}} in New York City and {{v.cities.london.n_items}} in London. In Hong Kong {{v.cities.hk.n_items_left_out_by_headline_rule}} more items were coded and left out of the score, because their outlet-years are not in the main series. Overall kappa was {{v.cities.hk.overall_kappa}}, {{v.cities.nyc.overall_kappa}} and {{v.cities.london.overall_kappa}} in the same order. {{calc.validation.checks_passed}} of {{calc.validation.checks_total}} category checks (twelve categories in each city) reached the threshold of {{v.threshold}}.

{{tables.validation_kappa}}

The first coder was also compared with a larger model on the same inputs: kappa {{v.consistency.first_coder_vs_larger_model.kappa}} on {{v.consistency.first_coder_vs_larger_model.n}} items.

<!-- FINAL PASS: the two tokens on the next line resolve only after the second-coder step writes its consistency results. If they still read "[not available]" at the end of the run, delete the line. -->
Two more consistency checks: a third AI pass against the second coder gave kappa {{v.consistency.third_pass.kappa_vs_second}}, and the second coder against itself on a fresh request gave kappa {{v.consistency.relabel.kappa}}.

**What it cost here.** {{run.pages_tried_total|comma}} article pages were tried and {{run.pages_fetched_total|comma}} were fetched ({{calc.pages_fetch_rate|pct}}). The second coder ran on its provider's free tier, logged as {{run.gemini_cost_usd|money}}, so this study cannot tell you what a paid second coder costs.

**What can go wrong.**

- **Pages you cannot fetch.** Old links die and some sites block automated requests. This study replaced an item it could not fetch with the next one from the same category in a fixed random order. That tilts the set toward outlets and years that are still online. Where no page could be read and the article was from 2020 on, the second coder read the stored headline alone ({{v.cities.hk.headline_only_items}} items in Hong Kong, {{v.cities.nyc.headline_only_items}} in New York City, {{v.cities.london.headline_only_items}} in London). One outlet's site challenged automated requests, so the run stopped using it. No Hong Kong article from before 2020 ended up in the scored set.
- **Scoring rules set late.** In this study three scoring rules (which items count, what to read when no page loads, and how to weight) were set after provisional scores had been seen and before the official second coder ran. Write those rules down before any score exists.
- **Two AI coders can share a blind spot.** Their agreement shows the labels are consistent. Only a person coding a sample can show the labels match a human reader.
- **Few items per category.** With about 20 items, one category's kappa has a wide interval. The intervals are in `data/public/validation_report.md`.
- **When a category fails.** Revise its wording once, label a fresh sample and test again. If it still falls short, drop it for that city and report it. Do not lower the threshold after seeing the result. Of the eight compared categories, this study dropped: Hong Kong: {{text.dropped_compared_hk}}. New York City: {{text.dropped_compared_nyc}}. London: {{text.dropped_compared_london}}.

### Step 7. Add search data with an anchor term and fixed term sets

**Do.** Write one fixed set of search terms per category, in the languages residents search in, before you look at any search data. Leave out names of people, places and programs. Put one anchor set in every request and divide every other set by it, which puts separate requests on one scale. Then turn the sets into shares. Download each request on three different days and average them. Decide in advance when a set is too sparse to test. Here the rule was zero in more than 10% of months.

**What it produced in this study.** {{counts.search_term_sets}} term sets in {{counts.search_requests}} requests, covering {{counts.search_months}} months from {{counts.search_first_month}} to {{counts.search_last_month}}. Downloads per request when this file was built: {{counts.search_downloads_per_request}}. {{main.search.h1.n_pairs}} city and category pairs could be tested for search.

**What it cost here.** No fees. {{run.trends_files}} files were downloaded through a browser.

**What can go wrong.**

- **Tiny sets.** Search values are whole numbers scaled to the busiest month in the request. A set that reads "under 1" in most months carries no signal, and its share only follows the anchor.
- **The platform changes its own collection.** The charts mark the dates. Treat them as breaks.
- **Geography is wider than the city.** Here it was the New York media market and all of England.
- **Shares move together.** One topic's spike lowers every other share that month.
- **Too few downloads.** Search results are drawn from a sample of searches. One download cannot show how much that sampling moves the numbers.

### Step 8. Compare yearly changes, not levels, on a matched panel

**Do.** Compare each period with the same period a year earlier, for the official series and for attention. Divide each pair's changes by their own standard deviation, computed outside the marked breaks. Match the attention window to the indicator's frequency. For news, compute each outlet's own yearly change and average across the outlets present in both years.

**What it produced in this study.** {{main.news.h1.n_obs|comma}} matched periods across {{main.news.h1.n_pairs}} news pairs, which is about {{main.news.h1.n_eff_years|0f}} independent pair-years. For search: {{main.search.h1.n_obs|comma}} periods across {{main.search.h1.n_pairs}} pairs, about {{main.search.h1.n_eff_years|0f}} independent pair-years. The file is `data/public/yearly_changes.csv`.

**What it cost here.** Computer time only.

**What can go wrong.**

- **Levels fool you.** Two series that both drift for twenty years correlate even when they are unrelated.
- **A changing panel fakes a jump.** When outlets are left out of some years, as the headline-check rule did in Hong Kong, their return looks like a jump in every category unless changes are computed outlet by outlet.
- **Monthly points overlap.** Each monthly yearly-change shares eleven months with its neighbor. The count of periods overstates how much independent information there is, so report independent pair-years next to it.

### Step 9. Run the pooled test, then the checks that the results hold

**Do.** Fit one regression across all pairs, with a separate intercept for each pair and equal weight per pair. Get intervals from a block bootstrap with 12-month blocks. To test asymmetry, split the official change into worsening and improving. Report single pairs as description, with adjusted p-values. Test the code on made-up series before it touches real data. Then rerun the main test under each check you registered.

**What it produced in this study.**

{{tables.main}}

{{tables.checks}}

For news, the H1 interval stayed above zero in {{calc.news.checks_h1_above_zero}} of the {{calc.news.checks_run}} checks that ran (the ones where it did not: {{calc.news.checks_h1_not_above_zero_labels}}). For search it stayed above zero in {{calc.search.checks_h1_above_zero}} of {{calc.search.checks_run}} (the ones where it did not: {{calc.search.checks_h1_not_above_zero_labels}}). News checks with no result: {{calc.news.checks_not_run_labels}}.

At the level of single pairs, {{text.pairs_adjusted_p_below_05}} of {{text.pairs_tested}} had a Benjamini-Hochberg adjusted p below 0.05, and {{text.pairs_not_tested}} could not be tested.

**What it cost here.** Computer time only, with {{bootstrap_reps|comma}} bootstrap resamples.

**What can go wrong.**

- **Intervals that are too narrow.** On made-up series with no link between them, the interval wrongly excluded zero in {{synthetic_tests.false_positive_check.intervals_that_wrongly_excluded_zero}} of {{synthetic_tests.false_positive_check.trials}} trials ({{synthetic_tests.false_positive_check.rate|pct}}). An honest 95% interval would do that about {{synthetic_tests.false_positive_check.nominal_rate|pct}} of the time. If the first rate is the higher one, call any interval that only just clears zero borderline.
- **One period carries the result.** Rerun the test without the unusual years. Without 2020 to 2022, the news interval {{calc.checks.without_covid.news.h1_interval}} and the search interval {{calc.checks.without_covid.search.h1_interval}}.
- **Many small tests.** Some single pairs pass by luck. Adjust the p-values and count pairs after the adjustment.
- **A check that did not run.** Treat it as missing evidence, and say which one.

### Step 10. List the disconnections and classify their causes

**Do.** For each pair, compute the share of periods in which attention and the official measure moved in opposite directions. List every stretch of six months or more. Give each one a cause from a short fixed list: the official measure changed how it counts, a real event drew coverage the indicator does not capture, attention followed a news cycle, the two measure different parts of the problem, or unclear. Read coverage from the period before you choose.

**What it produced in this study.** {{text.runs_total}} stretches, {{text.runs_news}} in news and {{text.runs_search}} in search.

{{tables.runs_by_cause}}

The longest news case with a named cause was {{text.case_city}} {{text.case_category}}, {{case_study.start}} to {{case_study.end}}: the official measure was {{case_study.official_direction}} while attention was {{case_study.attention_direction}} for {{case_study.months}} months. Proposed cause: {{case_study.proposed_cause}}. Proposed by: {{case_study.proposed_by}}.

**What it cost here.** Computer time. Confirming the causes is a person's time, and in this study that time has not been spent yet. Every cause is marked as proposed by AI, for Cayden to confirm.

**What can go wrong.**

- **Reading too much into a share near half.** Two unrelated series move in opposite directions about half the time. A share near 50% means no visible relationship.
- **Forcing a cause.** "Unclear" is an allowed answer. Here it was given to {{calc.runs.unclear}} of {{text.runs_total}} stretches.
- **Presenting a proposed cause as a finding.** Keep the "proposed" label until someone has read the coverage and the series notes.

### Step 11. Publish the data and the deviations

**Do.** Publish the monthly shares, the official series, the yearly changes, the results file, the code, the labeling card, the validation report and the deviations list. Publish no article text. Make every document take its numbers from the results file, so nothing is retyped.

**What it produced in this study.** A public repository, {{run.repository}}, with the result files in `data/public/` and the list of departures from the plan in `deliverables/deviations.md`. This guide is filled from those files by `src/build_docs.py`.

**What it cost here.** Nothing.

**What can go wrong.** A number typed by hand drifts away from the results. An API key gets committed with the code. A deviation is left out because it is awkward. List it anyway.

## When to trust attention over official data, and the reverse

Each row starts from a question you might face, gives what this study found, and then says what to do. Where a result could have gone either way, the advice covers both outcomes, so read the verdict word first. Slopes are in standard deviations.

| Your question | What this study found | What to do |
| :-- | :-- | :-- |
| News coverage of a problem is rising. Did the problem get worse? | H1 for news: **{{verdicts.h1_news}}**. {{verdicts.h1_news_sentence}} Without 2020 to 2022, the interval {{calc.checks.without_covid.news.h1_interval}}. | If "supported", treat rising coverage as a hint, no stronger than the link described, and go check the official number. If the interval without 2020 to 2022 includes zero, the study shows the link only when the pandemic years are in, so do not count on it in ordinary years. If "not supported" or "failed", do not read coverage changes as evidence about conditions. |
| Searches about a problem are rising. Did the problem get worse? | H1 for search: **{{verdicts.h1_search}}**. {{verdicts.h1_search_sentence}} Without 2020 to 2022, the interval {{calc.checks.without_covid.search.h1_interval}}. | Apply the same rule as for news. Keep in mind that search covers an area wider than the city, and that the downloads per request here numbered {{counts.search_downloads_per_request}}, from one night, where the plan said three on different days. |
| Which categories does attention track? | News interval above zero: {{calc.news.h1_categories_above_zero}}. News interval includes zero: {{calc.news.h1_categories_including_zero}}. Search interval above zero: {{calc.search.h1_categories_above_zero}}. Search interval includes zero: {{calc.search.h1_categories_including_zero}}. Not tested for search: {{calc.search.h1_categories_not_tested}}. | Use attention as a signal only in a category whose interval is above zero for that source. For the others this study gives no support. Each category rests on at most three cities, so treat the list as a lead to test in your own city. |
| Attention to a problem has gone quiet. Did the problem get better? | H2 for news: **{{verdicts.h2_news}}**. H2 for search: **{{verdicts.h2_search}}**. In {{calc.runs.worsening_falling}} of {{text.runs_total}} listed disconnections, the official measure was worsening while attention's share fell. | Do not take quiet as improvement without checking the official number. If H2 is "supported", attention reacts less to improvement than to worsening, so quiet is even weaker evidence. If "not supported", this study cannot say attention treats good and bad news differently, so do not assume it does. |
| Is crime coverage the least reliable signal? | H3 for news: **{{verdicts.h3_news}}**. {{verdicts.h3_news_sentence}} H3 for search: **{{verdicts.h3_search}}**. | If "supported", be most careful with Safety. If "not supported", do not single Safety out. Look up each category in the H3 tables below and check the same thing in your own city. |
| When is the news signal unusable, so the official number is all I have? | Categories that failed the agreement test: Hong Kong: {{text.dropped_hk}}. New York City: {{text.dropped_nyc}}. London: {{text.dropped_london}}. Tag-only labels in the headline check: kappa {{v.headline_check.hk.theme_tags_only.kappa}} against a bar of {{v.threshold}}. | Do not build a news signal for a category that fails validation in your city, or from outlets whose addresses carry no headline words. Use the official indicator alone there, and say that attention could not check it. |
| When should I doubt the official number? | {{calc.runs.counting_change}} of {{text.runs_total}} listed disconnections were put down to a change in how the official series counts, and {{calc.runs.different_parts}} to the indicator and the coverage measuring different parts of the problem. These causes were proposed by AI and are not yet confirmed. With every marked break month removed, the news interval {{calc.checks.without_all_breaks.news.h1_interval}} and the search interval {{calc.checks.without_all_breaks.search.h1_interval}}. | Before you trust an official change, read the series notes for a counting change in that window. If there is one, treat the change as unmeasured and look at the backup indicator. If the indicator covers one slice of the category, expect attention to move with the other slices too. |
| Can attention warn me before the official number moves? | Exploratory only, with no prediction made. {{text.leadlag_pairs_p_below_05}} of {{text.leadlag_pairs}} monthly pairs had a permutation p below 0.05 at their best lag. With official data lined up by release date, the news interval {{calc.checks.release_date.news.h1_interval}} and the search interval {{calc.checks.release_date.search.h1_interval}}. | Do not use attention as an early warning on this evidence. The lags differ by category (table below). Use them to pick categories worth a proper test. |
| Does the amount of coverage show which problem is worst right now? | Rank correlation between how far each official indicator sits from its 2015 to 2019 average and how much news coverage its category gets: {{text.ranking_rho_hk}} in Hong Kong, {{text.ranking_rho_nyc}} in New York City and {{text.ranking_rho_london}} in London. | A value near 1 would mean the most-covered problems are the ones furthest from normal. If these values are near zero or negative, do not rank problems by how much coverage they get. Each city has at most eight categories, so the values are rough. |

**H1 by category.** Each row pools at most three cities.

{{tables.h1_by_category}}

**Share of periods moving in opposite directions, news.**

{{tables.h3_news}}

**Share of periods moving in opposite directions, search.**

{{tables.h3_search}}

**Lead and lag by category (exploratory).** A negative lag means attention moved before the official measure. A positive lag means it moved after.

{{tables.leadlag_by_category}}

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

- **Categories.** Pick three with a monthly official indicator. Start from the categories whose interval sat above zero in this study (news: {{calc.news.h1_categories_above_zero}}; search: {{calc.search.h1_categories_above_zero}}), as long as they also passed in the kappa table under Step 6. Avoid a category with only annual data.
- **Outlets.** At least three steady local outlets whose web addresses carry headline words.
- **Sample.** Up to 1,000 articles a month, split equally across outlets.
- **Validation.** About 300 items, and code them yourself. That gives you the human check this study lacks.
- **Search.** One request holds an anchor set plus up to four others, so three categories fit in one request. Download it on three different days.
- **Analysis.** You will have three pairs. Run the pooled test and the checks, and expect wide intervals: this study had {{main.news.h1.n_pairs}} news pairs and its news interval still ran from {{main.news.h1.ci_low}} to {{main.news.h1.ci_high}}. Report the result as description. Skip lead and lag, and skip the comparison of gaps across categories, which needs more than three.

Rough cost, from this study's own numbers:

| Item | How it is worked out | Rough cost |
| :-- | :-- | --: |
| Labeling | Up to 1,000 articles a month for {{counts.news_months}} months is {{calc.mvp_items|comma}} items, at this study's measured cost per item | {{calc.mvp_label_cost_usd|money}} |
| News database queries | The yearly extracts read the same columns of the whole table however many cities you keep, so one city costs about what three did ({{run.bigquery_tb_billed}} terabytes) | {{run.bigquery_cost_usd|money}} |
| Second coder | Free tier in this study, or your own time if you hand-code | not measured |
| Official statistics and search data | Public downloads | no fee |
| **Total** | Labeling plus queries | **about {{calc.mvp_total_cost_usd|money}}** |

Fewer years cost less on both paid lines. Prices change, so measure your own cost per item on a small batch first (Step 5).

## Limits of the framework

- **Two AI coders are not a human check.** In this study an AI language model labeled every article and a second AI language model checked a sample. Their agreement shows the labels are consistent. It does not show that a person would agree. The study's plan called for hand-coding, and that step was replaced.
- **Official data are a benchmark, not truth.** Recorded crime counts only what is reported and recorded. Survey rates weaken when fewer people respond. When attention and an official number disagree, either one can be wrong.
- **Attention is volume.** It shows how much a problem is discussed. It does not show what people think should be done.
- **Moving together is not cause.** The tests show whether two series change together. The causes given for disconnections are proposals.
- **The news panels are narrow.** They hold the outlets a database happened to record steadily. In Hong Kong that means a mainstream, pro-establishment panel, and in London it means borough papers.
- **Search covers a wider area than the city.** Downloads per request here: {{counts.search_downloads_per_request}}, from one night, where the plan said three on different days.
- **The intervals may be too narrow.** See the made-up-series test under Step 9.
- **One run, three cities.** The whole study ran in one night, on three large cities with long-running local press. A smaller city, or one with few steady outlets, may behave differently. Treat each recommendation above as a starting hypothesis to test in your own city.
