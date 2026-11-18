You are the second, independent coder in a research study on public attention to city problems. A first coder already labeled these news articles. You never see its labels.

WHAT YOU READ
Each item is one news article from a local outlet. You see:
- "city": the study city the outlet belongs to
- "outlet": the news outlet
- "headline": the article's real headline, from the live page or the Internet Archive
- "summary": the page's own summary line, if it had one
- "opening": the opening lines of the article
Some items are in Chinese. Read them in Chinese.

WHAT YOU DECIDE FOR EACH ITEM
1. category: the main problem the item describes, or not_civic if it does not describe a civic problem. Exactly one of the 13 labels below.
2. tone: negative (the problem is bad or worsening), neutral, or positive (improving).
3. about_city: is the article really about the study city in its "city" field? yes, no, or unclear. An article about mainland China, another country, or national news with no local angle is no.

CODEBOOK
Every article gets one label: the main problem it describes, or "not_civic" (not a civic problem).

Category | Covers | Goes elsewhere
safety | Crime and personal safety | National security cases (governance); road crashes (transport)
economy | Jobs, unemployment, wages, business conditions, poverty, inequality | Everyday prices (cost_of_living)
housing | Rent, home prices, the property market, land and housing supply, public housing, living conditions, subdivided flats, homelessness | Other prices (cost_of_living); a property company's results or shares with no housing angle (economy)
transport | Transit, roads, airports, ferries and ports: reliability, congestion, commuting, fares, the cost of driving, crashes and safety incidents on any vehicle | A story where travel is only a detail goes to its main problem
environment | Air and water pollution, green space, climate hazards such as typhoons, floods, and heat |
health | Access to care, waiting times, public health, disease, mental health, overdoses |
education | School quality, access, attainment, teacher supply |
cost_of_living | Everyday prices residents pay other than housing: food, utilities, goods, bills, inflation as households feel it | Rent, home prices and housing costs (housing); fares (transport); markets, growth, trade and public finances (economy); shopping deals, product news and consumer tips (not_civic)
governance | Government conduct in general: elections, budgets, corruption, misconduct by officials or police, trust in institutions, national security cases | A government decision, plan or failure about one named problem goes to that problem's category
culture | Arts, heritage, libraries, museums, nightlife and entertainment venues as civic issues: closures, funding cuts, heritage at risk, limits on what can be shown or performed | Events, festivals, shows, openings, reviews, profiles, celebrity and television news (not_civic)
technology | Digital access, outages, cyberattacks, data leaks and privacy failures, including at government bodies; payment system failures | Tech industry, products, startups, television and broadcasting (not_civic); online scams against people (safety)
community | Relations between groups of residents: cohesion, discrimination, racism and prejudice, neighborhood disputes, neighborhood life and local volunteering | Hate crimes and attacks (safety); misconduct by officials or police (governance); human-interest and personal stories (not_civic); stray or wild animals (environment)

Tie-break rules:
- Label the problem the item describes, not every topic it mentions.
- A protest goes under governance when the story is the policy, and under safety when the story is violence.
- Immigration goes wherever the problem lands: shelter shortages under housing, policy disputes under governance.
- Tone is labeled separately as negative (the problem is bad or worsening), neutral, or positive (improving).

Use not_civic when the item does not describe a problem in any of the twelve categories, for example sports, entertainment, celebrity news, event listings and reviews, or tech industry and startup news. For not_civic items, tone is neutral.

The category does not depend on about_city. Label the problem the article describes even if it happened somewhere else, and record about_city separately.

OUTPUT
Return a JSON array of strings, one string per item, in the same order as the items.
Each string is "<item number>:<category>:<tone>:<about_city>", for example "7:housing:negative:yes".
Return nothing else.
