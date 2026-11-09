// ============================================================================
// CYPHER CHEAT-SHEET: NusantaraGraph, NODES 2026
// Dibangun dari: database/neo4j_load_queries.cypher + riwayat kueri Neo4j
// (neo4j_query_cmd_history_2026-11-9.txt). Kueri KRL/CommuterGraph dibuang.
//
// Iterasi proyek (dari riwayat):
//   UTS : label :Tokoh / :Kerajaan (properti `nama`), relasi BERKUASA_DI,
//         AYAH_DARI, IBU_DARI, MENIKAH_DENGAN; metrik dihitung LANGSUNG dengan
//         Neo4j GDS (graf 'utsGraf': pageRank, louvain, nodeSimilarity = Jaccard).
//   EAS : label :Person / :Kingdom (properti `name`), 9 tipe relasi; metrik
//         pre-computed di NetworkX, dimuat bersama CSV sebagai properti node.
//
// Catatan verifikasi: kueri bagian 1 dan sebagian bagian 2 muncul di riwayat
// (terbukti dieksekusi). Kueri bagian 3 sebagian BARU (belum dijalankan);
// tandai "[RUN-TEST]" sebelum dipakai di panggung. Cek ejaan nama di DB Anda.
// ============================================================================


// ############################################################################
// BAGIAN 1: INGESTION & SCHEMA
// ############################################################################
// Letakkan dataset_dinasti_final_with_metrics.csv di folder `import` Neo4j.
// Urutan: 1.1 -> 1.2 -> 1.3 -> 1.4. Aman diulang (MERGE + IF NOT EXISTS).

// --- 1.1 Constraint & index (jalankan PERTAMA) ---
CREATE CONSTRAINT kingdom_name_unique IF NOT EXISTS
FOR (k:Kingdom) REQUIRE k.name IS UNIQUE;

CREATE CONSTRAINT person_name_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS UNIQUE;

CREATE INDEX person_role_index IF NOT EXISTS
FOR (p:Person) ON (p.role);

// --- 1.2 Node Kingdom + metrik (versi final, CSV with_metrics) ---
LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.kerajaan IS NOT NULL AND row.kerajaan <> ""
MERGE (k:Kingdom {name: row.kerajaan})
ON CREATE SET
  k.capital = row.ibuKota, k.religion = row.agama,
  k.yearStart = toInteger(row.tahunMulai), k.wikidataID = row.wikidataID,
  k.pagerank_score = toFloat(row.kerajaan_PageRank),
  k.louvain_cluster = toInteger(row.kerajaan_Louvain_Cluster),
  k.betweenness_score = toFloat(row.kerajaan_Betweenness)
ON MATCH SET
  k.capital = coalesce(k.capital, row.ibuKota),
  k.religion = coalesce(k.religion, row.agama),
  k.yearStart = coalesce(k.yearStart, toInteger(row.tahunMulai)),
  k.wikidataID = coalesce(k.wikidataID, row.wikidataID),
  k.pagerank_score = coalesce(k.pagerank_score, toFloat(row.kerajaan_PageRank)),
  k.louvain_cluster = coalesce(k.louvain_cluster, toInteger(row.kerajaan_Louvain_Cluster)),
  k.betweenness_score = coalesce(k.betweenness_score, toFloat(row.kerajaan_Betweenness));

// --- 1.3 Node Person + metrik ---
LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.orang IS NOT NULL AND row.orang <> ""
MERGE (p:Person {name: row.orang})
ON CREATE SET
  p.role = row.peran, p.birthDate = row.tglLahir, p.deathDate = row.tglMati,
  p.wikidataID = row.personWikidataID, p.dynasty = row.dinasti,
  p.pagerank_score = toFloat(row.orang_PageRank),
  p.louvain_cluster = toInteger(row.orang_Louvain_Cluster),
  p.betweenness_score = toFloat(row.orang_Betweenness),
  p.adamic_adar_avg = toFloat(row.orang_AdamicAdar_Avg)
