"""NusantaraGraph pipeline v2 (DeepSeek).

Stages
 1. Grounded SPARQL (Wikidata) + DBpedia kingdom facts           -> sparql_v2.py
 2. Encoding healer (cp1252 -> UTF-8)
 3. Wikipedia fetch by QID sitelink (id first) + domain guardrail  -> wiki_guard.py
    + cross-validation: persons grounded by a single weak signal must also pass the Wikipedia guard
 4. DeepSeek imputation (JSON mode) with per-relation evidence quotes, verified against the page text
 5. Entity disambiguation (RapidFuzz + DeepSeek JSON verdict + Union-Find)
 6. Export. Graph metrics are still computed afterwards by analisis_graf.py (unchanged).

Usage (experiment): python scripts/pipeline_graf.py --names-file data/sample_v2_names.txt --out data/dataset_dinasti_deepseek_v2.csv
Usage (full)      : python scripts/pipeline_graf.py --out data/dataset_dinasti_deepseek_v2_full.csv
The script refuses to overwrite the legacy datasets and never touches Neo4j.
"""
import os, sys, re, json, time, argparse
import pandas as pd
from rapidfuzz import fuzz

if sys.stdout.encoding != "utf-8":
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import llm_client as llm
import sparql_v2 as sp
import wiki_guard as wg

PROTECTED = {"dataset_dinasti_final.csv", "dataset_dinasti_final_with_metrics.csv", "dataset_gabungan_uts_graf.csv"}
REL = ["ayah", "ibu", "pasangan", "anak", "saudara"]


# ---------- Stage 2: cleaning ----------
def clean_encoding(text):
    if not isinstance(text, str) or pd.isna(text):
        return ""
    text = text.strip()
    if text.lower() in ("nan", "none", "null", ""):
        return ""
    prev = ""
    for _ in range(3):
        if prev == text: break
        prev = text
        if any(c in text for c in ["Ã", "Â", "Å", "â", "€", "™", "œ", "¥", "¡", "¢", "„"]):
            cand = text.encode("cp1252", errors="ignore").decode("utf-8", errors="ignore")
            if cand == text: break
            text = cand
        else:
            break
    text = re.sub(r'^"+|"+$', "", text)
    text = text.replace("â‚¬â„¢", "'").replace("â€™", "'").replace("â€", '"').replace("Ã…Å¡", "Ś").replace("Ã¢â‚¬â„¢", "'")
    return text.strip()


def clean_uri(u):
    return u.strip().strip('"').strip("'") if isinstance(u, str) else ""


# ---------- Stage 4: DeepSeek imputation with evidence ----------
SYSTEM_IMPUTE = (
    "Anda adalah pakar ontologi silsilah Kerajaan Nusantara. Tugas: ekstrak relasi keluarga tokoh dari TEKS yang "
    "diberikan. Jika teks tidak menyebutkan relasi keluarga secara eksplisit dalam konteks sejarah Nusantara, "
    "kembalikan nilai null. DILARANG mengimputasi relasi dari tokoh sejarah Eropa/barat modern meskipun memiliki "
    "kesamaan nama. Jangan menebak, jangan memakai pengetahuan di luar teks. Setiap relasi WAJIB disertai kutipan "
    "bukti (kalimat persis dari teks).\n\nKeluarkan HANYA satu objek json dengan skema:\n"
    '{"tokoh_nusantara": true|false,\n'
    ' "ayah": {"nama": "...", "bukti": "..."} | null,\n'
    ' "ibu": {"nama": "...", "bukti": "..."} | null,\n'
    ' "pasangan": [{"nama": "...", "bukti": "..."}],\n'
    ' "anak": [{"nama": "...", "bukti": "..."}],\n'
    ' "saudara": [{"nama": "...", "bukti": "..."}]}\n'
    'Jika tokoh dalam teks bukan tokoh Nusantara, set "tokoh_nusantara": false dan semua relasi null/[].'
)


