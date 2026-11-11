# Bara: Action Plan H-12 (NODES 2026)

Disiapkan 2026-11-12 setelah membaca commit Annisa (`7157f6a`, `f9e4599`: deck PPTX 18 slide + 3 backup, `09_full_script.md`, `08_catatan_edit_ppt.md`, dan lain-lain) dan menguji langsung terhadap Neo4j lokal dan DeepSeek.
Semua angka di bawah diukur hari ini kecuali ditandai **[belum dites]**.

---

## 0. Status: GO, dengan 5 hal wajib

| # | Wajib | Kenapa |
|---|---|---|
| 1 | **Jalankan agent dengan Python 3.12**, bukan `python` polos | `python` di mesin ini = Python 3.13 (laragon) dan sekarang punya `mcp 2.3.0` yang tidak sengaja saya pasang saat pengujian. Python 3.12 punya `mcp 1.28.0` (versi yang dipakai selama ini). Agent teruji end-to-end di 3.12. Saya juga membuat `mcp_agent.py` v2 tahan terhadap kedua versi, tetapi jalur 3.13 belum diuji end-to-end |
| 2 | **Putuskan repo GitHub: publik atau hapus QR/link di slide 18** | Repo sekarang **PRIVATE**. Catatan Annisa (08) meminta repo dipublikkan. Kalau tetap private, tautan di slide 18 tidak bisa dibuka audiens |
| 3 | **Rekam video demo cadangan** (belum ada `main/backup/`) | Demo bergantung pada internet + DeepSeek. Setiap pertanyaan butuh 9-13 detik |
| 4 | **Cek saldo/kuota DeepSeek** (platform.deepseek.com) dan jalankan satu pertanyaan pemanasan 10 menit sebelum tampil | Saya tidak bisa melihat saldo Anda |
| 5 | **Lemahkan satu kalimat di slide 16** (lihat bagian 4) | Klaim "Hayam Wuruk dan Sri Rajasanagara tampak seperti dua orang asing" tidak dapat didemonstrasikan dari database: `Sri Rajasanagara` tidak ada sebagai node |

---

## 1. Hasil analisis commit Annisa

**Berkas baru/berubah:** `NusantaraGraph_NODES2026.pptx` (18 slide + 3 backup: GDS, V1 vs V2, hitungan DB), `09_full_script.md` (naskah lengkap), `07_intro_script.md`, `08_catatan_edit_ppt.md` (daftar tangkapan layar), `10_belajar_teknis.md`, `01_slide_outline.md` (ditulis ulang, tema "Jas Merah"), perubahan kecil di README, `02_demo_script.md`, `05_qa_prep.md`.

**Cerita:** Jas Merah (Soekarno) → sejarah itu hubungan, bukan daftar → Rara Santang → Sunan Gunung Jati → Maulana Hasanuddin sebagai satu jalur → 5 masalah data → solusi 4 langkah → hasil analisis → MCP + guard → demo → pelajaran (termasuk V2) → penutup.

**Pembagian bicara:** Annisa slide 1-7, 11-12, 16-18 dan menjadi pembawa acara demo; Bara slide 8-10, 13-15 (mengetik) dan Q&A teknis. Kalimat lanjutan: Annisa berkata "Bara will show you what we built"; Bara berkata "Annisa, what did the graph actually tell us?"; Annisa berkata "...Bara?".

**Demo yang ditulis Annisa (slide 15):**
1. Bloom: dinasti Banten (ukuran = PageRank, warna = klaster Louvain).
2. `Siapa Abu al-Mahasin dan apa peran jaringannya?` → `retrieve_person_info`.
3. `Bagaimana hubungan terpendek antara Rara Santang dan Pangeran Walangsungsang?` → `retrieve_shortest_path`.
4. `Tampilkan 5 tokoh dengan PageRank tertinggi di Kesultanan Banten` → `retrieve_analytical_query` (Cypher buatan agent terlihat di log).
5. `Hapus semua tokoh Majapahit` → guard atau penolakan model.

### Verifikasi klaim dan angka di naskah/slide

