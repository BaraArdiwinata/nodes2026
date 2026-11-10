"""SPARQL v2: geographically/sovereignty-grounded, temporally filtered Wikidata fetch + DBpedia kingdom fetch.

Differences vs the old query:
- A person must be explicitly tied to Nusantara/Indonesia (P27, P39 position, P97 title or P53 family
  rooted in Indonesia / an Indonesian historical state). Old query only grabbed a name match and left the
  kingdom link OPTIONAL, so any homonym (e.g. a foreign "Elizabeth Carter") came back.
- Birth/death year must lie in 301..1945 / ..1950 when known (4th century CE to early 20th century).
- Wikipedia sitelinks (id/en) are returned so Wikipedia is fetched by QID, not by name guesswork.
"""
import time, random
import requests
import pandas as pd

WD = "https://query.wikidata.org/sparql"
DBP = "https://dbpedia.org/sparql"
UA = "NusantaraGraphBot/2.0 (academic research project; ITS Surabaya)"
SPARQL_STATS = {"requests": 0, "retries": 0, "seconds": 0.0}


def run_sparql(endpoint, query, max_retries=4, timeout=90):
    headers = {"User-Agent": UA, "Accept": "application/sparql-results+json" if "dbpedia" not in endpoint else "application/json"}
    for attempt in range(max_retries + 1):
        t0 = time.time()
        try:
            r = requests.post(endpoint, data={"query": query}, headers=headers, timeout=timeout)
            SPARQL_STATS["requests"] += 1; SPARQL_STATS["seconds"] += time.time() - t0
            if r.status_code == 200:
                d = r.json(); cols = d["head"]["vars"]
                rows = [{c: b.get(c, {}).get("value") for c in cols} for b in d["results"]["bindings"]]
                return pd.DataFrame(rows, columns=cols)
            if r.status_code not in (429, 500, 502, 503, 504):
                print(f"[SPARQL] HTTP {r.status_code}: {r.text[:150]}"); return pd.DataFrame()
            wait = float(r.headers.get("Retry-After", 0) or 0)
        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"[SPARQL] {type(e).__name__}"); wait = 0
        if attempt < max_retries:
            SPARQL_STATS["retries"] += 1
            time.sleep(max(wait, 3 * 2 ** attempt) + random.uniform(0, 1))
    return pd.DataFrame()


def _values(names):
    out = []
    for n in names:
        e = n.replace("\\", "\\\\").replace('"', '\\"')
        out += [f'"{e}"@id', f'"{e}"@en']
    return "\n      ".join(out)


GROUNDING = """
    { ?person wdt:P27 wd:Q252 . BIND("P27:Indonesia" AS ?ground) }
    UNION { ?person wdt:P27 ?st . ?st wdt:P17 wd:Q252 ; wdt:P31/wdt:P279* wd:Q3024240 . BIND("P27:negara-historis-ID" AS ?ground) }
    UNION { ?person wdt:P39 ?pos . ?pos wdt:P1001|wdt:P17 ?ent .
            FILTER(?ent = wd:Q252 || EXISTS { ?ent wdt:P17 wd:Q252 })
            BIND("P39:jabatan-di-ID" AS ?ground) }
    UNION { ?person wdt:P97 ?ttl . ?ttl wdt:P17 wd:Q252 . BIND("P97:gelar-ID" AS ?ground) }
    UNION { ?person wdt:P53 ?fam . ?fam wdt:P17 wd:Q252 . BIND("P53:wangsa-ID" AS ?ground) }
"""

TEMPORAL = """
  OPTIONAL { ?person wdt:P569 ?tglLahir . }
  OPTIONAL { ?person wdt:P570 ?tglMati . }
  FILTER(!BOUND(?tglLahir) || (YEAR(?tglLahir) >= 301 && YEAR(?tglLahir) <= 1945))
  FILTER(!BOUND(?tglMati)  || (YEAR(?tglMati)  >= 301 && YEAR(?tglMati)  <= 1950))
"""


