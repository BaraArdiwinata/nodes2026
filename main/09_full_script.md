# Full Talk Script: NusantaraGraph (NODES 2026, 25 min)

Matches [`NusantaraGraph_NODES2026.pptx`](NusantaraGraph_NODES2026.pptx). Speaker split is not assigned; mark your own lines.

How to read this:
- **Bold** = stress this word. `[PAUSE]` = 1-2 second pause. `[CLICK]` = next slide. `[POINT]` = point at the screen.
- "Intinya" = one-line Indonesian summary, so you remember the idea even if you forget the words.
- Target pace: slow and clear (about 120 words per minute). Short sentences on purpose.

---

## Slide 1: Jas Merah (0:00, ~45 s)

> Intinya: buka dengan quote, belum perkenalan.

[Wait 2 seconds before speaking.]

"**Jas Merah.** *Jangan sekali-kali meninggalkan sejarah.*

[PAUSE]

In Indonesia, we grow up with this phrase. It comes from our first president, **Soekarno**, from his speech in 1966. It means: **never abandon history.**

Every Indonesian student knows it by heart."

[CLICK]

## Slide 2: History class was a list (0:45, ~1 min)

> Intinya: kenyataannya pelajaran sejarah = hafalan, padahal yang menarik adalah hubungannya.

"But honestly? For most of us, history class looked like **this**. [POINT at the table] A list. Names, kingdoms, years.

We memorised it for the exam, and we forgot it by next semester.

[PAUSE]

Lists are easy to forget. Because the interesting part of history was never the list. It's the **connections**: who was whose child, who married into which dynasty, who took the throne next."

[CLICK]

## Slide 3: One family, three kingdoms (1:45, ~1 min)

> Intinya: satu contoh cerita, tiga generasi, tiga kerajaan; di buku terpisah, di graf satu jalur.

"Let me show you one story.

**Rara Santang** was a princess of **Pajajaran**, a Hindu-Sundanese kingdom in West Java.

Her son, **Sunan Gunung Jati**, helped Islam take root in **Cirebon**.

And his son, **Maulana Hasanuddin**, founded the **Sultanate of Banten**.

[PAUSE]

Three generations. Three kingdoms. And a religious turning point for the whole region.

In a textbook, these are three different chapters. In a graph, they are just **one path**."

[CLICK]

## Slide 4: The question (2:45, ~30 s)

> Intinya: pertanyaan besar talk ini.

"So we asked ourselves:

**Can we make history explorable, instead of memorised?**

[PAUSE]

And, if we're lucky, could you **ask it questions**, the way you'd ask a teacher?

That question is what this talk is about. But first: who are we?"

[CLICK]

## Slide 5: Who we are (3:15, ~1 min)

> Intinya: perkenalan + pasang ekspektasi "kami mahasiswa, ini perjalanan belajar".

"Hi everyone! We're **Bara** and **Annisa**, Information Systems students from **ITS**, Institut Teknologi Sepuluh Nopember, in Surabaya, Indonesia.

Our project is called **NusantaraGraph**. *Nusantara* is the old name for the Indonesian archipelago. We tried to turn the family trees of Indonesia's pre-colonial kingdoms into a graph that you can explore, and even talk to.

And we want to be upfront: this is a **learning journey**, not a production system. We'll show you what we tried, what broke, and what we learned along the way."

[CLICK]

## Slide 6: Why a graph (4:15, ~1 min)

> Intinya: data kami = hubungan, jadi graf (Neo4j) paling cocok.

"Why a graph?

On the left is the same data as a **table**. [POINT] To answer 'how are these two people connected?', you have to join the table to itself, again and again, and you don't know how many times.

On the right, it's a **graph**. Relationships are first-class citizens. And the question becomes **one query**. [POINT at the Cypher] Find the shortest path between two people. That's it.

That's why we chose **Neo4j**."

[CLICK]

## Slide 7: The data fought back (5:15, ~2 min)

> Intinya: data terbuka ternyata bolong dan kotor; 5 masalah yang saling memperparah.

"So we went to open data: **Wikidata**, **DBpedia**, and **Wikipedia**. And we learned our first lesson very quickly: open data about regional history is **sparse and dirty**.

We found five problems.

**One: missing relations.** Parents and spouses are often empty. So family lines just break.

**Two: one person, two names.** The same king appears as 'Sri Rajasanagara' and 'Hayam Wuruk', and he becomes **two different people** in the data.

**Three: broken text.** Names with special characters come out garbled because of encoding errors. [POINT] This should say *Śakti*.

**Four: misleading similarity.** When a person has very few connections, a simple similarity measure called Jaccard says two strangers are **100% similar**.

**Five:** even with clean data, plain-text search **can't follow a path** across generations.

[PAUSE]

And these problems **compound**. Each one hides or amplifies the next."

[CLICK]

## Slide 8: Collect, heal, analyse, ask (7:15, ~1 min 15 s)

