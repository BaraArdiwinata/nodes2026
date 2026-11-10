"""Compare v2 output with the legacy dataset on the same persons (read-only on legacy files)."""
import os, sys, re, json
import pandas as pd
from rapidfuzz import fuzz

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import wiki_guard as wg

REL = ["ayah", "ibu", "pasangan", "anak", "saudara"]
OLD = os.path.join(here, "../../copy-of-repo-eas-graf/data/dataset_dinasti_final.csv")   # read-only baseline
NEW = os.path.join(here, "../data/dataset_dinasti_deepseek_v2.csv")
STATS = json.load(open(NEW.replace(".csv", "_stats.json")))


def names(v):
    return [x.strip() for x in str(v).split(",") if x.strip() and str(v) != "nan"]


def match(a, pool, thr=85):
    return any(fuzz.token_set_ratio(a.lower(), b.lower()) >= thr for b in pool)


old = pd.read_csv(OLD, sep=";", dtype=str).fillna("").drop_duplicates("orang").set_index("orang")
new = pd.read_csv(NEW, sep=";", dtype=str).fillna("").set_index("orang")
people = list(new.index)
old = old.loc[[p for p in people if p in old.index]]

# ---------- A. wrong-entity pages (old method: name lookup id -> en, no guard) ----------
texts, rows = {}, []
for p in old.index:
    pg = None
    for lang in ("id", "en"):
        pg = wg.fetch_page(lang, p)
        if pg and not pg["disambig"]:
            break
        pg = None
    texts[p] = pg
    kingdom = old.at[p, "kerajaan"]
    gd = wg.guard(pg, p, kingdom)
    rows.append((p, bool(pg), gd["status"], gd["reason"]))
A = pd.DataFrame(rows, columns=["orang", "page", "guard", "reason"]).set_index("orang")
old_llm = old[old["source"] == "llm_imputed"].index
wrong_old = [p for p in old_llm if A.at[p, "guard"] != "verified"]

# ---------- B. unsupported relation names in OLD llm_imputed rows ----------
old_rel_total = old_rel_unsupported = 0
unsupported_examples = []
for p in old_llm:
    pg = texts.get(p)
    for rel in REL:
        for nm in names(old.at[p, rel]):
            old_rel_total += 1
            ok = bool(pg) and A.at[p, "guard"] == "verified" and wg.in_text(nm, pg["text"], 88)
            if not ok:
                old_rel_unsupported += 1
                if len(unsupported_examples) < 6: unsupported_examples.append((p, rel, nm, A.at[p, "guard"]))

# ---------- C. SPARQL homonym noise ----------
hom = STATS["homonyms"]
amb_old = {p: n for p, n in hom.items() if n > 1}
new_amb_flag = new[new["manual_check"].str.lower() == "true"].index.tolist()

# ---------- D. v2 relation yield ----------
v2_total = {r: 0 for r in REL}
old_total = {r: 0 for r in REL}
new_only, old_only_supported, old_only_unsupported = [], 0, 0
for p in people:
    for rel in REL:
        nn, oo = names(new.at[p, rel]), names(old.at[p, rel]) if p in old.index else []
        v2_total[rel] += len(nn); old_total[rel] += len(oo)
        for x in nn:
            if not match(x, oo): new_only.append((p, rel, x, new.at[p, "source"]))
        for x in oo:
            if not match(x, nn):
                pg = texts.get(p)
                if pg and wg.in_text(x, pg["text"], 88): old_only_supported += 1
                else: old_only_unsupported += 1

raw, rej = STATS["totals"]["raw"], STATS["totals"]["rejected"]
status = new["entity_status"].value_counts().to_dict()
src = new["source"].value_counts().to_dict()
n_old_rel, n_new_rel = sum(old_total.values()), sum(v2_total.values())

