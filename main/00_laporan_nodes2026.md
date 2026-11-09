# Laporan Persiapan NODES 2026: NusantaraGraph

Penulis: Bara Ardiwinata & Annisa Nur Fauzi (ITS, Sistem Informasi)
Sumber: README, PRD, `docs/` (task, walkthrough, PDF Evaluasi Akhir Semester, PNG Presentation Dashboard), `mcp_server.py`, `mcp_agent.py`, `scripts/`, `database/`, `data/`.
Tidak dibaca dengan sengaja: `.env` (berisi kredensial).

---

## 0. PERINGATAN: Inkonsistensi yang Harus Diselesaikan Sebelum Tampil

Ini temuan paling penting. Audiens Neo4j akan membaca kode.

| # | Klaim di dokumen/slide | Kenyataan di kode | Risiko | Tindakan |
|---|---|---|---|---|
| 1 | "6 live tools": `lookup_figure`, `get_genealogy`, `find_connection_path`, `get_influential`, `get_community`, `find_similar` (README, PDF, dashboard PNG) | `mcp_server.py` hanya mendaftarkan **5 tools**: `retrieve_shortest_path`, `retrieve_person_info`, `retrieve_person_relationships`, `retrieve_kingdom_info`, `retrieve_analytical_query`. Enam nama tool di dokumen **tidak ada** di kode. README sendiri bertentangan (bagian MCP menulis 5, bagian lain 6). | Tinggi: klaim tidak bisa didemokan | Pakai 5 tool yang nyata di slide, atau implementasikan 6 tool itu sebelum hari-H |
| 2 | "Neo4j 5.x, GDS Louvain, PageRank di Neo4j" (dashboard) | **Versi final**: semua metrik dihitung offline di NetworkX (`analisis_graf.py`) lalu di-`LOAD CSV` sebagai properti node. **Prototipe UTS** (riwayat kueri, graf `utsGraf`, label `:Tokoh`/`:Kerajaan`) memang memakai GDS native (`gds.pageRank`, `gds.louvain`, `gds.nodeSimilarity`). | Sedang: audiens Neo4j akan bertanya soal GDS | Narasi resmi: "Awalnya pada tahap prototipe digunakan Neo4j GDS secara langsung, namun pada versi final diputuskan untuk menggunakan pre-computed metrics dari NetworkX demi efisiensi ingestion dan modularitas pipeline." Jangan klaim GDS pada versi final |
| 3 | "88% berhasil ditambal (95 dari 108)" | CSV final: `source` = 354 wikidata, 49 llm_imputed, 3 original (406 baris). Angka 95/108 tidak bisa diverifikasi dari dataset | Sedang | Verifikasi dari log pipeline, atau ganti dengan angka dari CSV |
| 4 | "~400+ nodes enriched", "354 tokoh" (PDF), "3.04s avg latency" (PNG), "~11 detik" (README) | CSV: 406 baris, **139 nama `orang` unik**, 24 kerajaan, 26 klaster Louvain. 354 = jumlah baris `wikidata`, bukan jumlah tokoh. Node `Person` di Neo4j lebih banyak karena relasi `MERGE` membuat node ayah/ibu/anak. Latensi 3.04s vs 11s tidak konsisten | Sedang | Hitung ulang di Neo4j: `MATCH (p:Person) RETURN count(p)`, pakai angka itu |
| 5 | Dedup: README "fuzzy >=85% + LLM"; walkthrough "auto-merge >=90%, 75-89% manual_check"; PDF "token_sort_ratio, bonus +5 kingdom, 75-90% divalidasi LLM" | Tiga versi threshold berbeda | Rendah-sedang | Cek `apply_entity_disambiguation` di `pipeline_graf.py:333`, pilih satu versi |
| 6 | Klaim "Jaccard menghasilkan false-merge 18%", "node count naik ~43%" (dashboard) | Tidak ada perhitungan di kode/dokumen lain | Sedang | Hapus atau sertakan bukti |
| 7 | Hasil tes di walkthrough: kueri PageRank Pajajaran mengembalikan **0 baris** (nama `Kerajaan Pajajaran` tidak cocok); 174 Person punya `louvain_cluster = None` | Node yang dibuat via `MERGE` relasi (ayah/anak) tidak mendapat metrik | Sedang | Hindari kueri ini di demo; pakai Majapahit/Banten/Aceh |
| 8 | Louvain: PDF menyebut "Louvain memetakan dinasti di Bali"; `get_community` baca "community_louvain" | Kolom sebenarnya `orang_Louvain_Cluster`, tool `get_community` tidak ada | Rendah | Ikuti kode |
| 9 | Fallback CSV "self-healing" | Hanya ada di `retrieve_person_info`/`kingdom_info` (`get_metrics_from_csv`). `retrieve_shortest_path` dan `retrieve_analytical_query` butuh Neo4j | Sedang: jangan klaim semua tool punya fallback | Cek `graph_rag_bot.py:125-350` |
| 10 | Model LLM: "Gemini Flash" | `mcp_agent.py` lewat OpenRouter dengan fallback beberapa model (default `google/gemini-2.5-flash`, lalu model free) | Rendah | Sebut "via OpenRouter" |
| 11 | Skema Neo4j | Relasi `AYAH`, `IBU`, `ANAK`, dll. arahnya Person -> Person ("p)-[:AYAH]->(ayah)"); `ANAK` dan `AYAH` redundan (keduanya dimuat dari dua kolom CSV, bisa menghasilkan relasi ganda arah berlawanan) | Rendah | Siapkan jawaban jika ditanya soal modeling |
| 12 | `.env` ikut di folder repo | Task log menyebut riwayat Git sudah dibersihkan; `.env` tetap ada di workspace | Keamanan | Pastikan `.env` ada di `.gitignore`, rotasi API key OpenRouter sebelum screen-share |
| 13 | Riwayat kueri Neo4j (diekspor 2026-11-09) | `louvain_cluster` pernah di-patch dengan `SET p.louvain_cluster = row.orang_Louvain_Cluster` **tanpa `toInteger`**; node yang sudah ada mempertahankan nilai itu lewat `coalesce`, sehingga bisa tersimpan sebagai STRING. Kueri cek duplikat relasi memakai `a.orang`/`b.orang` (properti tidak ada, hasil selalu null). Relasi `SAUDARA` self-loop sempat muncul dan dihapus manual; skrip import repo belum memfilternya | Sedang: sort/agregasi klaster salah, demo bisa aneh | Jalankan cek `valueType(p.louvain_cluster)` (cheatsheet 2.4), patch ulang (1.5), pakai versi import dengan filter self-loop (1.4) |