GENERIC_FIRST = {"anak", "saudara", "istri", "suami", "putra", "putri", "beberapa", "para", "seorang", "keturunan", "ayah", "ibu"}
TITLE_ONLY = {"kanjeng", "raden", "ratu", "pangeran", "sultan", "sunan", "prabu", "gusti", "nyai", "nyi", "raja", "pangeran", "mas", "dyah"}


def plausible_name(nm):
    """Reject counts ('3 anak laki-laki'), descriptions ('istri Airlangga') and bare titles ('Kanjeng')."""
    toks = nm.lower().replace(",", " ").split()
    if not toks or re.search(r"\d", nm) or toks[0] in GENERIC_FIRST: return False
    return not all(t in TITLE_ONLY for t in toks)


def _items(v):
    if not v: return []
    return [v] if isinstance(v, dict) else [x for x in v if isinstance(x, dict)]


def deepseek_impute(name, text, kingdom, subject_names):
    """Returns (fields: {rel: 'a, b'}, raw_items, rejected_items, nusantara_flag)."""
    j = llm.chat_json(SYSTEM_IMPUTE, f"Tokoh: {name}\nKerajaan terkait: {kingdom or '-'}\n\nTEKS:\n{text}",
                      max_tokens=1200)
    if j is None:
        return {}, 0, 0, None
    if j.get("tokoh_nusantara") is False:
        return {}, 0, 0, False
    out, raw, rej = {}, 0, 0
    for rel in REL:
        keep = []
        for it in _items(j.get(rel)):
            nm = clean_encoding(str(it.get("nama") or ""))
            ev = str(it.get("bukti") or "")
            if not nm: continue
            raw += 1
            # verification: name and evidence quote must occur in the page; no self-reference
            if (not plausible_name(nm) or not wg.in_text(nm, text, 88) or not wg.in_text(ev, text, 88)
                    or fuzz.token_set_ratio(nm.lower(), name.lower()) >= 95):
                rej += 1; continue
            keep.append(nm)
        if keep: out[rel] = ", ".join(dict.fromkeys(keep))
    return out, raw, rej, True


# ---------- Stage 5: disambiguation ----------
def same_person(n1, n2, k1, k2):
    j = llm.chat_json("Anda sejarawan kerajaan prakolonial Nusantara. Tentukan apakah dua nama merujuk ke individu yang SAMA. "
                      'Balas json: {"same_person": true|false, "alasan": "..."}',
                      f"1. {n1} (kerajaan: {k1 or '-'})\n2. {n2} (kerajaan: {k2 or '-'})", max_tokens=150)
    return bool(j and j.get("same_person") is True)


def disambiguate(df):
    names = [n for n in df["orang"].unique() if n]
    parent = {n: n for n in names}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    kmap = df.drop_duplicates("orang").set_index("orang")["kerajaan"].to_dict()
    checked = merged = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if find(a) == find(b) or fuzz.token_set_ratio(a, b) < 85: continue
            checked += 1
            if same_person(a, b, kmap.get(a), kmap.get(b)):
                parent[find(a)] = find(b); merged += 1
    print(f"Disambiguation: {checked} candidate pairs checked, {merged} merged.")
    df["master_id"] = df["orang"].map(lambda x: find(x) if x in parent else x)
    return df, checked, merged