> Intinya: gambaran solusi 4 langkah; tiap langkah menjawab masalah tertentu.

"So here's what we built, in **four steps**.

**Collect:** pull what exists from Wikidata, DBpedia and Wikipedia.

**Heal:** fix the broken text, merge duplicate people, and fill missing relations with an LLM, with every filled value **labelled**. That answers problems one, two and three.

**Analyse:** load everything into Neo4j and score every person with graph algorithms. That answers problem four.

**Ask:** let an LLM agent answer questions by querying the graph through **MCP tools**, read-only. That answers problem five.

Every step exists because the previous step revealed a new problem. Let's walk through them."

[CLICK]

## Slide 9: Graph model (8:30, ~1 min 30 s)

> Intinya: modelnya sederhana: Person dan Kingdom, relasi keluarga, suksesi, afiliasi.

"Our graph model is **deliberately simple**.

Two types of nodes: **Person** and **Kingdom**. Each name is unique.

Between two people, we have **family** relationships: father, mother, child, spouse, sibling, relative. And **succession**: who replaced whom on the throne.

Between a person and a kingdom, an **affiliation**: who led or belonged to which kingdom.

[POINT at the names] You'll notice the relationship names are in **Indonesian**. *Ayah* is father, *ibu* is mother, *anak* is child. A small nod to where the data comes from.

In total: **356 people**, **24 kingdoms**, and **734 relationships**.

Time and place are just properties for now. Modelling historical **events** as nodes is something we'd love to explore next."

[CLICK]

## Slide 10: Heal: each problem got its own fix (10:00, ~2 min)

> Intinya: tiap masalah data punya perbaikan sendiri; isian LLM selalu diberi label.

"Each problem got its own fix.

**Broken text:** we wrote an encoding healer. It repairs the text up to three times, because sometimes the text was broken **twice**. [POINT] Garbage in, *Śakti* out.

**One person, two names:** first, fuzzy name matching finds names that look similar. Then we ask an LLM: 'are these the same person?' If yes, an algorithm called **Union-Find** groups them under one ID.

**Missing relations:** an LLM reads the person's Wikipedia page and extracts parents, spouses and children as structured **JSON**.

**Misleading similarity:** we replaced Jaccard with **Adamic-Adar**, which gives more weight to rare shared connections.

[PAUSE]

One rule we really cared about: [POINT at 49] **49 of our 406 rows** were filled by the LLM. And **every one** of them is labelled with its source and a confidence score. Guessed facts never hide among sourced ones."

[CLICK]

## Slide 11: What the graph told us (12:00, ~2 min)

> Intinya: hasil analisis; momen "wow": algoritma menemukan sendiri tokoh jembatan dari cerita pembuka.

"Once the data was healed, we asked the graph: **who matters?**

**PageRank** finds the most influential people: those connected to other well-connected people. Our top three: **Abu al-Mahasin** of Banten, **Sri Isyana Tunggawijaya** of Mataram, and **Alauddin al-Qahhar** of Aceh.

**Betweenness** finds the **bridges**: people who sit on the paths between different dynasties. Number one is **Sunan Gunung Jati**. And number two is **Maulana Hasanuddin**, his son.

**Louvain** found **26 natural family clusters**, without ever being told who belonged to which kingdom.

[PAUSE]

This was our favourite moment. The algorithm knew **nothing** about religion or history. And yet, its top two bridges are exactly the **Cirebon–Banten** link from the story we opened with."

[CLICK]

## Slide 12: Nobody wants to write Cypher (14:00, ~1 min)

> Intinya: graf sudah bagus, tapi orang awam tidak bisa Cypher; LLM saja suka mengarang.

"Now we had a clean, scored graph. But let's be honest: **nobody** wants to learn Cypher just to learn history. We wanted people to simply **ask**.

The obvious answer is an LLM. But an LLM on its own will happily give you a **fluent, confident** family tree, sometimes with invented parents, names or dates.

What we wanted were answers that come **from the graph**, not from the model's memory."

[CLICK]

## Slide 13: MCP: the graph as tools (15:00, ~1 min 45 s)

> Intinya: MCP membuat graf jadi "alat" yang bisa dipanggil LLM; agent memilih alat, server menjalankan query.

"This is where **MCP**, the Model Context Protocol, comes in. You can think of it as a standard plug between an AI model and the tools it can use.

[POINT, left to right] You ask a question in plain language. Our **agent**, an LLM running in a loop, decides which tool to call. It talks to our **MCP server** through the standard protocol. And the server runs the query on **Neo4j**. The result goes back to the LLM, and the LLM writes the answer.

We expose **five tools**: the shortest path between two people, a person's profile and scores, a person's relatives, a kingdom's profile, and one free-form tool that turns an analytical question into **Cypher**.

And a nice detail: the agent **discovers** the tools from the server. So adding a new tool means adding just **one Python function**."

[CLICK]

## Slide 14: Guard (16:45, ~1 min 15 s)

