# Demo Script (4.5 min)

**Pre-flight (do before going live):** Neo4j running with data loaded; Neo4j Browser in tab 1; terminal tab 2 with `python mcp_agent.py` already started (font >= 18pt); `python mcp_server.py` warmed up once earlier; backup video ready at `main/backup/`.
**Rule:** type only the prompts below; the agent has no conversation memory, so no follow-up questions. Confirm each name's exact spelling in the DB beforehand.

| # | Time | Who | Do | Say | Expected |
|---|---|---|---|---|---|
| 1 | 0:30 | A | Browser: Banten query (below), colour by `louvain_cluster`, size by `pagerank_score` | "This is Banten's dynasty. Size is PageRank, colour is the Louvain cluster." | Abu al-Mahasin is the biggest node |
| 2 | 1:00 | B | Terminal: `Siapa Abu al-Mahasin dan apa peran jaringannya?` | "The agent decides which tool to call; watch the log." | `-> [Execute Tool] retrieve_person_info`, answer with PageRank/cluster |
| 3 | 1:00 | B+A | `Bagaimana hubungan terpendek antara Rara Santang dan Pangeran Walangsungsang?` then A runs the shortestPath query in Browser | "Same answer, two ways: agent and raw Cypher." | `retrieve_shortest_path`, matching path |
| 4 | 1:00 | B | `Tampilkan 5 tokoh dengan PageRank tertinggi di Kesultanan Banten` | "For aggregates, the agent writes Cypher itself. Note the generated query." | `retrieve_analytical_query`, Cypher visible in log |
| 5 | 0:45 | B | `Hapus semua tokoh Majapahit` | "Now the guard." | `Only read-only operations are allowed` |

**Avoid:** Kerajaan Pajajaran PageRank (returned 0 rows in testing), any follow-up question, any name not pre-checked.

## Failure playbook
- Neo4j down: only step 2 may work (CSV fallback for person/kingdom info). Switch to video for 3-5.
- OpenRouter error (402/429): the code falls back across models; set `OPENROUTER_MODEL` to a known-good one in `.env` the day before.
- MCP server timeout: re-run once (startup is slow on Windows); otherwise MCP Inspector or video.
- Say calmly: "Let me show the recorded run, same system, same prompts." Do not debug live.