# ---------- main ----------
def pick_candidate(name, g):
    if g.empty: return None, 0
    c = g[g["personLabel"].str.lower() == name.lower()]
    if c.empty:
        c = g[g["personLabel"].map(lambda l: fuzz.ratio(str(l).lower(), name.lower()) >= 95)]
    if c.empty: return None, 0
    c = c.assign(_s=c["ground"].map(lambda x: len([s for s in str(x).split(",") if s.strip()])),
                 _r=c[["ayahLabel", "ibuLabel", "pasanganLabel", "anakLabel"]].apply(lambda r: sum(bool(v) for v in r), axis=1))
    c = c.sort_values(["_s", "_r"], ascending=False)
    return c.iloc[0], len(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names-file", help="one person name per line (experiment mode)")
    ap.add_argument("--out", default=os.path.join(here, "../data/dataset_dinasti_deepseek_v2.csv"))
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if os.path.basename(out) in PROTECTED:
        sys.exit("Refusing to overwrite a legacy dataset.")
    t_start = time.time()

    src = os.path.join(here, "../data/dataset_gabungan_uts_graf.csv")
    df = pd.read_csv(src, sep=";", dtype=str).fillna("")
    for c in df.columns: df[c] = df[c].map(clean_encoding)
    df = df[df["orang"].str.len() > 2].drop_duplicates("orang").reset_index(drop=True)
    if a.names_file:
        want = [l.strip() for l in open(a.names_file, encoding="utf-8") if l.strip()]
        df = df[df["orang"].isin(want)].reset_index(drop=True)
        miss = set(want) - set(df["orang"])
        if miss: print("Not found in input CSV:", miss)
    names = list(df["orang"])
    print(f"Persons to process: {len(names)}")

    # Stage 1
    print("\n[1] Grounded SPARQL ...")
    g = sp.fetch_grounded(names)
    homonyms = sp.count_homonyms(names)
    dbp = sp.run_sparql(sp.DBP, sp.DBPEDIA_Q)
    print(f"    grounded QIDs: {len(g)}; DBpedia kingdoms: {len(dbp)}")

    for c in ["saudara", "jabatan", "pendahulu", "penerus", "tglLahir", "tglMati", "dinasti", "personWikidataID", "kerabat"]:
        if c not in df.columns: df[c] = ""
    meta = {k: [] for k in ["ground_basis", "ground_strength", "homonyms", "wiki_lang", "wiki_title", "wiki_how",
                            "guard_status", "guard_reason", "guard_kw_hits", "llm_raw_items", "llm_rejected_items",
                            "entity_status", "source", "confidence_score", "manual_check", "data_source"]}
    totals = {"raw": 0, "rejected": 0, "llm_calls": 0}

    for idx, r in df.iterrows():
        name, king = r["orang"], r["kerajaan"]
        cand, ncand = pick_candidate(name, g)
        row_meta = dict(ground_basis="", ground_strength=0, homonyms=homonyms.get(name, 0), wiki_lang="", wiki_title="",
                        wiki_how="", guard_status="", guard_reason="", guard_kw_hits=0, llm_raw_items=0,
                        llm_rejected_items=0, entity_status="", source="original", confidence_score=1.0,
                        manual_check=ncand > 1, data_source="")
        sl = {}
        if cand is not None:
            row_meta["ground_basis"] = cand["ground"]
            row_meta["ground_strength"] = len([s for s in str(cand["ground"]).split(",") if s.strip()])
            sl = {"id": cand["idTitle"] if isinstance(cand["idTitle"], str) else None,
                  "en": cand["enTitle"] if isinstance(cand["enTitle"], str) else None}
        page, how = wg.find_page(name, sl)
        gd = wg.guard(page, name, king)
        if page: row_meta.update(wiki_lang=page["lang"], wiki_title=page["title"])
        row_meta.update(wiki_how=how, guard_status=gd["status"], guard_reason=gd["reason"], guard_kw_hits=gd["kw_hits"])
        print(f"- {name}: grounded={cand is not None}(x{row_meta['ground_strength']}, homonyms={row_meta['homonyms']}) "
              f"page={row_meta['wiki_lang']}:{row_meta['wiki_title']} guard={gd['status']}({gd['reason']})")

        accept_wd = cand is not None
        if cand is not None and row_meta["ground_strength"] < 2 and gd["status"] != "verified":
            accept_wd = False          # weak single-signal grounding must be confirmed by Wikipedia
            row_meta["entity_status"] = "rejected_weak_grounding"
        if accept_wd:
            df.at[idx, "personWikidataID"] = cand["person"]
            for col, k in [("ayah", "ayahLabel"), ("ibu", "ibuLabel"), ("pasangan", "pasanganLabel"), ("anak", "anakLabel"), ("saudara", "saudaraLabel"),
                           ("dinasti", "dinastiLabel"), ("jabatan", "jabatanLabel"), ("pendahulu", "menggantikanLabel"),
                           ("penerus", "digantikanLabel")]:
                v = clean_encoding(cand[k]) if isinstance(cand[k], str) else ""
                if v: df.at[idx, col] = v
            df.at[idx, "tglLahir"] = cand["tglLahir"] if isinstance(cand["tglLahir"], str) else ""
            df.at[idx, "tglMati"] = cand["tglMati"] if isinstance(cand["tglMati"], str) else ""
            row_meta.update(source="wikidata", confidence_score=1.0 if row_meta["ground_strength"] >= 2 else 0.9)
            row_meta["entity_status"] = "grounded_verified" if gd["status"] == "verified" else "grounded_unconfirmed"
        elif not row_meta["entity_status"]:
            row_meta["entity_status"] = "ungrounded_verified" if gd["status"] == "verified" else "ungrounded_unverified"

        # Stage 4: LLM only when the page is verified AND some relation is still empty
        if gd["status"] == "verified" and row_meta["entity_status"] != "rejected_weak_grounding":
            ext, raw, rej, flag = deepseek_impute(name, page["text"], king, [name])
            totals["llm_calls"] += 1; totals["raw"] += raw; totals["rejected"] += rej
            row_meta.update(llm_raw_items=raw, llm_rejected_items=rej)
            added = 0
            for rl, v in ext.items():
                have = [x.strip() for x in str(df.at[idx, rl]).split(",") if x.strip()]
                fresh = [x for x in v.split(", ") if not any(fuzz.token_set_ratio(x.lower(), h.lower()) >= 85 for h in have)]
                if fresh:
                    df.at[idx, rl] = ", ".join(have + fresh); added += 1
            if added:
                if row_meta["source"] == "original":
                    row_meta["source"] = "llm_imputed"
                    row_meta["confidence_score"] = round(min(0.9, 0.7 + 0.1 * gd["kingdom_hit"] + 0.1 * (rej == 0)), 2)
                else:
                    row_meta["source"] = "wikidata+llm_imputed"
                row_meta["data_source"] = f"{page['lang']}.wikipedia:{page['title']}"
            if flag is False:
                row_meta["entity_status"] = "llm_flagged_non_nusantara"
            time.sleep(0.5)
        for k, v in row_meta.items(): meta[k].append(v)

    for k, v in meta.items(): df[k] = v

    # DBpedia kingdom facts for empty cells
    if not dbp.empty:
        dbp = dbp.groupby("namaKerajaan").agg({"ibuKota": sp._join, "agama": sp._join, "tahunMulai": "first",
                                               "wikidataID": "first"}).reset_index()
        for idx, r in df.iterrows():
            best = max(((fuzz.token_set_ratio(r["kerajaan"], x), i) for i, x in enumerate(dbp["namaKerajaan"])), default=(0, 0))
            if best[0] >= 85:
                m = dbp.iloc[best[1]]
                for c in ["ibuKota", "agama", "tahunMulai"]:
                    if c in df.columns and not str(r[c]).strip() and isinstance(m[c], str):
                        df.at[idx, c] = m[c]

    print("\n[5] Entity disambiguation ...")
    df, checked, merged = disambiguate(df)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, sep=";", index=False, encoding="utf-8")
    stats = {"persons": len(df), "grounded": int((df["ground_strength"] > 0).sum()), "totals": totals,
             "sparql": sp.SPARQL_STATS, "llm": llm.STATS, "disamb": {"checked": checked, "merged": merged},
             "seconds": round(time.time() - t_start, 1), "homonyms": {k: int(v) for k, v in homonyms.items()}}
    json.dump(stats, open(out.replace(".csv", "_stats.json"), "w"), indent=1)
    print(f"\nWrote {out}\nstats: {json.dumps({k: v for k, v in stats.items() if k != 'homonyms'})}")


if __name__ == "__main__":
    main()
