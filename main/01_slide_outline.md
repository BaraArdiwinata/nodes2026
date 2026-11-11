# Slide Outline v3: "Jas Merah" storyline (English, 25 min + Q&A)

Deck: [`NusantaraGraph_NODES2026.pptx`](NusantaraGraph_NODES2026.pptx). Full speaker script per slide is in the PowerPoint **speaker notes**; this file is the map. Speaker split is decided separately.

**Flow:** hook (quote → problem → question) → who we are → the problem → our answer, feature by feature → demo → lessons → close.
**Core message:** history is about connections, so we made Indonesian royal history explorable as a graph. Every feature answers a problem the previous step revealed.
**Numbers:** only from the live Neo4j (2026-11-10), see `04_verified_metrics.md`.

| # | Time | Section | Slide | One message |
|---|---|---|---|---|
| 1 | 0:00 | Hook | Jas Merah | "Never abandon history": a phrase every Indonesian student knows |
| 2 | 0:45 | Hook | History class was a list | Lists are easy to forget; history is connections |
| 3 | 1:45 | Hook | One family, three kingdoms | Pajajaran → Cirebon → Banten: three chapters in a textbook, one path in a graph (illustration) |
| 4 | 2:45 | Hook | The question | Can we make history explorable, instead of memorised? |
| 5 | 3:15 | Who we are | Two students, one curious question | ITS students; NusantaraGraph; a learning journey, not a production system |
| 6 | 4:15 | The problem | Why a graph | Relationships are the data; "how are they connected?" = one Cypher query |
| 7 | 5:15 | The problem | The data fought back | 5 compounding problems: missing relations, duplicates, broken text, misleading similarity, text search can't hop |
| 8 | 7:15 | Our answer | Collect, heal, analyse, ask | 4-step overview; each step answers specific problems |
| 9 | 8:30 | Our answer | Graph model | Person + Kingdom, 9 relationship types; 356 / 24 / 734 |
| 10 | 10:00 | Our answer | Heal: problem → fix | Encoding healer, dedup, LLM imputation (49 of 406 rows, labelled), Adamic-Adar |
| 11 | 12:00 | Our answer | What the graph told us | PageRank top 3; Sunan Gunung Jati #1 bridge, his son #2; 26 Louvain clusters |
| 12 | 14:00 | Our answer | Nobody wants to write Cypher | LLM alone invents history; we want graph-grounded answers |
| 13 | 15:00 | Our answer | MCP: graph as tools | You → Agent → MCP → server (5 tools) → Neo4j |
| 14 | 16:45 | Our answer | Guard for LLM-written queries | Allowed vs blocked; whole-word matching; 25-row cap |
| 15 | 18:00 | Demo | Live demo | 5 steps, see `02_demo_script.md` |
| 16 | 22:30 | Wrap-up | Lessons learned | Names are hardest; 217 nodes unscored; paper trail; V2 quote verification |
| 17 | 23:45 | Wrap-up | Closing: Jas Merah again | 3 takeaways + "we'd love your feedback on" |
| 18 | 24:45 | Wrap-up | Terima kasih / Q&A | Names, repo |
| 19-21 | - | Backup | GDS vs pre-computed; V1 vs V2 table; relationship counts | Show only if asked |

## Before the talk
- Check the slide 3 history facts (Rara Santang mother of Sunan Gunung Jati; Maulana Hasanuddin founded Banten).
- Run the slide 6 Cypher in Neo4j Browser to confirm both names exist with that spelling.
- Add a Neo4j Browser screenshot to slide 11 (size = PageRank, colour = Louvain) and a repo QR to slide 18.
- Make sure the repo is public before showing its link.
- The Cypher on slide 14 is illustrative; point at the real generated query during the demo.
