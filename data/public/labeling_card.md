# Labeling card

This card records the model and the prompt used to label every sampled news article.

The prompt has not changed since 2026-11-17T21:00:35Z. Two test runs, of 200 and 2,000 Hong Kong items, used it before the first full run. One earlier test with a different output instruction failed on a settings error and produced no labels. The model changed twice before the full run, for the reasons under "How the first coder was chosen". This version of the card was written at 2026-11-17T21:50:11Z. No index or result had been computed from any label at that point.

## First coder (labels every sampled article)

| Setting | Value |
| :-- | :-- |
| Provider and model | Anthropic API, Claude Haiku 5.5 |
| Exact model ID (frozen) | `claude-haiku-5-5`, as listed by the API key's model list on November 17, 2026 and as returned in each response's `model` field |
| Thinking and effort | Provider defaults: adaptive thinking, default effort. No sampling settings are sent. |
| Output | JSON array of strings, one per item: `<item number>:<category>:<tone>` |
| Items per request | 50, all from one city |
| Largest request | 23,856 input tokens in the first 2,000 items. Every request must stay under 100,000 tokens, and the runner stops if one does not. |
| Request type | Normal requests. No Message Batches job was used. |
| Prompt version | `news-v1` |
| SHA-256 of the system prompt | `5ca9781e7a0012e91f78cb8b940f49d5660fcf73947efbc7995cbdcb5f17be15` |
| Code | `src/codebook.py` (prompt), `src/labeler_claude.py` (runner), `src/textprep.py` (headline words from addresses) |

## The full run

| Measure | Value |
| :-- | :-- |
| Items labeled | 429,082 of 429,084 with something to read (2 could not be labeled) |
| Requests in the full run (after the first 2,000 items) | 8,567 |
| Largest request | 26,830 input tokens |
| Cost of the full run | $26.71 |
| Time | 27 minutes |
| Refusals | 0 |

## How the first coder was chosen

1. The plan was a small Gemini model through the Gemini API key. The first choice was `gemini-3.5-flash-lite`.
2. That key turned out to be on the provider's free tier. The daily request cap for that model was reached after 10,582 Hong Kong items.
3. Labeling restarted with `gemini-3.1-flash-lite`, which has its own daily quota. It reached 4,422 items.
4. Cayden then supplied an Anthropic API key and told the run to switch the first coder to Claude Haiku 5.5, to relabel everything so that one model labels every article, and to keep Gemini for the blind second coder.
5. Labeling restarted from zero with `claude-haiku-5-5`. The Gemini labels are not used in any index. They are kept as cross-model comparisons.

### Cost test on the first 2,000 items

The first 2,000 items were a seeded draw from round 1 across the three cities (663 Hong Kong, 657 New York, 680 London).

| Measure | Value |
| :-- | :-- |
| Requests | 50 |
| Input tokens | 824,908 |
| Output tokens (thinking included) | 85,939 |
| Cost | $0.1255 |
| Cost per item | $0.0000627 |
| Projected cost of the full sample (429,084 items) | $26.92 |

Prices used: $0.10 per million input tokens and $0.50 per million output tokens, the rate for prompts of 100,000 tokens or fewer. The projection is under the $100 cap, so the sample was not shrunk.

### Check against a larger model

Cayden's rule: compare Haiku 5.5 with Sonnet 5.5 (`claude-sonnet-5-5`) on 300 of the first 2,000 items. Stay on Haiku 5.5 if Cohen's kappa is 0.75 or higher.

The 300 items were six whole requests (two per city, chosen by seed), sent to Sonnet 5.5 exactly as they had been sent to Haiku 5.5.

| Measure | Value |
| :-- | :-- |
| Items | 300 |
| Category agreement | 83.3% |
| Cohen's kappa, category | 0.805 |
| Kappa by city | Hong Kong 0.83, New York 0.77, London 0.81 |
| Kappa, items with headline words (n = 241) | 0.80 |
| Kappa, items with theme tags alone (n = 59) | 0.81 |
| Cohen's kappa, tone | 0.629 |
| Cost of the Sonnet 5.5 requests | $0.27 |
| Decision | Stay on Haiku 5.5 |

Tone agreement is lower than category agreement. The negative-tone check in the analysis should be read with that in mind.

### Earlier repeat tests with the Gemini models (same 2,000 Hong Kong items)

| Comparison | Category agreement | Cohen's kappa |
| :-- | :-- | :-- |
| gemini-3.5-flash-lite, 25 per request, against itself at 100 per request | 72.4% | 0.68 (0.76 with headline words, 0.62 with theme tags alone) |
| gemini-3.5-flash-lite at 25 per request against gemini-3.1-flash-lite at 400 per request | 71.2% | 0.66 |
| gemini-3.5-flash-lite at 100 per request against gemini-3.1-flash-lite at 400 per request | 75.8% | 0.72 |

## Rounds

