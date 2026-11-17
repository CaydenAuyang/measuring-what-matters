"""Outlet lists from the methodology's Appendix A, exactly as pre-registered.

Each outlet: key, name, city, domain, panel ('main' or 'check'), number_only (addresses carry
no headline words), and an optional url_regex that an address must match (city sections).
SOURCE_NAMES (how GDELT spells each outlet in SourceCommonName) is filled in from
data/interim/gdelt/source_names.csv by src/gdelt_extract.py.
"""

OUTLETS = [
    # ---- Hong Kong ----
    dict(key="scmp", name="South China Morning Post", city="hk", domain="scmp.com", panel="main", number_only=False, url_regex=r"scmp\.com/news/hong-kong"),
    dict(key="orientaldaily", name="Oriental Daily", city="hk", domain="orientaldaily.on.cc", panel="main", number_only=False),
    dict(key="hkcna", name="HK China News Agency", city="hk", domain="hkcna.hk", panel="main", number_only=True),
    dict(key="nowtv", name="Now TV News", city="hk", domain="now.com", panel="check", number_only=True),
    dict(key="stheadline", name="Sing Tao Headline", city="hk", domain="stheadline.com", panel="check", number_only=False),
    dict(key="hkcd", name="HK Commercial Daily", city="hk", domain="hkcd.com", panel="check", number_only=True),
    dict(key="wenweipo", name="Wen Wei Po", city="hk", domain="wenweipo.com", panel="check", number_only=True),
    dict(key="mingpao", name="Ming Pao", city="hk", domain="mingpao.com", panel="check", number_only=False),
    dict(key="takungpao", name="Ta Kung Pao", city="hk", domain="takungpao.com.hk", panel="check", number_only=False),
    dict(key="hkej", name="HKEJ", city="hk", domain="hkej.com", panel="check", number_only=False),
    dict(key="hket", name="HKET", city="hk", domain="hket.com", panel="check", number_only=False),
    dict(key="thestandard", name="The Standard", city="hk", domain="thestandard.com.hk", panel="check", number_only=False),
    dict(key="rthk", name="RTHK", city="hk", domain="rthk.hk", panel="check", number_only=False),
    dict(key="hk01", name="HK01", city="hk", domain="hk01.com", panel="check", number_only=False),
    dict(key="ejinsight", name="EJ Insight", city="hk", domain="ejinsight.com", panel="check", number_only=False),
    dict(key="inmedia", name="InMedia", city="hk", domain="inmediahk.net", panel="check", number_only=False),
    dict(key="hkfp", name="Hong Kong Free Press", city="hk", domain="hongkongfp.com", panel="check", number_only=False),
    dict(key="standnews", name="Stand News", city="hk", domain="thestandnews.com", panel="check", number_only=False),
    dict(key="appledaily", name="Apple Daily", city="hk", domain="appledaily.com", panel="check", number_only=False),
    dict(key="tvb", name="TVB News", city="hk", domain="tvb.com", panel="check", number_only=False),
    dict(key="metroradio", name="Metro Radio", city="hk", domain="metrohk.com.hk", panel="check", number_only=False),
    dict(key="am730", name="am730", city="hk", domain="am730.com.hk", panel="check", number_only=False),
    dict(key="chinadailyhk", name="China Daily Hong Kong", city="hk", domain="chinadailyhk.com", panel="check", number_only=False),
    dict(key="bastillepost", name="Bastille Post", city="hk", domain="bastillepost.com", panel="check", number_only=False),
    # ---- New York City ----
    dict(key="nydailynews", name="Daily News", city="nyc", domain="nydailynews.com", panel="main", number_only=False),
    dict(key="nbcnewyork", name="NBC New York", city="nyc", domain="nbcnewyork.com", panel="main", number_only=False),
    dict(key="gothamist", name="Gothamist", city="nyc", domain="gothamist.com", panel="main", number_only=False),
    dict(key="nypost", name="New York Post", city="nyc", domain="nypost.com", panel="check", number_only=False),
    dict(key="amny", name="amNewYork", city="nyc", domain="amny.com", panel="check", number_only=False),
    dict(key="abc7ny", name="ABC7 New York", city="nyc", domain="abc7ny.com", panel="check", number_only=False),
    dict(key="pix11", name="PIX11", city="nyc", domain="pix11.com", panel="check", number_only=False),
    dict(key="ny1", name="NY1", city="nyc", domain="ny1.com", panel="check", number_only=False),
    dict(key="silive", name="Staten Island Advance", city="nyc", domain="silive.com", panel="check", number_only=False),
    dict(key="brooklyneagle", name="Brooklyn Eagle", city="nyc", domain="brooklyneagle.com", panel="check", number_only=False),
    dict(key="brooklynpaper", name="Brooklyn Paper", city="nyc", domain="brooklynpaper.com", panel="check", number_only=False),
    dict(key="qns", name="QNS", city="nyc", domain="qns.com", panel="check", number_only=False),
    dict(key="timesledger", name="TimesLedger", city="nyc", domain="timesledger.com", panel="check", number_only=False),
    dict(key="bkreader", name="BK Reader", city="nyc", domain="bkreader.com", panel="check", number_only=False),
    dict(key="riverdalepress", name="Riverdale Press", city="nyc", domain="riverdalepress.com", panel="check", number_only=False),
    dict(key="citylimits", name="City Limits", city="nyc", domain="citylimits.org", panel="check", number_only=False),
    dict(key="thecity", name="THE CITY", city="nyc", domain="thecity.nyc", panel="check", number_only=False),
    dict(key="wnyc", name="WNYC", city="nyc", domain="wnyc.org", panel="check", number_only=False),
    dict(key="nytimes", name="New York Times, N.Y. region section", city="nyc", domain="nytimes.com", panel="check", number_only=False, url_regex=r"nytimes\.com/.*/nyregion/|nytimes\.com/nyregion/"),
    dict(key="cbsnewyork", name="CBS New York", city="nyc", domain="cbsnews.com", panel="check", number_only=False, url_regex=r"cbsnews\.com/newyork|newyork\.cbslocal\.com", extra_domains=["cbslocal.com"]),
    # ---- London ----
    dict(key="newsshopper", name="News Shopper", city="london", domain="newsshopper.co.uk", panel="main", number_only=False),
    dict(key="wandsworthguardian", name="Wandsworth Guardian", city="london", domain="wandsworthguardian.co.uk", panel="main", number_only=False),
    dict(key="guardianseries", name="Guardian Series", city="london", domain="guardian-series.co.uk", panel="main", number_only=False),
    dict(key="richmondtwickenham", name="Richmond and Twickenham Times", city="london", domain="richmondandtwickenhamtimes.co.uk", panel="main", number_only=False),
    dict(key="timesseries", name="Times Series", city="london", domain="times-series.co.uk", panel="main", number_only=False),
    dict(key="harrowtimes", name="Harrow Times", city="london", domain="harrowtimes.co.uk", panel="main", number_only=False),
    dict(key="ealingtimes", name="Ealing Times", city="london", domain="ealingtimes.co.uk", panel="main", number_only=False),
    dict(key="enfieldindependent", name="Enfield Independent", city="london", domain="enfieldindependent.co.uk", panel="main", number_only=False),
    dict(key="hamhigh", name="Ham & High", city="london", domain="hamhigh.co.uk", panel="main", number_only=False),
    dict(key="romfordrecorder", name="Romford Recorder", city="london", domain="romfordrecorder.co.uk", panel="main", number_only=False),
    dict(key="ilfordrecorder", name="Ilford Recorder", city="london", domain="ilfordrecorder.co.uk", panel="main", number_only=False),
    dict(key="islingtongazette", name="Islington Gazette", city="london", domain="islingtongazette.co.uk", panel="main", number_only=False),
    dict(key="hackneygazette", name="Hackney Gazette", city="london", domain="hackneygazette.co.uk", panel="main", number_only=False),
    dict(key="kilburntimes", name="Kilburn Times", city="london", domain="kilburntimes.co.uk", panel="main", number_only=False),
    dict(key="eastlondonadvertiser", name="East London Advertiser", city="london", domain="eastlondonadvertiser.co.uk", panel="main", number_only=False),
    dict(key="standard", name="Evening Standard", city="london", domain="standard.co.uk", panel="check", number_only=False),
    dict(key="thisislocallondon", name="This Is Local London", city="london", domain="thisislocallondon.co.uk", panel="check", number_only=False),
    dict(key="mylondon", name="MyLondon", city="london", domain="mylondon.news", panel="check", number_only=False),
    dict(key="londonnow", name="London Now", city="london", domain="london-now.co.uk", panel="check", number_only=False),
    dict(key="getwestlondon", name="Get West London", city="london", domain="getwestlondon.co.uk", panel="check", number_only=False),
    dict(key="croydonguardian", name="Croydon Guardian", city="london", domain="croydonguardian.co.uk", panel="check", number_only=False),
    dict(key="croydonadvertiser", name="Croydon Advertiser", city="london", domain="croydonadvertiser.co.uk", panel="check", number_only=False),
    dict(key="bbclondon", name="BBC London section", city="london", domain="bbc.co.uk", panel="check", number_only=False, url_regex=r"bbc\.(co\.uk|com)/news/uk-england-london", extra_domains=["bbc.com"]),
    dict(key="itvlondon", name="ITV London section", city="london", domain="itv.com", panel="check", number_only=False, url_regex=r"itv\.com/news/london"),
]