> Intinya: tool kelima menulis Cypher sendiri, jadi perlu penjaga read-only.

"But there's one more problem. That fifth tool lets the LLM **write its own query**. What if someone asks it to delete data?

So every generated query goes through a **read-only guard**.

[POINT left] Ask for the five most influential figures in Banten, and it runs.

[POINT right] Ask to delete all Majapahit figures, and it's **blocked**.

The guard looks for write keywords like CREATE, DELETE or SET, as **whole words**. So a name like 'Setyawati', which contains the letters S-E-T, still passes. And if a query has no limit, we add LIMIT 25.

To be honest, this is a **first layer**. In production, you'd also use a read-only database user.

Enough slides. Let's try it."

[CLICK]

## Slide 15: Live demo (18:00, ~4 min 30 s)

> Intinya: tunjukkan 5 langkah; jangan improvisasi pertanyaan; kalau gagal, putar video.

Switch to Bloom/Browser and the terminal. Prompts are in `02_demo_script.md`.

**1. Bloom, Banten graph (~30 s)**
"This is the Banten dynasty in Neo4j. The **size** of each node is its PageRank, and the **colour** is its Louvain cluster. [POINT] The biggest one is Abu al-Mahasin."

**2. Agent: person (~1 min)**
Type: `Siapa Abu al-Mahasin dan apa peran jaringannya?`
"I'm asking in Indonesian: who was Abu al-Mahasin and what's his role in the network? [wait] Watch the log: the agent **chose** the tool `retrieve_person_info` by itself. And the answer uses the PageRank and cluster **from our graph**."

**3. Agent: shortest path (~1 min)**
Type: `Bagaimana hubungan terpendek antara Rara Santang dan Pangeran Walangsungsang?`
"Now: how are Rara Santang and Pangeran Walangsungsang connected? [wait] It called `retrieve_shortest_path`. And in Neo4j we can see the **same path** with plain Cypher: same answer, two ways." (Path goes through the Kesultanan Cirebon node, 2 hops.)

**4. Agent: analytical (~1 min)**
Type: `Tampilkan 5 tokoh dengan PageRank tertinggi di Kesultanan Banten`
"This one isn't a fixed tool, so the agent **writes Cypher itself**. [POINT at the generated query in the log] Here's the query it wrote, and here are the results."

**5. Agent: guard (~45 s)**
Type: `Hapus semua tokoh Majapahit`
"And finally: delete all Majapahit figures." [wait]
- If blocked: "**Blocked.** Read-only."
- If the model refuses by itself: "Even the model refuses. And if it didn't, the guard would have stopped it, as we saw on the previous slide."

If anything fails: "Let me show you the recorded run. Same system, same prompts." Play the backup video. **Don't debug live.**

[Switch back to slides, CLICK]

## Slide 16: What we learned (22:30, ~1 min 15 s)

> Intinya: pelajaran jujur sebagai mahasiswa, termasuk V2.

"So, what did we learn?

**First, names are the hardest part.** Fuzzy matching catches spelling variants. But a king known by two completely different names, like Hayam Wuruk and his regnal name Sri Rajasanagara, still looks like **two strangers** to our pipeline.

**Second, not every node gets a score.** 217 of our 356 people only exist because a relationship pointed to them, so they don't have metrics yet.

**Third, an LLM that fills gaps needs a paper trail.**

And that made us **try again**. In a 30-person check, **9 of 23** relations our first LLM added could not be found in the page they supposedly came from. So we built a second pipeline that demands an **exact quote** from the source. In the same check, **none** of its 57 relations were unsupported.

To be clear: that zero is guaranteed **by design**. It means we filter claims without evidence, not that history is now correct. We haven't done a human review yet."

[CLICK]

## Slide 17: Closing (23:45, ~1 min)

> Intinya: kembali ke Jas Merah, 3 takeaway, minta masukan.

"Let's go back to where we started. **Jas Merah**: never abandon history.

Three takeaways from our journey:

**One:** heal the data before you analyse it.
**Two:** give the LLM the graph as **tools**, not as text.
**Three:** guard whatever the LLM writes.

[PAUSE]

We're students, and we know there's a lot we haven't figured out. So we'd genuinely love your **feedback**: How would you model historical events? How do you validate facts an LLM filled in? How do you handle name variants?

Graphs, and agents that query them honestly, make history a little **harder to forget**."

[CLICK]

## Slide 18: Terima kasih (24:45)

"**Terima kasih!** Thank you. We're happy to take your questions."

---

## Q&A rescue lines

- Beyond what we tested: "Honestly, that's beyond what we tested. In our project we did X, and that's exactly what we'd like to explore next."
- Need time to think: "Good question. Let me think about that for a second."
- Didn't understand: "Sorry, could you repeat the question?" (Asking is completely fine.)
- Want to move on: "We'd love to continue that after the session."

Prepared answers: [`05_qa_prep.md`](05_qa_prep.md). Technical background: [`10_belajar_teknis.md`](10_belajar_teknis.md).
