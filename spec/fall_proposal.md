**Independent Study Proposal**

*Pomfret School \| For Fall 2026-27*

**STUDENT NAME: Cayden Auyang**

**MENTOR TEACHER(S): Mr. Qua, Mr. Lake**

**PROJECT TITLE / COURSE NAME: Measuring What Matters: A Comparative Analysis of Formal and Informal Signals in Identifying Urban Social Problems**

# **Pre-Submission Checklist**

Please review the following checklist to make sure that you have met all of the requirements before submitting your proposal. All elements must be completed before submitting to be eligible for the IS.    

**\[X\]** I have spoken with my advisor. My advisor agrees that I am ready for the level of organization and self-direction that independent study requires.

**\[X\]** I have spoken to my mentor teacher, shown them my proposal, and they have agreed to be my mentor.

**\[X\]** I have spoken with my college counselor, and they agree that my proposal is a good fit for my overall academic program.

**Select the box below that applies to this IS:**

**\[X\]** This independent study is my 6th course, and I do not require it to fulfill any graduation requirements within the 7 academic departments. My other 5 courses are core academic courses, so I do not need core academic department head approval.

**\[ \]** This independent study is one of my 5 core academic courses, so I have spoken to the department head, shown them my proposal, and received approval for this to receive department credit.

**\[ \]** This independent study will fulfill my art or well-being requirement. I have spoken to the department head, shown them my proposal, and received approval for this to receive art or well-being credit.

# **Project Description**

This independent study investigates a question at the intersection of social science methodology and civic technology: when a city's problems get better or worse, does public attention follow, and what does it mean when the two disagree? Governments measure problems through official statistics such as crime rates, unemployment, rents, air pollution, and hospital waiting times. Journalists and residents register them differently, through what local news covers and what people search for and post about. That informal signal is scattered across outlets and platforms with no common scale, so it must first be modeled into a form that can be compared with the official numbers.

The central research question has three parts. First, can scattered informal signal be turned into a defensible monthly measure of public attention to each problem in a city? Second, over the past two decades, does that attention rise and fall with the official measure of the same problem, which one moves first, and does attention react more strongly when conditions worsen than when they improve? Third, where do the two stay disconnected, and what does that reveal about how each system measures reality?

I will study Hong Kong, New York City, and London, three cities of similar population with very different political and media systems, using Hong Kong as the pilot. Problems are sorted into the twelve civic dimensions used by OurCityHealth. Eight of them (Safety, Economy, Housing, Transport, Environment, Health, Education, and Cost of Living) have official statistics. For those, I will compare official data from about 2005 to 2026 with local news attention measured through GDELT (2015 to 2026\) and resident search interest from Google Trends (2004 to 2026). The other four (Governance, Culture, Technology, and Community) have no official statistic, so I will report what the informal signal shows on its own. A current-year snapshot of social media (YouTube, X, Threads, and LIHKG in Hong Kong) adds what residents are saying now. The output is a research paper, a public dataset, and a practical framework others could apply to new cities.

# **Rationale and Connection to My Existing Work**

I run OurCityHealth, a civic intelligence API platform that aggregates signals about urban conditions for researchers and builders. The platform rests on an assumption I share with most of the civic-tech field: that news and online discussion tell you something real about how a city is doing. I have never tested whether that attention moves with official measures of the same problems, runs ahead of them, or drifts away from them. Official statistics have blind spots of their own, so this independent study treats both as imperfect measures and asks when, and why, they disagree. Testing that across three cities and two decades is the first step toward knowing when each signal can be trusted.

Beyond OurCityHealth, this project develops research and quantitative methodology skills that are central to my intended college trajectory and to my work with the Civic AI Club at Pomfret. Producing a full-length research paper with original methodology and primary data analysis is a level of rigor that Pomfret's regular course offerings do not require, and that I believe I am ready for. After the term, I plan to submit the paper to a peer-reviewed journal for student research and publish the dataset alongside it.

# **Resources and Materials**

No specialized campus spaces are required. I will use the library for academic database access (JSTOR, Academic Search Complete) and my own laptop for data collection, analysis, and writing. All data sources are publicly accessible: government statistics portals, the GDELT news database through Google BigQuery, Google Trends, and public social media posts. Query and AI-labeling costs are expected to stay under \$300 in total and will be covered personally.

# **Time Commitment**

This project will require approximately 60 to 70 hours of directed academic effort over the trimester. This is above the 45-hour guideline for a typical Pomfret course, and the overage is intentional. The most demanding parts are assembling 24 main official data series, plus backups, from three different statistical systems, building the pipeline that measures news and search attention month by month, and validating the AI labels against my own hand-coding before any comparison is made. A full draft of the paper is the end-of-term deliverable; revising it for journal submission will happen after the term and is not counted in these hours.

I am willing to accept this above-baseline workload because the project develops research and quantitative methodology skills that are central to my college trajectory and overlap substantially with work I am already doing through OurCityHealth and the Civic AI Club. If my mentors or advisor believe the scope should be reduced to better match the 45-hour standard, I would first drop the optional pre-2015 news extension and the social media snapshot, and then reduce the number of cities.

