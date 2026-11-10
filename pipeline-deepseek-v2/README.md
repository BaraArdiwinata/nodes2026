# NusantaraGraph Pipeline V2 (DeepSeek)

Isolated, experimental upgrade of the V1 enrichment pipeline (`../copy-of-repo-eas-graf`, left untouched). It uses the DeepSeek API, grounded SPARQL, a Wikipedia guardrail, and quote-verified extraction. It **never writes to Neo4j**; output goes to a separate CSV.

## Why V2: problems found in V1

| Problem | Evidence |
|---|---|
| Wrong-entity imputation | "Elizabeth Carter" (Kerajaan Kubu) received a father from an unrelated Wikipedia page. The cause is a mislink in Wikidata itself (her `P27` points to the Kingdom of Kubu), so SPARQL grounding alone does not catch it |
| Loose SPARQL | Name-only lookup returns every homonym (e.g. 11 human entities labelled "Elizabeth Carter") with the kingdom link optional |
| Unsupported LLM relations | In the 30-person benchmark, **9 of 23 (39%)** relation names in V1 LLM-imputed rows do not appear in the Wikipedia text they were supposedly extracted from |
| No self-check | V1 stored the model's own confidence and had no mechanism to reject a relation |

## V2 innovations

1. **Geographic and sovereign grounding** (`scripts/sparql_v2.py`). A human (`wdt:P31 wd:Q5`) must be tied to Indonesia through at least one of: nationality `P27` (Indonesia or an Indonesian historical state), position `P39`, noble title `P97`, or noble family `P53`. Birth year must lie in 301-1945 and death year up to 1950 when known. Relations are pulled as structured data: `P22`, `P25`, `P26`, `P40`, `P3373`, `P53`, `P39`, `P1365`, `P1366`. Wikipedia sitelinks (id/en) are returned with each person.
2. **Wikipedia: Indonesian first, fetched by QID sitelink, then guarded** (`scripts/wiki_guard.py`). Order: `id` sitelink, `id` by name, `en` sitelink, `en` by name. Before any text reaches the LLM, the page must pass a domain check (royal/local terminology, kingdom name, no dominant modern/foreign markers). Pages that fail are marked `ambiguous_unverified` and are not used for imputation.
3. **Cross-validation.** A person grounded by only one weak signal must also pass the Wikipedia guard, otherwise their Wikidata relations are discarded (`rejected_weak_grounding`). This is what stops the Elizabeth Carter case.
4. **Strict evidence extraction** (`scripts/pipeline_graf.py`). DeepSeek runs in JSON mode with a guardrail system prompt (return `null` unless family relations are explicit in a Nusantara context; never impute from modern Western namesakes). Every relation must carry an exact quote. The name and the quote must both be found in the page text, otherwise the relation is dropped. Counts ("3 anak laki-laki"), descriptions ("istri Airlangga"), and bare titles ("Kanjeng") are rejected.
5. **Robust LLM calls** (`scripts/llm_client.py`): `https://api.deepseek.com`, `deepseek-chat`, `DEEPSEEK_API_KEY` from `.env`, retry with exponential backoff on timeout, 429 and 5xx.
6. **Provenance columns** in the output: `entity_status`, `ground_basis`, `ground_strength`, `homonyms`, `wiki_lang`, `wiki_title`, `guard_status`, `guard_reason`, `llm_raw_items`, `llm_rejected_items`, `source`, `confidence_score`.

## Benchmark (30 persons: Javanese, Sundanese/Cirebon/Banten, Banjar, plus one canary)

Full tables in [`docs/v2_vs_old_report.md`](docs/v2_vs_old_report.md).

| Metric | V1 | V2 |
|---|---|---|
| LLM imputation from a page that fails the guardrail | 1 of 9 rows (11%) | 0 |
| Relation names not supported by the page text | 9 of 23 (39%) | 0 of 57 |
| Raw LLM proposals rejected by verification | no mechanism | 4 of 61 (7%) |
| Relations captured (father, mother, spouse, child, sibling) | 58 | 83 |
| Relations not present in V1 | - | 42 |
| Entities rejected (weak grounding and guard fail) | - | 2 |
| Cost (30 persons) | - | 3 SPARQL requests, 30 LLM calls, about 23k tokens, about 228 s |

**Read these numbers carefully.**
- The V2 "0" is guaranteed by the verification design. It shows that unsupported relations are filtered, not that the remaining relations are historically correct. No human review has been done.
- The sample is small (30 persons, one wrong-entity canary, 9 V1 LLM rows).
- Some of the 42 "new" relations may be aliases of existing ones (for example "Prabu Siliwangi" for Sri Baduga Maharaja).
- V2 lost recall in places: 10 of the 17 V1 relations missing from V2 are supported by the page text, and "Patih Masih" was rejected because no Wikipedia page was found.

## How to run

```bash
cd pipeline-deepseek-v2
pip install pandas requests python-dotenv rapidfuzz networkx
# .env in this folder must contain DEEPSEEK_API_KEY
python scripts/pipeline_graf.py --names-file data/sample_v2_names.txt --out data/dataset_dinasti_deepseek_v2.csv
python scripts/eval_v2_vs_old.py
```

- The pipeline entry point is `scripts/pipeline_graf.py` (there is no `run_pipeline.py`). Omit `--names-file` to process all persons, with a different `--out` name. The script refuses to overwrite the legacy datasets.
- `eval_v2_vs_old.py` reads the V1 baseline CSV from `../copy-of-repo-eas-graf/data/` (read-only), fetches Wikipedia pages, and writes `docs/v2_vs_old_report.md`.
- `scripts/analisis_graf.py` (PageRank, Louvain, Betweenness, Adamic-Adar) is unchanged from V1.
- `graph_rag_bot.py` and `mcp_agent.py` in this folder call DeepSeek through `llm_client`. JSON mode is used only for Text-to-Cypher; tool-calling and prose answers cannot use JSON mode. The full agent loop has not been run end to end with DeepSeek.

## Limitations and next steps
- Run the full dataset (about 139 unique persons) and review a random sample by hand.
- Add alias handling for names such as regnal titles before counting "new" relations.
- Recover recall for persons without a Wikipedia page, for example through Wikidata-only evidence.
- Import V2 output into a **separate** Neo4j database before replacing the V1 data.

See also [`V2_NOTES.md`](V2_NOTES.md) for a file-by-file summary.