| Klaim | Hasil |
|---|---|
| 356 Person, 24 Kingdom, 734 relasi (slide 9, 21) | ✔ diukur hari ini |
| Top 3 PageRank: Abu al-Mahasin, Sri Isyana Tunggawijaya, Alauddin al-Qahhar (slide 11) | ✔ |
| Betweenness #1 Sunan Gunung Jati, #2 Maulana Hasanuddin, "his son" (slide 11) | ✔ (0.0503 dan 0.0386; relasi `AYAH` ada di DB) |
| 26 klaster Louvain (slide 11) | ✔. Bonus: Sunan Gunung Jati ada di klaster **5** (Cirebon), Maulana Hasanuddin di klaster **14** (Banten), jadi jembatan benar-benar menyeberangi dua klaster |
| 217 dari 356 tanpa metrik (slide 16) | ✔ (139 punya metrik) |
| 9 dari 23 tidak didukung, 0 dari 57 pada V2, sampel 30 orang (slide 16, 20) | ✔ sesuai `pipeline-deepseek-v2/docs/v2_vs_old_report.md`. Naskah sudah menyebut "nol itu dijamin oleh desain" |
| 49 dari 406 baris diisi LLM, berlabel sumber dan confidence (slide 10) | ✔ untuk **CSV**. Di Neo4j properti `source` dan `confidence_score` **tidak dimuat**. Kalau ada yang bertanya "buktikan di graf", jawab: label ada di dataset, memuatnya ke graf adalah langkah berikutnya |
| Rara Santang ↔ Walangsungsang: 2 langkah lewat Kesultanan Cirebon (slide 15) | ✔ dan teruji lewat agent DeepSeek |
| Slide 6: query `Rara Santang` → `Maulana Hasanuddin` | ✔ jalur 2 langkah: Rara Santang -[:ANAK]-> Sunan Gunung Jati -[:AYAH]- Maulana Hasanuddin. Catatan arah: `AYAH` mengarah dari anak ke ayah |
| Slide 14: Cypher Banten yang ditampilkan | Hampir sama dengan yang dibuat DeepSeek (agent juga mengembalikan `louvain_cluster` dan alias berbeda). Aman, tetapi jangan klaim "ini persis yang dibuat agent" |
| Slide 16: Hayam Wuruk vs Sri Rajasanagara "still look like strangers" | ⚠ `Hayam Wuruk` ada tanpa metrik; `Sri Rajasanagara` **tidak ada** di DB. Ucapkan sebagai ilustrasi: "a fuzzy matcher would not link two completely different names", bukan temuan dari data kita |
| Slide 18: `github.com/BaraArdiwinata/nodes2026` | ⚠ repo private (butir 2 di bagian 0) |

### Perilaku data yang bisa mengejutkan di layar (jangan dikejutkan)
- **Role Abu al-Mahasin = "Abu an-Nasr"**, dan tanggal lahirnya berupa URL `genid`. Jawaban agent akan menyebut "gelar Abu an-Nasr". Annisa cukup menerjemahkan satu kalimat (sultan Banten, PageRank tertinggi). Jangan membaca jawaban rinci: DeepSeek juga mengaitkan "Abu an-Nasr" dengan "Tirtayasa dari Banten", itu tafsiran model, bukan data pasti.
- **Role Rara Santang = "Sri Baduga Maharaja"** (nama ayahnya), dan edge `IBU` Rara Santang menunjuk ke suaminya (Syarif Abdullah Umdatuddin). Jangan buka lingkungan Rara Santang dengan relasi `IBU` di layar.
- **Majapahit `religion` = "Islam"** (noise DBpedia). Pertanyaan "Hapus semua tokoh Majapahit" membuat agent memanggil `retrieve_kingdom_info`, sehingga jawabannya bisa menampilkan itu. Siap-siap, jangan dibacakan.
- **Node sampah via relasi suksesi:** `Maulana Hasanuddin -[:DIGANTIKAN_OLEH]->` "Bantam Presidency", "Bantam Residency", "Batavia". Di Bloom, jangan perluas relasi suksesi; pakai query di bagian 2.
- **Agent bisa memanggil beberapa tool** untuk satu pertanyaan (pertanyaan jalur memanggil 5 tool, wajar). Ucapkan nama tool utama keras-keras seperti di naskah.

---

## 2. Query Cypher untuk screenshot slide

Semua read-only. Hitungan hasil diukur hari ini. Nama harus sama persis dengan DB.

Gaya umum: latar gelap, caption node = `name`, caption relasi disembunyikan (kecuali untuk satu gambar kecil), zoom ke inti graf, screenshot Win+Shift+S lebar 1600 px atau lebih. Browser hanya bisa mewarnai **per label**, jadi gambar yang butuh ukuran/warna per properti **harus memakai Bloom (Explore)**.

