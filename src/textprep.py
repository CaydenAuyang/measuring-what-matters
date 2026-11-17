"""Turn a web address into the headline words it carries (if any). Used for every year, 2015 to 2026.

Number-only addresses return '' and the model then reads GDELT's theme tags alone.
"""
import re, hashlib
from urllib.parse import urlsplit, unquote

EXT = re.compile(r"\.(html?|php|shtml|ssf|aspx?|jsp)$", re.I)
CJK = re.compile(r"[㐀-鿿豈-﫿]")
STOP_SEGS = {"display", "index", "article", "articles", "news", "story", "content", "player", "detail"}

def item_id(akey: str) -> str:
    return hashlib.sha1(akey.encode("utf-8")).hexdigest()[:12]

def _clean_segment(seg: str) -> str:
    seg = unquote(seg, errors="ignore")
    seg = EXT.sub("", seg)
    seg = re.sub(r"^\d+\.", "", seg)                                   # Newsquest: 16277139.Headline_words
    seg = re.sub(r"-article-\d+\.\d+$", "", seg)                       # Daily News: -article-1.1400715
    seg = re.sub(r"-\d{8}-[a-z0-9]{20,}-story$", "", seg)              # Daily News: -20210922-<hash>-story
    seg = re.sub(r"-\d{8}-story$", "", seg)
    seg = re.sub(r"[-_]1[-_]\d{6,}$", "", seg)                         # Archant: _1_4038640 / -1-5685471
    seg = re.sub(r"-[ab]\d{6,}$", "", seg)                             # Evening Standard: -a3145846
    seg = re.sub(r"[-_]\d{6,}$", "", seg)                              # trailing numeric id
    seg = re.sub(r"^\d{6,}[-_]", "", seg)                              # leading numeric id
    seg = seg.replace("&#39;", "'")
    seg = re.sub(r"__\d+_+", " ", seg)                                 # Newsquest escaped punctuation ___39_
    seg = re.sub(r"[-_+.,:;|/\\　]+", " ", seg)
    toks = []
    for t in seg.split():
        if len(t) >= 20 and not CJK.search(t):      # hashes
            continue
        if re.fullmatch(r"[a-z0-9]{10,}", t) and re.search(r"\d", t) and re.search(r"[a-z]", t):
            continue
        toks.append(t)
    return " ".join(toks).strip()

def _score(text: str) -> int:
    latin = [t for t in text.split() if re.fullmatch(r"[A-Za-z][A-Za-z'’]+", t)]
    cjk = len(CJK.findall(text))
    return len(latin) + cjk // 2

def headline_words(url: str) -> str:
    """Return the headline words in a web address, or '' if the address carries none."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return ""
    segs = [s for s in parts.path.split("/") if s]
    best, best_score = "", 0
    for s in segs:
        c = _clean_segment(s)
        if c.lower() in STOP_SEGS:
            continue
        sc = _score(c)
        if sc >= best_score and sc > 0:
            best, best_score = c, sc
    latin = [t for t in best.split() if re.fullmatch(r"[A-Za-z][A-Za-z'’]+", t)]
    cjk = len(CJK.findall(best))
    if len(latin) >= 3 or cjk >= 4:
        return best[:200]
    return ""

def has_headline(url: str) -> bool:
    return headline_words(url) != ""

if __name__ == "__main__":
    tests = [
        "http://www.scmp.com/news/hong-kong/law-crime/article/1838335/internet-article-23-protesters-handed-150-hour-community",
        "http://orientaldaily.on.cc/cnt/china_world/20150724/00192_001.html",
        "http://orientaldaily.on.cc/content/%E7%94%A2%E7%B6%93/odn-20240831-0831_00202_001/4%E5%A4%A7%E5%85%A7%E9%8A%80%E3%80%8C%E7%9B%88%E3%80%8D%E5%AD%98%E6%8C%91%E6%88%B0",
        "http://www.hkcna.hk/docDetail.jsp?id=100684820&channel=100",
        "http://www.nydailynews.com/new-york/nyc-crime/ny-man-giving-food-in-queens-park-stabbed-20210922-j4plnb6rkzbghaa45bgi624tsu-story.html",
        "http://www.nydailynews.com/new-york/rep-grimm-lists-wrong-district-number-election-forms-article-1.1400715",
        "http://www.nbcnewyork.com/news/local/Winter-Weather-March-Storm-New-York-City-NY-NJ-Long-Island-294974681.html",
        "http://gothamist.com/2015/03/19/you_cant_have_these_animals.php",
        "http://www.newsshopper.co.uk/news/12942507.display/",
        "http://www.thisislocallondon.co.uk/news/16178400.Penge_teenager_jailed_for_slashing_homeless_woman_as_she___39_cowered_like_a_dog_under_a_sink__39_/",
        "http://www.hamhigh.co.uk:80/news/politics/boris_johnson_saves_golders_green_s_number_13_bus_after_call_from_mike_freer_1_4038640",
        "https://www.hamhigh.co.uk/news/haringey-council-free-school-meals-expanded-6919780",
        "https://www.standard.co.uk/news/politics/oliver-letwin-apologises-over-racist-1980s-riots-memo-a3145846.html",
        "https://news.mingpao.com/ins/instantnews/web_tc/article/20180724/s00001/1532416921490",
        "https://www.scmp.com/news/hong-kong/hong-kong-economy",
    ]
    for t in tests:
        print(repr(headline_words(t)), "<-", t[:90])
