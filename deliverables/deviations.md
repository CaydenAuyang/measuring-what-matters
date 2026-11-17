# Deviations from the pre-registered plan

The plan is `spec/methodology.md`, posted on November 17, 2026 (commit `e8d5f32`, tag `prereg-v1`). This file lists every place where the study did something different, what was planned, what was done, and why. Nothing here is hidden in the paper or on the poster.

The whole study ran in one unattended session on November 17 and 18, 2026. An AI agent (Claude Code) carried out the plan. Times are Eastern.

## 1. Changes Cayden decided before the run

| # | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| 1.1 | Cayden hand-codes about 900 items. Agreement between the AI labels and his hand-coding decides which categories are analyzed. | A second AI language model from a different model family codes the same validation set without seeing the first model's labels. It reads the real headline and opening lines of each article. The rest of the check is as written: about 300 items per city, at least 20 per category per city, weighted back to the full sample, Cohen's kappa per category, the 0.61 threshold, one revision, then the category is dropped for that city. | The study was compressed into one run with nobody available to hand-code. This measures agreement between two independent AI coders. It does not show that either one matches a human reader. |
| 1.2 | A classmate labels 150 of the same items. Cayden re-labels 50 items two weeks later. | A third AI pass (a different model, recorded in the labeling card) codes the same items. The second coder re-labels 50 items in a fresh request. | Same reason. |
| 1.3 | Pre-registration on the Open Science Framework in October, after the mentors approve the plan. | Pre-registration on GitHub and the Internet Archive on November 17, 2026. It still came before any outcome data. The record is in `deliverables/preregistration.md`. | Later than planned. Whether and when the mentors approved the plan is for Cayden to state. [CAYDEN TO CONFIRM: date of mentor approval, if any] |
| 1.4 | Each Google Trends request is downloaded on three different days and averaged. | Downloads were taken closer together: one on the evening of November 17 and one after local midnight. Every search figure reports how many downloads it rests on. | One-night run. |
| 1.5 | Work spread over October 12 to November 20. | All stages ran in one session on November 17 and 18. | Compressed schedule. |

An optional file, `deliverables/optional_hand_check_50.csv`, lets Cayden hand-code 50 validation items later. `src/score_hand_check.py` computes his kappa against both AI coders. Nobody has filled it in.

## 2. Changes Cayden decided during the run (labeling)

These came from messages Cayden sent while the run was under way, after the problem in 3.1 appeared.

| # | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| 2.1 | The first coder is a small Gemini model through the Gemini API key. | The first coder is Claude Haiku 5.5 through the Anthropic API (exact ID `claude-haiku-5-5`, taken from the key's model list). Every item was labeled by this one model. Items that Gemini had already labeled were relabeled. | The Gemini key hit a daily cap (see 3.1). Cayden added an Anthropic API key and gave this instruction. |
| 2.2 | The second coder is a model from a different family than the first. The run's first design used Claude for that role. | The second coder is Gemini (`gemini-3.5-flash-lite`), run blind after its daily quota reset at about 3 AM. The third pass is a different Gemini model (`gemini-3.1-flash-lite`). | Cayden's instruction. The two coders are still from different model families. |
| 2.3 | Model and prompt are frozen before the full run. | The prompt was frozen once and never changed. The model changed before the full run, as in 2.1. Before the full run the first 2,000 items were labeled to measure cost: $0.1255, or $0.0000627 per item, which projects to about $27 for the full sample. That is under the $100 cap, so the sample was not shrunk. | Cayden's instruction: label 2,000 first, work out the real cost per item, and shrink only if the full run would pass $100. |
| 2.4 | Not in the plan. | Claude Haiku 5.5 was compared with Claude Sonnet 5.5 on 300 of the first 2,000 items, sent as the same six requests. Cohen's kappa on category was 0.805 (agreement 83.3%). The rule was to stay on Haiku 5.5 at kappa 0.75 or higher, and otherwise switch to Sonnet 5.5 on the largest complete sample level under $150. The run stayed on Haiku 5.5. | Cayden's instruction. Tone kappa in the same comparison was 0.63. |
| 2.5 | Not in the plan. | Every request stayed under 100,000 tokens (largest in the cost test: 23,856 input tokens, 50 items per request). All labeling used normal requests. No batch job was submitted, so nothing was billed twice. | Cayden's instructions. |

## 3. Things found during the run that forced a change

| # | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| 3.1 | Bulk labeling with the Gemini API key, with a $100 budget. | The key was on the provider's free tier: 15 requests a minute, about 250,000 input tokens a minute, and a daily request cap. `gemini-3.5-flash-lite` reached its daily cap after 10,582 Hong Kong items. `gemini-3.1-flash-lite` was started as a replacement and reached 4,422 items before Cayden's instruction in 2.1 arrived. Neither set of Gemini labels is used in any index. They are kept as cross-model comparisons. | Found in the throughput test. Paid Gemini access through Google Cloud was not turned on, because that would have changed Cayden's cloud settings. |
| 3.2 | The Internet Archive saves the repository page and the raw methodology file. | The raw methodology, source inventory, proposal and README were saved and checked against their SHA-256. The github.com repository page returned an error from the Archive on every try. A retry job kept trying. The result is in `deliverables/preregistration.md`. | Archive error 523 for github.com pages. |
| 3.3 | London Health: share of the waiting list waiting under 18 weeks (NHS England), with A&E four-hour performance as the backup. | Both are missing. London Health has no official series in this study, so that pair is not tested. | The NHS England statistics pages returned a browser challenge. The rules for this run say to stop when a site blocks collection. No open-portal copy was found. |
| 3.4 | New York Health: deaths of city residents by month from CDC WONDER, from 1999. | All-cause deaths for New York City from the CDC's open provisional file (`r8kw-7aab`), by place of occurrence, from January 2020. | CDC WONDER requires accepting a data-use agreement on a web form, which this run does not do. The open file starts in 2020. |
| 3.5 | The model reads the same inputs for every outlet. | True, but 1.4% of sampled items (6,117 of 435,201) had no headline words and no theme tags. They could not be labeled and are left out of the shares. | GDELT recorded no themes for them. |

## 4. Official indicators: differences from the tables in the methodology

Hong Kong

| Series | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| Health main | Specialist outpatient waiting time from 2013 (all specialties from 2015). | Starts 2018 Q3. | The data.gov.hk archive of the Hospital Authority file is the only machine-readable history. |
| Transport main | Fatal and serious road accidents from 2003. | Starts January 2013. | The 2003 to 2012 figures are only in PDF digests, which were not extracted. |
| Cost of Living main | Composite CPI without the housing section, from 1981. | Starts October 2004. Built from table 510-60001A, which has the section indices, with housing weights of 29.17, 31.66, 34.29 and 40.25 for the four base periods. | Table 510-60001 has no section indices. The 1999/2000 weights were not found. |
| Economy main | Break for the change in seasonal adjustment marked at 2008. | Marked at January to December 2007. | C&SD revised the series back to the period November 2006 to January 2007, so those are the comparisons that mix methods. |
| Environment main | Hourly NO2 and PM10 averaged by month. | EPD's published station monthly averages, 11 general stations. Ends May 2026. | The EPD export provides monthly averages. |
| Safety main | Annual from 2001, monthly for 2022 to 2024. | Annual 2001 to 2025. The 2022 to 2024 monthly file was not found. 2014 and 2015 come from an Internet Archive copy of the police workbook. | Source pages moved. |
| Education main | Share of day-school candidates meeting the entrance requirement, from 2012. | 2012 to 2025, core subjects only (HKEAA Table 3d). 2012 was read from a scanned PDF and checked against the counts. 2026 was not at the usual address. | Source format. |
| Backups | Public rental waiting time (quarterly), MTR delays of 8 minutes or more (annual from 2008), very hot days, teacher wastage. | Waiting time 2014 Q1 to 2026 Q2 with three quarters missing. MTR delays 2008 to 2024 with 2017 to 2019 missing. Very hot days annual. Teacher wastage 2018 to 2026 as the mean of primary and secondary. | Assembled from dated official pages and Legislative Council papers. |

New York City

| Series | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| Education main | Four-year graduation rate. | The June rate, classes of 2005 to 2025. | The Department of Education publishes no August rate for the classes of 2005 to 2007. |
| Transport main | Subway on-time performance from 2009. | Starts June 2009, weekday trains, two months of 2010 missing. Two files are joined at 2015. Where they overlap (36 months) they differ by 0.016 points on average. | Source coverage. |
| Housing main | DHS shelter census, with the Coalition for the Homeless series before 2013. | Three files joined. The Coalition total runs 4.1% above the DHS figure at the join, which is marked as a break. 19 Coalition months have no total and are left out. | Source coverage. |
| Environment | PM2.5 from 1999, air quality index from 1989. | Both from 1999, ending May 2026. Five thin months dropped. Before 2025 most days rest on two or three of the five boroughs. | EPA file coverage. |
| Economy backup | Nonfarm jobs from 1950. | From 1990. | The open series starts in 1990. |
| Prices | Break for the 2018 area redraw. | Marked for 2018, and the analysis extends it through 2019 because the change in a 12-month rate looks back two years. | Follows from the transformation in Appendix C. |

London

| Series | Planned | Done | Why |
| :-- | :-- | :-- | :-- |
| Safety main | Recorded crime from 2008. | Starts April 2010. A break was added at February 2013, when fraud left the count. | No older-categories file exists. |
| Housing main | Older rent index joined to the current one at 2015. | Joined at January 2015. 24 months are marked as a break at the join. | The two indices differ by up to 4.0 points of 12-month growth where both exist. |
| Transport main | Severity-adjusted killed or seriously injured, from 1979. | 2004 to December 2025. | Adjusted figures do not exist before 2004. |
| Environment main | NO2 at Marylebone Road and Bloomsbury. | 30 months are empty, nearly all because Bloomsbury has no readings, including September 2023 to March 2025. Ends May 2026. | Missing readings in the network's API. A month with one site missing is left empty, not filled. |
| Education main | Attainment 8 from 2015/16. | 2015/16 to 2025/26. The first three years come from a London Datastore workbook of DfE figures. 2025/26 is provisional. | Source coverage. |
| Backups | Temporary accommodation, Underground lost customer hours, PM2.5 at the same sites, absence rate. | Temporary accommodation has five empty quarters. Lost customer hours run May 2011 to February 2020. PM2.5 uses Marylebone Road site MY7 and runs 2009 to 2021. The absence rate lacks 2019/20. | Source coverage. |
| Cost of Living backup | None exists. | None. | As the methodology says. |

