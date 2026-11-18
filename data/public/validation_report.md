# Validation report

Status: **final**. These numbers come from the blind second coder.

## What this report measures

Two AI language models labeled the same news articles without seeing each other's labels. The first coder read headline words from each article's web address plus GDELT's theme tags. The second coder, from a different model family, read the article's real headline and opening lines from the live page or the Internet Archive. Cohen's kappa measures how far they agree beyond chance.

This is agreement between two independent AI coders. It does not show that either coder matches a human reader. Nobody hand-coded any article in this run.

A category is analyzed in a city only if its kappa is at least 0.61. A category that falls short gets one revision of its wording and a fresh sample. If it still falls short it is dropped for that city.

## Hong Kong

- Items in the validation set: 299. Items used for the 0.61 rule: 228. 71 items come from outlet-years that the headline-check rule leaves out of the main series, so they are not part of the measure being analyzed. Kappa on all 299 items is 0.58.
- For 130 of these items the second coder read the real headline alone, taken from GDELT's stored page title, because no page could be read. One site (scmp.com) answered automated requests with a challenge page, and the run stopped using it and did not fetch its pages from anywhere else. Other pages were gone from both the live site and the Internet Archive.
- Pages tried: 601. Fetched: 432 (183 from the live site, 19 from the Internet Archive). Items that could not be fetched were replaced by the next item from the same category and city in a fixed random order.
- Overall kappa, weighted back to the full sample: 0.65 (95% interval 0.56 to 0.74). Unweighted: 0.58.
- Weighted agreement: 70%.
- Weights match the validation set to the measure on two margins: the first coder's category (in proportion to the labeled sample) and the outlet (in proportion to its weight in the index). Effective sample size after weighting: 105.
- Outlet weights follow the attention index, where each outlet counts equally in each month it has articles. South China Morning Post carries 46% of the index weight and is 49% of the validation items; HK China News Agency carries 27% of the index weight and is 12% of the validation items; Oriental Daily carries 27% of the index weight and is 39% of the validation items.
- Tone kappa (negative, neutral, positive): 0.51.
- Share of articles the second coder judged not really about the city: 15% weighted (11% of the validation items).

| Category | Kappa | 95% interval | First coder n | Second coder n | Result |
| :-- | --: | :-- | --: | --: | :-- |
| Safety | 0.72 | 0.44 to 0.90 | 15 | 17 | kept |
| Economy | 0.65 | 0.46 to 0.80 | 18 | 31 | kept |
| Housing | 0.46 | 0.25 to 0.71 | 15 | 24 | dropped |
| Transport | 0.36 | 0.13 to 0.68 | 16 | 11 | dropped |
| Environment | 0.79 | 0.59 to 0.96 | 17 | 19 | kept |
| Health | 0.76 | 0.58 to 0.90 | 20 | 19 | kept |
| Education | 0.82 | 0.63 to 0.94 | 17 | 12 | kept |
| Cost of Living | 0.44 | 0.13 to 0.69 | 15 | 5 | dropped |
| Governance | 0.73 | 0.55 to 0.85 | 24 | 36 | kept |
| Culture | 0.18 | 0.06 to 0.55 | 20 | 17 | dropped |
| Technology | 0.11 | 0.02 to 0.39 | 16 | 8 | dropped |
| Community | 0.36 | 0.14 to 0.68 | 15 | 9 | dropped |
| Not a civic problem | 0.62 | 0.37 to 0.82 | 20 | 20 | reported only |

Kept: Safety, Economy, Environment, Health, Education, Governance.
Dropped: Housing, Transport, Cost of Living, Culture, Technology, Community.

City filter error by outlet (share of validation items the second coder judged not about the city):

| Outlet | Items | Not about the city |
| :-- | --: | --: |
| South China Morning Post | 111 | 1% |
| Oriental Daily | 89 | 12% |
| HK China News Agency | 28 | 50% |

City filter error by the first coder's category:

| Category | Items | Not about the city |
| :-- | --: | --: |
| Safety | 15 | 20% |
| Economy | 18 | 11% |
| Housing | 15 | 7% |
| Transport | 16 | 31% |
| Environment | 17 | 0% |
| Health | 20 | 0% |
| Education | 17 | 0% |
| Cost of Living | 15 | 27% |
| Governance | 24 | 8% |
| Culture | 20 | 0% |
| Technology | 16 | 25% |
| Community | 15 | 0% |
| Not a civic problem | 20 | 25% |

Confusion table (rows: first coder, columns: second coder, counts in the validation set):

| | Safety | Econom | Housin | Transp | Enviro | Health | Educat | Cost o | Govern | Cultur | Techno | Commun | Not a  |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Safety | 10 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 1 |
| Economy | 0 | 13 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 2 | 0 | 0 |
| Housing | 0 | 2 | 12 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Transport | 2 | 2 | 0 | 8 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| Environment | 0 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 |
| Health | 0 | 2 | 1 | 0 | 0 | 14 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Education | 1 | 0 | 1 | 0 | 0 | 1 | 12 | 0 | 1 | 0 | 0 | 0 | 1 |
| Cost of Living | 1 | 5 | 3 | 1 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 |
| Governance | 1 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 18 | 0 | 1 | 0 | 1 |
| Culture | 0 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 4 | 10 | 0 | 1 | 1 |
| Technology | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 2 | 5 | 0 | 1 |
| Community | 1 | 1 | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 6 | 1 |
| Not a civic problem | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 2 | 0 | 1 | 12 |

Spread of the scored items. By outlet: South China Morning Post 111, Oriental Daily 89, HK China News Agency 28. By period: 2023-2026 133, 2019-2022 95. By language of the article: Chinese 117, English 111. By source of the text: stored headline only 130, live page 89, Internet Archive 9.

The same test under simpler rules. Three rules were set during the run, after provisional scores from the third pass had been seen and before the second coder ran: which items count, the stored-headline fallback, and the outlet weights. This table shows what the first two alternatives would give.

| Rule | Items | Overall kappa | Categories below 0.61 |
| :-- | --: | --: | :-- |
| Every validation item, weights by category only (the plan as written) | 299 | 0.56 | Safety, Economy, Housing, Transport, Cost of Living, Governance, Culture, Technology, Community |
| Items that remain in the main series, weights by category only | 228 | 0.64 | Housing, Transport, Cost of Living, Culture, Technology, Community |
| Items that remain in the main series, weights by category and outlet (the rule used) | 228 | 0.65 | Housing, Transport, Cost of Living, Culture, Technology, Community |

## New York City

- Items in the validation set: 300. Items used for the 0.61 rule: 300.
- For 1 of these items the second coder read the real headline alone, taken from GDELT's stored page title, because no page could be read. One site (scmp.com) answered automated requests with a challenge page, and the run stopped using it and did not fetch its pages from anywhere else. Other pages were gone from both the live site and the Internet Archive.
- Pages tried: 895. Fetched: 869 (865 from the live site, 3 from the Internet Archive). Items that could not be fetched were replaced by the next item from the same category and city in a fixed random order.
- Overall kappa, weighted back to the full sample: 0.76 (95% interval 0.69 to 0.82). Unweighted: 0.71.
- Weighted agreement: 81%.
- Weights match the validation set to the measure on two margins: the first coder's category (in proportion to the labeled sample) and the outlet (in proportion to its weight in the index). Effective sample size after weighting: 158.
- Outlet weights follow the attention index, where each outlet counts equally in each month it has articles. NBC New York carries 34% of the index weight and is 33% of the validation items; Daily News carries 34% of the index weight and is 32% of the validation items; Gothamist carries 32% of the index weight and is 35% of the validation items.
- Tone kappa (negative, neutral, positive): 0.44.
- Share of articles the second coder judged not really about the city: 8% weighted (6% of the validation items).

