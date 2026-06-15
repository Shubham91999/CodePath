# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**ASU Off-Campus Housing Experiences (Tempe)**

Student off-campus housing knowledge near Arizona State University is scattered across Reddit threads, apartment review sites, personal blogs, and unofficial student guides. No single source aggregates pricing, safety, management quality, commute times, and peer-to-peer experiences in one place — making it genuinely hard to answer questions like "Is this apartment worth it?" or "Which complex has the best management?" through official channels. ASU's official housing portal only lists properties without tenant reviews, and word-of-mouth knowledge disappears every graduation cycle.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | RamblerTempe — Apollo Tempe | Detailed student review: amenities, pricing, floor plans | https://ramblertempe.com/resources/apartment-review-apollo-tempe/ |
| 2 | RamblerTempe — University House Tempe | Student review: studio to 5×5, furnished, proximity to campus | https://ramblertempe.com/resources/apartment-review-university-house-tempe/ |
| 3 | RamblerTempe — Union Tempe | Student review: 5-min walk to campus, pricing | https://ramblertempe.com/resources/apartment-review-union-tempe/ |
| 4 | RamblerTempe — ōLiv Tempe | Student review: modern units, $1,150–$1,980/person/month | https://ramblertempe.com/resources/arizona-state-apartment-review-oliv-tempe/ |
| 5 | RamblerTempe — Canvas Tempe | Student review: rooftop pool, esports lounge, sauna, pricing | https://ramblertempe.com/resources/tempe-student-apartment-review-canvas-tempe/ |
| 6 | RamblerTempe — The District on Apache | Student review: walkability, central Tempe location | https://ramblertempe.com/resources/asu-apartment-review-district-on-apache/ |
| 7 | RamblerTempe — Marshall Tempe | Student review: pricing, location, amenities | https://ramblertempe.com/resources/tempe-student-apartment-review-marshall-tempe/ |
| 8 | RamblerTempe — Nine20 Tempe | Student review: 5-min to campus, $1,025–$1,999/person | https://ramblertempe.com/resources/arizona-state-apartment-review-nine20-tempe/ |
| 9 | RamblerTempe — 7 Best Apartments Near ASU | Ranked comparison guide covering top student housing options | https://ramblertempe.com/resources/best-student-apartments-asu-tempe/ |
| 10 | ApartmentRatings — Paseo on University | 214 raw tenant reviews covering management, noise, value | https://www.apartmentratings.com/az/tempe/paseo-on-university_4809688118852818420/ |
| 11 | ApartmentRatings — Gateway at Tempe | 63 tenant reviews on maintenance, safety, pricing | https://www.apartmentratings.com/az/tempe/gateway-at-tempe_9199332346275143488/ |
| 12 | ApartmentRatings — SoL | 53 tenant reviews, near university, furnished options | https://www.apartmentratings.com/az/tempe/sol_480894194985281/ |
| 13 | ApartmentRatings — Vertex Student Apartments | 49 reviews, 3.7/5, proximity to ASU campus | https://www.apartmentratings.com/az/tempe/vertex-student-apartments_9199332346275160627/ |
| 14 | ApartmentRatings — The District on Apache | 15 tenant reviews | https://www.apartmentratings.com/az/tempe/the-district-on-apache_9199332346275170990/ |
| 15 | ASU Off-Campus Housing Portal | Official ASU listings with pricing and amenity info | https://offcampushousing.asu.edu/ |
| 16 | ASU Thunderbird Off-Campus Housing Guide | Official PDF guide for students; tips, checklists, area breakdown | https://thunderbird.asu.edu/sites/default/files/2022-04/ThunderbirdOffCampusHousingGuide20222023.pdf |
| 17 | Amber Student — Tempe Housing | International student-focused housing reviews and listings | https://amberstudent.com/places/search/tempe-1811051325535 |
| 18 | ASU State Press — College Town Housing Prices | Student newspaper article on Tempe housing affordability (April 2026) | https://www.statepress.com/article/2026/04/college-town-housing-prices |
| 19 | Reddit — r/ASU off campus housing threads | Student discussion threads: recommendations, warnings, personal experiences | reddit.com/r/ASU (search: "off campus housing") |
| 20 | Reddit — r/Tempe student housing threads | Neighborhood-level housing experiences from Tempe residents | reddit.com/r/Tempe (search: "student housing ASU") |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 tokens (~300 words) — safe with `nomic-embed-text` (8,192 token limit). Note: would require lowering to ~200 tokens if using `all-MiniLM-L6-v2` (256 token limit).

