# Belajar Teknis NusantaraGraph (versi santai)

Untuk kamu yang lupa bagaimana proyek ini bekerja. Semua di sini sudah dicocokkan dengan kode di [`copy-of-repo-eas-graf/`](../copy-of-repo-eas-graf) (versi V1, yang dipakai di demo).

Waktu baca: sekitar 30-40 menit. Bagian 7 (menelusuri satu pertanyaan) adalah yang paling penting kalau waktumu sempit.

---

## 0. Peta besar

```
 FASE 1: MENYIAPKAN DATA (dijalankan sekali, offline)
 ┌──────────────────────────────────────────────────────────────────────┐
 │ CSV lama (UTS) ─▶ pipeline_graf.py ─▶ analisis_graf.py ─▶ CSV final │
 │                   (ambil + bersihkan)  (hitung skor graf)  + skor    │
 └──────────────────────────────────────────────────────────────────────┘
                                   │ LOAD CSV (neo4j_load_queries.cypher)
                                   ▼
                               [ Neo4j ]
                                   ▲
 FASE 2: TANYA-JAWAB (saat demo)   │ Cypher
 ┌──────────────────────────────────────────────────────────────────────┐
 │ Kamu ─▶ mcp_agent.py ─(MCP/stdio)─▶ mcp_server.py ─▶ graph_rag_bot.py│
 │          (LLM + loop)                (5 tools)       (query Neo4j)   │
 └──────────────────────────────────────────────────────────────────────┘
```

Dua hal yang perlu kamu ingat:
1. **Fase 1** menyiapkan data sekali saja. Hasil akhirnya CSV, lalu dimuat ke Neo4j.
2. **Fase 2** adalah chatbot yang **tidak mengarang**: setiap jawaban diambil dari Neo4j lewat "tools".

---

## 1. Konsep dasar

### Knowledge graph
Data disimpan sebagai **titik (node)** dan **garis (relationship)**.
- Node = benda: `Person` (tokoh), `Kingdom` (kerajaan).
- Relationship = hubungan: `AYAH`, `IBU`, `MENGGANTIKAN`, dll.
- Properti = keterangan tambahan pada node, misalnya `name`, `birthDate`, `pagerank_score`.

Analogi: peta MRT. Stasiun = node, rel = relationship. Pertanyaan "dari A ke B lewat mana?" jauh lebih mudah dijawab di peta daripada di tabel.

### Neo4j dan Cypher
Neo4j adalah database graf. Bahasa query-nya **Cypher**, yang bentuknya seperti gambar ASCII:

```cypher
// "Cari tokoh yang terafiliasi dengan Kesultanan Banten"
MATCH (p:Person)-[:MEMIMPIN_ATAU_TERAFILIASI]->(k:Kingdom {name:'Kesultanan Banten'})
RETURN p.name
```
- `(p:Person)` = node berlabel Person, diberi nama variabel `p`.
- `-[:REL]->` = relasi dengan arah.
- `{name:'...'}` = filter properti.

```cypher
// "Jalur terpendek antara dua tokoh"
MATCH (a:Person {name:'Rara Santang'}), (b:Person {name:'Pangeran Walangsungsang'})
MATCH path = shortestPath((a)-[*..8]-(b))
RETURN path
```
- `[*..8]` = boleh lewat relasi apa saja, maksimal 8 langkah, arah bebas.

Dua kata Cypher yang perlu kamu tahu artinya:
- `MERGE` = "buat kalau belum ada, pakai yang sudah ada kalau sudah ada".
- `LIMIT` = batasi jumlah hasil.

---

## 2. Fase 1a: Mengambil dan membersihkan data ([pipeline_graf.py](../copy-of-repo-eas-graf/scripts/pipeline_graf.py))

Urutan di fungsi `main()`:

**1. Baca CSV lama dari tugas UTS** (`dataset_gabungan_uts_graf.csv`), lalu bersihkan encoding semua kolomnya.