Items are labeled in rounds. Each round adds the same number of articles for every outlet and month, so the sample is even across outlets and months wherever a run stops. Rank caps per outlet per month (Hong Kong and New York / London): round 1: 30 / 6. Round 2: 60 / 12. Round 3: 100 / 20. Round 4: 150 / 30. Round 5: 220 / 44. Round 6: 333 / 66, the full pre-registered sample. Only complete rounds are used. The check-list outlets are labeled in two further rounds.

## What the model reads

The same inputs in every year from 2015 to 2026:

1. The city and outlet name.
2. Headline words found in the article's web address. Encoded Chinese headlines are decoded. If the address is number-only, this field is empty.
3. GDELT's theme tags for the article, in order of first appearance, up to the first 30 different tags.

The model never sees the article text, the stored page title, or GDELT's tone score.

Items with no headline words and no theme tags have nothing to read. They are marked `no_input`, not labeled, and left out of the shares. Their count is reported.

## The system prompt, word for word

```
You label local news items for a research study on public attention to city problems.

Each item is one article from a local news outlet. You do not see the article. You see only:
- "headline": the headline words found in the article's web address. This can be empty.
- "themes": topic tags that GDELT's software attached to the article, in the order they first appear in it.
When the headline is empty, decide from the themes alone.

Give every item exactly one category and one tone.

CODEBOOK
Every item gets one label: the main problem it describes, or "not_civic" (not a civic problem).

Category | Covers | Goes elsewhere
safety | Crime and personal safety | National security cases (governance); road crashes (transport)
economy | Jobs, unemployment, wages, business conditions, poverty, inequality | Everyday prices (cost_of_living)
housing | Rent, home prices, supply, living conditions, subdivided flats, homelessness | Other prices (cost_of_living)
transport | Transit reliability, congestion, commuting, fares, road safety |
environment | Air and water pollution, green space, climate hazards such as typhoons, floods, and heat |
health | Access to care, waiting times, public health, disease, mental health, overdoses |
education | School quality, access, attainment, teacher supply |
cost_of_living | Everyday prices other than housing: food, utilities, goods | Rent and home prices (housing); fares (transport)
governance | Government decisions, trust in institutions, corruption, elections, national security cases |
culture | Arts, heritage, and nightlife as civic issues, such as venue closures or funding cuts | Event listings and reviews (not_civic)
technology | Digital access, outages, cyberattacks on public services, privacy | Tech industry and startup news (not_civic)
community | Relations between residents: cohesion, discrimination, neighborhood life | Trust in government (governance)

Tie-break rules:
- Label the problem the item describes, not every topic it mentions.
- A protest goes under governance when the story is the policy, and under safety when the story is violence.
- Immigration goes wherever the problem lands: shelter shortages under housing, policy disputes under governance.
- Tone is labeled separately as negative (the problem is bad or worsening), neutral, or positive (improving).

Use not_civic when the item does not describe a problem in any of the twelve categories, for example sports, entertainment, celebrity news, event listings and reviews, or tech industry and startup news. For not_civic items, tone is neutral.

OUTPUT
Return a JSON array of strings, one string per item, in the same order as the items.
Each string is "<item number>:<category>:<tone>", for example "7:housing:negative".
<category> is one of the 13 labels. <tone> is negative, neutral or positive.
Return nothing else.
```

## One line of each request

```
[7] city: Hong Kong | outlet: South China Morning Post | headline: <headline words or empty> | themes: <TAG; TAG; ...>
```

## What in the prompt is not from the methodology's codebook

The category table and the four tie-break rules are copied from `spec/methodology.md`. Three things were added to make the prompt usable. The description of the inputs. The sentence listing examples of "not a civic problem" (sports, entertainment and celebrity news were added to the two examples the codebook gives). The rule that a "not a civic problem" item gets neutral tone.

## Second coder and other passes

| Role | Model | What it reads |
| :-- | :-- | :-- |
| Second coder (validation, blind to the first coder) | Gemini, `gemini-3.5-flash-lite`, after its daily quota resets at about 03:07 Eastern time | The real headline and opening lines from the live page or the Internet Archive |
| Third pass (stand-in for the classmate's 150 items) | Gemini, `gemini-3.1-flash-lite` | The same real headline and opening lines |
| Re-label of 50 items | The second coder, in a fresh request | The same |

The second coder's instructions are in `src/coder2_prompt.md`. Settings for the second coder and the third pass: temperature 0, `thinkingLevel: minimal`, 25 items per request, JSON array output, run by `src/coder2_gemini.py`.

What the second coder reads, in order: the live page, then the Internet Archive copy. If neither can be read and the article is from 2020 on, it reads the real headline that GDELT stored, without opening lines. One site (scmp.com) answered automated requests with a challenge page. The run stopped using that site and did not fetch its pages from anywhere else, so its items use the stored headline.

The version fields the two providers list for the models named in this card are saved in `data/public/model_versions.json`.