**Overlap:** 50 tokens (~40 words)

**Reasoning:**

This corpus is structurally heterogeneous — RamblerTempe articles are long-form (500–1,500 words) organized by sections, while ApartmentRatings entries are short individual tenant blurbs (50–200 words each), and Reddit comments vary widely. A single fixed character split would either slice long reviews mid-thought or awkwardly merge multiple unrelated short reviews into one chunk.

400 tokens is large enough to capture a complete thought (one section of a long review, or 1–2 short tenant reviews) while staying small enough that retrieved chunks stay focused on a single apartment and a single topic (pricing, management, amenities, location). In housing reviews, the key signal is often one sentence — "Management never responds to maintenance requests" — and larger chunks bury that signal in noise, hurting retrieval precision.

50-token overlap prevents cutting sentences mid-thought in longer reviews without being wasteful. For short, naturally-bounded reviews (tenant blurbs, Reddit comments), the overlap has minimal effect.

**Split strategy:** Use `RecursiveCharacterTextSplitter` with separators `["\n\n", "\n", ". ", " "]` — this respects paragraph breaks first, then sentence breaks, then words, before falling back to a hard character cut. Per-source chunking logic:

| Source | Chunk boundary |
|--------|----------------|
| RamblerTempe articles | Split at section headers (Location, Amenities, Pricing, Pros/Cons) |
| ApartmentRatings | Each individual tenant review = one chunk |
| Reddit threads | Each top-level comment or reply = one chunk |
| ASU official portal / PDF | Each property entry = one chunk |

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `nomic-embed-text` via Ollama (local)

- Max context: 8,192 tokens — handles 400-token chunks without any truncation
- Dimensions: 768
- Runs fully locally via `ollama serve` — no API key, no cost, no rate limits
- Setup: `brew install ollama` → `ollama pull nomic-embed-text` → `ollama serve`
- Python usage: `pip install ollama` then `ollama.embed(model="nomic-embed-text", input=chunks)`

**Top-k:** 5

Retrieving 5 chunks gives enough coverage for comparison queries ("Apollo vs Canvas") without flooding the LLM context with noise. At ~400 tokens per chunk, 5 chunks = ~2,000 tokens of context, well within `llama-3.3-70b-versatile`'s context window.

**Production tradeoff reflection:**

