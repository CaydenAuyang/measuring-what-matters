"""Phase 2, steps 4-6: outlet assignment, city filter, duplicate removal, seeded sampling.

Usage: python src/gdelt_build.py art0      # union the yearly extracts and assign outlets
       python src/gdelt_build.py filter    # city filter + dedupe  -> mwm.articles
       python src/gdelt_build.py sample    # seeded samples        -> mwm.sample, local parquet + counts
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import bq_util, outlets

P = f"{bq_util.PROJECT}.{bq_util.DATASET}"
SEED = "mwm-2026-11-17"   # fixed random seed for every sample in this study

def outlet_case():
    lines = []
    for o in outlets.OUTLETS:
        doms = [o["domain"]] + o.get("extra_domains", [])
        rx = "(^|[.])(" + "|".join(d.replace(".", "[.]") for d in doms) + ")$"
        cond = f"REGEXP_CONTAINS(host, r'{rx}')"
        if o["key"] == "nowtv":
            cond = "host = 'news.now.com'"            # Now TV News only, not the finance portal
        if o["key"] == "appledaily":
            cond += " AND NOT STARTS_WITH(host, 'tw.')"  # the Taiwan edition is a different paper
        lines.append(f"    WHEN {cond} THEN '{o['key']}'")
    return "CASE\n" + "\n".join(lines) + "\n  END"

def city_case():
    return "CASE " + " ".join(f"WHEN outlet = '{o['key']}' THEN '{o['city']}'" for o in outlets.OUTLETS) + " END"

def art0():
    sql = f"""
WITH base AS (
  SELECT pdate, gkg_datetime, source, url, NET.HOST(url) AS host, V2Locations, V2Themes, V2Tone, TranslationInfo
  FROM `{P}.gkg_*`
), keyed AS (
  SELECT *, {outlet_case()} AS outlet FROM base
)
SELECT *, {city_case()} AS city, FORMAT_DATE('%Y-%m', pdate) AS month FROM keyed WHERE outlet IS NOT NULL"""
    bq_util.run(sql, "phase2", "art0: union years, assign outlets", destination="art0")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "art0": art0()


# ---------------------------------------------------------------------------------------------
# City filter, cleaning, duplicate removal (Appendix A)
# ---------------------------------------------------------------------------------------------
HK_TAG = r"(^|;)[0-9]#[^#;]*#HK#"     # any location entry whose country code is Hong Kong
NYC_TAG = (r"(^|;)3#(Manhattan|Brooklyn|Bronx|The Bronx|Queens|Staten Island|New York City|City Of New York|"
           r"Kings County|Queens County|Bronx County|Richmond County|New York County), New York, United States#")
# London national-news addresses (wire copy), dropped. Section names found in the address check.
LONDON_NATIONAL = r"/(national|national-news|uk_national_news|uk_national_entertainment|uk-world-news|national_news)/"
STANDARD_NATIONAL = r"standard[.]co[.]uk/news/(uk|world)/"
# Pages that are not articles (tag, author, topic and section index pages).
NON_ARTICLE = r"/(tag|tags|author|authors|topic|topics|category|search|about|contact|sitemap)(/|$)"

def filter_sql():
    main_keys = ",".join(f"'{k}'" for c in outlets.CITIES for k in outlets.MAIN_PANEL[c])
    return f"""
WITH a AS (
  SELECT city, outlet, pdate, month, url, V2Locations, V2Themes, V2Tone, TranslationInfo,
    REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(LOWER(url),
        r'^https?://(www[0-9]?[.]|m[.]|beta[.])?', ''), r':(80|443)/', '/'),
        r'[?&](utm_[a-z]+|home|mtc|icid|d_str)=[^&]*', ''), r'[/?&]+$', '') AS akey,
    REGEXP_EXTRACT(url, r'^https?://[^/]+(/[^?#]*)') AS path
  FROM `{P}.art0`
), f AS (
  SELECT * FROM a
  WHERE path IS NOT NULL AND path != '/'
    AND NOT REGEXP_CONTAINS(LOWER(path), r'{NON_ARTICLE}')
    AND (REGEXP_CONTAINS(REGEXP_EXTRACT(url, r'^https?://[^/]+(/.*)'), r'[0-9]') OR ARRAY_LENGTH(REGEXP_EXTRACT_ALL(REGEXP_EXTRACT(path, r'([^/]+)/?$'), r'[A-Za-z]{{2,}}')) >= 4
         OR REGEXP_CONTAINS(path, r'%[A-Fa-f0-9]{{2}}'))
    AND CASE city
      WHEN 'hk' THEN REGEXP_CONTAINS(V2Locations, r'{HK_TAG}')
      WHEN 'nyc' THEN REGEXP_CONTAINS(V2Locations, r'{NYC_TAG}')
      WHEN 'london' THEN NOT REGEXP_CONTAINS(LOWER(url), r'{LONDON_NATIONAL}') AND NOT REGEXP_CONTAINS(LOWER(url), r'{STANDARD_NATIONAL}')
    END
), d AS (   -- duplicates removed by address: keep the first time GDELT saw the address
  SELECT * EXCEPT(rn) FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY city, akey ORDER BY pdate, url) rn FROM f) WHERE rn = 1
), s AS (
  SELECT d.*, outlet IN ({main_keys}) AS is_main,
    FARM_FINGERPRINT(CONCAT('{SEED}|', akey)) AS rnd,
    -- headline words in the address, used to spot one story on several London papers
    IF(city = 'london',
       NULLIF(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(LOWER(REGEXP_EXTRACT(path, r'([^/]+)/?$')),
           r'^[0-9]+[.]', ''), r'[-_](1[-_])?[0-9]{{6,}}$|[.]html?$|-[ab][0-9]{{6,}}([.]html)?$', ''), r'[^a-z0-9]+', '-'), 'display'),
       NULL) AS slug_key
  FROM d
), k AS (
  SELECT s.*,
    -- London: a story on more than one paper in a month counts once (the copy with the lowest seeded hash)
    IF(city = 'london' AND slug_key IS NOT NULL AND ARRAY_LENGTH(SPLIT(slug_key, '-')) >= 3,
       ROW_NUMBER() OVER (PARTITION BY city, month, slug_key, is_main ORDER BY rnd) = 1, TRUE) AS keep_main,
    IF(city = 'london' AND slug_key IS NOT NULL AND ARRAY_LENGTH(SPLIT(slug_key, '-')) >= 3,
       ROW_NUMBER() OVER (PARTITION BY city, month, slug_key ORDER BY rnd) = 1, TRUE) AS keep_all
  FROM s
)
SELECT city, outlet, is_main, month, pdate, url, akey, slug_key, keep_main, keep_all, rnd,
  SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) AS gdelt_tone,
  IFNULL(REGEXP_EXTRACT(TranslationInfo, r'srclc:([a-z]+)'), 'eng') AS lang,
  (SELECT STRING_AGG(theme, ';' ORDER BY off) FROM (
      SELECT SPLIT(t, ',')[OFFSET(0)] AS theme, MIN(IFNULL(SAFE_CAST(SPLIT(t, ',')[SAFE_OFFSET(1)] AS INT64), 999999)) AS off
      FROM UNNEST(SPLIT(V2Themes, ';')) t WHERE t != '' GROUP BY 1 ORDER BY off LIMIT 40)) AS themes40,
  (SELECT COUNT(DISTINCT SPLIT(t, ',')[OFFSET(0)]) FROM UNNEST(SPLIT(V2Themes, ';')) t WHERE t != '') AS n_themes
