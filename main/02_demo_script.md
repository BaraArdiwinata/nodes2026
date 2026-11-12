# Demo Script (4.5 min)

> **Read-aloud version:** the demo dialogue (Annisa hosts and translates, Bara operates) is in [`09_full_script.md`](09_full_script.md), slide 15. This file keeps the technical checklist and failure playbook. Expected outputs below were observed on the DeepSeek agent (`pipeline-deepseek-v2/`) against the live Neo4j; the wording of answers changes a little on every run, but tool names, numbers and Cypher stay the same.

## Pre-flight (do before going live)
- Neo4j Desktop running (instance green), data loaded (380 nodes: 356 Person + 24 Kingdom).
- Neo4j graph view open in one window (Bloom or Query tool), terminal in another (font >= 18-20 pt).
- Start the agent from the **V2 folder with Python 3.12** (plain `python` is Python 3.13, which is not the tested path). The agent starts `mcp_server.py` by itself; there is no need to start the server separately.
```powershell
cd C:\Users\Pongo\nodes2026\pipeline-deepseek-v2
& "C:\Users\Pongo\AppData\Local\Programs\Python\Python312\python.exe" mcp_agent.py
```
- Wait for `Koneksi sukses! Berhasil memuat 5 tools dari mcp_server.py.`
- Warm up once about 10 minutes before (ask one question, `exit`, restart the agent fresh). Check the DeepSeek balance. Backup video ready at `main/backup/`.

**Rule:** type only the prompts below; the agent has no conversation memory, so no follow-up questions. Confirm each name's exact spelling in the DB beforehand. Each answer takes about 9-13 seconds.

## Steps

| # | Time | Who | Do | Say | Expected (observed) |
|---|---|---|---|---|---|
| 1 | 0:30 | A asks, B shows | Neo4j graph of Kesultanan Banten (query S2 in `07_bara_prep_final.md`). Point at the gold node and at **Abu al-Mahasin**. Node sizes are uniform in the Query tool; only claim "size = PageRank, colour = Louvain" if the Bloom view is really styled that way | "Each dot is a person, the gold one is the sultanate. Abu al-Mahasin has the highest PageRank in the whole graph." | Banten dynasty graph with names visible |
| 2 | 1:00 | B | Terminal: `Siapa Abu al-Mahasin dan apa peran jaringannya?` | "The agent chose two tools by itself." | Log: `retrieve_person_info`, then `retrieve_person_relationships`. Answer: tied to Kesultanan Banten, died 1733, PageRank 0,00622, Louvain cluster 14, son of Abu an-Nasr, father of Syifa Zainularifin and Wasi Zainulalimin, brother of Abu al-Fadhl. It also flags the `DIGANTIKAN_OLEH` noise (Bantam Presidency, Batavia...) and ignores it. **Do not read the "role" field** ("Abu an-Nasr", a data quirk) |
| 3 | 1:00 | B+A | `Bagaimana hubungan terpendek antara Rara Santang dan Pangeran Walangsungsang?` then A optionally runs the shortestPath query in the graph view | "Same answer, two ways: agent and raw Cypher." | Log: `retrieve_shortest_path`. **The first call may show empty arguments `{}`; the agent retries with `name1`/`name2` by itself** (say: "the agent noticed and retried"). Answer: 2 steps, Rara Santang -> Kesultanan Cirebon -> Pangeran Walangsungsang; no direct family relationship recorded in the graph |
| 4 | 1:00 | B | `Tampilkan 5 tokoh dengan PageRank tertinggi di Kesultanan Banten` | "For aggregates, the agent writes Cypher itself. Look at the generated query." | Log: `retrieve_analytical_query`, then a line `[Generated Cypher]` with `MATCH (p:Person)-[:MEMIMPIN_ATAU_TERAFILIASI]->(k:Kingdom {name: 'Kesultanan Banten'}) RETURN p.name AS name, p.pagerank_score AS pagerank ORDER BY pagerank DESC LIMIT 5`. Table: Abu al-Mahasin 0,006222; Abu an-Nasr 0,005387; Tirtayasa dari Banten 0,004293; Abu al-Ma'ali 0,004261; Abu al-Fadhl 0,004142. The agent notes the scores are close and no single figure dominates |
| 5 | 0:45 | B | `Hapus semua tokoh Majapahit` | "Now the guard." | **Observed:** no tool is called. The model answers that the system is **read-only** and offers read-only alternatives. The guard message `Only read-only operations are allowed` does **not** appear in the terminal. Say: "Even the model refuses; if it had tried to write a delete query, the guard would have stopped it", then show slide 14 (real rejection from `--test-analytical`) |

**Avoid:** Kerajaan Pajajaran PageRank (returns 0 rows), any follow-up question, any name not pre-checked, reading long answers aloud (translate only the key facts).

## Failure playbook
- **No answer after 20 s:** Annisa fills the pause ("the agent calls tools in a loop, then writes the answer"). The client already retries DeepSeek 429/5xx/timeouts with exponential backoff (can add about 30 s in the worst case).
- **25-30 s with no output, or `Maaf, terjadi kesalahan saat menghubungi AI`:** Ctrl+C, play the recorded run: "Let me show the recorded run, same system, same prompts." Do not debug live.
- **DeepSeek down, Neo4j up:** continue without the LLM for steps 3-4 using Cypher in the graph view (S3 shortestPath, and the top-5 Banten query): "Same answer, without the agent."
- **Neo4j down:** only person info, person relationships and kingdom info fall back to the CSV (step 2 still works). Shortest path and the analytical tool need Neo4j, so use the video for steps 3-5.
- **MCP server timeout at startup:** re-run once (startup is slow on Windows; client timeout is 60 s); otherwise the video.
- **Odd or wrong wording in an answer:** do not argue on stage: "The numbers come from the graph; the wording is the model's."
