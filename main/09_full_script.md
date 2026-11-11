# Full Talk Script: NusantaraGraph (NODES 2026, 25 min)

One document to read from start to finish: slides, transitions, and demo dialogue. Matches [`NusantaraGraph_NODES2026.pptx`](NusantaraGraph_NODES2026.pptx).

**Speakers:** 🟣 **ANNISA** (story, opening, insights, closing, demo host) · 🔵 **BARA** (technical parts, demo operator; everything runs on Bara's laptop)

**Marks:**
- **bold** = stress this word
- ↗ = voice goes up · ↘ = voice goes down (sounds confident)
- ‖ = short pause · ‖‖ = long pause (2 s)
- `[CLICK]` = next slide · `[ACTION]` = what to do

> Intinya = one-line Indonesian summary. Not read aloud.

| Block | Slides | Speaker | Time |
|---|---|---|---|
| Opening | 1-7 | 🟣 Annisa (Bara says one line on slide 5) | 0:00-7:15 |
| How we built it | 8-10 | 🔵 Bara | 7:15-12:00 |
| What the graph told us | 11-12 | 🟣 Annisa | 12:00-15:00 |
| Agent, guard, demo | 13-15 | 🔵 Bara (+ 🟣 Annisa hosts the demo) | 15:00-22:30 |
| Lessons and closing | 16-18 | 🟣 Annisa (Bara joins on 18) | 22:30-25:00 |

---

# PART 1: OPENING (🟣 Annisa)

## Slide 1: Jas Merah (0:00, ~45 s)

> Intinya: buka dengan quote, belum perkenalan.

`[ACTION]` Wait 2 seconds. Look at the camera. Speak slowly.

🟣 **ANNISA:**
"**Jas Merah.** ‖ *Jangan sekali-kali meninggalkan sejarah.* ↘ ‖‖

In Indonesia, we grow up with this phrase. ‖ It comes from our first president, **Soekarno**, ‖ from his speech in nineteen sixty-six. ↘

It means: ‖ **never abandon history.** ↘ ‖

Every Indonesian student knows it by **heart**." ↘

`[CLICK]`

## Slide 2: History class was a list (0:45, ~1 min)

> Intinya: kenyataannya pelajaran sejarah = hafalan, padahal yang menarik adalah hubungannya.

🟣 **ANNISA:**
"But honestly? ↗ ‖ For most of us, history class looked like **this**. ↘ ‖ A list. ‖ Names ↗, kingdoms ↗, years. ↘

We memorised it for the **exam** ↗, ‖ and we forgot it by next **semester**. ↘ ‖

Lists are **easy to forget**. ↘ ‖ Because the interesting part of history was never the **list**. ↘ ‖‖ It's the **connections**: ‖ who was whose **child** ↗, who married into which **dynasty** ↗, ‖ who took the **throne** next." ↘

`[CLICK]`

## Slide 3: One family, three kingdoms (1:45, ~1 min)

> Intinya: satu contoh cerita; di buku terpisah, di graf satu jalur.

🟣 **ANNISA:**
"Let me show you **one story**. ↘ ‖

**Rara Santang** was a princess of **Pajajaran**, ↗ ‖ a Hindu-Sundanese kingdom in West Java. ↘ ‖

Her son, ‖ **Sunan Gunung Jati**, ‖ helped Islam take root in **Cirebon**. ↘ ‖

And **his** son, ‖ **Maulana Hasanuddin**, ‖ founded the **Sultanate of Banten**. ↘ ‖‖

Three generations ↗. ‖ Three kingdoms ↗. ‖ And a religious **turning point** for the whole region. ↘ ‖

In a textbook, ‖ these are three different **chapters**. ↘ ‖ In a graph, ‖ they are just ‖ **one path**." ↘

`[CLICK]`

## Slide 4: The question (2:45, ~30 s)

> Intinya: pertanyaan besar talk ini.

🟣 **ANNISA:**
"So we asked ourselves: ‖

Can we make history **explorable** ↗, ‖ instead of **memorised**? ↗ ‖‖

And, if we're lucky, ‖ could you **ask it questions**, ‖ the way you'd ask a **teacher**? ↗ ‖‖

That question is what this talk is about. ↘ ‖ But first: ‖ who are we?" ↗

`[CLICK]`

## Slide 5: Who we are (3:15, ~1 min)

> Intinya: perkenalan + pasang ekspektasi "kami mahasiswa, ini perjalanan belajar".

🟣 **ANNISA:**
"Hi everyone! ↗ I'm **Annisa** ‖"

🔵 **BARA:**
"‖ and I'm **Bara**. Hi!"

🟣 **ANNISA:**
"We're Information Systems students from **ITS**, ‖ Institut Teknologi Sepuluh Nopember, ‖ in **Surabaya**, Indonesia. ↘ ‖

Our project is called **NusantaraGraph**. ↘ ‖ *Nusantara* is the old name for the **Indonesian archipelago**. ↘ ‖ We tried to turn the family trees of Indonesia's pre-colonial kingdoms ‖ into a graph that you can **explore** ↗, ‖ and even **talk to**. ↘ ‖

And we want to be upfront: ‖ this is a **learning journey**, ‖ not a production system. ↘ ‖ We'll show you what we **tried** ↗, what **broke** ↗, ‖ and what we **learned** along the way." ↘

`[CLICK]`

## Slide 6: Why a graph (4:15, ~1 min)

> Intinya: data kami = hubungan, jadi graf (Neo4j) paling cocok.

🟣 **ANNISA:**
"So, ‖ why a **graph**? ↗ ‖

On the left is our data as a **table**. ↘ ‖ To answer *'how are these two people connected?'* ↗, ‖ you have to join the table to itself, ‖ again ‖ and again, ‖ and you don't even know **how many times**. ↘ ‖

On the right, ‖ it's a **graph**. ↘ ‖ Relationships are **first-class**. ↘ ‖ And the question becomes ‖ **one query**: ‖ find the shortest path between two people. ↘ ‖ That's it. ↘ ‖

That's why we chose **Neo4j**." ↘

`[CLICK]`

## Slide 7: The data fought back (5:15, ~2 min)

> Intinya: data terbuka bolong dan kotor; 5 masalah yang saling memperparah.

🟣 **ANNISA:**
"So we went to **open data**: ‖ Wikidata ↗, DBpedia ↗, and Wikipedia. ↘ ‖ And we learned our first lesson very quickly: ‖ open data about regional history is **sparse** ↗ ‖ and **dirty**. ↘ ‖‖

We found **five** problems. ↘ ‖

**One**: missing relations. ↘ ‖ Parents and spouses are often **empty**, ‖ so family lines just **break**. ↘ ‖

**Two**: one person, ‖ two names. ↘ ‖ The same king appears as *'Sri Rajasanagara'* ↗ ‖ and *'Hayam Wuruk'* ↗, ‖ and he becomes **two different people**. ↘ ‖

**Three**: broken text. ↘ ‖ Names with special characters come out **garbled**. ↘ ‖ This one ‖ should say *Śakti*. ↘ ‖

**Four**: misleading similarity. ↘ ‖ When a person has very few connections, ‖ a simple measure called Jaccard says two strangers are ‖ **one hundred percent** similar. ↘ ‖

And **five**: ‖ even with clean data, ‖ plain-text search **can't follow a path** across generations. ↘ ‖‖

And these problems **compound**. ↘ ‖ Each one hides ‖ or amplifies ‖ the next. ↘ ‖‖

**[HANDOFF]** So, ‖ how did we fix all this? ↗ ‖ **Bara** will show you what we built." ↘

`[CLICK]`

---

# PART 2: HOW WE BUILT IT (🔵 Bara)

## Slide 8: Collect, heal, analyse, ask (7:15, ~1 min 15 s)

> Intinya: gambaran solusi 4 langkah; tiap langkah menjawab masalah tertentu.

🔵 **BARA:**
"Thanks, Annisa. ‖ We built it in **four steps**.

**Collect**: ‖ pull what exists from Wikidata, DBpedia and Wikipedia.

**Heal**: ‖ fix the broken text, merge duplicate people, and fill missing relations with an LLM, ‖ with every filled value **labelled**. ‖ That answers problems one, two and three.

**Analyse**: ‖ load everything into Neo4j and score every person with **graph algorithms**. ‖ That answers problem four.

**Ask**: ‖ let an LLM agent answer questions by querying the graph through **MCP tools**, ‖ read-only. ‖ That answers problem five.

Every step exists because the **previous** step revealed a new problem. ‖ Let's walk through them."

`[CLICK]`

## Slide 9: Graph model (8:30, ~1 min 30 s)

> Intinya: modelnya sederhana: Person dan Kingdom, relasi keluarga, suksesi, afiliasi.

🔵 **BARA:**
"Our graph model is **deliberately simple**.

Two types of nodes: **Person** and **Kingdom**. ‖ Each name is unique.

Between two people, we have **family** relationships: ‖ father, mother, child, spouse, sibling, relative. ‖ And **succession**: ‖ who replaced whom on the throne.

Between a person and a kingdom, an **affiliation**: ‖ who led or belonged to which kingdom.

You'll notice the relationship names are in **Indonesian**. ‖ *Ayah* is father, *ibu* is mother, *anak* is child. ‖ A small nod to where the data comes from.

In total: ‖ **356** people, ‖ **24** kingdoms, ‖ and **734** relationships.

Time and place are just properties for now. ‖ Modelling historical **events** as nodes is something we'd love to explore next."

`[CLICK]`

## Slide 10: Heal: each problem got its own fix (10:00, ~2 min)

> Intinya: tiap masalah data punya perbaikan sendiri; isian LLM selalu diberi label.

🔵 **BARA:**
"Each problem got its **own fix**.

**Broken text**: ‖ we wrote an encoding healer. ‖ It repairs the text up to **three times**, ‖ because sometimes the text was broken **twice**. ‖ Garbage in, ‖ *Śakti* out.

**One person, two names**: ‖ first, fuzzy name matching finds names that **look** similar. ‖ Then we ask an LLM: ‖ *'are these the same person?'* ‖ If yes, ‖ an algorithm called **Union-Find** groups them under one ID.

**Missing relations**: ‖ an LLM reads the person's Wikipedia page ‖ and extracts parents, spouses and children ‖ as structured **JSON**.

**Misleading similarity**: ‖ we replaced Jaccard with **Adamic-Adar**, ‖ which gives more weight to **rare** shared connections.

One rule we really cared about: ‖ **forty-nine** ‖ of our four hundred and six rows ‖ were filled by the LLM. ‖ And **every one** of them is labelled with its source and a confidence score. ‖ Guessed facts never hide among sourced ones.

**[HANDOFF]** So now the data was clean and labelled. ‖ Annisa, ‖ what did the graph actually **tell** us?"

`[CLICK]`

---

# PART 3: WHAT THE GRAPH TOLD US (🟣 Annisa)

## Slide 11: What the graph told us (12:00, ~2 min)

> Intinya: hasil analisis; momen "wow": algoritma menemukan sendiri tokoh jembatan dari cerita pembuka.

🟣 **ANNISA:**
"Once the data was healed, ‖ we asked the graph a simple question: ‖ **who matters**? ↗ ‖‖

**PageRank** finds the most **influential** people: ‖ those connected to other well-connected people. ↘ ‖ Our top three: ‖ **Abu al-Mahasin** of Banten ↗, ‖ **Sri Isyana Tunggawijaya** of Mataram ↗, ‖ and **Alauddin al-Qahhar** of Aceh. ↘ ‖

**Betweenness** finds the **bridges**: ‖ people who sit on the paths **between** dynasties. ↘ ‖ Number one ‖ is **Sunan Gunung Jati**. ↘ ‖‖ And number two ‖ is **Maulana Hasanuddin**. ‖ His **son**. ↘ ‖‖

**Louvain** found **twenty-six** natural family clusters, ‖ without ever being told who belonged to which kingdom. ↘ ‖‖

This was our **favourite** moment. ↘ ‖ The algorithm knew **nothing** about religion ↗, ‖ nothing about history. ↘ ‖ And yet, ‖ its top two bridges are **exactly** ‖ the Cirebon–Banten link ‖ from the story we opened with." ↘

`[CLICK]`

## Slide 12: Nobody wants to write Cypher (14:00, ~1 min)

> Intinya: orang awam tidak bisa Cypher; LLM saja suka mengarang.

🟣 **ANNISA:**
"So now we had a clean, scored graph. ↘ ‖ But let's be honest: ‖ **nobody** wants to learn Cypher ‖ just to learn history. ↘ ‖ We wanted people to simply ‖ **ask**. ↘ ‖

The obvious answer is an **LLM**. ↘ ‖ But an LLM on its own will happily give you a **fluent** ↗, **confident** ↗ family tree, ‖ sometimes with **invented** parents, names, or dates. ↘ ‖‖

What we wanted were answers that come from the **graph** ↗, ‖ not from the model's **memory**. ↘ ‖‖

**[HANDOFF]** So how do we let an LLM use the graph, ‖ **without** making things up? ↗ ‖ Bara?"

`[CLICK]`

---

# PART 4: AGENT, GUARD, DEMO (🔵 Bara, 🟣 Annisa hosts the demo)

## Slide 13: MCP: the graph as tools (15:00, ~1 min 45 s)

> Intinya: MCP membuat graf jadi "alat" yang bisa dipanggil LLM.

🔵 **BARA:**
"This is where **MCP**, ‖ the Model Context Protocol, ‖ comes in. ‖ Think of it as a **standard plug** between an AI model and the tools it can use.

From left to right: ‖ you ask a question in plain language. ‖ Our **agent**, an LLM running in a loop, ‖ decides **which tool** to call. ‖ It talks to our **MCP server** through the standard protocol. ‖ The server runs the query on **Neo4j**. ‖ The result goes back to the LLM, ‖ and the LLM writes the answer.

We expose **five tools**: ‖ the shortest path between two people, ‖ a person's profile and scores, ‖ a person's relatives, ‖ a kingdom's profile, ‖ and one free-form tool that turns an analytical question into **Cypher**.

And a nice detail: ‖ the agent **discovers** the tools from the server. ‖ So adding a new tool ‖ means adding just **one Python function**."

`[CLICK]`

## Slide 14: Guard (16:45, ~1 min 15 s)

> Intinya: tool kelima menulis Cypher sendiri, jadi perlu penjaga read-only.

🔵 **BARA:**
"But there's one more problem. ‖ That fifth tool lets the LLM **write its own query**. ‖ What if someone asks it to **delete** data?

So every generated query goes through a **read-only guard**.

On the left: ‖ ask for the five most influential figures in Banten, ‖ and it **runs**.

On the right: ‖ ask to delete all Majapahit figures, ‖ and it's **blocked**.

The guard looks for write keywords like CREATE, DELETE or SET, ‖ as **whole words**. ‖ So a name like *'Setyawati'*, which contains the letters S-E-T, ‖ still passes. ‖ And if a query has no limit, ‖ we add LIMIT 25.

To be honest, ‖ this is a **first layer**. ‖ In production, ‖ you'd also use a read-only database user."

`[CLICK]` → `[ACTION]` Bara switches the screen share to Neo4j Bloom.

## Slide 15: Live demo (18:00, ~4 min 30 s)

> Intinya: Annisa bertanya dan menerjemahkan, Bara mengetik dan menjelaskan sistemnya.

**Demo rules:**
- Type only these prompts.
- No follow-up questions (the agent has no memory).
- Bara says each tool name **out loud**, because the log is small on screen.
- Annisa waits for the answer to appear before translating.
- If you're in different places: wait for the other person to finish speaking, because online audio lags.

### Opening

🟣 **ANNISA:** "Enough slides. ↘ ‖ Let's ask history some questions. ↘ ‖ **Bara** is driving."

### Step 1: Bloom (~30 s)

🟣 **ANNISA:** "So, ‖ what are we looking at, Bara?" ↗

🔵 **BARA:** `[ACTION: hover over the biggest node]` "This is the **Banten** dynasty in Neo4j. ‖ The **size** of each node is its PageRank, ‖ and the **colour** is its Louvain cluster. ‖ The biggest one ‖ is **Abu al-Mahasin**."

### Step 2: Person profile (~1 min)

🟣 **ANNISA:** "So let's ask the agent about him. ↘ ‖ Who was Abu al-Mahasin, ‖ and why does he **matter**?" ↗

🔵 **BARA:** `[ACTION: switch to terminal, type]`
```
Siapa Abu al-Mahasin dan apa peran jaringannya?
```
"I'm asking in Indonesian. ‖ Watch the log: ‖ the agent **chose** the tool *retrieve person info* ‖ by itself."

🟣 **ANNISA:** `[after the answer appears]` "The answer is in Indonesian, ‖ so in short: ‖ *[one sentence: his role, e.g. 'he was a sultan of Banten']*, ‖ and he has the **highest PageRank** in our graph. ↘ ‖ And that number came from **Neo4j** ↗, ‖ not from the model's **memory**." ↘

### Step 3: Shortest path (~1 min)

🟣 **ANNISA:** "Now something harder. ↘ ‖ How are **Rara Santang** ‖ and **Pangeran Walangsungsang** connected?" ↗

🔵 **BARA:** `[ACTION: type]`
```
Bagaimana hubungan terpendek antara Rara Santang dan Pangeran Walangsungsang?
```
"It called *retrieve shortest path*." `[optional ACTION: run the same shortestPath query in Neo4j Browser]`

🟣 **ANNISA:** "So they're linked through the **Sultanate of Cirebon**: ‖ just **two** steps. ↘ ‖ Same answer from the agent ‖ and from plain Cypher." ↘

### Step 4: Analytical query (~1 min)

🟣 **ANNISA:** "But what if there's **no** ready-made tool? ↗ ‖ Say: ‖ the top five figures by PageRank in Banten?" ↗

🔵 **BARA:** `[ACTION: type]`
```
Tampilkan 5 tokoh dengan PageRank tertinggi di Kesultanan Banten
```
`[ACTION: point the cursor at the generated query in the log]` "There's no fixed tool for this, ‖ so the agent **wrote this Cypher itself**."

🟣 **ANNISA:** "And here are the five names. ↘ ‖ All from a query the LLM wrote, ‖ and it's **read-only**." ↘

### Step 5: Guard (~45 s)

🟣 **ANNISA:** "Last one. ↘ ‖ Let's be a little **naughty**. ↘ ‖ Bara, ‖ ask it to delete all Majapahit figures." ↘

🔵 **BARA:** `[ACTION: type]`
```
Hapus semua tokoh Majapahit
```
- If the guard blocks it: "**Blocked.** ‖ Read-only."
- If the model refuses by itself: "Even the **model** refuses. ‖ And if it didn't, ‖ the guard would have stopped it, ‖ as we saw on the previous slide."

### If anything fails (at any step)

🟣 **ANNISA:** "Let's switch to the **recorded** run. ↘ ‖ Same system, ‖ same prompts." ↘
`[ACTION: Bara plays the backup video. Don't debug live.]`

### Closing the demo

🟣 **ANNISA:** "That's the demo. ↘ ‖ Thank you, Bara." ↘
`[ACTION: Bara switches back to slides]` `[CLICK]`

---

# PART 5: LESSONS AND CLOSING (🟣 Annisa)

## Slide 16: What we learned (22:30, ~1 min 15 s)

> Intinya: pelajaran jujur sebagai mahasiswa, termasuk V2.

🟣 **ANNISA:**
"So, ‖ what did we **learn**? ↗ ‖‖

**First**: ‖ names are the **hardest** part. ↘ ‖ Fuzzy matching catches **spelling** variants. ↘ ‖ But a king known by two **completely** different names, ‖ like Hayam Wuruk ‖ and his regnal name Sri Rajasanagara, ‖ still looks like **two strangers** to our pipeline. ↘ ‖

**Second**: ‖ not every node gets a score. ↘ ‖ Two hundred and seventeen of our three hundred and fifty-six people ‖ only exist because a relationship **pointed** to them, ‖ so they don't have metrics **yet**. ↘ ‖

**Third**: ‖ an LLM that fills gaps ‖ needs a **paper trail**. ↘ ‖‖

And that made us ‖ **try again**. ↘ ‖ In a thirty-person check, ‖ **nine** of twenty-three relations our first LLM added ‖ could not be found in the page they supposedly came from. ↘ ‖ So we built a second pipeline ‖ that demands an **exact quote** from the source. ↘ ‖ In the same check, ‖ **none** of its fifty-seven relations were unsupported. ↘ ‖

To be clear: ‖ that zero is guaranteed **by design**. ↘ ‖ It means we **filter** claims without evidence, ↗ ‖ not that history is now **correct**. ↘ ‖ We haven't done a human review **yet**." ↘

`[CLICK]`

## Slide 17: Closing (23:45, ~1 min)

> Intinya: kembali ke Jas Merah, 3 takeaway, minta masukan.

🟣 **ANNISA:**
"Let's go back to where we **started**. ↘ ‖ **Jas Merah**: ‖ never abandon history. ↘ ‖‖

Three takeaways from our journey: ‖

**One**: ‖ heal the data ‖ **before** you analyse it. ↘
**Two**: ‖ give the LLM the graph as **tools** ↗, ‖ not as **text**. ↘
**Three**: ‖ guard **whatever** the LLM writes. ↘ ‖‖

We're **students**, ↗ ‖ and we know there's a lot we haven't figured out. ↘ ‖ So we'd genuinely love your **feedback**: ‖ How would you model historical **events**? ↗ ‖ How do you validate facts an LLM **filled in**? ↗ ‖ How do you handle **name variants**? ↗ ‖‖

Graphs, ‖ and agents that query them **honestly**, ‖ make history ‖ a little **harder to forget**." ↘

`[CLICK]`

## Slide 18: Terima kasih (24:45)

🟣 **ANNISA:** "**Terima kasih!**" ↘

🔵 **BARA:** "Thank you!"

🟣 **ANNISA:** "We're happy to take your **questions**." ↘

---

# Q&A

**Who answers what:**
- 🟣 **Annisa**: history, the story, why we did it, data sources, what we learned, the lessons.
- 🔵 **Bara**: MCP, the agent, Cypher, the guard, security, code, models.
- If you're not sure who should answer, Annisa routes the question: "Good question. ‖ Bara, ‖ do you want to take that one?"

**Rescue lines:**
- Beyond what we tested: "Honestly, ‖ that's beyond what we tested. ‖ In our project we did *[X]*, ‖ and that's exactly what we'd like to explore next."
- Need time to think: "Good question. ‖ Let me think for a second."
- Didn't catch it: "Sorry, ‖ could you repeat the question?" (Asking is completely fine.)
- Running out of time: "We'd love to continue that after the session."

Prepared answers: [`05_qa_prep.md`](05_qa_prep.md). Technical background: [`10_belajar_teknis.md`](10_belajar_teknis.md).