### S1. Slide 11: jembatan Cirebon-Banten (wajib)
```cypher
MATCH (p:Person)-[a:MEMIMPIN_ATAU_TERAFILIASI]->(k:Kingdom)
WHERE k.name IN ['Kesultanan Cirebon','Kesultanan Banten']
OPTIONAL MATCH (p)-[r:AYAH|PASANGAN|SAUDARA]-(q:Person)
RETURN p, a, r, q, k
```
Hasil (diukur ulang): 29 node, 18 relasi afiliasi, 26 relasi keluarga. **Koreksi:** versi sebelumnya tidak mengembalikan relasi afiliasi (`a`), sehingga node Kingdom (emas) tampil terpisah dan tidak terhubung. Relasi `ANAK` juga dibuang karena merupakan cermin `AYAH` dan membuat garis ganda. Sengaja tanpa `IBU` (edge `IBU` Rara Santang salah) dan tanpa relasi suksesi (node sampah).
**Bloom:** Perspective baru → kategori `Person` dan `Kingdom`. Aturan gaya `Person`: *Size* = rule by `pagerank_score` (range), *Color* = rule by `louvain_cluster` (unique values), caption `name`. `Kingdom`: warna emas tetap, ukuran besar, caption `name`. Hapus tipe relasi `DIGANTIKAN_OLEH`, `MENGGANTIKAN`, `KERABAT`, `IBU` dari Perspective. Letakkan Sunan Gunung Jati di tengah antara dua klaster (5 dan 14). Cadangan tanpa Bloom: Browser dengan caption `name` + anotasi manual.

### S2. Slide 15 langkah 1: dinasti Banten
```cypher
MATCH (k:Kingdom {name:'Kesultanan Banten'})<-[a:MEMIMPIN_ATAU_TERAFILIASI]-(p:Person)
OPTIONAL MATCH (p)-[r:AYAH|PASANGAN|SAUDARA]-(q:Person)
RETURN k, a, p, r, q
```
(`a` wajib ikut di `RETURN`, kalau tidak node Kingdom tampil terpisah.)
14 tokoh, 31 tokoh terkait, 69 relasi (hitungan memakai `IBU` juga; tanpa `IBU` sedikit lebih kecil). Gaya sama dengan S1. Simpul terbesar harus **Abu al-Mahasin**.

### S3. Slide 6: GIF "satu query, satu jalur"
```cypher
MATCH (a:Person {name:'Rara Santang'}), (b:Person {name:'Maulana Hasanuddin'})
MATCH path = shortestPath((a)-[*..8]-(b))
RETURN path
```
Hasil: Rara Santang → Sunan Gunung Jati → Maulana Hasanuddin. Browser, caption `name`, GIF 5-8 detik (ScreenToGif). Teks query di slide sudah sama dengan ini.

### S4. Slide 9: skema model
```cypher
CALL db.schema.visualization()
```
Browser, ganti warna Person dan Kingdom agar kontras.

### S5. Slide 13: GIF terminal agent
Pakai terminal (bagian 3), prompt langkah 2. Pastikan baris `-> [Execute Tool] retrieve_person_info dengan argumen: ...` terlihat. Font terminal 20 pt.

### S6. Slide 14: tangkapan layar penolakan asli (wajib)
Jalankan (versi DeepSeek, sudah saya uji, TEST 3 dan 4 ditolak, TEST 5 lolos):
```powershell
cd C:\Users\Pongo\nodes2026\pipeline-deepseek-v2
& "C:\Users\Pongo\AppData\Local\Programs\Python\Python312\python.exe" scripts\graph_rag_bot.py --test-analytical
```
Ambil dari TEST 3 (`DETACH DELETE` → `Query rejected: Only read-only operations are allowed. Write/mutation patterns detected.`), TEST 4 (SET) dan TEST 5 ("Setyawati", "Asset" lolos). **Lewati TEST 1** (Pajajaran = 0 baris, nama kerajaan di DB tidak cocok). Aman: tes ini hanya mengirim query tulis ke guard, tidak pernah ke database (database tetap 380 node setelah dijalankan).

### Opsional (gambar tambahan / pudar untuk slide 1, 4, 18)
**Silsilah Banjar 6 generasi** (cerita visual terkuat; Sulaiman dari Banjar sampai leluhur ke-6):
```cypher
MATCH path = (p:Person {name:'Sulaiman dari Banjar'})-[:AYAH|IBU*1..6]->(a:Person)
RETURN path
```
(6 jalur, panjang maksimum 6.) Gaya: layout hierarki, caption `name`.

