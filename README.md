# NusantaraGraph: Tracing Indonesian Royal Genealogies with Neo4j, MCP, and LLM Agents

**NODES 2026 (Neo4j Developer Conference)**
Speakers: **Bara Ardiwinata** and **Annisa Nur Fauzi**, Information Systems, Institut Teknologi Sepuluh Nopember (ITS), Surabaya.

NusantaraGraph reconstructs the genealogies and succession lines of pre-colonial Indonesian kingdoms (Majapahit, Aceh, Banjar, Banten, Mataram, and others) from sparse open data, stores them in Neo4j, and lets an LLM agent query the graph through the Model Context Protocol (MCP).

> Research prototype. Data comes from Wikidata, DBpedia, Wikipedia, and LLM extraction. It is not a historical authority.

---

## Workspace structure

| Path | Purpose |
|---|---|
| [`main/`](main) | Conference preparation: report, slide outline, demo script, verified Cypher cheat-sheet, verified metrics, Q&A prep, day-of checklist |
| [`copy-of-repo-eas-graf/`](copy-of-repo-eas-graf) | **Baseline pipeline V1**: the dataset currently loaded in Neo4j. Keep unchanged as the fallback |
| [`pipeline-deepseek-v2/`](pipeline-deepseek-v2) | **Experimental pipeline V2**: DeepSeek, grounded SPARQL, Wikipedia guardrail, quote verification (see its [README](pipeline-deepseek-v2/README.md)) |
| [`docs/`](docs) | Original course report (PDF) and the presentation dashboard (PNG) |

Files in `main/`:

| File | Content |
|---|---|
| [`00_laporan_nodes2026.md`](main/00_laporan_nodes2026.md) | Full project refresher, presentation strategy, and a list of inconsistencies found in the original docs |
| [`01_slide_outline.md`](main/01_slide_outline.md) | 13-slide outline with speaker notes (English) |
| [`02_demo_script.md`](main/02_demo_script.md) | Live demo script and failure playbook |
| [`03_cypher_cheatsheet.cypher`](main/03_cypher_cheatsheet.cypher) | Ingestion, data-quality checks, and demo-ready queries |
| [`04_verified_metrics.md`](main/04_verified_metrics.md) | Numbers measured on the live Neo4j instance |
| [`05_qa_prep.md`](main/05_qa_prep.md) | Likely audience questions with honest answers |
| [`06_checklist_hari_h.md`](main/06_checklist_hari_h.md) | Technical checklist from H-3 to the day of the talk (Indonesian) |

---

## What the system does

```
Wikidata / DBpedia / Wikipedia --> enrichment pipeline (clean, dedupe, LLM impute)
        --> CSV + NetworkX metrics (PageRank, Louvain, Betweenness, Adamic-Adar)
        --> Neo4j (LOAD CSV)  <--  mcp_server.py (FastMCP, stdio)  <--  mcp_agent.py (LLM tool-calling)
```

**Graph model** (final version): nodes `Person` and `Kingdom` (unique `name`); relationships `MEMIMPIN_ATAU_TERAFILIASI`, `AYAH`, `IBU`, `ANAK`, `PASANGAN`, `SAUDARA`, `KERABAT`, `MENGGANTIKAN`, `DIGANTIKAN_OLEH`. Graph metrics are pre-computed in NetworkX and stored as node properties. The prototype stage used Neo4j GDS directly; the final version switched to pre-computed metrics for ingestion efficiency and pipeline modularity.

**MCP tools** (5, registered in `mcp_server.py`): `retrieve_shortest_path`, `retrieve_person_info`, `retrieve_person_relationships`, `retrieve_kingdom_info`, `retrieve_analytical_query` (Text-to-Cypher with a read-only guard).

### Verified numbers (live Neo4j, 2026-11-10)
| Item | Value |
|---|---|
| `Person` nodes | 356 (139 with graph metrics) |
| `Kingdom` nodes | 24 |
| Relationships | 734 |
| Louvain clusters | 26 |
| Top PageRank | Abu al-Mahasin (Banten) |

Details and caveats (for example, metrics in the database differ slightly from the current CSV) are in [`main/04_verified_metrics.md`](main/04_verified_metrics.md).

---

## Quickstart

Requirements: Python 3.12+, Neo4j Desktop (Neo4j 5.13 or newer is recommended for the cheat-sheet queries), a DeepSeek API key (V2) or an OpenRouter key (V1 baseline).

### 1. Python environment
```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install pandas requests wikipedia-api python-dotenv networkx mcp rapidfuzz neo4j
```

### 2. Configure `.env`
Each pipeline folder reads its **own** `.env` (the repository root has none). Copy the template below into `copy-of-repo-eas-graf/.env` and/or `pipeline-deepseek-v2/.env`. Never commit these files; `.gitignore` already excludes them.

```env
# Neo4j (local)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password

# V2 pipeline and agent
DEEPSEEK_API_KEY=your-deepseek-key

# V1 baseline only
OPENROUTER_API_KEY=your-openrouter-key
```

### 3. Start Neo4j and load the data
1. Start a local Neo4j instance (port 7687).
2. Copy `copy-of-repo-eas-graf/data/dataset_dinasti_final_with_metrics.csv` into the instance's `import` folder.
3. In Neo4j Browser, run the sections of [`main/03_cypher_cheatsheet.cypher`](main/03_cypher_cheatsheet.cypher) in order: **1 (Ingestion and schema)**, **2 (Data quality)**, then **3 (Showcase queries)**.

The cheat-sheet marks which queries were verified against the live database. Queries tagged `[RUN-TEST]` must be tried before using them on stage, and names such as `Rara Santang` must match the spelling in your database.

### 4. Run the agent (V1 baseline)
```bash
cd copy-of-repo-eas-graf
python mcp_agent.py
```
Example prompt: `Siapa Abu al-Mahasin dan apa peran jaringannya?`. The agent starts `mcp_server.py` over stdio, lists its tools, and calls them as needed. The V2 folder contains an agent that calls DeepSeek instead of OpenRouter (`pipeline-deepseek-v2/mcp_agent.py`).

### 5. Re-run analytics or the V2 experiment
See [`pipeline-deepseek-v2/README.md`](pipeline-deepseek-v2/README.md).

---

## Safety notes
- `.env` files, virtual environments, and Python caches are git-ignored. Rotate any API key that was ever shared.
- The Text-to-Cypher tool uses a regex read-only guard. It is a first layer, not a substitute for a read-only database user.
- The V2 pipeline never writes to Neo4j.

## Authors
Bara Ardiwinata (NRP 5026231232) and Annisa Nur Fauzi (NRP 5026231228), Information Systems, ITS.