FROM k"""

def do_filter():
    bq_util.run(filter_sql(), "phase2", "articles: city filter, cleaning, duplicate removal", destination="articles")

def sample_sql():
    cap_main = " ".join(f"WHEN '{c}' THEN {outlets.MAIN_CAP[c]}" for c in outlets.CITIES)
    cap_chk = " ".join(f"WHEN '{c}' THEN {outlets.CHECK_CAP[c]}" for c in outlets.CITIES)
    return f"""
WITH r AS (
  SELECT *,
    IF(is_main AND keep_main, ROW_NUMBER() OVER (PARTITION BY city, outlet, month, (is_main AND keep_main) ORDER BY rnd), NULL) AS rk_main,
    IF(keep_all, ROW_NUMBER() OVER (PARTITION BY city, outlet, month, keep_all ORDER BY rnd), NULL) AS rk_all
  FROM `{P}.articles`
)
SELECT *, (rk_main IS NOT NULL AND rk_main <= CASE city {cap_main} END) AS in_main,
          (rk_all IS NOT NULL AND rk_all <= CASE city {cap_chk} END) AS in_check
FROM r
WHERE (rk_main IS NOT NULL AND rk_main <= CASE city {cap_main} END) OR (rk_all IS NOT NULL AND rk_all <= CASE city {cap_chk} END)"""

def do_sample():
    import pandas as pd
    bq_util.run(sample_sql(), "phase2", "sample: seeded draw per outlet per month", destination="sample")
    out = os.path.join(bq_util.ROOT, "data", "interim", "gdelt")
    os.makedirs(out, exist_ok=True)
    df, _ = bq_util.run(f"SELECT city, outlet, is_main, month, pdate, url, akey, in_main, in_check, rk_main, rk_all, gdelt_tone, lang, themes40, n_themes FROM `{P}.sample`",
                        "phase2", "download sample", to_df=True)
    df["pdate"] = df["pdate"].astype(str)
    for c in ["in_main", "in_check", "is_main"]:
        df[c] = df[c].astype(bool)
    df.to_parquet(os.path.join(out, "sample.parquet"), index=False)
    cnt, _ = bq_util.run(f"""
SELECT a.city, a.outlet, a.is_main, a.month, COUNT(*) AS n_after_filter, COUNTIF(keep_main AND is_main) AS n_main_pool, COUNTIF(keep_all) AS n_all_pool
FROM `{P}.articles` a GROUP BY 1,2,3,4""", "phase2", "monthly counts after filter", to_df=True)
    smp = df.groupby(["city", "outlet", "month"]).agg(n_sample_main=("in_main", "sum"), n_sample_check=("in_check", "sum")).reset_index()
    raw, _ = bq_util.run(f"SELECT city, outlet, month, COUNT(*) AS n_gdelt_rows FROM `{P}.art0` GROUP BY 1,2,3", "phase2", "monthly raw counts", to_df=True)
    m = raw.merge(cnt.drop(columns=["is_main"]), on=["city", "outlet", "month"], how="left").merge(smp, on=["city", "outlet", "month"], how="left")
    num = ["n_after_filter", "n_main_pool", "n_all_pool", "n_sample_main", "n_sample_check"]
    m[num] = m[num].astype("float").fillna(0).astype(int)
    m["is_main"] = m.outlet.isin([k for c in outlets.CITIES for k in outlets.MAIN_PANEL[c]])
    m.sort_values(["city", "outlet", "month"]).to_csv(os.path.join(out, "monthly_counts.csv"), index=False)
    print("sample rows", len(df), "main", int(df.in_main.sum()), "check", int(df.in_check.sum()))
    print(df.groupby("city").agg(main=("in_main", "sum"), check=("in_check", "sum"), union=("url", "count")))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "filter": do_filter()
    if cmd == "sample": do_sample()