| Category | Kappa | 95% interval | First coder n | Second coder n | Result |
| :-- | --: | :-- | --: | --: | :-- |
| Safety | 0.80 | 0.69 to 0.89 | 31 | 42 | kept |
| Economy | 0.77 | 0.60 to 0.91 | 21 | 22 | kept |
| Housing | 0.98 | 0.95 to 1.00 | 22 | 24 | kept |
| Transport | 0.82 | 0.68 to 0.92 | 24 | 24 | kept |
| Environment | 0.65 | 0.45 to 0.87 | 21 | 20 | kept |
| Health | 0.86 | 0.75 to 0.95 | 23 | 27 | kept |
| Education | 0.74 | 0.56 to 0.89 | 21 | 14 | kept |
| Cost of Living | 0.67 | 0.46 to 0.82 | 20 | 10 | kept |
| Governance | 0.77 | 0.65 to 0.87 | 29 | 46 | kept |
| Culture | 0.20 | 0.10 to 0.44 | 20 | 18 | dropped |
| Technology | 0.68 | 0.44 to 0.95 | 20 | 16 | kept |
| Community | 0.46 | 0.26 to 0.68 | 21 | 15 | dropped |
| Not a civic problem | 0.72 | 0.57 to 0.86 | 27 | 22 | reported only |

Kept: Safety, Economy, Housing, Transport, Environment, Health, Education, Cost of Living, Governance, Technology.
Dropped: Culture, Community.

City filter error by outlet (share of validation items the second coder judged not about the city):

| Outlet | Items | Not about the city |
| :-- | --: | --: |
| Gothamist | 104 | 3% |
| NBC New York | 100 | 11% |
| Daily News | 96 | 4% |

City filter error by the first coder's category:

| Category | Items | Not about the city |
| :-- | --: | --: |
| Safety | 31 | 13% |
| Economy | 21 | 5% |
| Housing | 22 | 5% |
| Transport | 24 | 0% |
| Environment | 21 | 5% |
| Health | 23 | 4% |
| Education | 21 | 5% |
| Cost of Living | 20 | 5% |
| Governance | 29 | 7% |
| Culture | 20 | 5% |
| Technology | 20 | 10% |
| Community | 21 | 5% |
| Not a civic problem | 27 | 7% |

Confusion table (rows: first coder, columns: second coder, counts in the validation set):

| | Safety | Econom | Housin | Transp | Enviro | Health | Educat | Cost o | Govern | Cultur | Techno | Commun | Not a  |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Safety | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| Economy | 0 | 16 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 |
| Housing | 0 | 0 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Transport | 2 | 0 | 0 | 18 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 |
| Environment | 0 | 1 | 0 | 1 | 16 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| Health | 1 | 1 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Education | 2 | 0 | 0 | 1 | 0 | 3 | 13 | 0 | 0 | 0 | 1 | 1 | 0 |
| Cost of Living | 0 | 4 | 0 | 2 | 1 | 1 | 0 | 10 | 0 | 1 | 0 | 0 | 1 |
| Governance | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 |
| Culture | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 4 | 11 | 0 | 1 | 2 |
| Technology | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 15 | 0 | 0 |
| Community | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 1 | 0 | 10 | 0 |
| Not a civic problem | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 2 | 4 | 0 | 1 | 17 |

Spread of the scored items. By outlet: Gothamist 104, NBC New York 100, Daily News 96. By period: 2019-2022 103, 2023-2026 102, 2015-2018 95. By language of the article: English 300. By source of the text: live page 297, Internet Archive 2, stored headline only 1.

The same test under simpler rules. Three rules were set during the run, after provisional scores from the third pass had been seen and before the second coder ran: which items count, the stored-headline fallback, and the outlet weights. This table shows what the first two alternatives would give.

| Rule | Items | Overall kappa | Categories below 0.61 |
| :-- | --: | --: | :-- |
| Every validation item, weights by category only (the plan as written) | 300 | 0.76 | Culture, Community |
| Items that remain in the main series, weights by category only | 300 | 0.76 | Culture, Community |
| Items that remain in the main series, weights by category and outlet (the rule used) | 300 | 0.76 | Culture, Community |

## London