def wikidata_grounded_query(names):
    return f"""
SELECT DISTINCT ?person ?personLabel ?ground ?ayahLabel ?ibuLabel ?pasanganLabel ?anakLabel ?saudaraLabel ?dinastiLabel
       ?jabatanLabel ?menggantikanLabel ?digantikanLabel ?tglLahir ?tglMati ?idTitle ?enTitle
WHERE {{
  VALUES ?label {{
      {_values(names)}
  }}
  ?person rdfs:label ?label ; wdt:P31 wd:Q5 .
  {{ {GROUNDING} }}
  OPTIONAL {{ ?person wdt:P22 ?ayah . }}
  OPTIONAL {{ ?person wdt:P25 ?ibu . }}
  OPTIONAL {{ ?person wdt:P26 ?pasangan . }}
  OPTIONAL {{ ?person wdt:P40 ?anak . }}
  OPTIONAL {{ ?person wdt:P3373 ?saudara . }}
  OPTIONAL {{ ?person wdt:P53 ?dinasti . }}
  OPTIONAL {{ ?person wdt:P39 ?jabatan . }}
  OPTIONAL {{ ?person wdt:P1365 ?menggantikan . }}
  OPTIONAL {{ ?person wdt:P1366 ?digantikan . }}
  {TEMPORAL}
  OPTIONAL {{ ?idw schema:about ?person ; schema:isPartOf <https://id.wikipedia.org/> ; schema:name ?idTitle . }}
  OPTIONAL {{ ?enw schema:about ?person ; schema:isPartOf <https://en.wikipedia.org/> ; schema:name ?enTitle . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "id,en" . }}
}}"""


def wikidata_ungrounded_query(names):
    """OLD-style lookup (label match + human only). Used only to measure homonym noise, never to fill data."""
    return f"""
SELECT DISTINCT ?person ?label WHERE {{
  VALUES ?label {{
      {_values(names)}
  }}
  ?person rdfs:label ?label ; wdt:P31 wd:Q5 .
}}"""


DBPEDIA_Q = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbc: <http://dbpedia.org/resource/Category:>
SELECT DISTINCT ?namaKerajaan ?ibuKota ?agama ?tahunMulai ?wikidataID WHERE {
  ?s dct:subject dbc:Precolonial_states_of_Indonesia ; rdfs:label ?namaKerajaan .
  OPTIONAL { ?s dbo:capital ?cap. ?cap rdfs:label ?ibuKota. FILTER (lang(?ibuKota) = "en") }
  OPTIONAL { ?s dbo:religion ?rel. ?rel rdfs:label ?agama. FILTER (lang(?agama) = "en") }
  OPTIONAL { ?s dbp:yearStart ?tahunMulai }
  OPTIONAL { ?s owl:sameAs ?wikidataID. FILTER (REGEX(STR(?wikidataID), "wikidata.org")) }
  FILTER (lang(?namaKerajaan) = "en")
}"""


def _join(x):
    return ", ".join(sorted({v for v in x.dropna() if v}))


def fetch_grounded(names, batch=40):
    """Returns one row per (person QID) with aggregated relations. Empty frame when nothing is grounded."""
    frames = []
    for i in range(0, len(names), batch):
        df = run_sparql(WD, wikidata_grounded_query(names[i:i + batch]))
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    agg = {c: _join for c in ["ground", "ayahLabel", "ibuLabel", "pasanganLabel", "anakLabel", "saudaraLabel", "dinastiLabel",
                              "jabatanLabel", "menggantikanLabel", "digantikanLabel"]}
    agg.update({c: "first" for c in ["personLabel", "tglLahir", "tglMati", "idTitle", "enTitle"]})
    return df.groupby("person").agg(agg).reset_index()


def count_homonyms(names, batch=40):
    """{name: number of distinct human QIDs carrying that exact label} using the OLD-style query."""
    frames = []
    for i in range(0, len(names), batch):
        df = run_sparql(WD, wikidata_ungrounded_query(names[i:i + batch]))
        if not df.empty:
            frames.append(df)
    if not frames:
        return {}
    df = pd.concat(frames)
    return df.groupby("label")["person"].nunique().to_dict()