* Methodology design and source inventory: \~12 hours

* Official data assembly and attention pipeline across three cities: \~22 hours

* Validation and time-series analysis: \~16 hours

* Final paper, framework document, and presentation preparation: \~12 hours

# **Anticipated Challenges**

The single largest methodological challenge is turning scattered informal signal into a fair measure of attention. Raw mention counts are misleading for three reasons: GDELT monitors more outlets every year, New York and London appear in global stories that have nothing to do with their residents' problems, and outlets differ in reach and editorial stance. I will measure each problem's share of a city's local coverage instead of raw counts, restrict news to outlets based in each city, and validate the AI labels against my own hand-coding before any comparison is made. A related risk is false correlation: two series that both trend upward for twenty years will correlate even if they are unrelated, so the analysis compares year-over-year changes and tests which series moves first.

A second challenge is data heterogeneity. Official statistics differ across the three cities in definition, frequency, and start date, and many changed their methods partway through the period. News coverage shifts too: several major Hong Kong outlets closed in 2021, and GDELT's current Hong Kong coverage leans heavily toward a few outlets. The methodology document handles this by marking each known break, treating the COVID years separately, and checking whether results hold with backup indicators.

A third challenge is scope discipline. I will impose checkpoints at weeks four, seven, and ten where I assess progress against the time budget. If I am significantly over budget at any checkpoint, I will reduce scope (first the pre-2015 news extension and the social media snapshot, then a city) rather than compress the analysis and writing phases. A smaller dataset with rigorous methodology and careful argument is more valuable than a sprawling dataset with a rushed final paper.

Finally, a note on AI. I will use AI in two ways. Inside the method, a language model will classify news articles and posts by problem category and tone; I will validate its labels against a sample I code by hand and report how closely they agree. Outside the method, AI will help with code, data cleaning, literature search, and drafting: I will outline or dictate each document, AI will turn that into prose, and I will edit the result. The research question, category definitions, index design, and interpretation of results are my own, and the midterm and end-of-term defenses are where I will demonstrate that. I will keep a log of AI use and include a disclosure statement in the final paper.

# **Midterm Checkpoint**

| Name of Learning Outcome | Weight | "I can…" Statement | Evidence of Learning |
| ----- | :---: | ----- | ----- |
| **Research Skills** | 30% | I can locate and critically evaluate both formal datasets (government statistical agencies, police and health authorities, municipal open-data portals, peer-reviewed studies) and informal data sources (GDELT news data, Google Trends, social media platforms) relevant to a social science research question. | Annotated source inventory covering formal and informal sources (target: about 15). Each entry includes the source's methodology, sample population, data lag, known biases, and relevance to the project. |
| **Quantitative Methodology** | 40% | I can design a defensible methodology for turning unstructured informal signal into monthly measures of public attention that can be compared with official statistics over time. | Written methodology document defining the cities studied, the twelve-category codebook, the official indicators for each category, how news and search attention are measured, the data collection protocol, how the model's labels will be validated, and how the official and attention series will be compared. Approved by my mentors before data collection begins, then posted publicly as a pre-registration. |
| **Methods Defense** | 30% | I can explain and justify each methodological choice under questioning. | A check-in with my mentors walking through the methodology document and any pilot results, where they can question any decision in the model. |

# **End-of-Term Checkpoint**

| Name of Learning Outcome | Weight | "I can…" Statement | Evidence of Learning |
| ----- | :---: | ----- | ----- |
| **Research Skills** | 15% | I can extend and refine my source base to cover every study city, evaluating each new source with the same methodological rigor. | Updated annotated source inventory covering every study city (target: about 25), including all midterm sources. |
| **Quantitative Methodology** | 15% | I can apply my attention model and the official-data process consistently across heterogeneous sources to build comparable monthly series for every study city. | Complete dataset covering every study city and problem category, with official series and attention series side by side, accompanied by the code, spreadsheets, and documentation used to produce it. |
| **Validation and Analysis** | 30% | I can test whether my findings are trustworthy by checking the model against my own hand-coding and checking whether the results hold under different choices of indicators, time periods, and index design. | Agreement between the model's labels and my hand-coded sample for each category, plus checks with backup indicators, with and without the COVID years, and with alternative index choices, reported in a cited final research paper. AI-assisted drafting is disclosed, with my AI-use log attached. |
| **Applied Synthesis** | 20% | I can translate research findings into a practical framework that journalists, municipal staff, or civic technologists could use to combine both data types. | A "Civic Signal Framework" explaining how a non-researcher could apply the methodology to a new city, as a standalone document or a clearly separated final section of the paper. Builds directly on the research paper. |
| **Research Defense** | 20% | I can defend my research and its limits under open questioning. | A presentation of about 15 to 20 minutes to my mentors and a small audience, followed by an extended Q\&A in which my mentors can question any part of the paper or the model. |

