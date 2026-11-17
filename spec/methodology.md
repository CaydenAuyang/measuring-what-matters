# **Measuring What Matters: Methodology**

October 7, 2026 · Cayden Auyang

## **Overview**

This study tests whether public attention to a city's problems moves with the official measures of those problems, and what it means when the two disagree. For Hong Kong, New York City, and London, I compare official statistics for eight problem categories (about 2005 to 2026\) with how much local news covered each problem (2015 to 2026\) and how much residents searched for it (2004 to 2026).

The answer matters beyond this course. OurCityHealth, the civic intelligence platform I built, scores cities from news coverage. Where news attention moves with official data, that is evidence it carries real information about conditions. Where the two diverge, the study asks why, because either one can be wrong.

Official statistics are the benchmark, not ground truth. They are measurements with their own blind spots: recorded crime counts only what is reported and recorded, survey-based unemployment rates weaken when fewer people respond, and shelter counts reflect policy as well as need. The study therefore treats official data and public attention as two imperfect measures of the same problems. Where they disagree, the cause is classified rather than assumed (see H3).

This document is fixed before I look at any outcome data. After my mentors approve it, it will be posted publicly as a pre-registration.

**Three voices, compared for each city and category**

| Voice | Source | Years | AI labels |
| :---- | :---- | :---- | :---- |
| Government | Official statistics | 2005 to 2026 | Not needed |
| Residents | Google search interest | 2004 to 2026 | Not needed |
| Journalists | Local news (GDELT), 1,000 articles a month | 2015 to 2026 | Checked against my hand-coding (kappa at least 0.61) |

All three feed one comparison of yearly changes: do they move together (H1), which moves first, does attention react more to worsening than improving (H2), and where do they split (H3).

Search needs no AI labels, because each search term belongs to a category in advance. News articles, and the posts in the social snapshot, are labeled by AI, so they pass through the hand-coded check before reaching the comparison.

## **Research questions and hypotheses**

The study asks three questions. Each has a test or a stated expectation, fixed before the data are pulled.

