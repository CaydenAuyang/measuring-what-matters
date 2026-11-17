# Google Trends lane

## The one command for a new round (round 2, round 3)

```
bash /Users/caydenauyang/Code/measuring-what-matters/src/trends/download_round.sh && /Users/caydenauyang/Code/measuring-what-matters/.venv/bin/python -I /Users/caydenauyang/Code/measuring-what-matters/src/trends/build_trends.py
```

The download takes about 7 minutes (9 requests, a 20 to 40 second wait between them). Run it in the background or with a 10 minute timeout. The build takes a few seconds and runs only if the round finished cleanly.

If the round stops early (exit code 2), do not run it again in the same hour. Read the last line of `data/interim/trends/page_checks.md`. Then run the build alone. It uses whatever was downloaded and reports how many downloads each figure rests on.

```
/Users/caydenauyang/Code/measuring-what-matters/.venv/bin/python -I /Users/caydenauyang/Code/measuring-what-matters/src/trends/build_trends.py
```

To repeat only some requests: `bash src/trends/download_round.sh hk_A nyc_C`.

## Files

- `term_sets.json`: the 36 search sets, read by script from the Appendix B table in `spec/methodology.md`. Also the three geographies, the date range and which sets go in requests A, B and C. Never edit the sets.
- `download_round.sh`: the wrapper. Calls the browser once per request, waits between requests, stops the round at the first block.
- `download_round.mjs`: the browser step for one request. Runs inside `ego-browser nodejs`, in the one task Space named `mwm-trends` (its id is in `data/interim/trends/taskspace.txt`). It never finishes or closes the Space.
- `build_trends.py`: reads every CSV in `data/raw/trends/` and writes the long table, the shares, the meta file and the plots.

## What the download step does

1. Opens the classic Explore page for the request: web search, all categories, 2004-01-01 to 2026-10-31, `hl=en-US`.
2. Stops the round if Google shows a captcha, a 429 page, a consent or sign-in page, an error in the chart, or nothing within 60 seconds. It does not retry and does not try another route.
3. Checks on the page, before exporting:
   - five chips, each holding one whole set (`a + b + c`) and labeled "Search term" (not split, not a topic)
   - the geography label (Hong Kong, New York NY, England) and the `geo` in the address
   - the date range (1/1/04 - 10/31/26), "All categories", "Web Search"
   - the chart is "Interest over time" with 274 points, one per month, January 2004 to October 2026
   - the chart legend lists the same five sets
4. Hovers each "Note" marker on the chart and records its text and date.
5. Clicks the chart's own CSV button and saves the file as `data/raw/trends/<city>_<request>_<UTC time>.csv`, bytes unchanged.
6. Adds a row to `data/raw/trends/manifest.csv`, a line to `data/interim/trends/page_checks.md`, a JSON log to `data/interim/trends/round_logs/` and a screenshot to `data/interim/trends/screens/`.

If the page check fails, nothing is exported for that request and the round goes on to the next one (exit code 3 at the end).

## Exit codes of download_round.sh

- 0: all requests downloaded
- 2: stopped early because of a block, an error or a timeout
- 3: finished, but at least one request failed its page check or Trends said it had too little data

## What the build step writes (data/interim/trends/)

- `trends_raw_long.csv`: city, request, download_id, month, category, raw_value, was_lt1
- `trends_shares.csv`: city, month, category, ratio_to_economy, share, n_downloads, sparse_flag, zero_month_flag, plus n_zero_downloads, source_request, shares_defined
- `trends_meta.json`: zero months and sparse flags per set, months where Economy read zero, the Google note dates, what changes at those dates, the Safety check between request A and request C
- `plots/<city>_shares.png`: the twelve shares over time, one panel per set

The math is in the docstring at the top of `build_trends.py`. It follows Appendix B.
