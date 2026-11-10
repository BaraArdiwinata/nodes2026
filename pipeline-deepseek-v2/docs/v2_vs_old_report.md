# Laporan Perbandingan: Pipeline v2 (DeepSeek) vs Pipeline Lama

Sampel: 30 tokoh (Jawa, Sunda/Cirebon/Banten, Banjar + 1 canary "Elizabeth Carter"). Baseline = `copy-of-repo-eas-graf/data/dataset_dinasti_final.csv` (tidak diubah).

## 1. Entitas salah / noise
| Metrik | Pipeline lama | Pipeline v2 |
|---|---|---|
| Baris imputasi LLM yang berasal dari halaman Wikipedia yang gagal guardrail (entitas salah/ambigu) | 1 dari 9 (11%) | 0 (halaman gagal guard tidak pernah dikirim ke LLM) |
| Nama relasi pada baris `llm_imputed` yang TIDAK didukung teks halaman | 9 dari 23 (39%) | 0 dari 57 (semua lolos verifikasi nama + kutipan bukti) |
| Usulan mentah LLM yang ditolak verifikasi bukti | tidak ada mekanisme | 4 dari 61 usulan (7%) |
| Nama dengan >1 kandidat manusia di Wikidata (homonim) | 3 nama (total 16 kandidat) | kandidat dipersempit ke yang grounded; ditandai manual_check: 0 |
| Entitas ditolak karena grounding lemah + guard gagal | tidak ada | 2 |

Penurunan entitas halusinasi (baris imputasi dari halaman salah): 11% -> 0%.
Penurunan relasi tak berdasar pada imputasi LLM: 39% -> 0% (angka v2 nol dijamin oleh konstruksi verifikasi, bukan bukti akurasi sejarah).

Contoh relasi lama yang tidak didukung teks: [('Panembahan Ratu I', 'pasangan', 'Glampok Raras', 'verified'), ('Rahmatullah dari Banjar', 'anak', 'Pangeran Damang', 'verified'), ('Rahmatullah dari Banjar', 'anak', 'Raden Zakaria', 'verified'), ('Rahmatullah dari Banjar', 'anak', 'Sultan Hidayatullah', 'verified'), ('Kertajaya', 'ayah', 'Bhathati', 'verified'), ('Dharmawangsa Teguh', 'anak', 'Istri Airlangga', 'verified')]

## 2. Distribusi status entitas v2
{
 "grounded_verified": 28,
 "rejected_weak_grounding": 2
}

Sumber data v2: {"wikidata+llm_imputed": 18, "wikidata": 10, "original": 2}

## 3. Relasi yang berhasil ditangkap (ayah+ibu+pasangan+anak+saudara)
| Field | Lama | v2 |
|---|---|---|
| ayah | 20 | 23 |
| ibu | 3 | 8 |
| pasangan | 5 | 8 |
| anak | 21 | 32 |
| saudara | 9 | 12 |
| **Total** | 58 | 83 |

- Relasi BARU di v2 yang tidak ada di data lama: 42 (semua berasal dari Wikidata terstruktur atau LLM + bukti tervalidasi).
- Relasi lama yang tidak muncul di v2: 17; dari itu 10 sebenarnya didukung teks halaman (potensi kehilangan recall), 7 tidak didukung teks (noise yang terbuang atau data lama dari Wikidata tanpa teks pendukung).