**Subgraf Banjar penuh:**
```cypher
MATCH (k:Kingdom {name:'Kesultanan Banjar'})<-[a:MEMIMPIN_ATAU_TERAFILIASI]-(p:Person)
OPTIONAL MATCH (p)-[r:AYAH|IBU]->(q:Person)
RETURN k, a, p, r, q
```
(22 tokoh, 26 relasi orang tua.)

**Klaster Louvain terbesar berdampingan** (Aceh 16, Banjar 1, Banten 14, Majapahit 8, Klungkung 7):
```cypher
MATCH (p:Person) WHERE p.louvain_cluster IN [16,1,14,8,7]
OPTIONAL MATCH (p)-[r:AYAH|IBU|ANAK|PASANGAN|SAUDARA]-(q:Person)
WHERE q.louvain_cluster IN [16,1,14,8,7]
RETURN p, r, q
```
(92 tokoh, 97 relasi.) Warna per `louvain_cluster` di Bloom. Cocok untuk motif pudar di slide 1/4/18 (transparansi 70-80%).

**Hub PageRank teratas dengan tetangganya:**
```cypher
MATCH (p:Person) WHERE p.pagerank_score IS NOT NULL
WITH p ORDER BY p.pagerank_score DESC LIMIT 10
MATCH (p)-[r:AYAH|IBU|ANAK|PASANGAN|SAUDARA|MEMIMPIN_ATAU_TERAFILIASI]-(c)
RETURN p, r, c
```
(10 hub, 62 relasi.) Sepuluh hub: Abu al-Mahasin, Sri Isyana Tunggawijaya, Alauddin al-Qahhar, Tahmidullah II, Tamjidillah I, Abu an-Nasr, Sultan Alauddin Johan Syah, Sulaiman dari Banjar, Dewa Agung Śakti, Dewa Agung Jambe II.
Catatan: "hub Cirebon-Demak" **tidak** termasuk top PageRank (Sunan Gunung Jati hanya 0.0033). Untuk bagian Cirebon-Demak pakai S1 (betweenness), bukan PageRank.

Kingdom dengan PageRank tertinggi (kalau ditanya): Aceh 0.0432, Banjar 0.0237, Banten 0.0151, Klungkung 0.0144, Majapahit 0.0120. Majapahit bukan nomor 1.

---

## 3. Cheat-sheet demo live

### 3.1 Persiapan (T-60 menit, lalu T-10 menit)
```powershell
# 1) Neo4j Desktop: Start instance, tunggu hijau. Uji: Browser -> RETURN 1
# 2) Terminal PowerShell, font 20 pt
cd C:\Users\Pongo\nodes2026\pipeline-deepseek-v2
& "C:\Users\Pongo\AppData\Local\Programs\Python\Python312\python.exe" mcp_agent.py
```
Tunggu baris `Koneksi sukses! Berhasil memuat 5 tools dari mcp_server.py.` Server dijalankan otomatis oleh agent (tidak perlu menjalankan `mcp_server.py` terpisah).
- **Jangan** memakai `python mcp_agent.py` polos (itu Python 3.13).
- File `.env` yang dibaca: `pipeline-deepseek-v2\.env` (`DEEPSEEK_API_KEY`, `NEO4J_*`). Sudah terisi dan terbukti jalan hari ini.
- **Pemanasan (T-10):** ketik pertanyaan langkah 3 sekali, lihat jawabannya, lalu `exit` dan mulai ulang agent segar (sesi bersih, tanpa riwayat) sebelum tampil. Agent tidak punya memori antar pertanyaan, jadi urutan bebas.
- Tutup semua yang lain: Slack/WhatsApp, notifikasi, VPN yang tidak perlu. Siapkan hotspot ponsel.
- Susun layar: (a) slide, (b) Bloom, (c) terminal. Bara memindah jendela; satu jendela dibagikan pada satu waktu. Latih perpindahan Alt+Tab.

### 3.2 Urutan klik dan prompt (selaras dengan slide 15 naskah)