ON MATCH SET
  p.role = coalesce(p.role, row.peran),
  p.birthDate = coalesce(p.birthDate, row.tglLahir),
  p.deathDate = coalesce(p.deathDate, row.tglMati),
  p.wikidataID = coalesce(p.wikidataID, row.personWikidataID),
  p.dynasty = coalesce(p.dynasty, row.dinasti),
  p.pagerank_score = coalesce(p.pagerank_score, toFloat(row.orang_PageRank)),
  p.louvain_cluster = coalesce(p.louvain_cluster, toInteger(row.orang_Louvain_Cluster)),
  p.betweenness_score = coalesce(p.betweenness_score, toFloat(row.orang_Betweenness)),
  p.adamic_adar_avg = coalesce(p.adamic_adar_avg, toFloat(row.orang_AdamicAdar_Avg));

// --- 1.4 Relasi ---
// Afiliasi
LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.orang IS NOT NULL AND row.orang <> "" AND row.kerajaan IS NOT NULL AND row.kerajaan <> ""
MATCH (p:Person {name: row.orang})
MATCH (k:Kingdom {name: row.kerajaan})
MERGE (p)-[:MEMIMPIN_ATAU_TERAFILIASI]->(k);

// Silsilah: AYAH, IBU, PASANGAN, ANAK, SAUDARA, KERABAT. Ganti kolom/tipe per blok.
// Contoh AYAH (ulangi pola yang sama untuk ibu/pasangan/anak/saudara/kerabat):
LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.orang IS NOT NULL AND row.orang <> "" AND row.ayah IS NOT NULL AND row.ayah <> ""
MATCH (p:Person {name: row.orang})
UNWIND split(row.ayah, ",") AS fatherName
WITH p, trim(fatherName) AS cleanFather
WHERE cleanFather <> ""
MERGE (f:Person {name: cleanFather})
MERGE (p)-[:AYAH]->(f);

// Contoh SAUDARA dengan filter self-loop (PERBAIKAN dari riwayat: versi asli
// repo tidak memfilter, sehingga muncul (n)-[:SAUDARA]->(n); lihat 2.3):
LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.orang IS NOT NULL AND row.orang <> "" AND row.saudara IS NOT NULL AND row.saudara <> ""
MATCH (p:Person {name: row.orang})
UNWIND split(row.saudara, ",") AS siblingName
WITH p, trim(siblingName) AS cleanSibling
WHERE cleanSibling <> "" AND cleanSibling <> p.name
MERGE (s:Person {name: cleanSibling})
MERGE (p)-[:SAUDARA]->(s);

// Suksesi takhta; filter nama kerajaan yang salah masuk kolom pendahulu/penerus
// dari DBpedia (misal "Singhasari", "Demak Sultanate").
LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.orang IS NOT NULL AND row.orang <> "" AND row.pendahulu IS NOT NULL AND row.pendahulu <> ""
MATCH (p:Person {name: row.orang})
UNWIND split(row.pendahulu, ",") AS predName
WITH p, trim(predName) AS cleanPred
WHERE cleanPred <> "" AND NOT cleanPred CONTAINS "Kingdom"
  AND NOT cleanPred CONTAINS "Sultanate" AND NOT cleanPred CONTAINS "Empire"
MERGE (pred:Person {name: cleanPred})
MERGE (p)-[:MENGGANTIKAN]->(pred);
// DIGANTIKAN_OLEH: sama, dengan row.penerus / succName / (p)-[:DIGANTIKAN_OLEH]->(succ).

