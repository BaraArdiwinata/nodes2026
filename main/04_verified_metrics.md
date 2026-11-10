# Verified Metrics (live Neo4j Desktop, bolt://localhost:7687, 2026-11-10)

Sumber: kueri langsung ke database lokal. Tidak ada perubahan data (patch tidak dijalankan, lihat "Tipe data").

## Node
| Label | Jumlah | Catatan |
|---|---|---|
| `Person` | **356** | 139 punya metrik graf; **217 tanpa metrik** (dibuat oleh `MERGE` relasi: orang tua/anak/penerus) |
| `Kingdom` | **24** | semua punya metrik |

## Relasi (total 734)
| Tipe | Jumlah |
|---|---|
| MEMIMPIN_ATAU_TERAFILIASI | 146 |
| MENGGANTIKAN | 140 |
| DIGANTIKAN_OLEH | 122 |
| ANAK | 107 |
| AYAH | 101 |
| SAUDARA | 42 |
| PASANGAN | 37 |
| IBU | 33 |
| KERABAT | 6 |

## Tipe data `louvain_cluster`
- Person: `INTEGER` pada 139 node, `NULL` pada 217. Kingdom: `INTEGER` pada 24 node.
- **Dugaan bug string TIDAK terbukti; patch konversi tidak perlu dijalankan.**
- 26 klaster Louvain berbeda di antara Person.

## Data quality
- Relasi duplikat (pasangan node + tipe sama): **0**.
- Self-loop: **1** (`Zaqiatuddin dari Aceh` -[:ANAK]-> dirinya sendiri). Self-loop `SAUDARA` sudah bersih.
- Duplikat nama yang lolos dedup: mis. "Tamjidullah II dari Banjar" vs "Tahmidullah II dari Banjar" (keduanya ada sebagai node terpisah).

## Demo: Top 5 PageRank (Person)
| # | Tokoh | PageRank | Klaster |
|---|---|---|---|
| 1 | Abu al-Mahasin | 0.006222 | 14 |
| 2 | Sri Isyana Tunggawijaya | 0.006069 | 4 |
| 3 | Alauddin al-Qahhar dari Aceh | 0.005890 | 16 |
| 4 | Tahmidullah II dari Banjar | 0.005553 | 1 |
| 5 | Tamjidillah I dari Banjar | 0.005411 | 1 |

Top Betweenness: Sunan Gunung Jati 0.0503, Maulana Hasanuddin 0.0386, Raden Hamzah 0.0248.

Afiliasi per kerajaan: Aceh 40, Banjar 22, Majapahit 15, Banten 14, Klungkung 11.

## Peringatan untuk demo
1. **Nilai metrik di DB berbeda dari CSV saat ini.** Contoh Abu al-Mahasin: DB 0.00622 vs CSV 0.00697; Sunan Gunung Jati betweenness DB 0.0503 vs CSV 0.0389. DB dimuat dari versi CSV lebih lama dan import memakai `coalesce` sehingga tidak menimpa. Peringkat atas sama, tetapi angka tidak konsisten dengan CSV/fallback agent. Opsi: jalankan patch metrik (cheatsheet 1.5, ini mengubah data) atau pakai angka DB di slide. Putuskan satu sumber.
2. **Rantai suksesi hanya 1 hop.** `*2..5` pada `DIGANTIKAN_OLEH` = 0 baris. Jangan janjikan "rantai suksesi multi-generasi".
3. **Tidak ada saudara kandung penuh** (berbagi ayah dan ibu): 0 pasang. Berbagi minimal satu orang tua: **13 pasangan** (mis. Rara Santang & Pangeran Walangsungsang via Sri Baduga Maharaja).
4. **Jalur terpendek Rara Santang -> Pangeran Walangsungsang** = 2 hop **lewat node `Kesultanan Cirebon`**, bukan lewat orang tua.
5. **Jalur leluhur terpanjang: 6 tingkat** (dinasti Banjar, mulai dari Sulaiman dari Banjar). Kandidat demo silsilah yang kuat.
6. `Hayam Wuruk` ada di DB tetapi tanpa metrik (hanya dibuat lewat relasi). `Kesultanan Banten` ada dan punya 14 afiliasi.

## Angka yang TIDAK bisa diverifikasi dari DB/dataset
- Latensi SPARQL ~11 s (README) vs 3.04 s (dashboard).
- "88% (95 dari 108) berhasil ditambal": di dataset hanya 49 dari 406 baris `llm_imputed` (12%), rata-rata `confidence_score` 0.82.
- "18% false-merge" dan "43% node inflation" dari dashboard.
