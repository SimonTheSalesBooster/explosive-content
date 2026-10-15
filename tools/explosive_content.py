#!/usr/bin/env python3
"""Explosive Content: find the YouTube topics strangers watch.

For each keyword in keywords.json, searches YouTube
(relevance + view count), and keeps long-form videos whose views beat the
channel's subscriber count (views / subs = "explosion ratio"). A video that
reaches far beyond its own audience means the TOPIC pulls strangers in.

Output: <out>/<date>.json and <out>/latest.json
  - all qualifying outliers per keyword
  - top: best outlier per keyword, ranked, top 20 (one per keyword)

Read-only, stdlib only, YouTube Data API v3 (env YOUTUBE_API_KEY).
Quota: ~200 units per keyword (2 searches) + a few list calls = ~5,100/run.

Usage:
  explosive_content.py [--keywords keywords.json] [--out runs] [--top 20]
  explosive_content.py --selftest

Not in B2B sales? Set "topic_terms" and "off_topic_terms" in keywords.json
to your own market's words (the defaults below are for B2B selling).
"""
import json, os, re, sys, time, datetime, urllib.error, urllib.parse, urllib.request
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3/"
OWN_CHANNELS = set()    # filled from keywords.json "exclude_channels" (your own channels)
MIN_SUBS = 500          # below this the ratio is noise
MIN_VIEWS = 2000
MIN_SECONDS = 180       # long-form only, Shorts inflate ratios
PUBLISHED_AFTER = "2022-01-01T00:00:00Z"   # topics still hot, not 2016 relics
MIN_LIKE_RATE = 0.003   # organic videos get >=0.3% likes; promoted ads get views without likes
# On-topic check: the title must talk about selling, and not about jobs/drama.
SALES_TERMS = ("sale", "sell", "b2b", "prospect", "lead", "client", "customer", "deal", "clos",
               "pipeline", "cold", "outreach", "pric", "discount", "objection", "gtm", "go-to-market",
               "revenue", "discovery", "follow", "crm", "quota", "buyer", "conversion", "cro", "ghost", "negotiat")
OFF_TOPIC = ("interview", "recruiter", "job", "career", "drama", "resume", "salary", "real estate",
             "amazon fba", "dropshipping", "shopify", "ecommerce", "e-commerce", "car sales", "mlm", "crypto")


def load_key():
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        sys.exit("Set YOUTUBE_API_KEY (free key: see README, 'Get a free YouTube API key').")
    return key


def get(endpoint, **params):
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                time.sleep(0.5)
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(10 * (attempt + 1))   # rate limit burst, back off


