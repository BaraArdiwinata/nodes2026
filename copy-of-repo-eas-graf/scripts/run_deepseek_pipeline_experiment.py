"""
EXPERIMENT (isolated): Wikipedia scrape + DeepSeek imputation on a small sample.

- Does NOT modify pipeline_graf.py or any existing CSV.
- Does NOT import or call Neo4j in any way.
- Writes only data/dataset_dinasti_deepseek_experimental.csv.
- Reuses clean_encoding / fetch_wikipedia_text from pipeline_graf (imports have no side effects).
- SPARQL (Wikidata/DBpedia) stage is intentionally skipped: this experiment isolates the LLM stage.

Usage: python scripts/run_deepseek_pipeline_experiment.py [--n 17] [--seed 42]
"""
import os, sys, re, json, time, argparse
import requests
import pandas as pd
from dotenv import load_dotenv
from rapidfuzz import fuzz

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from pipeline_graf import clean_encoding, fetch_wikipedia_text  # noqa: E402

load_dotenv(os.path.join(here, "../.env"))
KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

SRC = os.path.join(here, "../data/dataset_dinasti_final.csv")
OUT = os.path.join(here, "../data/dataset_dinasti_deepseek_experimental.csv")
FIELDS = ["ayah", "ibu", "pasangan", "anak", "saudara"]

SYSTEM = (
    "You are a professional historian and data scientist. Extract the father, mother, spouse(s), "
    "children and siblings of the historical figure from the text. Use only names stated in the text; "
    "leave a field as an empty string if it is not stated. Estimate confidence_score from 0.0 to 1.0. "
    "Respond ONLY with a JSON object:\n"
    '{"ayah": "", "ibu": "", "pasangan": "comma separated", "anak": "comma separated", '
    '"saudara": "comma separated", "confidence_score": 0.85}'
)


def deepseek_extract(name, text):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Historical figure: '{name}'\n\nText:\n{text}"},
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1000,
        "temperature": 0.1,
    }
    t0 = time.time()
    r = requests.post(f"{BASE_URL}/chat/completions", json=payload, timeout=90,
                      headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    lat = time.time() - t0
    if r.status_code != 200:
        return None, lat, 0, f"HTTP {r.status_code}: {r.text[:200]}"
    j = r.json()
    content = j["choices"][0]["message"]["content"].strip()
    toks = j.get("usage", {}).get("total_tokens", 0)
    try:
        return json.loads(re.sub(r"^```json\s*|^```\s*|```$", "", content, flags=re.M).strip()), lat, toks, ""
    except Exception as e:
        return None, lat, toks, f"JSON parse error: {e}"


def filled(v):
    return isinstance(v, str) and v.strip() not in ("", "nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=17)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    if not KEY:
        sys.exit("DEEPSEEK_API_KEY missing in .env")
    out_abs = os.path.abspath(OUT)
    assert out_abs.endswith("dataset_dinasti_deepseek_experimental.csv")

    df = pd.read_csv(SRC, sep=";", dtype=str).fillna("")
    df = df[df["orang"].str.strip() != ""].drop_duplicates("orang")
    # stratified sample: about half rows previously LLM-imputed, rest SPARQL-sourced
    n_llm = a.n // 2
    s_llm = df[df["source"] == "llm_imputed"]
    s_wd = df[df["source"] == "wikidata"]
    sample = pd.concat([s_llm.sample(min(n_llm, len(s_llm)), random_state=a.seed),
                        s_wd.sample(min(a.n - n_llm, len(s_wd)), random_state=a.seed)])
    print(f"Sample: {len(sample)} persons ({(sample.source=='llm_imputed').sum()} old llm_imputed, "
          f"{(sample.source=='wikidata').sum()} old wikidata)")

    rows = []
    for _, r in sample.iterrows():
        name = r["orang"]
        print(f"\n> {name}")
        wiki = fetch_wikipedia_text(name)
        rec = r.to_dict()
        rec.update({"ds_status": "", "ds_latency_s": "", "ds_tokens": "", "ds_confidence": "",
                    **{f"ds_{f}": "" for f in FIELDS}})
        if not wiki:
            rec["ds_status"] = "no_wikipedia_page"
            rows.append(rec); continue
        ext, lat, toks, err = deepseek_extract(name, wiki)
        rec["ds_latency_s"] = round(lat, 2); rec["ds_tokens"] = toks
        if ext is None:
            rec["ds_status"] = err
            print("  ERROR:", err)
        else:
            rec["ds_status"] = "ok"
            rec["ds_confidence"] = ext.get("confidence_score", "")
            for f in FIELDS:
                v = ext.get(f, "")
                rec[f"ds_{f}"] = clean_encoding(", ".join(v) if isinstance(v, list) else str(v or ""))
            print(f"  ok {lat:.1f}s  " + " | ".join(f"{f}={rec['ds_'+f][:40]}" for f in FIELDS))
        rows.append(rec)
        time.sleep(1)

    res = pd.DataFrame(rows)
    res.to_csv(OUT, sep=";", index=False, encoding="utf-8")
    print(f"\nWrote {len(res)} rows to {out_abs}")

    # ---- comparison summary ----
    ok = res[res["ds_status"] == "ok"]
    print("\n=== SUMMARY ===")
    print("status counts:", res["ds_status"].str[:30].value_counts().to_dict())
    if len(ok):
        print(f"latency s: mean={ok['ds_latency_s'].astype(float).mean():.2f} "
              f"max={ok['ds_latency_s'].astype(float).max():.2f}; tokens mean={ok['ds_tokens'].astype(int).mean():.0f}")
    print(f"\nField completeness over {len(res)} sampled rows (old vs DeepSeek, among status=ok rows too):")
    print(f"{'field':10} {'old':>5} {'deepseek':>9} {'old(ok)':>8} {'ds(ok)':>7} {'agree':>6}/{'both':<4}")
    for f in FIELDS:
        old_all = res[f].map(filled).sum(); ds_all = res[f"ds_{f}"].map(filled).sum()
        old_ok = ok[f].map(filled).sum(); ds_ok = ok[f"ds_{f}"].map(filled).sum()
        both = ok[ok[f].map(filled) & ok[f"ds_{f}"].map(filled)]
        agree = sum(fuzz.token_set_ratio(str(x), str(y)) >= 80 for x, y in zip(both[f], both[f"ds_{f}"]))
        print(f"{f:10} {old_all:5d} {ds_all:9d} {old_ok:8d} {ds_ok:7d} {agree:6d}/{len(both):<4d}")
    print("\nBy old source (status=ok): filled fields old vs deepseek (sum over 5 fields)")
    for src, g in ok.groupby("source"):
        print(f"  {src:12} n={len(g):2d} old={sum(g[f].map(filled).sum() for f in FIELDS)} "
              f"deepseek={sum(g['ds_'+f].map(filled).sum() for f in FIELDS)}")


if __name__ == "__main__":
    main()
