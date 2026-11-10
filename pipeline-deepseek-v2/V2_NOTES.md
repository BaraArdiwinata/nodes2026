# pipeline-deepseek-v2

Isolated upgrade of `copy-of-repo-eas-graf` (baseline, untouched). Never writes to Neo4j.

- `scripts/llm_client.py`: DeepSeek (`https://api.deepseek.com`, `deepseek-chat`, `DEEPSEEK_API_KEY`), retry + exponential backoff, `response_format=json_object`.
- `scripts/sparql_v2.py`: grounded Wikidata query (P27 / P39 / P97 / P53 tied to Indonesia), 301-1945 CE date filter, structured relations (P22/25/26/40/3373/53/39/1365/1366), id/en sitelinks.
- `scripts/wiki_guard.py`: Wikipedia fetch (id first, QID sitelink first), domain keyword guard, quote verification.
- `scripts/pipeline_graf.py`: orchestrator (experiment: `--names-file data/sample_v2_names.txt`).
- `scripts/eval_v2_vs_old.py`: comparison report -> `docs/v2_vs_old_report.md`.
- `graph_rag_bot.py` / `mcp_agent.py`: now call DeepSeek via `llm_client` (JSON mode only for Text-to-Cypher; tool-calling and prose answers cannot use JSON mode).

Not changed: `analisis_graf.py` (metrics), Neo4j load queries.
