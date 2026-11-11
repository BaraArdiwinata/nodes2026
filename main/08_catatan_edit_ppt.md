# Catatan Edit PPT (untuk dipoles sebelum tampil)

Deck: [`NusantaraGraph_NODES2026.pptx`](NusantaraGraph_NODES2026.pptx). Slide yang perlu diedit diberi **tag kuning "EDIT"** di pojok kanan atas. Setelah selesai, hapus tag-nya (Home → Arrange → Selection Pane, cari `EDIT-TAG` dan `EDIT-TAG-text`).

Legenda: 🔴 wajib · 🟡 sangat disarankan · ⚪ opsional

## A. Media dari Neo4j / terminal

| Slide | Prioritas | Ambil apa | Caranya | Ganti bagian mana |
|---|---|---|---|---|
| 15 Demo | 🔴 | **Video rekaman demo lengkap** (cadangan kalau live demo gagal) | Rekam layar seluruh demo 5 langkah (Win+Alt+R / OBS). Simpan juga di `main/backup/` | Buat **slide tersembunyi** setelah slide 15 (klik kanan → Hide Slide), Insert → Video |
| 11 Insights | 🔴 | Screenshot/GIF graf: **ukuran node = PageRank, warna = klaster Louvain** | **Neo4j Bloom/Explore** (bukan Browser; Browser hanya bisa styling per label). Rule-based style: size by `pagerank_score`, colour by `louvain_cluster` (unique values). Tampilkan Banten atau Cirebon–Banten supaya Sunan Gunung Jati terlihat | Kalau ingin gambar besar, perkecil kartu atas atau pindahkan kartu Louvain |
| 14 Guard | 🔴 | Screenshot **penolakan asli** + **query Cypher asli** | Terminal: `cd copy-of-repo-eas-graf` lalu `python scripts/graph_rag_bot.py --test-analytical`. TEST 3 (minta DETACH DELETE), TEST 4 (SET langsung), TEST 5 ("Setyawati", "Asset" lolos). Lewati TEST 1 (Pajajaran = 0 baris) | Dua kotak kode gelap (kiri: query hasil, kanan: pesan penolakan) |
| 9 Graph model | 🟡 | Screenshot skema asli | Neo4j Browser: `CALL db.schema.visualization()` | Diagram Person–Person–Kingdom di kiri (angka 356/24/734 tetap) |
| 6 Why a graph | 🟡 | GIF: query dijalankan → path muncul | Browser, jalankan query yang ada di slide. Kalau Maulana Hasanuddin tidak ketemu, pakai `Pangeran Walangsungsang` (sudah terverifikasi: 2 hop lewat Kesultanan Cirebon) | Graf gambar di kanan atas. **Kalau nama di query diganti, ganti juga teks query di slide** |
| 13 MCP | 🟡 | GIF terminal agent memanggil tool | `python mcp_agent.py`, ketik `Siapa Abu al-Mahasin dan apa peran jaringannya?`. Log yang muncul: `-> [Execute Tool] retrieve_person_info dengan argumen: ...` | Baris 5 kotak alur atau baris "The five tools" (pilih salah satu) |
| 10 Heal | ⚪ | Before/after mojibake | Screenshot baris CSV mentah vs bersih | Baris "Broken text" |
| 1 / 4 / 18 | ⚪ | Screenshot graf asli yang dibuat pudar | Screenshot Bloom, transparansi gambar 70–80% | Motif node dekoratif di kanan |

**Tips GIF:** pakai ScreenToGif (gratis) atau ShareX, durasi 5–10 detik, lebar sekitar 1200 px, font Browser/terminal diperbesar. Masukkan GIF lewat Insert → Pictures (otomatis bergerak saat slideshow). Video lewat Insert → Video, set Playback → Start: When Clicked.

## B. Konten yang harus dicek

| Slide | Prioritas | Cek |
|---|---|---|
| 3 Story | 🔴 | Fakta sejarah: Rara Santang ibu Sunan Gunung Jati; Maulana Hasanuddin putra Sunan Gunung Jati dan pendiri Kesultanan Banten. Slide ini **ilustrasi**, bukan output query |
| 6 | 🔴 | Ejaan `Rara Santang` dan `Maulana Hasanuddin` di DB (lihat A) |
| 18 Terima kasih | 🔴 | Tambah QR repo + kontak/LinkedIn. **Pastikan repo GitHub publik**, atau hapus link-nya |
| 15 Demo | 🔴 | Latih langkah 5: LLM mungkin menolak sendiri sebelum guard bekerja. Kalimat cadangan ada di speaker notes |
| 2 | ⚪ | Nama di tabel hanya contoh; bebas diganti tokoh yang lebih dikenal penonton |

## C. Hasil cek kode (sudah diperbaiki di deck)

| Temuan | Bukti di kode | Perubahan |
|---|---|---|
| `LIMIT 25` hanya ditambahkan kalau query belum punya LIMIT | [graph_rag_bot.py:420-424](../copy-of-repo-eas-graf/scripts/graph_rag_bot.py#L420-L424) | Slide 14: "LIMIT 25 added when a query has none" (sebelumnya "every query capped") |
| Dedup hanya mengirim pasangan dengan fuzzy `token_set_ratio ≥ 85` ke LLM | [pipeline_graf.py:375-378](../copy-of-repo-eas-graf/scripts/pipeline_graf.py#L375-L378) | Slide 16: Hayam Wuruk vs Sri Rajasanagara dijadikan contoh nama yang **belum** tertangani (jujur dan cocok dengan cerita "names are the hardest part") |
| `confidence_score` adalah perkiraan LLM sendiri | [pipeline_graf.py:230](../copy-of-repo-eas-graf/scripts/pipeline_graf.py#L230) | Speaker notes slide 10. Kalau ditanya: "self-estimated by the LLM, not calibrated" |
| Neo4j Browser tidak bisa styling berdasarkan properti | - | Slide 11, 15 dan `02_demo_script.md` langkah 1 sekarang memakai Bloom |

Sudah cocok dengan kode: 5 tool MCP ([mcp_server.py](../copy-of-repo-eas-graf/mcp_server.py)), transport stdio, guard regex `\b` + pesan "Only read-only operations are allowed", healer cp1252 maksimal 3 kali, Union-Find, PageRank alpha 0.85, Louvain seed 42, Betweenness, Adamic-Adar menggantikan Jaccard ([analisis_graf.py](../copy-of-repo-eas-graf/scripts/analisis_graf.py)), log agent `-> [Execute Tool]`.

Catatan kecil: [04_verified_metrics.md](04_verified_metrics.md) menyebut "Tamjidullah II vs Tahmidullah II" sebagai duplikat yang lolos. Secara sejarah keduanya kemungkinan **dua sultan Banjar yang berbeda**, jadi jangan dipakai sebagai contoh dedup gagal.
