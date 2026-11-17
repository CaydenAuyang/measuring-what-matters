"""The codebook, word for word from spec/methodology.md, and the frozen labeling prompt."""

LABELS = ["safety", "economy", "housing", "transport", "environment", "health", "education",
          "cost_of_living", "governance", "culture", "technology", "community", "not_civic"]
TONES = ["negative", "neutral", "positive"]

CODEBOOK_TABLE = """Category | Covers | Goes elsewhere
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
community | Relations between residents: cohesion, discrimination, neighborhood life | Trust in government (governance)"""

TIE_BREAKS = """Tie-break rules:
- Label the problem the item describes, not every topic it mentions.
- A protest goes under governance when the story is the policy, and under safety when the story is violence.
- Immigration goes wherever the problem lands: shelter shortages under housing, policy disputes under governance.
- Tone is labeled separately as negative (the problem is bad or worsening), neutral, or positive (improving)."""

NOT_CIVIC_NOTE = ("Use not_civic when the item does not describe a problem in any of the twelve categories, for example "
                  "sports, entertainment, celebrity news, event listings and reviews, or tech industry and startup news. "
                  "For not_civic items, tone is neutral.")

PROMPT_VERSION = "news-v1"
SYSTEM_PROMPT = f"""You label local news items for a research study on public attention to city problems.

Each item is one article from a local news outlet. You do not see the article. You see only:
- "headline": the headline words found in the article's web address. This can be empty.
- "themes": topic tags that GDELT's software attached to the article, in the order they first appear in it.
When the headline is empty, decide from the themes alone.

Give every item exactly one category and one tone.

CODEBOOK
Every item gets one label: the main problem it describes, or "not_civic" (not a civic problem).

{CODEBOOK_TABLE}

{TIE_BREAKS}

{NOT_CIVIC_NOTE}

OUTPUT
Return a JSON array of strings, one string per item, in the same order as the items.
Each string is "<item number>:<category>:<tone>", for example "7:housing:negative".
<category> is one of the 13 labels. <tone> is negative, neutral or positive.
Return nothing else."""

RESPONSE_SCHEMA = {"type": "ARRAY", "items": {"type": "STRING"}}


def parse_label(s):
    """'7:housing:negative' -> (7, 'housing', 'negative'); raises ValueError if malformed."""
    n, cat, tone = [x.strip() for x in s.split(":")]
    if cat not in LABELS or tone not in TONES:
        raise ValueError(s)
    return int(n), cat, tone
