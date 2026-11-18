# Data card

| Field | Value |
| :-- | :-- |
| Name | Measuring What Matters: monthly attention and official series for three cities |
| Version | Built 2026-11-18T09:20:01Z (UTC) |
| Author | Cayden Auyang, Pomfret School. Produced by an AI agent run (Claude Code, model `claude-fable-5-2`) following his pre-registered plan. [CAYDEN TO CONFIRM: his own role in the question, codebook, design and interpretation] |
| Cities | Hong Kong, New York City, London |
| Categories | Safety, Economy, Housing, Transport, Environment, Health, Education, Cost of Living (compared with official data). Governance, Culture, Technology, Community (attention only). |
| Time span | News 2015-02 to 2026-10. Search 2004-01 to 2026-10. Official series from 2004 or earlier where the source allows, to 2026. |
| Unit | One row per city, category and month (attention). One row per series and period (official). |

## Sources

- **News:** GDELT Global Knowledge Graph 2.0, queried on BigQuery (3.29 TB billed in total, about $20.57). 6,363,992 records from 68 listed outlets. 2,466,900 articles left after the city filters and duplicate removal.
- **Search:** Google Trends, downloaded from the website as CSV files. 9 requests. Each of the nine requests was downloaded 2 times: on the evening of November 17 and again after local midnight on November 18.
- **Official statistics:** government and official bodies in each city. Addresses for every series are in `official_series_meta.json`.

## How the news shares were made

1. Outlets: a fixed main panel per city (3 in Hong Kong, 3 in New York, 15 borough papers in London), set before any data were pulled.
2. City filter: Hong Kong articles must carry a Hong Kong location tag. New York articles must carry a city or borough tag. London papers' national wire stories are dropped.
3. Sample: a seeded random draw of up to 333 articles per outlet per month in Hong Kong and New York and up to 66 per paper per month in London. 435,201 items were sampled. 6,117 had nothing for the model to read and were left out.
4. Labels: 429,081 items were labeled by `claude-haiku-5-5` (Anthropic API), 50 items per request, with the revised prompt (`news-v2`) in `labeling_card.md`. Because revised categories passed the retest, every article was labeled a second time on November 18 with the revised prompt, by the same model with the same settings (429,081 items, $27.87, 35 minutes). Every news number in the results rests on this second set of labels. The first validation test, the headline check and the consistency checks were run on the first set of labels. The AI-written notes on causes and events were read from samples drawn under the first labels. The two sets give the same category for these shares of articles: Hong Kong 85% (kappa 0.82), New York 89% (kappa 0.87), London 89% (kappa 0.87). The model read the headline words in each article's web address plus GDELT's theme tags. Cost: about $55.18 in total, $6.273e-05 per item in the cost test.
5. Shares: each category's share per outlet per month, averaged across outlets with equal weights. `neg_share` counts only articles labeled with negative tone.

## Validation

- Second coder: `gemini-3.5-flash-lite` (Google Gemini API), blind to the first coder, reading each article's real headline and opening lines from the live page or the Internet Archive, or the stored headline alone where no page could be read. The blind second coder ran on November 18 after its daily quota reset and labeled 898 validation items. It re-labeled 50 items in a fresh request.
- Third pass: `gemini-3.1-flash-lite`, same text.
- Status of the numbers below: final.

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

- First coder against a larger model of the same family (`claude-sonnet-5-5`) on 300 items: kappa 0.81.
- Headline check (2020 onward, same model): labels from address words plus theme tags against labels from the real stored headline. Hong Kong items with headline words: kappa 0.80. Hong Kong items with theme tags alone: kappa 0.42. Theme-tag-only labels agreed with real-headline labels at kappa 0.42, below 0.61. HK China News Agency and Oriental Daily, whose addresses were number-only before 2020, are left out of 2015 to 2019. Hong Kong's news series for those years rests on the South China Morning Post alone.

This is agreement between AI coders. It is not a check against a human reader.

## Known limits

- Theme-tag-only labels are weak. Outlets with number-only web addresses are affected most.
- GDELT's Hong Kong coverage leans on a few outlets. The London panel is borough papers with no citywide outlet. GDELT rarely tags the Bronx.
- The South China Morning Post's site challenged automated requests, so its validation items rest on headlines alone and only from 2020.
- London has no Health series. New York's Health series starts in 2020.
- Google Trends values come from a sample of searches and change between downloads.
- Break periods (COVID, method changes, real events) are flagged, not removed.

## Files, columns and checks

See `codebook.md`. Shares in `news_attention_monthly.csv` sum to 1 across the thirteen labels for every city, month and variant.

[CAYDEN TO CONFIRM: license for the dataset]