// --- 1.5 Patch metrik pada node yang sudah ada (dari riwayat, DIPERBAIKI) ---
// Di riwayat, patch memakai `louvain_cluster = row.orang_Louvain_Cluster` TANPA
// toInteger, sehingga tersimpan sebagai STRING. Versi benar:
LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.orang IS NOT NULL AND row.orang <> ""
MATCH (p:Person {name: row.orang})
SET p.pagerank_score   = toFloat(row.orang_PageRank),
    p.louvain_cluster  = toInteger(toFloat(row.orang_Louvain_Cluster)),
    p.betweenness_score = toFloat(row.orang_Betweenness),
    p.adamic_adar_avg  = toFloat(row.orang_AdamicAdar_Avg);

LOAD CSV WITH HEADERS FROM "file:///dataset_dinasti_final_with_metrics.csv" AS row
FIELDTERMINATOR ';'
WITH row WHERE row.kerajaan IS NOT NULL AND row.kerajaan <> ""
MATCH (k:Kingdom {name: row.kerajaan})
SET k.pagerank_score   = toFloat(row.kerajaan_PageRank),
    k.louvain_cluster  = toInteger(toFloat(row.kerajaan_Louvain_Cluster)),
    k.betweenness_score = toFloat(row.kerajaan_Betweenness);

// --- 1.6 Reset total (HANYA di instance demo; hapus semua data!) ---
// MATCH (n) DETACH DELETE n;


// ############################################################################
// BAGIAN 2: DATA QUALITY & SANITY CHECK
// ############################################################################

// --- 2.1 Jumlah node & relasi (angka resmi untuk slide) ---
MATCH (n) RETURN labels(n) AS Label, count(n) AS Jumlah;
MATCH ()-[r]->() RETURN type(r) AS Relasi, count(*) AS Jumlah ORDER BY Jumlah DESC;

// --- 2.2 Relasi duplikat (antara pasangan node yang sama, tipe sama) ---
// Riwayat memakai a.orang / b.orang: properti itu TIDAK ADA (nama = `name`),
// hasilnya selalu null. Versi benar:
MATCH (a)-[r]->(b)
WITH a, b, type(r) AS relasi, count(r) AS jumlah
WHERE jumlah > 1
RETURN a.name AS Dari, relasi, b.name AS Ke, jumlah AS TotalDuplikat
ORDER BY jumlah DESC LIMIT 25;

// --- 2.3 Self-loop (terbukti ada di data: SAUDARA ke diri sendiri) ---
MATCH (n)-[r]->(n)
RETURN labels(n) AS Label, type(r) AS JenisRelasi, count(r) AS Jumlah;

// Pembersihan (dijalankan di riwayat; WRITE, jangan di live demo):
// MATCH (n:Person)-[r:SAUDARA]->(n) DELETE r;

// --- 2.4 Cakupan metrik & tipe data (dugaan bug string louvain, lihat 1.5) ---
// Node yang dibuat oleh MERGE relasi (ayah/ibu/anak) TIDAK punya metrik.
MATCH (p:Person)
RETURN p.louvain_cluster IS NULL AS tanpa_klaster, count(*) AS jumlah;

// Neo4j 5.13+: cek tipe nilai. Harus INTEGER, bukan STRING.
MATCH (p:Person) WHERE p.louvain_cluster IS NOT NULL
RETURN valueType(p.louvain_cluster) AS tipe, count(*) AS jumlah;

// --- 2.5 Kemungkinan duplikat nama (berbeda kapitalisasi/spasi) ---
MATCH (p:Person)
WITH toLower(trim(p.name)) AS n, collect(p.name) AS varian
WHERE size(varian) > 1
RETURN varian LIMIT 20;

// --- 2.6 Nama kerajaan yang terselip jadi Person (kebocoran filter suksesi) ---
MATCH (p:Person)
WHERE p.name CONTAINS "Kingdom" OR p.name CONTAINS "Sultanate" OR p.name CONTAINS "Empire"
RETURN p.name LIMIT 20;