BY_KEY = {o["key"]: o for o in OUTLETS}
CITIES = ["hk", "nyc", "london"]
CITY_NAMES = {"hk": "Hong Kong", "nyc": "New York City", "london": "London"}
MAIN_PANEL = {c: [o["key"] for o in OUTLETS if o["city"] == c and o["panel"] == "main"] for c in CITIES}
ALL_LISTED = {c: [o["key"] for o in OUTLETS if o["city"] == c] for c in CITIES}

# Sample caps per outlet per month (Appendix A): 333 in Hong Kong and New York, 66 in London.
MAIN_CAP = {"hk": 333, "nyc": 333, "london": 66}
# "All listed outlets" check: the same 1,000-a-month city budget split equally over every listed outlet.
CHECK_CAP = {c: 1000 // len(ALL_LISTED[c]) for c in CITIES}

CATEGORIES = ["safety", "economy", "housing", "transport", "environment", "health", "education",
              "cost_of_living", "governance", "culture", "technology", "community"]
COMPARED = CATEGORIES[:8]
SIGNAL_ONLY = CATEGORIES[8:]
CATEGORY_NAMES = {"safety": "Safety", "economy": "Economy", "housing": "Housing", "transport": "Transport",
                  "environment": "Environment", "health": "Health", "education": "Education",
                  "cost_of_living": "Cost of Living", "governance": "Governance", "culture": "Culture",
                  "technology": "Technology", "community": "Community", "not_civic": "Not a civic problem"}

if __name__ == "__main__":
    for c in CITIES:
        print(c, "main:", len(MAIN_PANEL[c]), "listed:", len(ALL_LISTED[c]), "check cap:", CHECK_CAP[c])