**2. Bersihkan encoding** (`clean_encoding`, baris 25)
- Masalahnya: teks UTF-8 terbaca sebagai cp1252, sehingga "Śakti" jadi "Ã…Å¡akti" (disebut **mojibake**).
- Solusinya: kalau ada karakter mencurigakan (Ã, Â, Å, ...), kode mencoba `encode('cp1252')` lalu `decode('utf-8')`, sampai **3 kali**, karena kadang teksnya rusak dua lapis.

**3. Tanya Wikidata lewat SPARQL** (baris 433)
- SPARQL adalah bahasa query untuk Wikidata/DBpedia.
- Ada dua cara pencarian yang digabung (`UNION`):
  - (a) cari berdasarkan **nama** dari CSV lama (pakai `VALUES` supaya cepat dan tidak timeout);
  - (b) cari semua manusia (`Q5`) yang terhubung ke **"historical state" di Indonesia** (`Q3024240`, `Q252`).
- Yang diambil: ayah (P22), ibu (P25), pasangan (P26), anak (P40), saudara (P3373), dinasti (P53), tanggal lahir/wafat, serta **menggantikan/digantikan** (P1365/P1366).

**4. Tanya DBpedia** (baris 484): data kerajaan (ibu kota, agama, tahun mulai), lalu digabung dengan data Wikidata berdasarkan ID kerajaan.

**5. Isi yang kosong dengan LLM** (`impute_missing_with_llm`, baris 182)
- Ambil teks Wikipedia tokoh, lalu minta LLM (lewat OpenRouter, model Gemini dengan cadangan model gratis) mengembalikan **JSON**: `ayah`, `ibu`, `pasangan`, `anak`, `saudara`, `confidence_score`.
- Baris yang diisi LLM diberi `source = llm_imputed`. Totalnya **49 dari 406 baris**.
- ⚠️ `confidence_score` adalah **perkiraan LLM sendiri** (diminta di prompt), bukan hasil perhitungan.

**6. Gabungkan duplikat** (`apply_entity_disambiguation`, baris 333)
- Bandingkan semua pasangan nama dengan **RapidFuzz** (`token_set_ratio`). Kalau kemiripannya **≥ 85**, tanya LLM "orang yang sama? YES/NO".
- Kalau YES, gabungkan dengan **Union-Find**. Analogi: kelompok pertemanan. Kalau A = B dan B = C, otomatis A, B, C satu kelompok dan semuanya mendapat satu `master_id`.
- ⚠️ Keterbatasannya: "Hayam Wuruk" vs "Sri Rajasanagara" kemiripan hurufnya rendah, jadi tidak pernah sampai ke LLM. Inilah pelajaran "names are the hardest part".

---

## 3. Fase 1b: Menghitung skor graf ([analisis_graf.py](../copy-of-repo-eas-graf/scripts/analisis_graf.py))

CSV diubah menjadi graf di memori dengan **NetworkX** (library Python), lalu dihitung empat skor:

| Skor | Pertanyaan yang dijawab | Analogi | Hasil kita |
|---|---|---|---|
| **PageRank** (alpha 0.85) | Siapa paling berpengaruh? | Kamu penting kalau "ditunjuk" oleh orang-orang penting | Abu al-Mahasin (Banten) |
| **Betweenness** | Siapa jembatan antar-kelompok? | Stasiun transit: banyak rute terpendek lewat situ | Sunan Gunung Jati, lalu Maulana Hasanuddin |
| **Louvain** (seed 42) | Kelompok alami apa saja? | Grup WhatsApp: di dalam grup ramai, antar-grup sepi | 26 klaster |
| **Adamic-Adar** | Seberapa mirip dua tokoh? | Punya teman yang sama; teman yang "langka" lebih berarti | Menggantikan Jaccard |

