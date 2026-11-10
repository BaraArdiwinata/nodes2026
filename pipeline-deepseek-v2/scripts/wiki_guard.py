"""Wikipedia fetch (id first, then en) + domain/context guardrail + evidence verification.

Guard goal: never impute family relations from a page about the wrong entity (e.g. a foreign homonym).
"""
import re, time, random
import requests
from rapidfuzz import fuzz

UA = "NusantaraGraphBot/2.0 (academic research project; ITS Surabaya)"
MAX_CHARS = 8000

# Domain lexicon (id + en). 'Distinct hits' are counted, not occurrences.
KEYWORDS = [
    "raja", "sultan", "sultanah", "kerajaan", "kesultanan", "kesunanan", "kadipaten", "putra", "putri", "nusantara",
    "adipati", "ratu", "pangeran", "maharaja", "prabu", "panembahan", "sunan", "pangeran", "dinasti", "wangsa",
    "bupati", "patih", "mahapatih", "permaisuri", "menantu", "takhta", "tahta", "keraton", "candi", "prasasti",
    "kingdom", "sultanate", "king", "queen", "prince", "princess", "dynasty", "throne", "javanese", "sundanese",
    "balinese", "malay", "indonesia", "java", "sumatra", "borneo", "kalimantan", "bali", "majapahit", "mataram",
]
MODERN_FOREIGN = [
    "united states", "amerika serikat", "england", "inggris", "london", "british", "american", "actress", "actor",
    "singer", "footballer", "politician", "penyanyi", "aktris", "aktor", "pemain sepak bola", "poet", "novelist",
    "translator", "university", "universitas", "born in", "kent,", "new york", "california",
]
KINGDOM_STOP = r"\b(kerajaan|kesultanan|kesunanan|kadipaten|kingdom|sultanate|of|the|dari)\b"


def _api(lang, params, tries=4):
    params = {**params, "format": "json", "formatversion": 2}
    for a in range(tries):
        try:
            r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", params=params,
                             headers={"User-Agent": UA}, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code not in (429, 500, 502, 503, 504):
                return None
        except (requests.Timeout, requests.ConnectionError):
            pass
        time.sleep(2 * 2 ** a + random.uniform(0, 0.5))
    return None


def fetch_page(lang, title):
    """Exact-title fetch (redirects followed). Returns dict(lang,title,text,disambig) or None."""
    j = _api(lang, {"action": "query", "prop": "extracts|pageprops", "ppprop": "disambiguation", "explaintext": 1,
                    "redirects": 1, "titles": title, "exchars": MAX_CHARS, "exlimit": 1})
    try:
        p = j["query"]["pages"][0]
    except Exception:
        return None
    if p.get("missing") or not p.get("extract"):
        return None
    return {"lang": lang, "title": p["title"], "text": p["extract"],
            "disambig": "pageprops" in p and "disambiguation" in p["pageprops"]}


def find_page(name, sitelinks=None):
    """Priority: id sitelink -> id by name -> en sitelink -> en by name. Sitelink = exact QID-linked title.
    Returns (page|None, how)."""
    sitelinks = sitelinks or {}
    plan = [("id", sitelinks.get("id"), "id_sitelink"), ("id", name, "id_name"),
            ("en", sitelinks.get("en"), "en_sitelink"), ("en", name, "en_name")]
    for lang, title, how in plan:
        if not title:
            continue
        pg = fetch_page(lang, title)
        if pg and not pg["disambig"]:
            return pg, how
    return None, "none"


def _norm(s):
    return re.sub(r"\s+", " ", s.lower()).strip()


def kingdom_key(k):
    k = re.sub(KINGDOM_STOP, " ", (k or "").lower())
    return _norm(k)


def guard(page, name, kingdom=""):
    """Returns dict(status in {'verified','ambiguous_unverified'}, kw_hits, kingdom_hit, modern_hits, reason)."""
    if not page:
        return {"status": "ambiguous_unverified", "kw_hits": 0, "kingdom_hit": False, "modern_hits": 0,
                "reason": "no_page"}
    t = _norm(page["text"])
    kw = sorted({k for k in KEYWORDS if re.search(rf"\b{re.escape(k)}\b", t)})
    kkey = kingdom_key(kingdom)
    khit = bool(kkey) and len(kkey) >= 4 and kkey in t
    modern = sum(1 for m in MODERN_FOREIGN if m in t)
    name_ok = fuzz.partial_ratio(_norm(name), t[:1500]) >= 85 or fuzz.token_set_ratio(_norm(name), _norm(page["title"])) >= 70
    ok = name_ok and ((khit and len(kw) >= 1) or len(kw) >= 3) and (modern < 3 or khit)
    reason = "ok" if ok else ("name_mismatch" if not name_ok else "few_domain_keywords" if len(kw) < 3 else "foreign_modern_markers")
    return {"status": "verified" if ok else "ambiguous_unverified", "kw_hits": len(kw), "kingdom_hit": khit,
            "modern_hits": modern, "reason": reason}


def in_text(needle, text, thr=88):
    """Fuzzy verbatim check that a quote/name occurs in the (normalised) page text."""
    n, t = _norm(needle or ""), _norm(text)
    if len(n) < 3:
        return False
    return n in t or fuzz.partial_ratio(n, t) >= thr