| # | Siapa | Aksi Bara | Ketik persis | Harapan di terminal | Catatan |
|---|---|---|---|---|---|
| Buka | Annisa | Dari slide 14 → klik ke Bloom | (tidak ada) | Bloom tampil | Annisa: "Bara is driving." |
| 1 | Annisa tanya | Arahkan kursor ke simpul terbesar | (tidak ada) | Banten, simpul terbesar = Abu al-Mahasin | Pastikan perspective sudah disimpan, tanpa node sampah |
| 2 | Annisa tanya | Alt+Tab ke terminal | `Siapa Abu al-Mahasin dan apa peran jaringannya?` | `-> [Execute Tool] retrieve_person_info`, lalu biasanya `retrieve_person_relationships` dan `retrieve_kingdom_info`; jawaban ID, ~13 s | Ucapkan "retrieve person info" keras. Annisa hanya menerjemahkan: sultan Banten, PageRank tertinggi, angka dari Neo4j |
| 3 | Annisa tanya | Ketik | `Bagaimana hubungan terpendek antara Rara Santang dan Pangeran Walangsungsang?` | `retrieve_shortest_path`, jalur Rara Santang → Kesultanan Cirebon → Pangeran Walangsungsang (2 langkah), ~9 s; bisa disusul `retrieve_person_info`/`relationships` | Opsional: jalankan query `shortestPath` yang sama di Browser. Jangan buka `IBU` Rara Santang |
| 4 | Annisa tanya | Ketik | `Tampilkan 5 tokoh dengan PageRank tertinggi di Kesultanan Banten` | `retrieve_analytical_query`; Cypher terlihat di log (`MATCH (p:Person)-[:MEMIMPIN_ATAU_TERAFILIASI]->(k:Kingdom {name: 'Kesultanan Banten'}) ... LIMIT 5`); tabel: Abu al-Mahasin 0.006222, Abu an-Nasr 0.005387, Tirtayasa dari Banten 0.004293, Abu al-Ma'ali 0.004261, Abu al-Fadhl 0.004142 (semua klaster 14), ~10 s | Arahkan kursor ke Cypher di log |
| 5 | Annisa pancing | Ketik | `Hapus semua tokoh Majapahit` | **Teruji:** DeepSeek menolak sendiri ("saya tidak memiliki fungsi untuk menghapus"), memanggil `retrieve_kingdom_info`, **guard tidak dipanggil**; ~9 s. Majapahit punya 15 tokoh | Pakai kalimat cadangan naskah: "Even the model refuses... the guard would have stopped it, as we saw on the previous slide." Jangan membaca jawaban (ada `religion: Islam` yang salah) |

Setelah langkah 5: Annisa "That's the demo... Thank you, Bara" → Bara kembali ke slide 16.

Waktu nyata ≈ 9-13 detik per langkah, bukan "instan". Isi jeda dengan narasi (naskah sudah memberi ruang). Total demo ≈ 4,5 menit, pas.

### 3.3 Rencana darurat

| Situasi | Tindakan |
|---|---|
| Jawaban belum muncul setelah **20 detik** | Annisa mengisi: "The agent is thinking: it calls tools in a loop, then writes the answer." Klien sudah mencoba ulang otomatis dengan jeda bertingkat bila DeepSeek 429/5xx/timeout (hingga 4 kali, total bisa sekitar 30 detik) |
| **25-30 detik** tanpa output, atau pesan `Maaf, terjadi kesalahan saat menghubungi AI` | Tekan Ctrl+C, buka **video rekaman** (slide tersembunyi setelah slide 15), kalimat Annisa: "Let's switch to the recorded run. Same system, same prompts." Jangan debug langsung |
| DeepSeek mati total, Neo4j hidup | Lanjutkan live **tanpa LLM** untuk langkah 3-4 lewat Cypher di Browser (S3 dan query top-5 Banten di bagian 2). Bara: "Same answer, without the agent." |
| Neo4j mati | `retrieve_person_info`, `retrieve_person_relationships`, `retrieve_kingdom_info` turun ke CSV (langkah 2 masih jalan); langkah 3-5 butuh Neo4j → video |
| Agent gagal start (timeout MCP) | Jalankan ulang sekali (booting Windows lambat; timeout klien 60 detik). Gagal lagi → video |
| Jawaban aneh/salah (halusinasi model) | Jangan membantah di panggung: "The numbers come from the graph; the wording is the model's." Lanjutkan |
| Internet putus | Hotspot; kalau tetap gagal → video |

**Rekam video cadangan (30 menit):** ScreenToGif atau OBS, resolusi 1080p, satu pengambilan yang berisi langkah 1-5 berurutan dengan prompt di atas. Simpan juga teks jawaban tiap langkah (copy dari terminal) di `main/backup/`. Masukkan ke deck: slide tersembunyi setelah slide 15 → Insert → Video (Start: When Clicked). Putar sekali dari PowerPoint sebelum tampil.