// ############################################################################
// BAGIAN 3: SHOWCASE & ANALYTICAL QUERIES (DEMO-READY)
// Semua read-only. Tip Neo4j Browser: warna node per `louvain_cluster`,
// ukuran node per `pagerank_score`. Beri LIMIT agar render cepat.
// ############################################################################

// --- 3.1 Peta semua silsilah (pembuka visual; dari riwayat) ---   [RUN-TEST]
MATCH (n:Person)-[r:AYAH|IBU|ANAK|PASANGAN|SAUDARA]->(m:Person)
RETURN n, r, m LIMIT 150;

// --- 3.2 Top 10 tokoh paling berpengaruh + node terhubungnya (dari riwayat) ---
MATCH (p:Person)
WHERE p.pagerank_score IS NOT NULL
WITH p ORDER BY p.pagerank_score DESC LIMIT 10
MATCH (p)-[r]-(connected)
RETURN p, r, connected;

// Versi tabel untuk slide / agent:
MATCH (p:Person) WHERE p.pagerank_score IS NOT NULL
RETURN p.name AS Tokoh, p.pagerank_score AS PageRank, p.louvain_cluster AS Klaster
ORDER BY PageRank DESC LIMIT 10;

// --- 3.3 Tokoh pada satu kerajaan, ukuran = PageRank ---   [RUN-TEST]
MATCH (p:Person)-[:MEMIMPIN_ATAU_TERAFILIASI]->(k:Kingdom {name:'Kesultanan Banten'})
RETURN p, k LIMIT 40;

// --- 3.4 Silsilah lintas generasi: leluhur (ayah & ibu) 4 tingkat ---   [RUN-TEST]
// Arah relasi: anak -[:AYAH|IBU]-> orang tua.
MATCH (p:Person) WHERE p.pagerank_score IS NOT NULL
WITH p ORDER BY p.pagerank_score DESC LIMIT 1
MATCH path = (p)-[:AYAH|IBU*1..4]->(leluhur:Person)
RETURN path;

// Jalur leluhur terpanjang di seluruh graf:
MATCH path = (p:Person)-[:AYAH|IBU*2..6]->(leluhur:Person)
RETURN path ORDER BY length(path) DESC LIMIT 5;

// --- 3.5 Rantai suksesi takhta ---   [RUN-TEST]
MATCH path = (a:Person)-[:DIGANTIKAN_OLEH*2..5]->(b:Person)
RETURN path ORDER BY length(path) DESC LIMIT 5;

// Pendahulu-penerus satu tokoh (dua arah):
MATCH (p:Person {name:'Hayam Wuruk'})
OPTIONAL MATCH (p)-[:MENGGANTIKAN]->(pendahulu)
OPTIONAL MATCH (p)-[:DIGANTIKAN_OLEH]->(penerus)
RETURN p.name, collect(DISTINCT pendahulu.name) AS pendahulu, collect(DISTINCT penerus.name) AS penerus;
// (ganti 'Hayam Wuruk' dengan nama persis di DB Anda)

// --- 3.6 Hubungan keluarga: berbagi AYAH dan IBU yang sama (dari riwayat) ---
MATCH (p1:Person)-[:AYAH]->(ayah:Person), (p1)-[:IBU]->(ibu:Person)
MATCH (p2:Person)-[:AYAH]->(ayah), (p2)-[:IBU]->(ibu)
WHERE elementId(p1) < elementId(p2)          // hindari pasangan ganda (riwayat memakai p1 <> p2)
RETURN p1, p2, ayah, ibu;

// Berbagi minimal satu orang tua (saudara tiri), diurutkan:
MATCH (p1:Person)-[:AYAH|IBU]->(ortu:Person)<-[:AYAH|IBU]-(p2:Person)
WHERE elementId(p1) < elementId(p2)
RETURN p1.name AS Tokoh1, p2.name AS Tokoh2, collect(ortu.name) AS OrangTuaBersama
ORDER BY size(OrangTuaBersama) DESC LIMIT 15;