**Kenapa Jaccard diganti?** Jaccard = jumlah tetangga bersama ÷ total tetangga.
- Kalau dua tokoh sama-sama hanya punya 1 tetangga dan tetangganya sama, hasilnya 1/1 = **100% mirip**, padahal datanya hanya sedikit.
- Kalau keduanya tidak punya tetangga, hasilnya 0/0, tidak terdefinisi.
- Adamic-Adar memberi bobot `1/log(jumlah teman)` untuk setiap tetangga bersama, sehingga tidak "tertipu" oleh data yang jarang.

Skor ditulis ke kolom CSV (`orang_PageRank`, `orang_Louvain_Cluster`, ...).

**Kenapa tidak pakai Neo4j GDS?** Di prototipe UTS memang pakai GDS. Di versi final skor dihitung di Python lalu dimuat sebagai properti. Alasannya: grafnya kecil dan jarang berubah, tidak perlu plugin, dan algoritmanya mudah diganti.

---

## 4. Fase 1c: Memuat ke Neo4j ([neo4j_load_queries.cypher](../copy-of-repo-eas-graf/database/neo4j_load_queries.cypher))

1. Buat **constraint**: `name` harus unik untuk Person dan Kingdom.
2. `LOAD CSV ... FIELDTERMINATOR ';'` membaca CSV baris per baris.
3. `MERGE (p:Person {name: row.orang})` membuat node tokoh beserta skornya.
4. Relasi dibuat dengan `MERGE` juga. Contohnya, kalau kolom `ayah` berisi "X", dibuat relasi ke node "X".

Dua kejanggalan di data ternyata dijelaskan oleh mekanisme ini:
- **Kenapa 217 dari 356 tokoh tidak punya skor?** Node ayah/ibu/anak dibuat lewat `MERGE` relasi, tidak lewat baris utama CSV, sehingga skornya tidak ikut terisi.
- **Kenapa angka di DB berbeda dari CSV sekarang?** Import memakai `coalesce` (nilai lama dipertahankan). DB pertama kali dimuat dari CSV versi lama, jadi skor lama tidak tertimpa. Urutan peringkatnya tetap sama.

---

## 5. Fase 2: MCP dan agent

### Apa itu MCP?
**Model Context Protocol** adalah standar terbuka supaya model AI bisa memakai "alat" (tools) dari luar. Analogi: **colokan USB-C untuk AI**. Server cukup dibuat sekali, lalu klien MCP mana pun (Claude Desktop, MCP Inspector, agent buatan kita) bisa memakainya.

### Server ([mcp_server.py](../copy-of-repo-eas-graf/mcp_server.py))
- `FastMCP("Nusantara Dynasty Graph Server")` membuat server.
- Setiap fungsi diberi dekorator `@mcp.tool()` supaya menjadi tool. Ada 5:

| Tool | Apa yang dilakukan | Query di balik layar ([graph_rag_bot.py](../copy-of-repo-eas-graf/scripts/graph_rag_bot.py)) |
|---|---|---|
| `retrieve_shortest_path` | Jalur terpendek dua tokoh | `shortestPath((n1)-[*..5]-(n2))`, maksimal 5 langkah |
| `retrieve_person_info` | Profil + PageRank + klaster | `MATCH (p:Person {name: $name})` |
| `retrieve_person_relationships` | Daftar kerabat | semua relasi tokoh, maksimal 15 |
| `retrieve_kingdom_info` | Profil kerajaan + anggota | properti kerajaan + 15 anggota |
| `retrieve_analytical_query` | Pertanyaan bebas | LLM menulis Cypher sendiri (lihat bagian 6) |