- Items in the validation set: 299. Items used for the 0.61 rule: 299.
- For 16 of these items the second coder read the real headline alone, taken from GDELT's stored page title, because no page could be read. One site (scmp.com) answered automated requests with a challenge page, and the run stopped using it and did not fetch its pages from anywhere else. Other pages were gone from both the live site and the Internet Archive.
- Pages tried: 617. Fetched: 509 (474 from the live site, 11 from the Internet Archive). Items that could not be fetched were replaced by the next item from the same category and city in a fixed random order.
- Overall kappa, weighted back to the full sample: 0.71 (95% interval 0.64 to 0.78). Unweighted: 0.67.
- Weighted agreement: 76%.
- Weights match the validation set to the measure on two margins: the first coder's category (in proportion to the labeled sample) and the outlet (in proportion to its weight in the index). Effective sample size after weighting: 164.
- Outlet weights follow the attention index, where each outlet counts equally in each month it has articles. Ealing Times carries 7% of the index weight and is 9% of the validation items; East London Advertiser carries 7% of the index weight and is 5% of the validation items; Enfield Independent carries 7% of the index weight and is 8% of the validation items; Guardian Series carries 7% of the index weight and is 8% of the validation items.
- Tone kappa (negative, neutral, positive): 0.68.
- Share of articles the second coder judged not really about the city: 9% weighted (10% of the validation items).

| Category | Kappa | 95% interval | First coder n | Second coder n | Result |
| :-- | --: | :-- | --: | --: | :-- |
| Safety | 0.83 | 0.73 to 0.92 | 28 | 42 | kept |
| Economy | 0.64 | 0.44 to 0.87 | 21 | 21 | kept |
| Housing | 0.81 | 0.67 to 0.93 | 21 | 24 | kept |
| Transport | 0.80 | 0.63 to 0.92 | 24 | 19 | kept |
| Environment | 0.61 | 0.44 to 0.80 | 22 | 26 | kept |
| Health | 0.81 | 0.64 to 0.94 | 23 | 17 | kept |
| Education | 0.88 | 0.75 to 0.96 | 21 | 16 | kept |
| Cost of Living | 0.41 | 0.20 to 0.80 | 20 | 18 | dropped |
| Governance | 0.52 | 0.32 to 0.71 | 24 | 30 | dropped |
| Culture | 0.20 | 0.07 to 0.48 | 21 | 13 | dropped |
| Technology | 0.45 | 0.22 to 0.87 | 20 | 16 | dropped |
| Community | 0.34 | 0.15 to 0.61 | 21 | 12 | dropped |
| Not a civic problem | 0.75 | 0.62 to 0.87 | 33 | 45 | reported only |

Kept: Safety, Economy, Housing, Transport, Environment, Health, Education.
Dropped: Cost of Living, Governance, Culture, Technology, Community.

City filter error by outlet (share of validation items the second coder judged not about the city):

| Outlet | Items | Not about the city |
| :-- | --: | --: |
| Harrow Times | 28 | 21% |
| Ealing Times | 26 | 15% |
| Wandsworth Guardian | 26 | 12% |
| Richmond and Twickenham Times | 25 | 4% |
| Enfield Independent | 24 | 17% |
| Guardian Series | 23 | 26% |
| Times Series | 22 | 9% |
| Islington Gazette | 19 | 0% |
| Ilford Recorder | 18 | 11% |
| News Shopper | 18 | 0% |
| Ham & High | 15 | 0% |
| Kilburn Times | 15 | 0% |
| Romford Recorder | 15 | 0% |
| East London Advertiser | 14 | 14% |
| Hackney Gazette | 11 | 9% |

City filter error by the first coder's category:

| Category | Items | Not about the city |
| :-- | --: | --: |
| Safety | 28 | 4% |
| Economy | 21 | 14% |
| Housing | 21 | 0% |
| Transport | 24 | 0% |
| Environment | 22 | 5% |
| Health | 23 | 0% |
| Education | 21 | 14% |
| Cost of Living | 20 | 25% |
| Governance | 24 | 8% |
| Culture | 21 | 5% |
| Technology | 20 | 30% |
| Community | 21 | 10% |
| Not a civic problem | 33 | 21% |

Confusion table (rows: first coder, columns: second coder, counts in the validation set):