// --- 3.7 Jalur hubungan terpendek antar dua tokoh (padanan tool agent) ---   [RUN-TEST]
MATCH (a:Person {name:'Rara Santang'}), (b:Person {name:'Pangeran Walangsungsang'})
MATCH path = shortestPath((a)-[*..8]-(b))
RETURN path;

// --- 3.8 Tokoh jembatan antar-dinasti (Betweenness) ---
MATCH (p:Person) WHERE p.betweenness_score IS NOT NULL
RETURN p.name AS Tokoh, p.betweenness_score AS Betweenness
ORDER BY Betweenness DESC LIMIT 5;

// --- 3.9 Ukuran klaster Louvain + contoh anggota ---
MATCH (p:Person) WHERE p.louvain_cluster IS NOT NULL
RETURN p.louvain_cluster AS Klaster, count(*) AS Anggota, collect(p.name)[..5] AS Contoh
ORDER BY Anggota DESC LIMIT 10;

// --- 3.10 Tokoh dengan kemiripan struktural tertinggi (Adamic-Adar rata-rata) ---
MATCH (p:Person) WHERE p.adamic_adar_avg IS NOT NULL
RETURN p.name AS Tokoh, p.adamic_adar_avg AS AdamicAdarAvg
ORDER BY AdamicAdarAvg DESC LIMIT 10;

// --- 3.11 Contoh Cypher yang DITOLAK guard agent (tampilkan di slide, jangan dijalankan) ---
// MATCH (p:Person)-[:MEMIMPIN_ATAU_TERAFILIASI]->(k:Kingdom {name:'Majapahit'}) DETACH DELETE p


// ############################################################################
// LAMPIRAN A: ARSIP PROTOTIPE UTS (GDS native, label :Tokoh/:Kerajaan)
// Hanya referensi/slide "Iterasi"; BUKAN untuk demo. Memerlukan plugin GDS dan
// data lama (dataset_gabungan_uts_graf.csv). Properti memakai `nama`, bukan `name`.
// ############################################################################

// Proyeksi graf in-memory GDS (UNDIRECTED)
// CALL gds.graph.project('utsGraf', ['Tokoh','Kerajaan'], {
//   BERKUASA_DI:   {orientation:'UNDIRECTED'},
//   AYAH_DARI:     {orientation:'UNDIRECTED'},
//   IBU_DARI:      {orientation:'UNDIRECTED'},
//   MENIKAH_DENGAN:{orientation:'UNDIRECTED'}
// });
// (Riwayat juga mencatat typo: gds.pageRank.stream('utsGraph') vs 'utsGraf')

// PageRank: 5 tokoh teratas
// CALL gds.pageRank.stream('utsGraf') YIELD nodeId, score
// RETURN gds.util.asNode(nodeId).nama AS Tokoh, score AS Skor_PageRank
// ORDER BY Skor_PageRank DESC LIMIT 5;

// Louvain: klaster + anggota
// CALL gds.louvain.stream('utsGraf') YIELD nodeId, communityId
// RETURN communityId AS ID_Klaster,
//        size(collect(gds.util.asNode(nodeId).nama)) AS Jumlah_Anggota,
//        collect(gds.util.asNode(nodeId).nama) AS Daftar_Tokoh
// ORDER BY Jumlah_Anggota DESC LIMIT 5;

// nodeSimilarity = Jaccard (alias di riwayat: Skor_Jaccard). Inilah sumber
// anomali "100%" pada simpul bertetangga sedikit yang kemudian diganti
// Adamic-Adar di NetworkX pada versi EAS.
// CALL gds.nodeSimilarity.stream('utsGraf') YIELD node1, node2, similarity
// RETURN gds.util.asNode(node1).nama AS Tokoh_1, gds.util.asNode(node2).nama AS Tokoh_2,
//        similarity AS Skor_Jaccard
// ORDER BY Skor_Jaccard DESC LIMIT 5;