> 1. **Can scattered informal signal be turned into a defensible monthly measure of attention?** A category is only analysed if the AI labels behind it agree with my hand-coding at a Cohen's kappa of 0.61 or higher, the threshold Landis and Koch (1977) call substantial agreement.  
> 2. **Does attention move with the official measure of the same problem?**  
   * H1: Year-over-year changes in news attention correlate positively with changes in the matching official indicator, but weakly. Funkhouser (1973) found 1960s news coverage tracked real-world statistics poorly. Behr and Iyengar (1985) found real conditions shaped public concern partly through how much television covered them.  
   * H2: Attention reacts more to a problem getting worse than to it getting better. Soroka (2006) found UK coverage and opinion responded more strongly to negative economic changes than to equal positive ones.  
   * Exploratory: whether news or search moves first, reported for each category without a prediction. Searches for jobs have tracked official US unemployment closely in past work (D'Amuri and Marcucci, 2017).  
> 3. **Where do official data and attention stay disconnected, and why?**  
   * H3: Safety shows the largest gap between attention and official data, measured as the share of months in which the two move in opposite directions, in at least two of the three cities. In 23 of 27 Gallup surveys since 1993, at least 60% of US adults said crime was rising nationally, while it fell over most of that period (Gramlich, 2024).  
   * Downs (1972) argued attention to a problem fades even while the problem continues, so long stretches where a problem stays bad but coverage drops are expected and will be reported.

The four categories with no official statistic (Governance, Culture, Technology, Community) are described, not tested.

## **Cities**

Hong Kong, New York City, and London have similar populations (roughly 7.5 to 9 million each, approximate) and very different political and media systems. Comparing how attention behaves inside each city, rather than comparing the cities' problems against each other, keeps those differences from biasing the result.

| City | Media system relevant to this study | Role |
| :---- | :---- | :---- |
| Hong Kong | Chinese- and English-language press; several major outlets closed in 2021; LIHKG is the main local forum | Pilot: every method is built and tested here first |
| New York City | Commercial local press and local TV; US national media also based here | Second city |
| London | National press and the BBC based in the city, plus London-only outlets | Third city |

Hong Kong is the pilot because it is the city I know best, which helps most when I hand-code its news and posts.

## **Codebook**

Every article or post gets one label: the main problem it describes, or "not a civic problem." The twelve categories are OurCityHealth's dimensions, rewritten with boundaries so that the AI and I apply the same rules. Eight are compared with official data; four have no official statistic and are reported on their own.

| Category | Covers | Goes elsewhere | Compared with official data |
| :---- | :---- | :---- | :---- |
| Safety | Crime and personal safety | National security cases (Governance); road crashes (Transport) | Yes |
| Economy | Jobs, unemployment, wages, business conditions, poverty, inequality | Everyday prices (Cost of Living) | Yes |
| Housing | Rent, home prices, supply, living conditions, subdivided flats, homelessness | Other prices (Cost of Living) | Yes |
| Transport | Transit reliability, congestion, commuting, fares, road safety |  | Yes |
| Environment | Air and water pollution, green space, climate hazards such as typhoons, floods, and heat |  | Yes |
| Health | Access to care, waiting times, public health, disease, mental health, overdoses |  | Yes |
| Education | School quality, access, attainment, teacher supply |  | Yes |
| Cost of Living | Everyday prices other than housing: food, utilities, goods | Rent and home prices (Housing); fares (Transport) | Yes |
| Governance | Government decisions, trust in institutions, corruption, elections, national security cases |  | No |
| Culture | Arts, heritage, and nightlife as civic issues, such as venue closures or funding cuts | Event listings and reviews (not a civic problem) | No |
| Technology | Digital access, outages, cyberattacks on public services, privacy | Tech industry and startup news (not a civic problem) | No |
| Community | Relations between residents: cohesion, discrimination, neighborhood life | Trust in government (Governance) | No |

Tie-break rules:

> * Label the problem the item describes, not every topic it mentions.  
> * A protest goes under Governance when the story is the policy, and under Safety when the story is violence.  
> * Immigration goes wherever the problem lands: shelter shortages under Housing, policy disputes under Governance.  
> * Tone is labeled separately as negative (the problem is bad or worsening), neutral, or positive (improving).

## **Official indicators**

Each compared category has a main indicator and a backup in each city, all from government or official bodies. Most are monthly from 2005 or earlier; Education is annual everywhere, and Hong Kong crime is annual before 2022\. Each series is used at its own frequency and never interpolated. Full entries, with caveats, are in the source inventory. Appendix C fixes each indicator's direction (which way is worse) and how it is transformed.

**Hong Kong**

| Category | Main indicator | From | Frequency | Backup |
| :---- | :---- | :---- | :---- | :---- |
| Safety | [Overall reported crime, HK Police](https://www.police.gov.hk/ppp_en/09_statistics/csc_2001_2013.html) | 2001 | Annual (monthly only for 2022 to 2024\) | Violent crime, HK Police |
| Economy | [Unemployment rate, seasonally adjusted, C\&SD table 210-06101](https://www.censtatd.gov.hk/api/get.php?id=210-06101&lang=en&full_series=1) | 1981 | Monthly, 3-month average | Underemployment rate, same table |
| Housing | [Private domestic rental index, Rating and Valuation Dept](https://www.rvd.gov.hk/doc/en/statistics/his_data_3.xls) | 1993 | Monthly | Public rental housing waiting time, Housing Bureau (quarterly) |
| Transport | [Fatal and serious road accidents, Transport Dept digest](https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/table71_eng.csv) | 2003 (PDF), 2013 (CSV) | Monthly | MTR incidents delaying 8+ minutes (annual, from 2008\) |
| Environment | [NO2 and particulate concentrations, EPD stations](https://cd.epic.epd.gov.hk/EPICDI/air/station/?lang=_en) | 1990 | Hourly, averaged monthly | Very hot days, HK Observatory |
| Health | [Specialist outpatient waiting time, Hospital Authority](https://data.gov.hk/en-data/dataset/hospital-hadata-sop-waiting-time) | 2013 (all specialties from 2015\) | Quarterly | Notifiable disease notifications, Centre for Health Protection (monthly, 1997\) |
| Education | [HKDSE candidates meeting university entrance requirements, HKEAA](https://www.hkeaa.edu.hk/DocLibrary/HKDSE/Exam_Report/Examination_Statistics/dseexamstat24_3.pdf) | 2012 | Annual | Teacher wastage rate, Education Bureau (from 2017/18) |
| Cost of Living | [Composite CPI, C\&SD table 510-60001](https://www.censtatd.gov.hk/api/get.php?id=510-60001&lang=en&full_series=1), rent component removed | 1981 | Monthly | Underlying Composite CPI (from 2007\) |

**New York City**

| Category | Main indicator | From | Frequency | Backup |
| :---- | :---- | :---- | :---- | :---- |
| Safety | [Felony complaints, NYPD complaint data](https://data.cityofnewyork.us/resource/qgea-i56i.json) | 2006 | Monthly | Shooting incidents, NYPD (2006) |
| Economy | [Unemployment rate, seasonally adjusted, NYS DOL / BLS](https://data.ny.gov/resource/dh9m-5v4d.json) | 1976 | Monthly | Total nonfarm jobs, BLS (1950) |
| Housing | [People in DHS shelters, NYC DHS](https://data.cityofnewyork.us/resource/k46n-sa2m.json), with the Coalition for the Homeless series before 2013 | 1983 | Monthly | Rent of primary residence CPI, NY metro, BLS |
| Transport | [Subway on-time performance, MTA](https://data.ny.gov/resource/f6rf-2a3t.json) | 2009 | Monthly | People killed or injured in crashes, NYPD (from July 2012\) |
| Environment | [Daily PM2.5 concentrations by county, EPA AirData](https://aqs.epa.gov/aqsweb/airdata/download_files.html) | 1999 | Daily, averaged monthly | Daily air quality index, EPA (1989) |
| Health | [Deaths by month, CDC WONDER](https://wonder.cdc.gov/mcd.html) | 1999 | Monthly | Overdose deaths, CDC (12-month rolling, 2015\) |
| Education | [Four-year graduation rate, NYC DOE](https://infohub.nyced.org/reports-and-policies/citywide-information-and-data/graduation-results) | Class of 2005 | Annual | Daily attendance, NYC DOE (2006 to 2021\) |
| Cost of Living | [CPI all items less shelter, NY metro, BLS](https://fred.stlouisfed.org/series/CUURA101SA0L2) | 1975 | Monthly | CPI food, NY metro, BLS |

**London**

| Category | Main indicator | From | Frequency | Backup |
| :---- | :---- | :---- | :---- | :---- |
| Safety | [Recorded crime, Metropolitan Police](https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m) | 2008 (current categories 2010\) | Monthly | Police recorded crime, Home Office (quarterly, 2002/03) |
| Economy | [Unemployment rate, London, ONS series YCNI](https://www.ons.gov.uk/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/ycni/lms) | 1992 | Monthly, rolling 3 months | Claimant count, London, ONS series DPDK |
| Housing | [Private rents, London, ONS](https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/priceindexofprivaterentsukmonthlypricestatistics) (older index joined to the current one at 2015\) | 2005 | Monthly | Households in temporary accommodation, MHCLG (quarterly, 2004\) |
| Transport | [Killed or seriously injured road casualties, DfT](https://www.gov.uk/government/statistics/road-safety-data) | 1979 | Monthly by collision date | Underground lost customer hours, TfL (2011 to 2019\) |
| Environment | [NO2 at Marylebone Road and Bloomsbury, London Air Quality Network](https://api.erg.ic.ac.uk/AirQuality/Data/SiteSpecies/SiteCode=MY1/SpeciesCode=NO2/StartDate=2005-01-01/EndDate=2005-01-03/Json) | 1992 | Hourly, averaged monthly | PM2.5 at the same sites (1998) |
| Health | [Waiting list: share waiting under 18 weeks, NHS England, London region](https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/) | Aug 2007 | Monthly | A\&E four-hour performance, NHS England (monthly, 2015\) |
| Education | [Attainment 8 at GCSE, London, DfE](https://explore-education-statistics.service.gov.uk/data-catalogue/data-set/9e761bdf-fe02-4e1e-9d3d-b32dac9fa6ef) | 2015/16 (earlier years to confirm) | Annual | Absence rate, London, DfE (2006/07) |
| Cost of Living | [CPI annual rate, ONS series D7G7](https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7g7/mm23), UK-wide | 1989 | Monthly | None official; no London price index exists |

Two gaps are built into the design. London has no city-level price index, so its Cost of Living comparison uses UK-wide inflation and is reported with that caveat. New York's price series are for the metro area, not the five boroughs.

## **Measuring attention**

Attention is each category's share of a city's local coverage or search interest in a month, never a raw count. Shares cancel out the growth in GDELT's source list and the difference in size between cities.

**Local news (GDELT, 2015 to 2026).** GDELT's Global Knowledge Graph records each article's source, the places it mentions, its themes, and its tone; version 2 starts on 19 February 2015\. Every query runs on the partitioned BigQuery table (gdelt-bq.gdeltv2.gkg\_partitioned) and filters on the partition date, which keeps a decade of queries cheap.

> * **Which outlets count.** An outlet counts for a city if it is based there and mainly covers it. National outlets count only through their city-section web addresses, such as /nyregion/ on nytimes.com or /news/uk-england-london on bbc.co.uk. The lists are fixed in Appendix A before data are pulled.  
> * **A fixed panel.** The main series uses only outlets GDELT recorded steadily in every year from 2015, so an outlet joining or leaving cannot shift the shares. Applying this rule leaves three outlets in Hong Kong, three in New York, and 15 borough papers in London (Appendix A). All listed outlets are used as a check.  
> * **What the model reads.** GDELT stores headlines only from 2020, so for every year the model reads the same inputs: any headline words in the article's web address, plus GDELT's theme tags. For outlets with number-only addresses, including several large Hong Kong sources, that means theme tags alone. Using 2020 onward, labels from the real headline are compared with labels from these inputs, separately for outlets with and without headline addresses. If theme-tag-only labels fall below the kappa threshold, those outlets are left out of 2015 to 2019 and the change is reported.  
> * **Sample and index.** Duplicates are removed by web address. Each month, up to 1,000 local articles per city are drawn at random and labeled, up to an equal number per outlet. Each category's share is computed for each outlet and averaged across the city's outlets with equal weights (Appendix A). That average is the month's news attention, the attention index; the negative-tone share is the alternative used in checks.

**Resident search (Google Trends, 2004 to 2026).** Each category gets a fixed set of search terms, in English plus Traditional Chinese for Hong Kong, chosen before any data are pulled and listed in Appendix B.

> * Trends scales each request from 0 to 100 and draws on a sample of searches, so every request includes the same anchor term, and each request is downloaded three times on different days and averaged. Data come as CSV files from the Trends website.  
> * Geography: Hong Kong as a whole; the New York media market (about 20 million people, wider than the city); and England for London, since Trends offers nothing smaller in the UK.  
> * Mellon (2014) found search data measured issue salience well for some issues and poorly for others. The terms are fixed in advance and none are dropped after seeing results; weak categories are reported as weak.

**Social media snapshot (latest 12 months).** YouTube comments on local news channels, X posts, Threads posts (once Meta approves keyword search), and LIHKG threads for Hong Kong. This layer answers one question: does what residents are saying now match the 12-month news and search picture? Collection rules are under Breaks, limitations, and ethics.

**Optional pre-2015 news extension.** If time allows, one newspaper per city is carried back to 2005: the Guardian Open Platform for London (from 1999), the New York Times Archive API for New York (headlines and abstracts), and WiseNews for Hong Kong (Hong Kong papers from 1998\) if research access is granted. It is reported separately, because one paper is not a city's whole local press.

## **Feasibility check**

A one-week test of GDELT (1 to 7 September 2026\) found enough local news in all three cities, but showed that New York cannot be found by location tags alone and that GDELT's Hong Kong coverage leans on a few outlets. The test counted articles only; it did not look at what they said about any problem.

| City | Articles from local outlets in one week | Estimated per month | Largest sources on the draft outlet list |
| :---- | :---- | :---- | :---- |
| Hong Kong | about 1,900 | about 8,200 | HK China News Agency 573, Metro Radio 556, HK Commercial Daily 310, Wen Wei Po 203, SCMP 149 |
| New York City | about 780 | about 3,400 | New York Post 305, Newsday 87, Daily News 82, ABC7 52, NBC New York 49, Gothamist 48 |
| London | about 910 | about 3,900 | London Now 196, The Guardian 177, Metro 144, BBC 126, LBC 95, City AM 59 |

What changes because of it:

> * **New York needs the outlet list.** GDELT tags most New York stories as "New York, United States," which is the state, not the city: about 16,000 articles on 2 September alone, against a few hundred tagged Manhattan or Brooklyn. So an article counts only if it comes from a New York City outlet or city section and mentions the city or a borough. The draft list also needs tightening: Newsday mainly covers Long Island, and ABC7 and NBC New York cover the whole tri-state area.  
> * **Hong Kong's GDELT coverage is narrow.** HK01, Ming Pao, HKET, The Standard, and Hong Kong Free Press had no articles that week, and RTHK had 3\. Hong Kong results from GDELT therefore describe a narrow slice of the local press and are reported by outlet group, and WiseNews access is the most valuable addition to the study.  
> * **Headlines exist only from 2020\.** A second test found GDELT stored headlines for none of the test outlets' articles in June 2015 or June 2019, and for all of them from June 2020\. The English-language outlets tested put headline words in nearly every web address (98% to 100%). Oriental Daily, Ming Pao, and HK01 put the Chinese headline in theirs in encoded form. HK Commercial Daily, HK China News Agency, Wen Wei Po, and Now TV use number-only addresses, so before 2020 the model has only GDELT's theme tags for them.  
> * **The sample size works.** The main panels in Appendix A hold at least about 2,400 articles a month in every year from 2015 before the city filter, which will cut New York's most. The sample is up to 1,000 a month, and its size after filtering is reported for every month.  
> * **Partition filtering is essential.** This week of two fields scanned 0.77 GB with a partition filter. The same query filtered only on the article date scans 781 GB.

## **AI labeling and validation**

A language model labels each sampled article and post with one category and one tone, using the codebook word for word and returning a fixed structured format. For news it reads the headline words in the web address plus GDELT's theme tags (see Measuring attention). The model version and the prompt are frozen before labeling starts and saved with the data.

The labels are checked against my own judgment before any of them are used:

> 1. **Hand-coded set.** Before the full run, I label about 300 items per city (900 in total) without seeing the model's labels, reading each item's headline and opening lines from the live page or the Internet Archive. The set is drawn so every category has at least 20 items in each city, and is spread across years, languages, and outlets; agreement is weighted back to the full sample.  
> 2. **Agreement.** Cohen's kappa per category and overall, plus a table of which categories the model confuses.  
> 3. **Decision rule.** A category is analysed in a city only if kappa is at least 0.61. If it falls short, I revise that category's wording once, label a fresh sample, and test again. If it still falls short, the category is dropped for that city and reported as a limitation.  
> 4. **A second coder.** A classmate labels 150 of the same items, and I re-label 50 items two weeks later to measure my own consistency. If no second coder is found by the end of October, that is reported as a limitation.

Gilardi, Alizadeh, and Kubli (2023) found a language model labeled political text more accurately than crowd workers on most of their tasks, but accuracy varies by task, which is why the hand-coded check comes before the analysis rather than after it.

## **Analysis plan**

The main test compares changes, not levels: for each city and category, does attention rise when the official measure gets worse? Two series that both trend for twenty years will correlate even if unrelated, and changes remove that trap.

> 1. **Year-over-year change.** Each month (or year, for annual series) is compared with the same period a year earlier, for both the official and the attention series. This also removes seasonal patterns, such as summer air pollution or winter flu.  
> 2. **Main test (H1).** All city and category pairs are pooled in one regression of attention change on official change, with a separate intercept for each pair, after each pair's changes are put in standard deviations (Appendix C). Pooling matters because each pair has only about ten (news) to twenty (search) independent years of overlap; the effective sample size is reported. Confidence intervals come from a block bootstrap with 12-month blocks.  
> 3. **Asymmetry (H2).** The same pooled model, with official change split into months when the problem worsened and months when it improved. H2 holds if the worsening coefficient is larger.  
> 4. **Lead and lag (exploratory).** Correlations at lags from 12 months before to 12 months after, with significance from permutation tests. News is also tested against search the same way.  
> 5. **Disconnection (H3).** For each pair, the share of months in which attention and the official measure move in opposite directions. Periods of six months or more are listed, and each is assigned its most likely cause: the official measure changed how it counts, a real event drew coverage the indicator does not capture, attention followed a news cycle rather than conditions, the two measure different parts of the problem, or unclear. Each period is classified using the breaks table, the official series' documentation, and a sample of that period's coverage.

The main tests are the pooled H1 and H2 models for news and for search, four in all. Results for each of the 48 city, category, and source pairs are reported as description, with p-values adjusted using the Benjamini-Hochberg method.

**Checks that the results hold** (the end-of-term validation evidence):

> * Backup indicators in place of the main ones.  
> * With and without the COVID years (2020 to 2022\) and the other months marked as breaks.  
> * Official series aligned by release date as well as by the period they measure, since attention may react to a published figure rather than to conditions.  
> * All listed outlets in place of the fixed panel.  
> * Negative-tone share in place of all coverage.

**Other outputs.** A one-page current-year summary ranks each city's eight categories by how far each official indicator sits from its own 2015 to 2019 average, in standard deviations, next to the ranking by attention. Annual-only series (Education everywhere, Hong Kong crime) give only 9 to 20 annual points each, so they are reported as weaker evidence. The four signal-only categories get attention trends for 2015 to 2026, with major events named.

## **Breaks, limitations, and ethics**

Every known break is marked in the data before analysis, and every check runs with and without it.

| Where | Break | When | Handling |
| :---- | :---- | :---- | :---- |
| All cities | COVID distorts nearly every series | 2020 to 2022 | Treated as a separate period; results shown with and without it |
| All cities | GDELT's source list grows | Throughout | Shares, not counts; fixed panel of outlets |
| All cities | GDELT stores headlines only from 2020 | 2020 | The model reads web addresses and theme tags in every year |
| All cities | Google changes how Trends collects data | On the dates Google marks in its charts | Marked |
| Hong Kong | Protests (2019) and the National Security Law (2020) dominate coverage | 2019 to 2020 | Real events; marked; checks without those months |
| Hong Kong | Several major outlets closed | 2021 | Marked; results checked before and after |
| Hong Kong | Online fraud drives the rise in reported crime | 2023 onward | Violent crime as the backup indicator |
| Hong Kong | Seasonal adjustment of unemployment changed | 2008 | Marked |
| Hong Kong | Air index changed from API to AQHI | Dec 2013 | Raw pollutant concentrations used instead of the index |
| Hong Kong | University entrance requirement changed | 2024 | Marked |
| New York | Subway performance files joined | 2015 | Checked where the two files overlap |
| New York | Crash recording system changed | Mar 2016 | Marked |
| New York | Price index area boundaries redrawn | 2018 | Marked |
| New York | Exam waivers may have raised graduation rates | 2020 to 2022 | Marked (to confirm) |
| New York | Asylum-seeker arrivals raise the shelter count | 2022 to 2024 | A real event, named when interpreting results |
| London | Crime categories changed; police recording system changed | Mar 2019; Feb 2024 | Marked |
| London | Labour Force Survey reweighted; response problems | Jan 2019; 2023 to 2024 | Marked; claimant count as backup |
| London | NHS boundaries changed; community services dropped from the waiting list | 2013, 2022; Feb 2024 | Marked |
| London | GCSE grading changed; teacher-assessed grades | 2017; 2020 to 2021 | Marked |
| London | Met Police moved to injury-based casualty reporting | Nov 2016 | Severity-adjusted figures used |
| London | Ultra Low Emission Zone expansions cut pollution | 2019, 2021, 2023 | A real policy effect, named when interpreting results |
| London | Seven borough papers jump in GDELT volume | 2022 to 2023 | Shared stories counted once; results also shown without those papers |

**Limitations.**

> * Official statistics are a benchmark, not ground truth. When attention and an official measure disagree, the official measure may be the one that is wrong, so H3 classifies each disagreement instead of assuming either side is right.  
> * GDELT's Hong Kong coverage leans on a few outlets, and the Hong Kong main panel is mainstream and pro-establishment. London's main panel is borough papers, with no citywide outlet (Appendix A). Machine-coded GDELT locations are also unreliable below the country level (Hammond and Weidmann, 2014, on GDELT's event data), and my test found the same problem for New York.  
> * Labels for 2015 to 2019 rest on web-address headlines and theme tags, and on theme tags alone for Hong Kong outlets with number-only addresses, which carry less information than a full article.  
> * Search geography is wider than the city in New York (the media market) and in London (England).  
> * New York's price series cover the metro area; London's inflation is UK-wide and includes some rent.  
> * Attention shows how much a problem is discussed, not what people think should be done about it.  
> * The study shows whether series move together and which moves first. Its explanations of disagreements are judgments based on the coverage and the data documentation, not tested causes.

**Ethics and collection rules.**

> * Only data a logged-out visitor can see. No logins, and no getting around captchas or blocks; if a site challenges the collection, it stops.  
> * No usernames or profile details are stored. Posts are kept as text, date, and platform, and quotes in the paper are paraphrased so they cannot be searched back to a person.  
> * Reddit is excluded because its policy bars research using data collected outside its researcher program. Facebook, Instagram, and TikTok are excluded because their public data sits behind logins.  
> * LIHKG's terms of service could not be confirmed online; I will read them before collecting, and collection runs slowly on public threads only.  
> * Raw social data is deleted after the study. The published dataset holds monthly shares only.

## **Timeline, pre-registration, and AI use**

No outcome data are collected until my mentors approve this plan at the midterm check-in (week of October 12). The only data pulled so far are the outlet and headline counts in the feasibility check and Appendix A, which say nothing about any problem. Hong Kong runs first, so the method is tested on one city before it is applied to all three.

**Data collection starts only after my mentors approve the plan (planned schedule; the fall term ends November 20, 2026\)**

| Stage | Dates |
| :---- | :---- |
| **Midterm check-in, approval** | **Oct 12 to Oct 16** |
| Pre-register, build pipeline | Oct 12 to Oct 18 |
| Hong Kong pilot, validation | Oct 19 to Oct 28 |
| New York and London | Oct 29 to Nov 6 |
| Analysis and checks | Nov 7 to Nov 13 |
| Full draft, presentation | Nov 14 to Nov 20 |

**Pre-registration.** After approval, this document, the search terms, and the outlet lists are posted on the Open Science Framework with a timestamp, before any outcome data are pulled. Any later change is logged with its date and reason.

**After the term.** I revise the paper for submission to the Journal of Emerging Investigators, a peer-reviewed journal for student research, and publish the dataset.

**AI use.** AI helps with code, data cleaning, literature search, and drafting from my outlines and dictation, which I then edit. The research question, codebook, indicator choices, index design, and interpretation are mine. Every use goes in a log (date, tool, task, what I changed), and the final paper includes a disclosure statement.

## **References**

Data sources are listed with full entries in the source inventory.

> * Behr, R. L., & Iyengar, S. (1985). Television news, real-world cues, and changes in the public agenda. *Public Opinion Quarterly, 49*(1), 38–57. [https\://doi.org/10.1086/268900](https://doi.org/10.1086/268900)  
> * D'Amuri, F., & Marcucci, J. (2017). The predictive power of Google searches in forecasting US unemployment. *International Journal of Forecasting, 33*(4), 801–816. [https\://doi.org/10.1016/j.ijforecast.2017.03.004](https://doi.org/10.1016/j.ijforecast.2017.03.004)  
> * Downs, A. (1972). Up and down with ecology: The "issue-attention cycle." *The Public Interest, 28*, 38–50.  
> * Funkhouser, G. R. (1973). The issues of the sixties: An exploratory study in the dynamics of public opinion. *Public Opinion Quarterly, 37*(1), 62–75. [https\://doi.org/10.1086/268060](https://doi.org/10.1086/268060)  
> * Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences, 120*(30), e2305016120. [https\://doi.org/10.1073/pnas.2305016120](https://doi.org/10.1073/pnas.2305016120)  
> * Gramlich, J. (2024, April 24). *What the data says about crime in the U.S.* Pew Research Center. [https\://www\.pewresearch.org/short-reads/2024/04/24/what-the-data-says-about-crime-in-the-us/](https://www.pewresearch.org/short-reads/2024/04/24/what-the-data-says-about-crime-in-the-us/)  
> * Hammond, J., & Weidmann, N. B. (2014). Using machine-coded event data for the micro-level study of political violence. *Research & Politics, 1*(2). [https\://doi.org/10.1177/2053168014539924](https://doi.org/10.1177/2053168014539924)  
> * Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics, 33*(1), 159–174. [https\://doi.org/10.2307/2529310](https://doi.org/10.2307/2529310)  
> * Mellon, J. (2014). Internet search data and issue salience: The properties of Google Trends as a measure of issue salience. *Journal of Elections, Public Opinion and Parties, 24*(1), 45–72. [https\://doi.org/10.1080/17457289.2013.846346](https://doi.org/10.1080/17457289.2013.846346)  
> * Soroka, S. N. (2006). Good news and bad news: Asymmetric responses to economic information. *The Journal of Politics, 68*(2), 372–385. [https\://doi.org/10.1111/j.1468-2508.2006.00413.x](https://doi.org/10.1111/j.1468-2508.2006.00413.x)

## **Appendix A: Outlet lists**

The main panels are three outlets in Hong Kong, three in New York, and 15 borough papers in London. These are the only candidates GDELT recorded steadily in every year from 2015 to 2026\. I checked this on 7 October 2026 by counting each candidate outlet's GDELT articles by year and month. The check used outlet names and counts only, never what the articles said.

* **Main panel rule.** An outlet is in the main panel if GDELT holds its articles in at least three-quarters of the months of every year from 2015 to 2026, averaging at least 30 a month in each year. 2015 starts on 19 February and 2026 runs to September.  
* **Local, general news only.** The outlet is based in the city, mainly covers it, and covers all topics. Business and transport outlets are left out, because they would inflate one category.  
* **City sections.** National outlets count only through city-section web addresses. These were checked in the first week of March, June, September, and December of each year. None appears in every year, so none is in a main panel.  
* **City filter.** A New York article counts only if GDELT tags it with the city or a borough, which also keeps out NBC New York's stories from elsewhere in the tri-state area. A Hong Kong article counts only if it is tagged with Hong Kong, because these outlets also cover mainland China and the world. The South China Morning Post counts only through its Hong Kong news section. London papers carry national wire stories under national-news addresses (such as /news/national/), and those are dropped. The hand-coded set records whether each article is really about the city, so the filter's error rate is reported by category.  
* **Equal weight per outlet.** Each month, up to 333 articles per outlet are sampled in Hong Kong and New York, and up to 66 per paper in London. A city's attention share is the average of its outlets' shares, each outlet weighted equally. If an outlet has no articles in a month, the average uses the others and the month is flagged. Without equal weights, HK China News Agency would supply 66% to 78% of Hong Kong's articles each year, and the Daily News 40% to 88% of New York's.  
* **Shared stories.** A story that runs on more than one London paper in the same month (the same headline words in the web address) counts once. Seven of the London papers rose several-fold in GDELT in 2022 and 2023, which suggests shared content; results are also shown without those seven.  
* **The check list.** Every outlet below, main panel or not, is used in the "all listed outlets" check, in any month it has articles.

The Hong Kong panel is mainstream and pro-establishment. No outlet that closed in 2021, such as Apple Daily or Stand News, can be in a panel that runs to 2026\. HK China News Agency is the most pro-Beijing outlet on the panel and supplies most of GDELT's Hong Kong volume, so Hong Kong results are also shown without it. The check list and WiseNews are where the rest of the press shows up.

In the tables, a year counts when the outlet has articles in at least three-quarters of that year's months. The 30-a-month floor applies only to the main panel.

**Hong Kong**

| Outlet | Web address | Years recorded | Use |
| :---- | :---- | :---- | :---- |
| South China Morning Post | scmp.com, Hong Kong news section | 2015 to 2026 | Main panel |
| Oriental Daily | orientaldaily.on.cc | 2015 to 2026 | Main panel |
| HK China News Agency | hkcna.hk | 2015 to 2026 | Main panel; number-only addresses |
| Now TV News | now.com | 2015 to 2026; under 30 a month in 2021 and 2022 | Check; number-only addresses |
| Sing Tao Headline | stheadline.com | 2015 to 2026; under 30 a month in 2026 | Check |
| HK Commercial Daily | hkcd.com | 2016 to 2026 | Check; number-only addresses |
| Wen Wei Po | wenweipo.com | 2015 to 2016, 2019 to 2026 | Check; number-only addresses |
| Ming Pao | mingpao.com | 2015 to 2025 | Check |
| Ta Kung Pao | takungpao.com.hk | 2015 to 2025 | Check |
| HKEJ | hkej.com | 2015 to 2024 | Check |
| HKET | hket.com | 2015 to 2019, 2022 to 2026 | Check |
| The Standard | thestandard.com.hk | 2015 to 2021, 2023 to 2024 | Check |
| RTHK | rthk.hk | 2017 to 2026; under 30 a month from 2024 | Check |
| HK01 | hk01.com | 2016 to 2022 | Check |
| EJ Insight | ejinsight.com | 2015 to 2022 | Check |
| InMedia | inmediahk.net | 2015 to 2022, 2024 | Check |
| Hong Kong Free Press | hongkongfp.com | 2016 to 2019, 2023 to 2024 | Check |
| Stand News | thestandnews.com | 2016 to 2021 (closed 2021\) | Check |
| Apple Daily | appledaily.com | 2018 to 2019 (closed 2021\) | Check |
| TVB News | tvb.com | 2015 to 2018, 2020 to 2021 | Check |
| Metro Radio | metrohk.com.hk | 2015 to 2016; back in 2026 | Check |
| am730 | am730.com.hk | 2015 to 2018 | Check |
| China Daily Hong Kong | chinadailyhk.com | 2022 to 2024 | Check |
| Bastille Post | bastillepost.com | 2019 to 2022 | Check |

Sina Hong Kong and Hong Kong Herald are excluded because they mainly republish other outlets' stories.

**New York City**

| Outlet | Web address | Years recorded | Use |
| :---- | :---- | :---- | :---- |
| Daily News | nydailynews.com | 2015 to 2026 | Main panel |
| NBC New York | nbcnewyork.com | 2015 to 2026 | Main panel |
| Gothamist | gothamist.com | 2015 to 2026 | Main panel |
| New York Post | nypost.com | 2015 to 2019, 2023 to 2026 | Check; none in GDELT in 2021 and 2022 |
| amNewYork | amny.com | 2015 to 2019, 2023 to 2026 | Check |
| ABC7 New York | abc7ny.com | 2016 to 2020, 2023 to 2026 | Check |
| PIX11 | pix11.com | 2015 to 2020, 2023 | Check |
| NY1 | ny1.com | 2015 to 2024; under 30 a month from 2023 | Check |
| Staten Island Advance | silive.com | 2015 to 2020, 2023 to 2025 | Check |
| Brooklyn Eagle | brooklyneagle.com | 2015 to 2018, 2023 to 2026 | Check |
| Brooklyn Paper | brooklynpaper.com | 2015 to 2019, 2023 to 2026 | Check |
| QNS | qns.com | 2016 to 2018, 2023 to 2026 | Check |
| TimesLedger | timesledger.com | 2015 to 2018 | Check |
| BK Reader | bkreader.com | 2015 to 2016, 2023 to 2026 | Check |
| Riverdale Press | riverdalepress.com | 2015 to 2018, 2023 to 2026 | Check |
| City Limits | citylimits.org | 2015 to 2016, 2023 to 2026 | Check |
| THE CITY | thecity.nyc | 2020 to 2022, 2025 | Check |
| WNYC | wnyc.org | 2015 to 2017, 2026 | Check |
| New York Times, N.Y. region section | nytimes.com, /nyregion/ addresses | 2015 to 2024; few after | Check |
| CBS New York | cbsnews.com/newyork and newyork.cbslocal.com | 2015 to 2019, 2022 to 2026 | Check |

Newsday is excluded because it is based on Long Island. Crain's New York Business and Streetsblog are excluded as specialist outlets.

**London**

| Outlet | Web address | Years recorded | Use |
| :---- | :---- | :---- | :---- |
| News Shopper | newsshopper.co.uk | 2015 to 2026 | Main panel |
| Wandsworth Guardian | wandsworthguardian.co.uk | 2015 to 2026 | Main panel |
| Guardian Series | guardian-series.co.uk | 2015 to 2026 | Main panel |
| Richmond and Twickenham Times | richmondandtwickenhamtimes.co.uk | 2015 to 2026 | Main panel |
| Times Series | times-series.co.uk | 2015 to 2026 | Main panel |
| Harrow Times | harrowtimes.co.uk | 2015 to 2026 | Main panel |
| Ealing Times | ealingtimes.co.uk | 2015 to 2026 | Main panel |
| Enfield Independent | enfieldindependent.co.uk | 2015 to 2026 | Main panel |
| Ham & High | hamhigh.co.uk | 2015 to 2026 | Main panel |
| Romford Recorder | romfordrecorder.co.uk | 2015 to 2026 | Main panel |
| Ilford Recorder | ilfordrecorder.co.uk | 2015 to 2026 | Main panel |
| Islington Gazette | islingtongazette.co.uk | 2015 to 2026 | Main panel |
| Hackney Gazette | hackneygazette.co.uk | 2015 to 2026 | Main panel |
| Kilburn Times | kilburntimes.co.uk | 2015 to 2026 | Main panel |
| East London Advertiser | eastlondonadvertiser.co.uk | 2015 to 2026 | Main panel |
| Evening Standard | standard.co.uk | 2015 to 2021, 2023 to 2026 | Check; none in GDELT in 2022 |
| This Is Local London | thisislocallondon.co.uk | 2015 to 2025 | Check |
| MyLondon | mylondon.news | 2019 to 2024, 2026 | Check |
| London Now | london-now.co.uk | From December 2025 | Check |
| Get West London | getwestlondon.co.uk | 2015 to 2018 | Check |
| Croydon Guardian | croydonguardian.co.uk | 2015 to 2018 | Check |
| Croydon Advertiser | croydonadvertiser.co.uk | 2015 to 2018 | Check |
| BBC London section | bbc.co.uk, uk-england-london addresses | 2015 to 2024 | Check |
| ITV London section | itv.com, /news/london addresses | 2015 to 2025 | Check |

Metro, LBC, and the Guardian are excluded as national outlets without London-section addresses. City AM and London Loves Business are excluded as business outlets.

## **Appendix B: Search terms**

Each category has one fixed set of search terms per city, listed below. The sets are posted with the pre-registration and never changed after any data are seen.

* **What makes a term.** Words people search when a problem touches them, written the way residents write them: Traditional Chinese for Hong Kong, plus one English term where English searches are common.  
* **What is left out.** Names of places, events, people, and outlets. Program names that started during 2004 to 2026 (such as Universal Credit or the National Security Law), because a new name makes searches jump without the problem changing. Where a name changed, both are included (港鐵 replaced 地鐵 in 2007). Routine planning searches (booking appointments, school places, exam timetables, fares) and weather checks are left out, because they measure daily planning rather than concern.  
* **Scope.** Each set covers its category as the codebook defines it, so some sets are broader than their indicator. Transport sets include rail delays, while the main Transport indicators in Hong Kong and London measure road safety. Environment sets cover air pollution only, because heat and flood searches are mostly weather checks.  
* **How a set is entered.** Each set is one Trends item, with "+" between terms, so Trends counts searches containing any of them.  
* **Requests.** Web search, all categories, January 2004 to the last full month. Each request holds the Economy set plus four other sets, so three requests cover all twelve. The Economy set is the anchor: every set is divided by Economy in its own request, which puts the three requests on one scale before the shares are taken.  
* **Downloads.** Each request is downloaded on three different days and averaged. A value shown as "\<1" is recorded as 0.5.  
* **Sparse sets.** A set that reads zero in more than 10% of months is reported as too sparse to test in that city. It is not replaced, and it stays in the denominator so the twelve shares still add to 100%.  
* **Shares move together.** A spike in one category, such as Hong Kong's 2019 protests, lowers every other share. Those months are marked as breaks.  
* **Known gaps.** England is far wider than London; only the Tube terms are London-specific. New York's terms are English only, so Spanish- and Chinese-language searches are missed.

| Category | Hong Kong | New York media market | England (for London) |
| :---- | :---- | :---- | :---- |
| Safety | 罪案 \+ 搶劫 \+ 騙案 \+ 治安 \+ crime rate | crime rate \+ gun violence \+ robbery \+ stabbing \+ burglary | crime rate \+ stabbing \+ robbery \+ mugging \+ burglary |
| Economy | 失業 \+ 裁員 \+ 搵工 \+ 綜援 \+ unemployment | unemployment \+ layoffs \+ job search \+ food bank | unemployment \+ redundancy \+ jobcentre \+ food bank |
| Housing | 劏房 \+ 公屋輪候 \+ 租金 \+ 樓價 \+ 露宿者 | eviction \+ homeless shelter \+ affordable housing \+ rent stabilized \+ rent increase | eviction \+ homeless \+ social housing \+ rent increase \+ temporary accommodation |
| Transport | 港鐵故障 \+ 地鐵故障 \+ 塞車 \+ 交通意外 \+ MTR delay | subway delays \+ train delays \+ traffic jam \+ car crash | tube delays \+ tube strike \+ train delays \+ traffic jam \+ car crash |
| Environment | 空氣污染 \+ 空氣質素 \+ 煙霞 \+ air pollution \+ air quality | air quality \+ air pollution \+ smog | air pollution \+ air quality \+ smog |
| Health | 急症室 \+ 專科輪候 \+ 流感 \+ 精神健康 | emergency room \+ flu \+ overdose \+ mental health | A\&E \+ NHS waiting list \+ flu \+ mental health |
| Education | 收生不足 \+ 殺校 \+ 教師流失 \+ 學位不足 | teacher shortage \+ school overcrowding \+ failing schools \+ school budget cuts | teacher shortage \+ school funding cuts \+ failing schools \+ teacher strike |
| Cost of Living | 通脹 \+ 物價 \+ 加價 \+ inflation | inflation \+ grocery prices \+ gas prices \+ electric bill | inflation \+ energy bills \+ food prices \+ petrol prices |
| Governance | 特首 \+ 立法會 \+ 區議會 \+ 示威 \+ 貪污 | mayor \+ city council \+ corruption \+ protest | mayor of London \+ local council \+ corruption \+ protest |
| Culture | 文化保育 \+ 古蹟保育 \+ 藝術資助 | arts funding \+ venue closing \+ landmark preservation | arts funding \+ venue closure \+ pub closures \+ library closures |
| Technology | 上唔到網 \+ 資料外洩 \+ 網絡攻擊 \+ data breach | internet outage \+ data breach \+ cyberattack \+ ransomware | internet outage \+ data breach \+ cyber attack \+ ransomware |
| Community | 歧視 \+ 義工 \+ 社區中心 \+ 鄰居糾紛 | racism \+ discrimination \+ volunteer \+ community center | racism \+ discrimination \+ volunteering \+ community centre |

The news codebook counts typhoons, heat, and floods under Environment, but the search sets do not, for the reason above. Mellon (2014) expects some sets to work poorly. Education, Culture, and Community are the most likely, because searches about problems in those areas are rare.

## **Appendix C: Indicator direction and transformation**

Every official series is turned into a yearly change in which a positive number means the problem got worse. The rules below apply to all 24 main indicators and their backups.

* **Direction.** Five main indicators are better when higher, so their sign is reversed: Hong Kong's university entrance rate, New York's subway on-time rate and graduation rate, and London's 18-week waiting share and Attainment 8\. Three backups get the same treatment: New York's nonfarm jobs and school attendance, and London's A\&E four-hour performance.  
* **Comparison period.** Each value is compared with the same month, quarter, or year a year earlier.  
* **Counts, pollution levels, and waiting times.** Change is in percent, computed as 100 times the natural log of the ratio, so a rise and a fall of the same size count equally.  
* **Rates, shares, and scores.** Change is in percentage points or score points.  
* **Prices and rents.** The problem is how fast prices rise. The 12-month inflation rate is computed first, and its yearly change is measured in percentage points. Rents are used as published, not adjusted for inflation. Hong Kong's and New York's Cost of Living series leave housing out, so the two categories do not overlap there; London's UK-wide CPI includes some rent, which is a stated limitation.  
* **Matching attention.** Monthly series are matched with that month's attention share. Quarterly series are matched with the mean of the quarter's three months, and annual series with the mean of the year's 12 months (the September to August school year for Education). A series reported as a 3-month or 12-month average is matched with attention averaged over the same window.  
* **Pooling.** Before the pooled H1 and H2 models, each pair's official change and attention change are divided by their own standard deviation over the years they overlap. Slopes are then in standard deviations, so pairs measured in different units can be pooled. Each standard deviation is computed from years outside the marked breaks, so COVID does not set the scale. Every pair gets equal total weight, so monthly pairs (about 120 points) do not swamp annual ones (about 10).

**Hong Kong**

| Category | Indicator as used | Worse when | Yearly change |
| :---- | :---- | :---- | :---- |
| Safety | Overall reported crime, annual total | Higher | Percent |
| Economy | Unemployment rate, 3-month average | Higher | Points |
| Housing | Private domestic rental index | Rents rise faster | Change in 12-month rent increase, points |
| Transport | Fatal and serious road accidents | Higher | Percent |
| Environment | NO2 and PM10, monthly mean across general stations running since 2005 | Higher | Percent, averaged across the two pollutants |
| Health | Median wait for stable new specialist cases, averaged over the cluster and specialty pairs reported every quarter since 2015 | Longer | Percent |
| Education | Share of day-school HKDSE candidates meeting entrance requirements | Lower | Points, sign reversed |
| Cost of Living | Composite CPI without the housing section (which holds rent), using C\&SD's published section weights | Prices rise faster | Change in 12-month inflation, points |

**New York City**

| Category | Indicator as used | Worse when | Yearly change |
| :---- | :---- | :---- | :---- |
| Safety | Felony complaints | Higher | Percent |
| Economy | Unemployment rate | Higher | Points |
| Housing | People in DHS shelters, monthly average | Higher | Percent |
| Transport | Subway on-time performance | Lower | Points, sign reversed |
| Environment | PM2.5, monthly mean of daily readings across the five boroughs | Higher | Percent |
| Health | Deaths of city residents | Higher | Percent |
| Education | Four-year graduation rate | Lower | Points, sign reversed |
| Cost of Living | CPI all items less shelter, NY metro | Prices rise faster | Change in 12-month inflation, points |

**London**

| Category | Indicator as used | Worse when | Yearly change |
| :---- | :---- | :---- | :---- |
| Safety | Recorded crime, all offences | Higher | Percent |
| Economy | Unemployment rate, rolling 3 months | Higher | Points |
| Housing | Private rents index | Rents rise faster | Change in 12-month rent increase, points |
| Transport | Killed or seriously injured, severity-adjusted | Higher | Percent |
| Environment | NO2, monthly mean of Marylebone Road and Bloomsbury | Higher | Percent |
| Health | Share of the waiting list waiting under 18 weeks | Lower | Points, sign reversed |
| Education | Attainment 8 average score | Lower | Points, sign reversed |
| Cost of Living | CPI 12-month rate, UK | Higher | Points |

All other backups are worse when higher (price backups, when prices rise faster) and follow the same rules.