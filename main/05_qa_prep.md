# Q&A Prep (A = Annisa, B = Bara)

| Likely question | Honest answer | Who |
|---|---|---|
| Why not Neo4j GDS for PageRank/Louvain? | We did start with GDS in the prototype (UTS stage: `gds.pageRank`, `gds.louvain`, `gds.nodeSimilarity` on an in-memory projection). For the final version we deliberately switched to pre-computed metrics from NetworkX for ingestion efficiency and pipeline modularity. GDS remains the natural next step for live recomputation. | A |
| Why store metrics as node properties instead of computing live with GDS? | (1) Graph is small and mostly static, so a metric changes only when the data changes, not per query. (2) One pipeline produces a single enriched CSV; `LOAD CSV` is idempotent and needs no GDS plugin or projection step, so the demo runs on any Neo4j instance (including Aura Free / Desktop). (3) Agent tools just read a property (cheap, deterministic, same value in the CSV fallback when Neo4j is down). (4) Pre-computing let us swap algorithms freely, e.g. replacing Jaccard (`gds.nodeSimilarity`) with Adamic-Adar and adding Betweenness without touching the database. Trade-off we accept: metrics go stale after data changes until the pipeline reruns, and nodes created only by relationship `MERGE` have no scores. Next step: write results back with `gds.*.write` or recompute on schedule. | A |
| Did Jaccard cause problems? | Yes: in the GDS prototype `gds.nodeSimilarity` is Jaccard and gave false 100% for sparse nodes. We replaced it with Adamic-Adar. Do not quote the "18%" figure unless verified. | A |
| How accurate is the LLM imputation? | Rows carry `source=llm_imputed` and a `confidence_score` (about 0.8-0.9). We did not run a formal accuracy study; confidence is a heuristic, not a calibrated probability. Success-rate figure: use only the verified number. | A |
| Is the regex read-only guard enough? | No, it is a first layer. Production: read-only DB user or `execute_read` transactions, query allow-lists, timeouts. | B |
| Why MCP instead of plain function calling? | One server, any MCP client (Claude Desktop, Inspector, our agent); tool schemas are discovered, not hand-copied. | B |
| Why are `ANAK` and `AYAH` both modelled? | They are loaded from separate source columns; the same fact can appear in both directions. A cleanup into one canonical direction is future work. | A |
| Does the agent remember earlier questions? | Not currently: history is rebuilt per question. Easy fix: keep `messages` across turns. | B |
| How do you avoid hallucination? | The system prompt forces tool calls first and answers are built from tool JSON; it reduces but does not eliminate errors. Provenance in the graph would let the agent cite confidence. | B |
| Fallback when Neo4j is down? | Person and kingdom lookups fall back to the CSV; path and analytical tools need Neo4j. | B |
| How did you resolve duplicate people? | RapidFuzz fuzzy match, LLM confirmation for borderline scores, Union-Find to assign one `master_id`. State the thresholds you verified in the code. | A |
| Why Adamic-Adar over Jaccard? | Jaccard gave 0/0 or false 100% on sparse nodes; Adamic-Adar weights shared neighbours by 1/log(degree). | A |
| Is the history correct? | The graph is only as good as Wikidata/DBpedia/Wikipedia plus LLM extraction; it is a research prototype, not a historical authority. | A |
| Event / place modelling? | Not modelled yet; only properties (capital, dates). Planned. | A |
| Scale? | About 400 rows / 139 unique people; a small proof of concept. Pipeline cost is dominated by LLM and SPARQL calls. | B |