def iso_seconds(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def qualifies(v):
    """v: dict with title, views, subs, seconds, hidden, channel_id. Returns reason or None."""
    t = v.get("title", "").lower()
    if not any(w in t for w in SALES_TERMS) or any(w in t + " " + v.get("channel", "").lower() for w in OFF_TOPIC):
        return "off topic"
    lang = v.get("lang", "")
    if (lang and not lang.startswith("en")) or re.search(r"[áéíóúñ¿¡àèçãõ]", t):
        return "not English"
    if v["views"] >= MIN_VIEWS and v.get("likes") is not None and v["likes"] / v["views"] < MIN_LIKE_RATE:
        return "likely paid ad (views without likes)"
    if v["channel_id"] in OWN_CHANNELS:
        return "own channel"
    if v["hidden"] or v["subs"] < MIN_SUBS:
        return "subs hidden or too small"
    if v["seconds"] < MIN_SECONDS:
        return "short"
    if v["views"] < MIN_VIEWS:
        return "too few views"
    if v["views"] <= v["subs"]:
        return "did not beat subs"
    return None


def chunks(xs, n=50):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def search_ids(key, q, order, cache):
    ck = f"{q}|{order}|{PUBLISHED_AFTER}"
    if ck not in cache:   # same-day reruns cost no quota
        res = get("search", part="id", q=q, type="video", maxResults=50, order=order,
                  relevanceLanguage="en", publishedAfter=PUBLISHED_AFTER, key=key)
        cache[ck] = [i["id"]["videoId"] for i in res.get("items", [])]
    return cache[ck]


def scan(key, keywords, out):
    cpath = out / f"search-cache-{datetime.date.today().isoformat()}.json"
    cpath.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(cpath.read_text()) if cpath.exists() else {}
    per_kw = {}
    try:
        for k in keywords:
            kw = k["kw"]
            ids = search_ids(key, kw, "relevance", cache) + search_ids(key, kw, "viewCount", cache)
            for alt in k.get("also", []):          # phrasing variants, view-count order only
                ids += search_ids(key, alt, "viewCount", cache)
            per_kw[kw] = list(dict.fromkeys(ids))
    finally:
        cpath.write_text(json.dumps(cache))
    all_ids = list(dict.fromkeys(i for ids in per_kw.values() for i in ids))
    videos = {}
    for c in chunks(all_ids):
        for it in get("videos", part="snippet,statistics,contentDetails", id=",".join(c), key=key).get("items", []):
            videos[it["id"]] = it
    ch_ids = list({v["snippet"]["channelId"] for v in videos.values()})
    channels = {}
    for c in chunks(ch_ids):
        for it in get("channels", part="statistics,snippet", id=",".join(c), key=key).get("items", []):
            channels[it["id"]] = it
    out = {}
    for k in keywords:
        kw = k["kw"]
        rows = []
        for vid in per_kw[kw]:
            v = videos.get(vid)
            if not v:
                continue
            ch = channels.get(v["snippet"]["channelId"], {})
            st = ch.get("statistics", {})
            rec = {
                "keyword": kw, "tag": k.get("tag", ""), "video_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "title": v["snippet"]["title"], "lang": v["snippet"].get("defaultAudioLanguage", ""), "channel": v["snippet"]["channelTitle"],
                "channel_id": v["snippet"]["channelId"],
                "published": v["snippet"]["publishedAt"][:10],
                "views": int(v.get("statistics", {}).get("viewCount", 0)),
                "likes": int(v["statistics"]["likeCount"]) if "likeCount" in v.get("statistics", {}) else None,
                "comments": int(v.get("statistics", {}).get("commentCount", 0)),
                "subs": int(st.get("subscriberCount", 0)),
                "hidden": bool(st.get("hiddenSubscriberCount")),
                "seconds": iso_seconds(v.get("contentDetails", {}).get("duration")),
            }
            if qualifies(rec):
                continue
            rec["ratio"] = round(rec["views"] / rec["subs"], 1)
            rows.append(rec)
        rows.sort(key=lambda r: r["ratio"], reverse=True)
        out[kw] = rows
    return out


def pick_top(per_kw, n):
    """Best outlier per keyword (a video counts once), ranked by ratio."""
    used, top = set(), []
    for kw, rows in per_kw.items():
        for r in rows:
            if r["video_id"] not in used:
                used.add(r["video_id"])
                top.append(dict(r, outliers_for_keyword=len(rows)))
                break
    top.sort(key=lambda r: r["ratio"], reverse=True)
    return top[:n]


STALE_DAYS = 35


def selftest():
    OWN_CHANNELS.add("MINE")
    base = dict(channel_id="X", hidden=False, seconds=600, title="How to close B2B deals")
    assert qualifies(dict(base, views=3000, subs=1000, title="How to ACE Your Recruiter Phone Screen Interview")) == "off topic"
    assert qualifies(dict(base, views=3000, subs=1000, title="How to Start a Tech Career in 2026")) == "off topic"
    assert qualifies(dict(base, views=3000, subs=1000)) is None          # Simon's example
    assert qualifies(dict(base, views=2500, subs=3000)) == "did not beat subs"
    assert qualifies(dict(base, views=3000, subs=100)) == "subs hidden or too small"
    assert qualifies(dict(base, views=3000, subs=1000, seconds=40)) == "short"
    assert qualifies(dict(base, views=3000, subs=1000, hidden=True)) == "subs hidden or too small"
    assert qualifies(dict(base, views=3000, subs=1000, channel_id="MINE")) == "own channel"
    assert qualifies(dict(base, views=3000, subs=1000, title="Cómo prospectar en LinkedIn")) == "not English"
    assert qualifies(dict(base, views=240000, subs=937, likes=90)) == "likely paid ad (views without likes)"
    assert qualifies(dict(base, views=3000, subs=1000, likes=60)) is None
    assert iso_seconds("PT1H2M3S") == 3723 and iso_seconds("PT45S") == 45
    per = {"a": [{"video_id": "1", "ratio": 5}], "b": [{"video_id": "1", "ratio": 5}, {"video_id": "2", "ratio": 3}], "c": []}
    t = pick_top(per, 20)
    assert [r["video_id"] for r in t] == ["1", "2"], t
    print("selftest PASS: 2 known-good kept, 9 known-bad dropped, dedup + per-keyword pick ok")


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    if "--selftest" in sys.argv:
        return selftest()
    n = int(arg("--top", 20))
    cfg = json.loads(Path(arg("--keywords", "keywords.json")).read_text())
    OWN_CHANNELS.update(cfg.get("exclude_channels", []))
    global SALES_TERMS, OFF_TOPIC
    SALES_TERMS = tuple(w.lower() for w in cfg.get("topic_terms", SALES_TERMS))
    OFF_TOPIC = tuple(w.lower() for w in cfg.get("off_topic_terms", OFF_TOPIC))
    keywords = cfg["keywords"]
    out = Path(arg("--out", "runs"))
    out.mkdir(parents=True, exist_ok=True)
    per_kw = scan(load_key(), keywords, out)
    top = pick_top(per_kw, n)
    today = datetime.date.today().isoformat()
    result = {"date": today, "keywords": len(keywords),
              "rules": {"min_subs": MIN_SUBS, "min_views": MIN_VIEWS, "min_seconds": MIN_SECONDS,
                        "published_after": PUBLISHED_AFTER[:10], "min_like_rate": MIN_LIKE_RATE},
              "top": top, "per_keyword": per_kw}
    for p in (out / f"{today}.json", out / "latest.json"):
        p.write_text(json.dumps(result, indent=1))
    empty = [k for k, v in per_kw.items() if not v]
    print(f"{len(top)} explosive topics from {len(keywords)} keywords. No outlier: {empty or 'none'}")
    for i, r in enumerate(top, 1):
        print(f"{i:2}. {r['ratio']:>6}x  {r['keyword']:<38} {r['views']:>9,} views / {r['subs']:>8,} subs  {r['title'][:60]}  ({r['channel']})")
    print(f"Saved {out / 'latest.json'}. Now judge one honest outlier per keyword (see the skill).")


if __name__ == "__main__":
    main()