Daftar relasi baru: [('Rara Santang', 'ayah', 'Prabu Siliwangi', 'wikidata+llm_imputed'), ('Rara Santang', 'ibu', 'Nyai Subang Larang', 'wikidata+llm_imputed'), ('Rara Santang', 'saudara', 'Raden Walangsungsang (Pangeran Cakrabuana)', 'wikidata+llm_imputed'), ('Rara Santang', 'saudara', 'Raja Sengara (Raden Kian Santang)', 'wikidata+llm_imputed'), ('Inayatullah dari Banjar', 'pasangan', 'Gusti Timbuk binti Raden Aria Papati bin Sultan Hidayatullah I', 'wikidata+llm_imputed'), ('Inayatullah dari Banjar', 'anak', 'Saidullah dari Banjar', 'wikidata+llm_imputed'), ('Kusumawardhani', 'saudara', 'Nagarawardhani', 'wikidata+llm_imputed'), ('Prabu Gilingwesi', 'ayah', 'Mansiri', 'wikidata+llm_imputed'), ('Prabu Gilingwesi', 'pasangan', 'Dewi Samatha', 'wikidata+llm_imputed'), ('Rakeyan Medang', 'ibu', 'Kencana Sari', 'wikidata+llm_imputed'), ('Rakeyan Medang', 'anak', 'Dewi Samatha', 'wikidata+llm_imputed'), ('Kertabhumi', 'anak', 'Bathara Katong', 'wikidata+llm_imputed'), ('Kertabhumi', 'anak', 'Raden Bondan Kedjawen', 'wikidata+llm_imputed'), ('Kertabhumi', 'anak', 'Raden Patah', 'wikidata+llm_imputed'), ('Kertabhumi', 'anak', 'Ratu Ratna Pembayun', 'wikidata+llm_imputed'), ('Kertabhumi', 'saudara', 'Suraprabhawa', 'wikidata+llm_imputed'), ('Hidayatullah I dari Banjar', 'ayah', 'Rahmatullah dari Banjar', 'wikidata+llm_imputed'), ('Hidayatullah I dari Banjar', 'anak', 'Pangeran Senapati', 'wikidata+llm_imputed'), ('Hidayatullah I dari Banjar', 'anak', 'Gusti Nurasat', 'wikidata+llm_imputed'), ('Hidayatullah I dari Banjar', 'saudara', 'Pangeran Demang', 'wikidata+llm_imputed'), ('Hidayatullah I dari Banjar', 'saudara', 'Raden Zakaria', 'wikidata+llm_imputed'), ('Pangeran Walangsungsang', 'ibu', 'Nyi Subang Larang', 'wikidata+llm_imputed'), ('Pangeran Walangsungsang', 'pasangan', 'Nyimas Endang Geulis', 'wikidata+llm_imputed'), ('Pangeran Walangsungsang', 'anak', 'Nyimas Pakungwati', 'wikidata+llm_imputed'), ('Pangeran Walangsungsang', 'saudara', 'Nyai Mas Rara Santang', 'wikidata+llm_imputed'), ('Pangeran Walangsungsang', 'saudara', 'Pangeran Raja Sagara', 'wikidata+llm_imputed'), ('Sulaiman dari Banjar', 'anak', 'Pangeran Adam', 'wikidata+llm_imputed'), ('Suriansyah dari Banjar', 'ibu', 'Ratu Intan Sari', 'wikidata+llm_imputed'), ('Dharmawangsa Teguh', 'anak', 'Sri Jaya Merta', 'wikidata+llm_imputed'), ('Sunan Gunung Jati', 'ibu', 'Syarifah Mudaim (Nyai Rara Santang)', 'wikidata+llm_imputed'), ('Sunan Kudus', 'ibu', 'Nyai Ageng Manyuran', 'wikidata+llm_imputed'), ('Maulana Yusuf', 'ibu', 'Ratu Ayu Kirana', 'wikidata+llm_imputed'), ('Pangeran Pekik', 'ayah', 'Joyolengkoro', 'wikidata+llm_imputed'), ('Pangeran Pekik', 'pasangan', 'Ratu Wandansari', 'wikidata+llm_imputed'), ('Pangeran Pekik', 'saudara', 'Pangeran Trunojoyo', 'wikidata+llm_imputed'), ('Pangeran Pekik', 'saudara', 'Pangeran Indrajit', 'wikidata+llm_imputed'), ('Pangeran Pekik', 'saudara', 'Pangeran Wirodarmo', 'wikidata+llm_imputed'), ('Wikramawardhana', 'ayah', 'Raden Sumana', 'wikidata+llm_imputed'), ('Wikramawardhana', 'anak', 'Suhita', 'wikidata+llm_imputed'), ('Wikramawardhana', 'anak', 'Rajasakusuma', 'wikidata+llm_imputed'), ('Wikramawardhana', 'anak', 'Bhre Tumapel', 'wikidata+llm_imputed'), ('Sri Baduga Maharaja', 'anak', 'Pangeran Walangsungsang', 'wikidata')]

## 4. Biaya & kinerja v2
{
 "llm": {
  "calls": 30,
  "retries": 0,
  "failures": 0,
  "tokens": 23397,
  "latency": 51.583658933639526
 },
 "sparql": {
  "requests": 3,
  "retries": 0,
  "seconds": 4.678138017654419
 },
 "seconds": 227.5,
 "totals": {
  "raw": 61,
  "rejected": 4,
  "llm_calls": 28
 }
}

## Catatan metodologi (jujur)
- "Valid" berarti: dari Wikidata terstruktur dengan grounding, atau dari LLM dengan nama dan kutipan bukti yang ditemukan dalam teks halaman terverifikasi. Ini BUKAN verifikasi historis oleh manusia.
- Pengukuran noise pipeline lama memakai pencarian halaman berdasarkan nama (seperti pipeline lama) lalu guardrail v2 sebagai pengukur; ada kemungkinan false-positive guard. Sampel kecil (30).