Full notes for every series are in `data/interim/official/*_notes.md` and are carried into `deliverables/source_inventory_v2.md`.

## 5. Judgment calls made while applying the plan

Each of these is also one line in `logs/decisions.md`.

| Topic | Reading taken |
| :-- | :-- |
| Hong Kong city filter | An article counts if GDELT gives it any location tag whose country code is Hong Kong. |
| New York city filter | An article counts if GDELT gives it a city-level tag named New York City, a borough, or a borough's county. Neighborhood tags alone do not count. GDELT rarely tags the Bronx, so Bronx stories are under-counted. |
| London national news | Addresses under `/national/`, `/national-news/`, `/uk_national_news/`, `/uk_national_entertainment/` and `/uk-world-news/` are dropped. For the Evening Standard (check list only), `/news/uk/` and `/news/world/` are dropped. |
| Pages that are not articles | Tag, author, topic and section index pages are dropped. |
| Duplicates | Addresses are compared after removing `www.`, `m.`, ports and tracking parameters. The first appearance is kept. |
| London shared stories | Headline words in the address are compared within a month. One copy is kept, chosen by the seeded random order. |
| Apple Daily and Now TV (check list) | The Taiwan edition of Apple Daily and the finance pages of now.com are left out. |
| The seven London papers that jumped | Identified from yearly counts: East London Advertiser, Hackney Gazette, Ham & High, Ilford Recorder, Islington Gazette, Kilburn Times, Romford Recorder. |
| Google Trends requests | There are 11 sets other than Economy and 12 open slots, so the third request repeats Safety. The first request's Safety is the one used. |
| Sample for the "all listed outlets" check | The same 1,000-a-month budget split equally over every listed outlet: 41 per outlet per month in Hong Kong and London, 50 in New York. |
| Theme tags sent to the model | The first 30 different tags in order of first appearance. |
| Poster size | A 48 by 36 inch board holds at most 16 US Letter pages laid flat (four rows of four landscape pages). The kit is 16 pages, not the 18 to 24 aimed for. |
| Yearly change in news attention | Computed on a matched panel: each outlet's own change from a year earlier, averaged across the outlets present in both periods. With every outlet present this equals the change in the city average. It matters for Hong Kong in 2020 (two outlets are left out of 2015 to 2019) and for months where an outlet had no articles. |
| Which validation items the 0.61 rule uses | Items that remain in the main series after the headline-check rule. Hong Kong items from the two outlets left out of 2015 to 2019 are not counted, because their labels are not used. Kappa on every validation item is reported beside it. This was decided before the second coder ran. |
| A site that challenged automated requests | scmp.com answered page requests with a challenge. The run stopped using the site and did not fetch its pages from anywhere else. South China Morning Post validation items from 2020 on were coded by the second coder from the real headline that GDELT stored, without opening lines. Earlier items were replaced by other items in the same category. |
| HK China News Agency in the validation set | Its article pages are gone from the live site and the Internet Archive holds few. Only 16 of 299 Hong Kong validation items are from this outlet, far below its share of the sample. |
| Minimum data for a pair | A pair enters the pooled model only with at least 24 matched months, 8 quarters, or 5 years. |
| Wording of verdicts | A hypothesis is called supported only when the 95% interval excludes zero in the predicted direction. A slope below 0.30 is called weak, below 0.50 moderate. These cutoffs are the run's, not the methodology's. |
| Effective sample size | Reported as matched periods divided by 12 months (4 quarters, 1 year), summed over pairs. |
| p-values | From the bootstrap: twice the smaller share of resampled slopes on either side of zero. |
| Release-date check | Each official series is shifted by its approximate publication lag in whole months, taken from the source inventory or from what the run saw. |
| Causes of disconnections | Proposed by rule from the breaks table and a short list of named events. For the seven longest news disconnections the run also read a seeded sample of that period's headlines. All causes are proposed by AI for Cayden to confirm. |
| Events named at attention peaks | For attention-only categories that passed validation, the run read a seeded sample of the peak month's headlines and named what they were about. For Cayden to confirm. |
| Checks added by the run | Three checks are labeled exploratory wherever they appear: every main-panel outlet in every year, Hong Kong from articles with headline words only, and a bootstrap with 24-month blocks. |
| Current-year ranking | Each main indicator's mean over its latest 12 months (or its latest annual value) is compared with its own 2015 to 2019 mean, in 2015 to 2019 standard deviations, signed so that positive is worse. Price indices use the 12-month rate. |

## 6. Items cut or still open

Pending: this section is completed at the end of the run (labeling round reached, validation outcome and categories dropped, the headline check and its effect on Hong Kong 2015 to 2019, the social media snapshot, and the pre-2015 news extension).