- `mcp.run(transport="stdio")`: server dan agent berkomunikasi lewat **stdin/stdout** (seperti dua program yang saling mengirim pesan JSON lewat terminal).
- **Fallback CSV:** kalau Neo4j mati, `person_info`, `person_relationships` dan `kingdom_info` membaca dari CSV. `shortest_path` dan `analytical_query` **tidak bisa** tanpa Neo4j.
- ⚠️ **Nama harus persis sama** (`{name: $name}`, peka huruf besar/kecil). Kalau LLM salah mengeja nama, hasilnya "not found". Ini risiko terbesar saat demo.

### Agent ([mcp_agent.py](../copy-of-repo-eas-graf/mcp_agent.py))
1. **Menjalankan server** sebagai subprocess (baris 35-49).
2. `session.initialize()` lalu `session.list_tools()` untuk **menemukan** tools dari server (baris 54-57).
3. **Menerjemahkan** daftar tools ke format "function calling" yang dipahami LLM (baris 61-70). Jadi menambah tool cukup dengan menambah satu fungsi di server; agent tidak perlu diubah.
4. **Loop tanya-jawab** (baris 89-151):
   - kirim `system prompt` + pertanyaanmu + daftar tools ke LLM (OpenRouter);
   - kalau LLM membalas "saya mau panggil tool X dengan argumen Y" (`tool_calls`), agent memanggil `session.call_tool(X, Y)` dan mencetak `-> [Execute Tool] X dengan argumen: Y`;
   - hasil tool dikirim balik ke LLM sebagai pesan `role: "tool"`;
   - ulangi sampai LLM membalas teks biasa, yaitu jawaban akhir.
5. ⚠️ **Tidak ada memori**: `messages` dibuat ulang setiap pertanyaan (baris 89). Karena itu jangan ajukan pertanyaan lanjutan ("dia anak siapa?") saat demo.

---

## 6. Text-to-Cypher dan guard (`retrieve_analytical_query`, baris 351)