---

## 0b. Iterasi Proyek (dari Riwayat Kueri Neo4j)

Kueri KRL/Commuter Line (`CommuterGraph`, `Station`, `Train`) di riwayat adalah tugas lain dan diabaikan.

| Fase | Label & properti | Relasi | Metrik graf | Sumber data |
|---|---|---|---|---|
| **UTS / ETS** | `:Tokoh`, `:Kerajaan` (properti `nama`, `peran`, `agama`, `tahun_mulai`, `ibu_kota`) | `BERKUASA_DI`, `AYAH_DARI` (ayah -> anak), `IBU_DARI`, `MENIKAH_DENGAN` | **GDS native** pada proyeksi `utsGraf` (UNDIRECTED): `gds.pageRank`, `gds.louvain`, `gds.nodeSimilarity` (dilabeli `Skor_Jaccard`) | `dataset_gabungan_uts_graf.csv` |
| **EAS / final** | `:Person`, `:Kingdom` (properti `name`, dst.) | 9 tipe (arah anak -> orang tua untuk `AYAH`/`IBU`) | **Pre-computed di NetworkX**, dimuat bersama CSV sebagai properti node | `dataset_dinasti_final_with_metrics.csv` |

Alasan peralihan (narasi untuk panggung): *"Awalnya pada tahap prototipe digunakan Neo4j GDS secara langsung, namun pada versi final diputuskan untuk menggunakan pre-computed metrics dari NetworkX demi efisiensi ingestion dan modularitas pipeline."* Bukti pendukung dari riwayat: `gds.nodeSimilarity` adalah Jaccard, konsisten dengan temuan "Jaccard distortion" (failure #4) yang kemudian diganti Adamic-Adar.

Perhatikan perubahan arah relasi: UTS `(ayah)-[:AYAH_DARI]->(anak)`; EAS `(anak)-[:AYAH]->(ayah)`. Kueri lama tidak bisa dipakai di skema baru tanpa penyesuaian.

Pembersihan data yang terbukti dari riwayat: (1) hapus self-loop `SAUDARA`; (2) filter nama kerajaan ("Kingdom/Sultanate/Empire") dari relasi suksesi; (3) kueri deteksi relasi duplikat (perlu diperbaiki, lihat #13).

---

## 1. Rekapitulasi Proyek

### 1.1 Judul & Gambaran Umum
- Judul repo: **NusantaraGraph: AI-Powered Genealogy Reconstruction for Pre-Colonial Nusantara** (juga "Nusantara Dynasty Knowledge Graph").
- Judul laporan EAS: *NusantaraGraph: Platform Data Engineering Hibrida Dua Fase Berbasis MCP Server untuk Pengayaan dan Analisis Jaringan Silsilah Kerajaan Prekolonial*.
- Judul dashboard NODES: *Knowledge Graph & Model Context Protocol (MCP) Integration for Nusantara Dynasties*.
- Domain: silsilah dan suksesi tokoh kerajaan prekolonial Indonesia (Majapahit, Aceh, Banjar, Banten, Mataram, Klungkung, dan lainnya; 24 kerajaan, 139 tokoh unik di CSV final).
- Kelanjutan dari tugas UTS/ETS (`dataset_gabungan_uts_graf.csv` -> `dataset_dinasti_final.csv` -> `..._with_metrics.csv`, masing-masing 406 baris).

### 1.2 Problem Statement & Use Case
Data sejarah di Wikidata/DBpedia untuk tokoh regional tidak lengkap dan kotor. "5 Compounding Failures":
1. **Relational sparsity**: ayah/ibu/pasangan kosong, jalur silsilah putus.
2. **Cross-source entity duplication**: "Sri Rajasanagara" vs "Hayam Wuruk" menjadi phantom node.
3. **Encoding corruption (CP1252)**: `Ã…Å¡akti` seharusnya `Śakti`.
4. **Jaccard distortion**: simpul sepi tetangga bernilai 100% semu.
5. **Static retrieval ceiling**: RAG teks statis tidak bisa multi-hop / agregasi.

Insight yang dituju: siapa tokoh paling berpengaruh, siapa penghubung antar-dinasti, bagaimana dua tokoh terhubung, dan klaster dinasti apa yang terbentuk secara alami.

### 1.3 Graph Modeling & Ontologi (dari `neo4j_load_queries.cypher`)

**Node**
| Label | Properti | Constraint |
|---|---|---|
| `Kingdom` | `name`, `capital`, `religion`, `yearStart`, `wikidataID`, `pagerank_score`, `louvain_cluster`, `betweenness_score` | `name` UNIQUE |
| `Person` | `name`, `role`, `birthDate`, `deathDate`, `wikidataID`, `dynasty`, `pagerank_score`, `louvain_cluster`, `betweenness_score`, `adamic_adar_avg` | `name` UNIQUE; index pada `role` |

**Relationship**
| Tipe | Arah | Makna |
|---|---|---|
| `MEMIMPIN_ATAU_TERAFILIASI` | Person -> Kingdom | afiliasi / kepemimpinan |
| `AYAH`, `IBU` | Person -> Person (orang tua) | silsilah vertikal |
| `ANAK` | Person -> Person | silsilah vertikal |
| `PASANGAN`, `SAUDARA`, `KERABAT` | Person -> Person | relasi horizontal |
| `MENGGANTIKAN` / `DIGANTIKAN_OLEH` | Person -> Person | suksesi takhta (P1365/P1366); pendahulu/penerus yang berupa nama kerajaan difilter |

**Representasi**
- Tokoh = `Person`; kerajaan = `Kingdom`; waktu = properti (`birthDate`, `deathDate`, `yearStart`), bukan node `Event`/`Time`.
- **Tidak ada node `Event` atau `Region`/`Place`.** Peristiwa dan wilayah hanya muncul sebagai atribut (`capital`, `religion`). Jangan klaim "event graph".
- Provenance di CSV (belum dimodelkan di graf): `source` (wikidata / llm_imputed / original), `confidence_score` (0.75-1.0 wikidata; ~0.8-0.9 LLM), `manual_check`, `data_source`, `master_id`.
- Catatan modeling: kolom `confidence_score` dan `source` **tidak dimuat** ke Neo4j oleh skrip Cypher. Klaim "auditable confidence di graf" belum benar; ini kandidat perbaikan cepat (tambahkan ke `SET`).

### 1.4 Tech Stack & Arsitektur

- **Database**: Neo4j (Bolt `localhost:7687`), Cypher, `LOAD CSV` dengan `FIELDTERMINATOR ';'`.
- **Python 3.12**: pandas, requests, wikipedia-api, python-dotenv, networkx, rapidfuzz, `mcp` (FastMCP), driver neo4j.
- **LLM**: OpenRouter (Gemini 2.5 Flash + fallback model gratis).

**Phase 1: Enrichment (`scripts/pipeline_graf.py`, `analisis_graf.py`)**
1. SPARQL fetch Wikidata + DBpedia (UNION: `VALUES` nama + pencarian kerajaan Indonesia `wd:Q3024240`/`P17 wd:Q252`).
2. Recursive encoding healer (cp1252 -> UTF-8, sampai 3 level).
3. Entity disambiguation: RapidFuzz + LLM + Union-Find (`master_id`).
4. LLM imputer: Wikipedia -> JSON terstruktur (ayah, ibu, pasangan, anak, `confidence_score`).
5. NetworkX: PageRank (alpha 0.85), Louvain (seed 42), Betweenness, Adamic-Adar.

**Phase 2: MCP**
```
User -> mcp_agent.py (MCP client + OpenRouter LLM loop)
          | stdio (JSON-RPC)
        mcp_server.py (FastMCP, 5 tools)
          | import
        scripts/graph_rag_bot.py (Neo4jConnector, retrieve_* , CSV fallback)
          | Cypher / Bolt
        Neo4j
```
- `mcp_server.py`: `FastMCP("Nusantara Dynasty Graph Server")`, transport **stdio**; tiap tool membungkus fungsi di `graph_rag_bot.py` dan menangkap exception menjadi `{"status":"error"}`.
- `mcp_agent.py`: spawn server sebagai subprocess (`stdio_client`), `session.initialize()`, `list_tools()`, memetakan `inputSchema` MCP ke format OpenAI `tools`, lalu loop: LLM -> `tool_calls` -> `session.call_tool()` -> hasil sebagai `role:"tool"` -> LLM sampai jawaban final. Read timeout 60 dtk (startup Windows).
- Riwayat chat **tidak dipertahankan antar giliran** (`messages` dibuat ulang tiap pertanyaan): agent tidak ingat konteks sebelumnya. Hindari pertanyaan lanjutan ("dia anak siapa?") saat demo.
- Keamanan `retrieve_analytical_query`: Text-to-Cypher dengan prompt skema, lalu guard regex `\b` terhadap `CREATE|MERGE|SET|DELETE|REMOVE|DROP|DETACH|LOAD CSV|apoc.*write*`, plus `LIMIT 25` otomatis. Tes mandiri `--test-analytical` membuktikan: DELETE/SET diblokir, "Setyawati"/"Asset" lolos. Ini cerita kuat untuk audiens.
  - Batasan jujur: guard berbasis regex, bukan transaksi read-only. Praktik terbaik: pakai `session.execute_read` / user Neo4j read-only. Sebutkan sebagai future work.

### 1.5 Temuan Kunci / Fitur Unggulan (terverifikasi dari CSV/log)
- **Tokoh paling berpengaruh (PageRank)**: Abu al-Mahasin (Banten, 0.00697), Sri Isyana Tunggawijaya (Mataram, 0.00678).
- **Tokoh jembatan (Betweenness)**: Sunan Gunung Jati (~0.039 di CSV final; 0.048 di log walkthrough lama).
- **Kerajaan jembatan**: Majapahit (0.0599 di walkthrough). Majapahit juga mendominasi dataset (180 dari 406 baris).
- **Similarity**: pasangan Rara Santang <-> Pangeran Walangsungsang (Adamic-Adar 2.2529, walkthrough); PDF melaporkan Dewa Agung Jambe I 1.4427. Pilih satu sumber dan cek ulang.
- **Louvain**: 26 klaster di CSV; klaster dinasti Bali tervisualisasi.
- **Fitur menonjol untuk panggung**: (1) tool-calling agent via MCP, (2) Text-to-Cypher dengan guard read-only, (3) pipeline penyembuhan data (encoding + dedup + imputasi LLM berprovenance), (4) pengganti Jaccard dengan Adamic-Adar.

---

## 2. Strategi & Alur Presentasi NODES 2026 (25 menit + 5 menit Q&A)

Pesan inti: **"Open knowledge graphs are sparse and dirty; we healed one with LLMs, then let an LLM agent reason over it through MCP, safely."** Bawakan dalam Bahasa Inggris (konferensi internasional); dashboard PNG sudah berbahasa Inggris.

### Slide Outline

| # | Waktu | Slide | Isi | Pembicara |
|---|---|---|---|---|
| 1 | 0:00 | Title | Judul, nama, ITS, QR repo | Bara |
| 2 | 1:00 | Hook | "Who was Hayam Wuruk's mother's sibling's successor?" Tunjukkan hasil Wikidata: kosong / duplikat / mojibake (`Ã…Å¡akti`). Pertanyaan: "Can an LLM answer this without hallucinating?" | Bara |
| 3 | 3:00 | 5 Compounding Failures | Satu slide, 5 ikon (dari dashboard PNG kiri-bawah) | Bara |
| 4 | 5:00 | Graph Data Model | Diagram: `Person`, `Kingdom`, 9 tipe relasi, constraint. Satu screenshot Neo4j Browser | Annisa |
| 5 | 8:00 | Phase 1 Pipeline | 5 stage (dashboard atas). Fokus pada 2 cerita: encoding healer dan dedup (fuzzy + LLM + Union-Find) | Annisa |
| 6 | 11:00 | Trust: provenance | `source`, `confidence_score`, `manual_check`; angka imputasi (setelah diverifikasi) | Annisa |
| 7 | 13:00 | Graph analytics | PageRank, Louvain, Betweenness, kenapa Adamic-Adar > Jaccard (contoh 0/0 dan 100% semu). Screenshot Banten/Bali | Annisa |
| 8 | 15:00 | Architecture: MCP + Neo4j | Diagram agent -> stdio -> FastMCP -> Neo4j; 5 tools | Bara |
| 9 | 17:00 | Safety: Text-to-Cypher guard | Tes 3-5 dari walkthrough (DELETE ditolak, "Setyawati" lolos) | Bara |
| 10 | 18:30 | **Live demo** | Lihat skenario di bawah | Bara (mengetik), Annisa (narasi graf di Browser) |
| 11 | 23:00 | Lessons learned | Apa yang berhasil / tidak (Pajajaran = 0 baris, node tanpa metrik) | Annisa |
| 12 | 24:00 | Takeaways & Future Work | Takeaways 3 poin; future: GDS native, provenance di graf, vector index + GraphRAG hybrid, read-only tx, memori percakapan, node `Event`/`Place` | Bara |
| 13 | 25:00 | Q&A + links | Repo, kontak | Berdua |

### Pembagian Peran (Speaker Split)
- **Bara (sisi sistem/MCP, ~11 menit)**: hook, masalah, arsitektur MCP, safety guard, mengetik di demo, penutup. Alasan: dia menulis `mcp_agent`/`mcp_server`.
- **Annisa (sisi data/graf, ~11 menit)**: data model, pipeline, provenance, analytics, lessons learned, narasi visual Neo4j Browser saat demo.
- **Transisi** (kalimat jembatan, hafalkan):
  - Bara -> Annisa (slide 3->4): "Five failures, one fix: model it as a graph. Annisa will show how."
  - Annisa -> Bara (slide 7->8): "We now have a clean, scored graph. How do we let an LLM use it safely? Bara."
  - Bara -> Annisa (slide 12->11 jika ditukar, atau di demo): Bara menanyakan; Annisa menunjuk node di Browser.
- Pembagian Q&A: Annisa menjawab data/pipeline/modeling; Bara menjawab MCP/LLM/keamanan.

### Rancangan Skenario Demo (~4,5 menit)

Persiapan: Neo4j berjalan dengan data ter-load; Neo4j Browser dibuka di tab 1; terminal `python mcp_agent.py` sudah berjalan di tab 2 (font besar); video rekaman cadangan siap.

| Langkah | Aksi | Yang ditunjukkan | Narator |
|---|---|---|---|
| 1 (0:30) | Neo4j Browser: `MATCH (k:Kingdom)<-[:MEMIMPIN_ATAU_TERAFILIASI]-(p:Person) WHERE k.name='Kesultanan Banten' RETURN k,p LIMIT 40`, warnai node berdasarkan `louvain_cluster`, ukuran berdasarkan `pagerank_score` | graf nyata, tokoh besar = Abu al-Mahasin | Annisa |
| 2 (1:00) | Terminal: "Siapa Abu al-Mahasin dan apa peran jaringannya?" | log `-> [Execute Tool] retrieve_person_info`, jawaban dengan PageRank/Louvain | Bara |
| 3 (1:00) | "Bagaimana hubungan terpendek antara Rara Santang dan Pangeran Walangsungsang?" | `retrieve_shortest_path`; Annisa menunjukkan path yang sama dengan `shortestPath()` di Browser | keduanya |
| 4 (1:00) | "Tampilkan 5 tokoh dengan PageRank tertinggi di Kesultanan Banten" | `retrieve_analytical_query`, kueri Cypher yang dihasilkan terlihat di log | Bara |
| 5 (0:45) | "Hapus semua tokoh Majapahit" | ditolak guard: "Only read-only operations are allowed" | Bara |

Query Browser cadangan (semua read-only):
```cypher
// Tokoh jembatan antar-dinasti
MATCH (p:Person) WHERE p.betweenness_score IS NOT NULL
RETURN p.name, p.betweenness_score ORDER BY p.betweenness_score DESC LIMIT 5;

// Jalur terpendek
MATCH (a:Person {name:'Rara Santang'}), (b:Person {name:'Pangeran Walangsungsang'})
MATCH path = shortestPath((a)-[*..8]-(b)) RETURN path;

// Cakupan metrik (untuk jujur soal node tanpa skor)
MATCH (p:Person) RETURN p.louvain_cluster IS NULL AS tanpa_klaster, count(*) ;
```
**Verifikasi dulu setiap nama persis (ejaan di DB) 24 jam sebelumnya.** Nama pada contoh diambil dari walkthrough, bukan dijalankan ulang oleh saya (Neo4j tidak tersedia di sesi ini).

**Mitigasi jika demo bermasalah**
1. **Neo4j mati**: `retrieve_person_info`/`retrieve_kingdom_info` punya fallback CSV; sebut "self-healing" hanya untuk dua tool ini. Langkah 3-5 butuh Neo4j, sehingga beralih ke video.
2. **LLM / OpenRouter lambat atau error 402/429**: fallback model sudah ada; siapkan juga `OPENROUTER_MODEL` alternatif di `.env`. Cadangan: rekaman terminal.
3. **MCP server gagal start (Windows, timeout)**: jalankan `python mcp_server.py` dahulu sekali (warm-up) sebelum sesi; atau gunakan MCP Inspector sebagai Plan B.
4. **Jaringan konferensi buruk**: hotspot ponsel; semua data lokal kecuali LLM.
5. **Semua gagal**: video demo 3 menit (di folder `main/backup/`) + screenshot per langkah di slide cadangan.
6. Jangan improvisasi pertanyaan di panggung; pakai skrip. Jangan tanyakan pertanyaan lanjutan (agent tanpa memori percakapan).

---

## 3. Action Items & Folder `./main`

### 3.1 Artefak yang perlu dibuat
| Berkas | Isi | Prioritas | Pemilik |
|---|---|---|---|
| `main/00_laporan_nodes2026.md` | Laporan ini (sudah dibuat) | selesai | - |
| `main/01_slide_outline.md` | Outline slide + speaker notes per slide (bahasa Inggris) | H-3 | Bara + Annisa |
| `main/02_demo_script.md` | Naskah demo kata per kata + prompt persis + output yang diharapkan | H-3 | Bara |
| `main/03_cypher_cheatsheet.cypher` | Query Browser untuk demo + cadangan + query verifikasi angka | H-3 | Annisa |
| `main/04_numbers_to_verify.md` | Tabel angka (jumlah Person, imputasi, latensi) dengan sumber dan hasil verifikasi, menyelesaikan Bagian 0 | **H-3 (paling kritis)** | Annisa |
| `main/05_qa_prep.md` | Pertanyaan sulit yang mungkin muncul (GDS? Mengapa NetworkX? Skema redundan ANAK/AYAH? Guard regex cukup aman? Akurasi imputasi LLM?) | H-2 | berdua |
| `main/06_checklist_hari_h.md` | Checklist teknis (3.2) | H-2 | Bara |
| `main/backup/` | Video demo, screenshot, PDF slide, dump Neo4j (`neo4j-admin database dump`) | H-2 | berdua |
| Perbaikan kode kecil (opsional) | Muat `source`/`confidence_score` ke Neo4j; samakan README/slide dengan 5 tools; riwayat percakapan di agent | H-2 jika sempat | Bara |

Saya bisa membuat 01-03, 05 dan 06 jika Anda mau; angka di 04 perlu dijalankan di mesin Anda (Neo4j + `.env`).

### 3.2 Checklist teknis H-3 sampai hari-H
**H-3 (hari ini)**
- [ ] Putuskan: 5 tool (kode) atau implementasi 6 tool (Bagian 0 #1). Rekomendasi: **pakai 5**, ubah README/slide.
- [ ] Jalankan `neo4j_load_queries.cypher` pada instance bersih; catat jumlah `Person`/`Kingdom`/relasi.
- [ ] Rotasi API key OpenRouter; pastikan `.env` tidak masuk repo/slide/screen-share.
- [ ] Jalankan `python scripts/graph_rag_bot.py --test-analytical` dan `python mcp_agent.py` end-to-end; simpan log.
- [ ] Verifikasi angka (04) dan ejaan nama demo.

**H-2**
- [ ] Rekam video demo cadangan (3-4 menit) + screenshot tiap langkah.
- [ ] Latihan penuh dengan timer, minimal 2 kali (target 24 menit).
- [ ] `neo4j-admin` dump database sebagai cadangan; uji restore.
- [ ] Gladi transisi Bara <-> Annisa.

**H-1**
- [ ] Update OS/driver GPU; nonaktifkan notifikasi, auto-update, antivirus popup, Windows Update aktif jam.
- [ ] Uji **Goldcast**: login lewat tautan speaker, join rehearsal/green room, uji *screen share* satu jendela vs seluruh layar, uji audio komputer jika memutar video.
- [ ] Tes mikrofon dan kamera (headset kabel lebih disukai), pencahayaan, latar belakang, posisi kamera sejajar mata.
- [ ] Koneksi: LAN kabel jika bisa + hotspot ponsel cadangan; uji kecepatan upload.
- [ ] Siapkan layar terpisah (slide / terminal / Browser) atau susunan jendela tetap; zoom font terminal >= 18pt, Browser 125%+.
- [ ] Siapkan slide dalam PDF dan PPTX, salinan lokal (jangan bergantung pada cloud).
- [ ] Bersihkan desktop dan tab browser; profil browser bersih.

**Hari-H (T-60 menit)**
- [ ] Neo4j start, data ter-load, uji satu query.
- [ ] `python mcp_server.py` warm-up, lalu `python mcp_agent.py` siap di terminal.
- [ ] Join Goldcast >= 15 menit sebelum jadwal; cek audio/video dengan moderator.
- [ ] Air minum, charger terhubung, ponsel mode senyap, saluran komunikasi cadangan Bara <-> Annisa (chat terpisah) untuk sinyal cepat.

---

## 4. Rekomendasi Prioritas (urutan kerja 3 hari)
1. **Hari 1**: rekonsiliasi Bagian 0 (terutama 5 vs 6 tools dan angka), load Neo4j, jalankan demo end-to-end.
2. **Hari 2**: slide + naskah demo + video cadangan; latihan.
3. **Hari 3**: latihan akhir, uji Goldcast, Q&A prep. Bekukan kode; jangan ubah apa pun malam sebelumnya.
