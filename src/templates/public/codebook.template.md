# Codebook: every column of every file

City codes: `hk` Hong Kong, `nyc` New York City, `london` London.
Category codes: `safety`, `economy`, `housing`, `transport`, `environment`, `health`, `education`, `cost_of_living`, `governance`, `culture`, `technology`, `community`. In the news file, `not_civic` is the label for articles that describe no civic problem.

## news_attention_monthly.csv

| Column | Meaning |
| :-- | :-- |
| `city`, `month` | City code and month (YYYY-MM). |
| `category` | One of the twelve categories or `not_civic`. |
| `share` | The category's share of labeled articles, computed per outlet and averaged across outlets with equal weights. Between 0 and 1. |
| `neg_share` | Share of labeled articles that are in the category and have negative tone. |
| `n_items` | Labeled articles behind the month's shares. |
| `n_outlets` | Outlets with at least one labeled article that month. |
| `min_items_per_outlet` | The smallest outlet's article count that month. |
| `variant` | `main`: the pre-registered series after the headline-check rule. `main_no_exclusion`: every main-panel outlet in every year. `hk_no_hkcna`: Hong Kong without HK China News Agency. `london_no_seven`: London without the seven papers that jumped in volume. `all_listed`: every listed outlet. |
| `missing_main_outlets` | Main-panel outlets with no articles that month (the month is flagged, and the average uses the others). |

## search_attention_monthly.csv

| Column | Meaning |
| :-- | :-- |
| `city`, `month`, `category` | As above. Geography is Hong Kong, the New York media market, and England. |
| `ratio_to_economy` | The set's Trends value divided by the Economy set's value in the same request, averaged across downloads. |
| `share` | The set's ratio divided by the sum of the twelve ratios. The twelve shares sum to 1. |
| `n_downloads` | How many downloads the figure rests on. |
| `sparse_flag` | 1 if the set reads zero in more than 10% of months. Sparse sets are not tested but stay in the denominator. |
| `zero_month_flag` | 1 if the set read zero that month. |

## official_series.csv

| Column | Meaning |
| :-- | :-- |
| `city`, `category` | As above. |
| `role` | `main` or `backup` indicator. |
| `series_id`, `component`, `indicator_name` | Series identifier, component name where a series has more than one (for example NO2 and PM10), and a plain name. |
| `frequency` | `M` monthly, `Q` quarterly, `A` annual. |
| `period`, `period_end_date` | The period label and its last day. Rolling averages use the end month. School-year series use the year the school year ends. |
| `window_months` | Months each value covers. |
| `value`, `unit` | The level as published or as built. Never interpolated. |
| `worse_when` | `higher`, `lower`, or `faster` (prices and rents: the problem is how fast they rise). |
| `change_rule` | How the yearly change is computed: `pct_log` (100 times the natural log of the ratio), `points` (difference), `inflation_points` (change in the 12-month rate). |
| `break_flag`, `break_note` | 1 and a note where the methodology's breaks table or the source's own documentation marks a break. |
| `provisional` | 1 where the source marks recent values as provisional. |

## yearly_changes.csv

| Column | Meaning |
| :-- | :-- |
| `city`, `category` | As above. |
| `source` | `news` or `search`. |
| `freq` | Frequency of the official series the pair uses. |
| `period_end_month` | End month of the period (YYYY-MM). |
| `official_change_worse_positive` | Yearly change in the official series, signed so that positive means the problem got worse. |
| `attention_change_points` | Yearly change in the attention share, in percentage points. News changes are computed on a matched panel of outlets. |
| `official_change_sd`, `attention_change_sd` | The same changes divided by the pair's own standard deviation over periods outside the marked breaks. |
| `covid`, `brk_official`, `brk_attention` | True where the period falls in 2020 to 2022, in a marked break of the official series, or in a marked break of the attention series. |

## sample_sizes.csv and sample_sizes_by_city_month.csv

| Column | Meaning |
| :-- | :-- |
| `city`, `outlet`, `outlet_name`, `panel`, `month` | Outlet key and name, `main` or `check` list, month. |
| `n_gdelt_records` | Records GDELT holds for the outlet that month. |
| `n_after_city_filter_and_dedupe` | Articles left after the city filter, the article-page rule and duplicate removal. |
| `n_sampled_main_panel`, `n_sampled_all_outlets_check` | Articles drawn for the main series and for the all-listed-outlets check. |
| `n_labeled_main`, `n_labeled_check` | Articles with a label. |
| `n_sampled`, `n_labeled`, `outlets_with_articles` | City-month totals for the main panel (second file). |

## outlets.csv, search_term_sets.json

The pre-registered outlet lists (Appendix A) and search term sets (Appendix B).

## results.json

Every reported number. Top-level keys: `counts`, `validation`, `main` (the four pooled models), `h1_by_category`, `h1_by_city`, `pair_level`, `h3`, `leadlag`, `case_study`, `checks`, `verdicts`, `ranking`, `signal_only`, `synthetic_tests`, `tables`, `text`. Slopes are in standard deviations of attention change per standard deviation of official worsening.