| | Safety | Econom | Housin | Transp | Enviro | Health | Educat | Cost o | Govern | Cultur | Techno | Commun | Not a  |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Safety | 26 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Economy | 0 | 16 | 2 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 |
| Housing | 1 | 0 | 18 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| Transport | 3 | 0 | 0 | 17 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| Environment | 0 | 0 | 0 | 1 | 17 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| Health | 1 | 1 | 0 | 0 | 1 | 17 | 0 | 0 | 1 | 0 | 0 | 1 | 1 |
| Education | 0 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 2 | 0 | 0 | 3 |
| Cost of Living | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 13 | 2 | 0 | 0 | 0 | 2 |
| Governance | 4 | 1 | 2 | 0 | 1 | 0 | 0 | 0 | 13 | 0 | 1 | 0 | 2 |
| Culture | 1 | 1 | 2 | 0 | 1 | 0 | 0 | 0 | 3 | 8 | 0 | 1 | 4 |
| Technology | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 3 | 0 | 0 | 14 | 0 | 1 |
| Community | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 8 | 2 |
| Not a civic problem | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 3 | 0 | 1 | 26 |

Spread of the scored items. By outlet: Harrow Times 28, Ealing Times 26, Wandsworth Guardian 26, Richmond and Twickenham Times 25, Enfield Independent 24, Guardian Series 23, Times Series 22, Islington Gazette 19, News Shopper 18, Ilford Recorder 18, Ham & High 15, Kilburn Times 15, Romford Recorder 15, East London Advertiser 14, Hackney Gazette 11. By period: 2023-2026 118, 2019-2022 113, 2015-2018 68. By language of the article: English 299. By source of the text: live page 276, stored headline only 16, Internet Archive 7.

The same test under simpler rules. Three rules were set during the run, after provisional scores from the third pass had been seen and before the second coder ran: which items count, the stored-headline fallback, and the outlet weights. This table shows what the first two alternatives would give.

| Rule | Items | Overall kappa | Categories below 0.61 |
| :-- | --: | --: | :-- |
| Every validation item, weights by category only (the plan as written) | 299 | 0.72 | Environment, Cost of Living, Governance, Culture, Technology, Community |
| Items that remain in the main series, weights by category only | 299 | 0.72 | Environment, Cost of Living, Governance, Culture, Technology, Community |
| Items that remain in the main series, weights by category and outlet (the rule used) | 299 | 0.71 | Cost of Living, Governance, Culture, Technology, Community |

## Headline check (2020 onward)

GDELT stores real page titles only from 2020. For a sample of 2020 to 2026 articles, the first coder labeled each article twice: once from the real stored headline alone, and once the way every year is labeled (headline words in the web address plus theme tags). The table shows how well the two agree.

| City | Items with headline words in the address | Kappa | Items with theme tags alone | Kappa |
| :-- | --: | --: | --: | --: |
| Hong Kong | 1467 | 0.80 | 1026 | 0.42 |
| New York City | 900 | 0.79 | 0 | n/a |
| London | 898 | 0.84 | 2 | n/a |

Theme-tag-only labels agreed with real-headline labels at kappa 0.42, below 0.61. HK China News Agency and Oriental Daily, whose addresses were number-only before 2020, are left out of 2015 to 2019. Hong Kong's news series for those years rests on the South China Morning Post alone.

Some London papers had number-only addresses in 2015 and 2016: 41% of London's sampled items in 2015 and 15% in 2016 carry no headline words, against 0% in 2017. The rule in the methodology is written for outlets, and these papers have headline words in every later year, so they stay in. Their theme-tag-only labels in 2015 and 2016 should be read with the Hong Kong result above in mind.

## Consistency checks

- First coder against a larger model from the same family, same inputs, 300 items: kappa 0.81 on category (83% agreement), 0.63 on tone.
- Third pass (a different AI model reading the same real headlines and opening lines, in place of the classmate): 150 items, kappa 0.76 against the second coder and 0.64 against the first coder.
- Re-label (the second coder labels 50 of the same items again in a fresh request, in place of Cayden's two-week re-label): kappa 0.80.
- Earlier repeat tests with two other small models on 2,000 Hong Kong items (same inputs as the first coder; details in the labeling card): kappa 0.68 for one model against itself at a different request size, 0.66 to 0.72 between the two models.

## Optional human check

`deliverables/optional_hand_check_50.csv` holds 50 validation items with a blank label column. If Cayden fills it in, `src/score_hand_check.py` computes his kappa against both AI coders. It has not been filled in.
