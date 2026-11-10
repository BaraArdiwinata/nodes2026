# Slide Outline + Speaker Notes (English, 25 min + 5 Q&A)

Core message: **Open knowledge graphs are sparse and dirty. We healed one with LLMs, then let an LLM agent reason over it through MCP, safely.**

Speakers: **B** = Bara, **A** = Annisa. Database-derived numbers were verified against the live Neo4j on 2026-11-10; see `04_verified_metrics.md`.

---

### 1. Title (0:00, B, 1 min)
- NusantaraGraph: healing a pre-colonial genealogy graph and querying it with an MCP agent
- Bara Ardiwinata, Annisa Nur Fauzi, ITS Surabaya
- Notes: one-line intro each; say "Nusantara = the Indonesian archipelago".

### 2. Hook (1:00, B, 2 min)
- Show a real Wikidata/DBpedia result: empty parents, two names for one person ("Sri Rajasanagara" / "Hayam Wuruk"), mojibake (`Ã…Å¡akti`).
- Question: "Can an LLM answer 'how are these two rulers related?' without hallucinating?"
- Notes: the answer is only yes if the graph is trustworthy AND the LLM queries it instead of guessing.

### 3. Five compounding failures (3:00, B, 2 min)
- Relational sparsity, entity duplication, encoding corruption, Jaccard distortion, static retrieval ceiling.
- Notes: "compounding" = each one hides or amplifies the next. Do not quote the 18% / 43% figures (no source in the repo).

### 4. Graph data model (5:00, A, 3 min)
- `Person` (name, role, dates, dynasty, metrics) and `Kingdom` (name, capital, religion, yearStart, metrics); unique constraints on `name`.
- Relationships: `MEMIMPIN_ATAU_TERAFILIASI`, `AYAH`, `IBU`, `ANAK`, `PASANGAN`, `SAUDARA`, `KERABAT`, `MENGGANTIKAN`, `DIGANTIKAN_OLEH`.
- Screenshot: Neo4j Browser subgraph.
- Notes: time and place are properties, not nodes. Be upfront: no Event/Place nodes yet.

### 5. Phase 1: enrichment pipeline (8:00, A, 3 min)
- 5 stages: SPARQL fetch, encoding healer, entity disambiguation, LLM imputer, graph analytics.
- Tell two stories only: (a) recursive cp1252 healer turns `Ã…Å¡akti` into `Śakti`; (b) RapidFuzz + LLM + Union-Find produce one `master_id` per person.
- Notes: SPARQL `VALUES` lookup avoided timeouts. README claims ~11 s and the dashboard claims 3.04 s average latency; neither is reproducible from the repo, so say "seconds instead of timeouts" and quote no figure.

### 6. Trust and provenance (11:00, A, 2 min)
- Every row carries `source` (wikidata / llm_imputed / original), `confidence_score`, `manual_check`.
- Current dataset: 354 wikidata, 49 llm_imputed, 3 original rows (406 total). Neo4j: 356 Person (139 with metrics), 24 Kingdom, 734 relationships.
- Notes: say provenance lives in the CSV and is the next thing to load into the graph. Verified: 49 of 406 rows (12%) are `llm_imputed`, mean confidence 0.82. Do NOT quote "88% / 95 of 108": it cannot be reproduced from the dataset.

### 7. Graph analytics (13:00, A, 2 min)
- PageRank, Louvain, Betweenness, Adamic-Adar; computed in NetworkX, stored as node properties.
- Why Adamic-Adar replaces Jaccard: sparse nodes gave 0/0 or a false 100%; Adamic-Adar weights shared neighbours by rarity.
- Results (live DB): top PageRank Abu al-Mahasin (Banten, 0.0062), then Sri Isyana Tunggawijaya, Alauddin al-Qahhar (Aceh); top bridge Sunan Gunung Jati (0.050), then Maulana Hasanuddin; 26 Louvain clusters.
- Notes: if asked about GDS, answer honestly (see Q&A prep). Transition: "We now have a clean, scored graph. How do we let an LLM use it safely? Bara."

### 8. Architecture: MCP + Neo4j (15:00, B, 2 min)
- Diagram: user -> `mcp_agent.py` (LLM loop via OpenRouter) -> stdio JSON-RPC -> `mcp_server.py` (FastMCP) -> Neo4j.
- 5 tools: shortest path, person info, person relationships, kingdom info, analytical query.
- Notes: the agent maps MCP `inputSchema` straight to the LLM tool format, so adding a tool = adding one decorated function.

### 9. Safe Text-to-Cypher (17:00, B, 1.5 min)
- `retrieve_analytical_query`: schema-aware prompt, strip markdown fences, auto `LIMIT 25`, read-only regex guard with word boundaries.
- Proof: DELETE and SET rejected; "Setyawati" and "Asset" pass.
- Notes: admit it is a regex guard; production would add read-only transactions / a read-only DB user.

### 10. Live demo (18:30, B types, A narrates graph, 4.5 min)
- See `02_demo_script.md`.

### 11. Lessons learned (23:00, A, 1 min)
- Name variants kill lookups; LLM imputation needs provenance; nodes created by relationship `MERGE` get no metrics (174 Person without Louvain cluster in our test); a query on a kingdom name that does not match returns 0 rows.

### 12. Takeaways and future work (24:00, B, 1 min)
- Takeaways: (1) heal data before analysing it; (2) expose the graph as tools, not as prompt text; (3) guard LLM-generated Cypher.
- Future: Neo4j GDS for metrics, provenance in the graph, vector index + GraphRAG hybrid, read-only transactions, conversation memory, Event/Place nodes.

### 13. Q&A and links (25:00, B + A)
- Repo, contact. Split answers: A = data/modeling, B = MCP/LLM/security.