pct = lambda a, b: f"{100 * a / b:.0f}%" if b else "n/a"
rep = f"""# Laporan Perbandingan: Pipeline v2 (DeepSeek) vs Pipeline Lama

Sampel: {len(people)} tokoh (Jawa, Sunda/Cirebon/Banten, Banjar + 1 canary "Elizabeth Carter"). Baseline = `copy-of-repo-eas-graf/data/dataset_dinasti_final.csv` (tidak diubah).

## 1. Entitas salah / noise
| Metrik | Pipeline lama | Pipeline v2 |
|---|---|---|
| Baris imputasi LLM yang berasal dari halaman Wikipedia yang gagal guardrail (entitas salah/ambigu) | {len(wrong_old)} dari {len(old_llm)} ({pct(len(wrong_old), len(old_llm))}) | 0 (halaman gagal guard tidak pernah dikirim ke LLM) |
| Nama relasi pada baris `llm_imputed` yang TIDAK didukung teks halaman | {old_rel_unsupported} dari {old_rel_total} ({pct(old_rel_unsupported, old_rel_total)}) | 0 dari {raw - rej} (semua lolos verifikasi nama + kutipan bukti) |
| Usulan mentah LLM yang ditolak verifikasi bukti | tidak ada mekanisme | {rej} dari {raw} usulan ({pct(rej, raw)}) |
| Nama dengan >1 kandidat manusia di Wikidata (homonim) | {len(amb_old)} nama (total {sum(amb_old.values())} kandidat) | kandidat dipersempit ke yang grounded; ditandai manual_check: {len(new_amb_flag)} |
| Entitas ditolak karena grounding lemah + guard gagal | tidak ada | {status.get('rejected_weak_grounding', 0)} |

Penurunan entitas halusinasi (baris imputasi dari halaman salah): {pct(len(wrong_old), len(old_llm)) if old_llm.size else 'n/a'} -> 0%.
Penurunan relasi tak berdasar pada imputasi LLM: {pct(old_rel_unsupported, old_rel_total)} -> 0% (angka v2 nol dijamin oleh konstruksi verifikasi, bukan bukti akurasi sejarah).

Contoh relasi lama yang tidak didukung teks: {unsupported_examples}

## 2. Distribusi status entitas v2
{json.dumps(status, indent=1)}

Sumber data v2: {json.dumps(src)}

## 3. Relasi yang berhasil ditangkap (ayah+ibu+pasangan+anak+saudara)
| Field | Lama | v2 |
|---|---|---|
""" + "\n".join(f"| {r} | {old_total[r]} | {v2_total[r]} |" for r in REL) + f"""
| **Total** | {n_old_rel} | {n_new_rel} |

- Relasi BARU di v2 yang tidak ada di data lama: {len(new_only)} (semua berasal dari Wikidata terstruktur atau LLM + bukti tervalidasi).
- Relasi lama yang tidak muncul di v2: {old_only_supported + old_only_unsupported}; dari itu {old_only_supported} sebenarnya didukung teks halaman (potensi kehilangan recall), {old_only_unsupported} tidak didukung teks (noise yang terbuang atau data lama dari Wikidata tanpa teks pendukung).

Daftar relasi baru: {new_only}

## 4. Biaya & kinerja v2
{json.dumps({k: STATS[k] for k in ['llm', 'sparql', 'seconds', 'totals']}, indent=1)}

## Catatan metodologi (jujur)
- "Valid" berarti: dari Wikidata terstruktur dengan grounding, atau dari LLM dengan nama dan kutipan bukti yang ditemukan dalam teks halaman terverifikasi. Ini BUKAN verifikasi historis oleh manusia.
- Pengukuran noise pipeline lama memakai pencarian halaman berdasarkan nama (seperti pipeline lama) lalu guardrail v2 sebagai pengukur; ada kemungkinan false-positive guard. Sampel kecil ({len(people)}).
"""
os.makedirs(os.path.join(here, "../docs"), exist_ok=True)
open(os.path.join(here, "../docs/v2_vs_old_report.md"), "w", encoding="utf-8").write(rep)
print(rep)