1. LLM diberi **skema database** (daftar node, properti, relasi) di prompt, lalu diminta mengubah pertanyaan menjadi **satu query Cypher read-only**.
2. Kode membersihkan hasilnya, misalnya membuang ```` ``` ```` kalau LLM menambahkannya.
3. Kalau query belum punya `LIMIT`, ditambahkan `LIMIT 25` (baris 420-424).
4. **Guard** (baris 427-444): query dicek dengan regex untuk `CREATE`, `MERGE`, `SET`, `DELETE`, `REMOVE`, `DROP`, `DETACH`, `LOAD CSV`, dan `apoc...write`. Kalau ada, query ditolak dengan pesan *"Only read-only operations are allowed"*.
5. **Kenapa `\b`?** `\b` artinya "batas kata". Tanpa itu, nama "**Set**yawati" atau kata "As**set**" ikut terblokir karena mengandung "SET". Dengan `\b`, yang diblokir hanya kata SET yang berdiri sendiri.
6. Keterbatasan (jawab jujur kalau ditanya): ini hanya lapisan pertama. Yang lebih aman adalah user database read-only atau transaksi `execute_read`.

Cara melihat guard bekerja tanpa agent: `python scripts/graph_rag_bot.py --test-analytical`

---

## 7. Menelusuri satu pertanyaan dari awal sampai akhir ⭐

Kamu mengetik: **"Siapa Abu al-Mahasin dan apa peran jaringannya?"**

1. `mcp_agent.py` mengirim ke LLM: system prompt ("kamu sejarawan + data scientist, selalu pakai tools"), pertanyaanmu, dan daftar 5 tools.
2. LLM membaca deskripsi tools lalu memutuskan: *"panggil `retrieve_person_info` dengan `person = 'Abu al-Mahasin'`"*.
3. Agent mencetak `-> [Execute Tool] retrieve_person_info ...` lalu mengirim permintaan itu ke `mcp_server.py` lewat stdio.
4. Server memanggil fungsi di `graph_rag_bot.py`, yang menjalankan Cypher `MATCH (p:Person {name:'Abu al-Mahasin'}) RETURN ...` di Neo4j.
5. Neo4j mengembalikan data: role, dynasty, PageRank 0.0062, klaster 14.
6. Hasil (JSON) dikirim balik ke agent, lalu ke LLM sebagai pesan `tool`.
7. LLM mungkin memanggil tool lain (misalnya `retrieve_person_relationships`), atau langsung menulis jawaban dalam Bahasa Indonesia **berdasarkan JSON tadi**.
8. Agent mencetak `JAWABAN BOT`.

Inti kalimat untuk panggung: **"The LLM decides, the tools fetch, the graph is the source of truth."**

---

## 8. V2 dalam satu paragraf

Di folder [`pipeline-deepseek-v2/`](../pipeline-deepseek-v2) ada pipeline eksperimen. Perbedaannya dengan V1:
- memakai DeepSeek;
- pencarian Wikidata lebih ketat (tokoh harus benar-benar terkait Indonesia);
- halaman Wikipedia dicek dulu relevan atau tidak sebelum dibaca LLM;
- setiap relasi yang diusulkan LLM **wajib disertai kutipan persis** dari halaman, dan kalau kutipannya tidak ditemukan di teks, relasinya dibuang.

Hasilnya, dari 30 tokoh uji, relasi tanpa bukti turun dari 9/23 menjadi 0/57. V2 **tidak** menulis ke Neo4j; demo tetap memakai data V1.

---

## 9. Glosarium cepat

| Istilah | Arti singkat |
|---|---|
| Node / relationship / property | titik / garis / keterangan |
| Cypher | bahasa query Neo4j |
| SPARQL | bahasa query Wikidata/DBpedia |
| Wikidata QID / P-code | ID entitas (Q5 = manusia) / ID properti (P22 = ayah) |
| Mojibake | teks rusak karena salah encoding |
| Fuzzy matching | mencocokkan teks yang mirip, bukan harus sama persis |
| Union-Find (DSU) | struktur data untuk mengelompokkan item yang "sama" |
| LLM imputation | LLM mengisi data yang kosong |
| Provenance | catatan asal-usul data (`source`, `confidence_score`) |
| MCP | standar agar AI bisa memakai tools eksternal |
| Tool calling | LLM meminta program menjalankan fungsi tertentu |
| stdio | komunikasi antarprogram lewat input/output standar |
| Text-to-Cypher | LLM mengubah pertanyaan menjadi query Cypher |
| GDS | Graph Data Science, plugin algoritma graf di Neo4j |

---

## 10. Latihan malam ini (±45 menit)

1. **Neo4j Browser (10 menit)**: jalankan tiga query ini dan lihat hasilnya.
   ```cypher
   CALL db.schema.visualization();
   MATCH (p:Person) WHERE p.pagerank_score IS NOT NULL
   RETURN p.name, p.pagerank_score ORDER BY p.pagerank_score DESC LIMIT 5;
   MATCH (a:Person {name:'Rara Santang'}), (b:Person {name:'Pangeran Walangsungsang'})
   MATCH path = shortestPath((a)-[*..8]-(b)) RETURN path;
   ```
2. **Agent (10 menit)**: `cd copy-of-repo-eas-graf` lalu `python mcp_agent.py`. Ketik pertanyaan demo nomor 2, lalu perhatikan baris `[Execute Tool]`.
3. **Guard (5 menit)**: `python scripts/graph_rag_bot.py --test-analytical`. Lihat TEST 3-5.
4. **Baca kode (10 menit)**: [mcp_agent.py baris 89-151](../copy-of-repo-eas-graf/mcp_agent.py#L89-L151). Ini inti agent, dan cukup dibaca sekali.
5. **Jelaskan dengan kata-katamu sendiri (10 menit)**: ceritakan bagian 7 ke Bara (atau ke dirimu sendiri) tanpa melihat catatan.

Kalau langkah 1-3 jalan di laptopmu, kamu sudah memahami ±80% yang mungkin ditanyakan.