| Tradeoff | Consideration |
|----------|--------------|
| **Context length** | `nomic-embed-text` supports 8,192 tokens vs 256 for `all-MiniLM-L6-v2` — eliminates silent truncation on longer reviews. In production this means fewer chunking artifacts and less information loss at boundaries. |
| **Domain accuracy** | Both are general-purpose models. A fine-tuned real estate or review-domain model would embed terms like "noisy neighbors", "thin walls", or "management responsiveness" closer together in vector space. For a production housing guide this would meaningfully improve retrieval precision. |
| **Multilingual support** | `nomic-embed-text` is English-only. ASU has a large international student population — a multilingual model like `paraphrase-multilingual-MiniLM-L12-v2` or OpenAI `text-embedding-3-large` would let non-English speakers query in their language and still retrieve English documents. |
| **Local vs API** | Local models (nomic-embed-text via Ollama) have zero marginal cost and no data privacy concerns. API models (OpenAI, Cohere) offer better accuracy but add per-token cost, network latency, and an external dependency that can fail during demos. |
| **Latency** | Ollama runs on CPU locally — embedding 500+ chunks at ingestion is slower than a GPU-backed API but acceptable as a one-time cost. At query time only the user's query is embedded (one call), so latency impact is negligible. |

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do student reviews say about whether Nine20 Tempe is worth the price? | Nine20 Tempe is priced at $1,025–$1,999/person/month. Students consider it good value given its 5-minute walk to campus near Hayden Library and Mill Avenue. Proximity to campus is the primary justification for the price point. (Source: RamblerTempe — Nine20 Tempe review) |
| 2 | What unique amenities does Canvas Tempe offer compared to a typical student apartment? | Canvas Tempe offers a rooftop pool, fitness center, esports lounge, podcast studio, sauna, and private study pods — well beyond a standard student apartment. Priced $999–$2,199/month at 1028 E. Orange St. (Source: RamblerTempe — Canvas Tempe review) |
| 3 | What do tenants at Gateway at Tempe say about maintenance response and management quality? | Should surface specific tenant experiences about maintenance response times and management quality from the 63 ApartmentRatings reviews. Answer must cite specific tenant experiences, not generic statements. (Source: ApartmentRatings — Gateway at Tempe) |
| 4 | How does ōLiv Tempe compare to Apollo Tempe in terms of monthly pricing and available amenities? | ōLiv Tempe: $1,150–$1,980/person/month, modern units. Apollo Tempe: two fitness centers, climbing wall, yoga studio, rooftop + ground pools, coffee bar. Answer should identify which is more amenity-rich vs. more affordable. (Source: RamblerTempe — ōLiv and Apollo reviews) |
| 5 | Which student apartments near ASU Tempe are within a 5-minute walk to campus? | Nine20 Tempe (~5 min, near Hayden Library) and Union Tempe (~5 min, 712 S Forest Ave near College of Design) are explicitly described as 5-minute walks. Canvas Tempe and University House Tempe are also short walks but without a specific minute count stated. (Source: RamblerTempe — Nine20, Union, Canvas, University House reviews) |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Missing apartment identity in short review chunks.** ApartmentRatings blurbs are scraped from pages where the apartment name exists only as a page header — not inside the review text itself. If only raw review text is stored as a chunk, the embedding carries no apartment identity. At retrieval time the LLM receives a chunk like *"Maintenance took 3 weeks. Management ignores emails. Would not renew."* with no way to know which property it describes, causing incorrect or missing attribution. This directly threatens Q3 (Gateway at Tempe management). Fix: prepend apartment name, source, and rating as a metadata header to every chunk before embedding.

2. **Stale or conflicting pricing information across sources.** Sources span different time periods — a RamblerTempe article updated for 2026 may cite Canvas Tempe at $999/month while an older ApartmentRatings review from 2023 says $850/month and a Reddit thread from 2024 says $1,100/month. All three chunks can be retrieved for the same pricing query. The LLM has no way to determine which figure is current and may average them, cite the oldest, or hedge with "prices vary" — making factual answers unreliable. This directly threatens Q1 (Nine20 pricing) and Q4 (ōLiv vs Apollo comparison). Fix: add a year/date field to chunk metadata during ingestion and instruct the LLM to prefer the most recent source when figures conflict.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

### Ingestion Pipeline (offline — run once)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RAW SOURCES (20 docs)                        │
│   RamblerTempe · ApartmentRatings · ASU Portal · Reddit · PDF       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     DOCUMENT INGESTION                              │
│   requests + BeautifulSoup4  →  strip HTML, nav, ads               │
│   pdfplumber                 →  extract text from Thunderbird PDF   │
│   Output: clean plain text per document                             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CHUNKING                                    │
│   RecursiveCharacterTextSplitter (LangChain)                        │
│   chunk_size = 400 tokens · overlap = 50 tokens                     │
│   Separators: ["\n\n", "\n", ". ", " "]                             │
│   Prepend metadata header to each chunk:                            │
│     "Apartment: <name> | Source: <site> | Date: <year>"            │
│   Output: list of chunks with metadata                              │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         EMBEDDING                                   │
│   nomic-embed-text via Ollama (local)                               │
│   768-dimensional vectors · 8,192 token limit                       │
│   Output: one vector per chunk                                      │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       VECTOR STORE                                  │
│   ChromaDB (local, persisted to disk)                               │
│   Stores: chunk text + embedding vector + metadata                  │
│   Collection: "asu_housing"                                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Query Pipeline (online — runs per user query)