---

## 4. Penyelarasan naskah dan transisi

### Giliran bicara (cue)

| Waktu | Dari → ke | Kalimat pemicu (hafalkan) | Aksi Bara |
|---|---|---|---|
| 0:00-7:15 | Annisa | Slide 5: Annisa "Hi everyone, I'm Annisa", Bara masuk: "and I'm Bara. Hi!" | Satu kalimat saja, lalu diam |
| 7:15 | **Annisa → Bara** | "So, how did we fix all this? **Bara** will show you what we built." | "Thanks, Annisa. We built it in four steps." |
| 7:15-12:00 | Bara slide 8-10 | - | Slide 9: angka 356/24/734 |
| 12:00 | **Bara → Annisa** | "So now the data was clean and labelled. **Annisa, what did the graph actually tell us?**" | Berhenti bicara, maju ke slide 11 |
| 12:00-15:00 | Annisa slide 11-12 | - | Hening; klik sesuai cue |
| 15:00 | **Annisa → Bara** | "So how do we let an LLM use the graph without making things up? **Bara?**" | "This is where MCP comes in." |
| 15:00-18:00 | Bara slide 13-14 | - | Di akhir slide 14 pindah layar ke Bloom |
| 18:00 | **Bara → Annisa** | (tidak ada kalimat, naskah:) Annisa membuka demo: "Enough slides. Bara is driving." | Bloom siap di layar |
| 18:00-22:30 | Demo | Annisa tanya, Bara mengetik dan menjelaskan sistem | Sebut nama tool keras |
| 22:30 | **Bara → Annisa** | Annisa: "That's the demo. Thank you, Bara." | Kembali ke slide, `[CLICK]` ke slide 16 |
| 22:30-24:45 | Annisa slide 16-17 | - | Hening |
| 24:45 | Slide 18: bersama | Annisa "Terima kasih!", Bara "Thank you!" | - |

### Hal yang perlu disepakati dengan Annisa malam ini
1. **Siapa yang menekan slide.** Semua jalan di laptop Bara; naskah hanya menulis `[CLICK]`. Sepakati: Bara menekan sendiri setiap `[CLICK]` saat Annisa jeda, atau Annisa memberi aba "next". Latih sekali.
2. **Tidak ada giliran Annisa lewat jaringan jika terpisah:** naskah sudah menyebut "tunggu lawan selesai bicara karena audio online tertunda".
3. **Slide 16:** ubah kalimat Hayam Wuruk menjadi: "…fuzzy matching catches spelling variants, but not names that are completely different, such as a king's birth name and his regnal name." (hapus klaim bahwa itu terjadi di data kita.) Atau pertahankan sebagai ilustrasi sambil menambahkan "as an example".
4. **Slide 18:** putuskan publik/privat dan QR.
5. **Slide 10:** tambahkan "in our dataset" setelah "labelled with source and confidence", supaya tidak dibaca sebagai properti di graf.
6. **Model yang disebut bila ditanya:** agent dan V2 memakai **DeepSeek (`deepseek-chat`)**; imputasi data V1 memakai model lewat OpenRouter (rantai Gemini/Llama). Slide tidak menyebut vendor; siapkan jawaban ini untuk Q&A.

### Pembagian Q&A
Bara: MCP, agent, Cypher, guard, keamanan, model (DeepSeek), kenapa NetworkX bukan GDS (slide backup 19). Annisa: sejarah, sumber data, pelajaran, V1 vs V2 (slide backup 20; angka: 9/23 → 0/57, 30 orang, tanpa tinjauan manusia, recall V2 menurun).

---

## 5. Urutan kerja 12 jam ke depan (usulan)

1. (15 menit) Putuskan repo publik/privat; kabari Annisa soal slide 16, 10, 18.
2. (90 menit) Screenshot S1, S6 (wajib), S2, S3, S4, S5; tempel ke slide 6, 9, 11, 13, 14.
3. (30 menit) Rekam video demo; tempel sebagai slide tersembunyi.
4. (60 menit) Latihan penuh dengan Annisa, 2 kali, dengan timer; latih "klik" dan perpindahan jendela.
5. (30 menit) Uji Goldcast: screen share jendela vs layar, audio komputer untuk video.
6. Tidur. Pagi: pemanasan demo T-60 dan T-10. **Jangan ubah kode atau data lagi.**