```
┌─────────────┐
│  User Query │  e.g. "Which apartments have good management near ASU?"
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      QUERY EMBEDDING                                │
│   nomic-embed-text via Ollama                                       │
│   Output: 768-dimensional query vector                              │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SEMANTIC SEARCH                                 │
│   ChromaDB cosine similarity search                                 │
│   top-k = 5 most similar chunks retrieved                           │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESPONSE GENERATION                              │
│   llama-3.3-70b-versatile via Groq API                              │
│   Input: user query + top-5 retrieved chunks                        │
│   System prompt: answer using ONLY retrieved context                │
│   Output: grounded answer with source attribution                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FINAL ANSWER                                   │
│   Natural language response + cited sources                         │
│   e.g. "(Source: RamblerTempe — Canvas Tempe review)"              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

- **Tool:** Claude Code
- **Input:** The Documents table (20 source URLs), the Document Ingestion stage from the Architecture diagram, and the Chunking Strategy section of this file
- **Expected output:**
  - `ingest.py` — scrapes each URL using `requests` + `BeautifulSoup4`, strips HTML/nav/ads, saves clean plain text to `data/raw/<apartment_name>.txt`; uses `pdfplumber` for the Thunderbird PDF
  - `chunk.py` — loads raw text files, applies `RecursiveCharacterTextSplitter` (chunk_size=400, overlap=50, separators=["\n\n", "\n", ". ", " "]), prepends metadata header (`"Apartment: <name> | Source: <site> | Date: <year>"`), saves chunks to `data/chunks/chunks.json`
- **Verification:** Print total chunk count and min/max/avg chunk size. Manually inspect 5 random chunks — each must contain an apartment name in the header and readable, self-contained text. Confirm no chunk exceeds 400 tokens.

---

**Milestone 4 — Embedding and retrieval:**

- **Tool:** Claude Code
- **Input:** The Retrieval Approach section of this file, the Embedding and Vector Store stages from the Architecture diagram, and `data/chunks/chunks.json` from Milestone 3
- **Expected output:**
  - `embed.py` — loads chunks, calls `ollama.embed(model="nomic-embed-text", input=chunks)`, stores vectors + text + metadata in ChromaDB local collection named `"asu_housing"`, persists to disk at `data/chroma/`
  - `retrieve.py` — accepts a query string, embeds it via `nomic-embed-text`, queries ChromaDB for top-5 by cosine similarity, returns list of `{text, source, apartment, score}`
- **Verification:** Run all 5 evaluation questions through `retrieve.py` and manually check that returned chunks are topically relevant and contain the correct apartment name. Confirm each result includes source metadata.

---

**Milestone 5 — Generation and interface:**

- **Tool:** Claude Code
- **Input:** The Generation stage from the Architecture diagram, the Evaluation Plan (5 test questions), and the grounded response requirement (source attribution on every answer, no use of general knowledge)
- **Expected output:**
  - `generate.py` — takes a query + top-5 retrieved chunks, calls `llama-3.3-70b-versatile` via Groq API (`from groq import Groq`, `GROQ_API_KEY` loaded from `.env`). System prompt **enforces** grounding — does not merely suggest it. Source attribution appended **programmatically** after generation, not left to the LLM.
  - `app.py` — Gradio web UI (`gradio>=6.9.0`) that chains `retrieve.py` → `generate.py`, displays answer + source list at `http://localhost:7860`. Run with `python app.py`.
- **System prompt (enforced grounding):**
  ```
  Answer the question using only the information in the provided documents.
  If the documents don't contain enough information to answer, say
  "I don't have enough information on that."
  Do not use any outside knowledge.
  ```
- **Output format:** LLM answer (grounded text) + programmatically appended source list (apartment name + source site per retrieved chunk)
- **Grounding test:** For each response ask — could this answer have come from anywhere other than the retrieved chunks? If yes, it is a grounding failure even if the answer happens to be correct.
- **Verification:** Run all 5 evaluation questions end-to-end. Confirm every response includes source attribution. Ask one out-of-scope question (answer not in any document) and verify the system responds with "I don't have enough information on that" rather than hallucinating.
