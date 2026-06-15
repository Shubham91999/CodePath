# The Unofficial Guide — Project 1
---

## Domain

**ASU Off-Campus Housing Experiences (Tempe)**

This system covers student experiences with off-campus apartments near Arizona State University's Tempe campus — including pricing, amenities, management quality, maintenance responsiveness, walkability to campus, and overall value. This knowledge is valuable because the decision of where to live significantly impacts a student's academic experience, budget, and wellbeing, yet it is genuinely hard to find through official channels. ASU's official off-campus housing portal lists properties and amenities but contains zero tenant reviews or honest assessments of management quality. The real knowledge — which complexes have unresponsive maintenance, which are actually a 5-minute walk to class, which are overpriced for what they offer — lives scattered across Reddit threads, apartment review sites, and word-of-mouth that disappears each graduation cycle. A RAG system that aggregates this knowledge into a single queryable interface provides real value to incoming and current students.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | RamblerTempe — Apollo Tempe Review | Student apartment review | https://ramblertempe.com/resources/apartment-review-apollo-tempe/ |
| 2 | RamblerTempe — University House Tempe Review | Student apartment review | https://ramblertempe.com/resources/apartment-review-university-house-tempe/ |
| 3 | RamblerTempe — Union Tempe Review | Student apartment review | https://ramblertempe.com/resources/apartment-review-union-tempe/ |
| 4 | RamblerTempe — oLiv Tempe Review | Student apartment review | https://ramblertempe.com/resources/arizona-state-apartment-review-oliv-tempe/ |
| 5 | RamblerTempe — Canvas Tempe Review | Student apartment review | https://ramblertempe.com/resources/tempe-student-apartment-review-canvas-tempe/ |
| 6 | RamblerTempe — The District on Apache Review | Student apartment review | https://ramblertempe.com/resources/asu-apartment-review-district-on-apache/ |
| 7 | RamblerTempe — Marshall Tempe Review | Student apartment review | https://ramblertempe.com/resources/tempe-student-apartment-review-marshall-tempe/ |
| 8 | RamblerTempe — Nine20 Tempe Review | Student apartment review | https://ramblertempe.com/resources/arizona-state-apartment-review-nine20-tempe/ |
| 9 | RamblerTempe — 7 Best Student Apartments Near ASU | Ranked comparison guide | https://ramblertempe.com/resources/best-student-apartments-asu-tempe/ |
| 10 | ASU Off-Campus Housing Portal | Official ASU listings | https://offcampushousing.asu.edu/ |
| 11 | ASU Thunderbird Off-Campus Housing Guide | Official PDF guide | https://thunderbird.asu.edu/sites/default/files/2022-04/ThunderbirdOffCampusHousingGuide20222023.pdf |
| 12 | Amber Student — Tempe Housing | International student housing listings | https://amberstudent.com/places/search/tempe-1811051325535 |
| 13 | ASU State Press — College Town Housing Prices | Student newspaper article | https://www.statepress.com/article/2026/04/college-town-housing-prices |

**Note:** 7 additional sources (all ApartmentRatings.com pages + one RamblerTempe page) failed during ingestion because ApartmentRatings uses Cloudflare anti-scraping protection. See Failure Case Analysis for how this affected evaluation.

---

## Chunking Strategy

**Chunk size:** 1,600 characters (~400 tokens at ~4 chars/token)

**Overlap:** 200 characters (~50 tokens)

**Why these choices fit your documents:**

This corpus is structurally heterogeneous — RamblerTempe articles are long-form structured reviews (500–1,500 words) organized by sections (Location, Amenities, Pricing, Pros/Cons), while other sources like the Thunderbird PDF and Amber Student listings contain denser factual text. A fixed character split at 1,600 characters captures roughly one full section of a RamblerTempe review without splitting mid-thought.

The 200-character overlap prevents key facts from being stranded at chunk boundaries. For example, a pricing fact might appear at the end of one section and a "utilities included" qualifier at the start of the next — without overlap, neither chunk alone answers a pricing query correctly. A metadata header (`Apartment: <name> | Source: <site> | Date: <year>`) is prepended to every chunk before embedding, ensuring each chunk carries apartment identity even when the review text itself doesn't repeat the name.

`RecursiveCharacterTextSplitter` from LangChain was used with separators `["\n\n", "\n", ". ", " ", ""]` — this respects paragraph and sentence boundaries before falling back to character splits, which is important for opinion text where coherence within a paragraph is the unit of meaning.

**Final chunk count:** 65 chunks across 13 documents (min: 104 chars, max: 1,682 chars, avg: 1,445 chars)

---

## Embedding Model

**Model used:** `nomic-embed-text` via Ollama (local)

`nomic-embed-text` was chosen over the originally planned `all-MiniLM-L6-v2` because it supports an 8,192-token context window versus 256 tokens for MiniLM. At 1,600-character (~400-token) chunk sizes, MiniLM would silently truncate every chunk — the last ~150 tokens of each chunk would be invisible to the embedding model, directly harming retrieval quality. `nomic-embed-text` handles our chunk sizes without any truncation. It runs fully locally via Ollama, requires no API key, and produces 768-dimensional vectors.

**Production tradeoff reflection:**

If deploying this for real users with no cost constraint, several tradeoffs would be worth evaluating. First, **domain accuracy**: `nomic-embed-text` is a general-purpose model not fine-tuned on real estate or housing review text. Terms like "management responsiveness," "pet-friendly," or "utilities included" are common in housing reviews but may not be as precisely clustered in its embedding space as they would be in a domain-fine-tuned model. Second, **multilingual support**: ASU has a large international student population. `nomic-embed-text` is primarily English — a multilingual model like `paraphrase-multilingual-MiniLM-L12-v2` or OpenAI's `text-embedding-3-large` would let non-English-speaking students query in their native language and still retrieve English documents. Third, **local vs. API**: running locally avoids per-token cost and data privacy concerns (student reviews could be considered sensitive), but API-hosted models like OpenAI's `text-embedding-3-large` offer higher accuracy and no server dependency during demos. Fourth, **latency at ingestion**: embedding 65 chunks on CPU took a few seconds, but a corpus of thousands of reviews would be slow locally; a GPU-backed API would be significantly faster for large-scale ingestion.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt explicitly forbids the model from using outside knowledge and provides a fallback response for out-of-scope questions:

```
You are a helpful assistant for ASU students looking for off-campus housing in Tempe, Arizona.

Answer the question using ONLY the information in the provided documents below.
If the documents don't contain enough information to answer the question, say exactly:
"I don't have enough information on that."

Do not use any outside knowledge. Do not guess or infer beyond what the documents say.
Be specific and refer to apartment names when they appear in the documents.
```

The temperature is set to 0.2 to minimize creative generation and keep answers factual and grounded. The LLM receives retrieved chunks formatted as numbered documents (`[Document 1]`, `[Document 2]`, etc.) followed by the user's question — this structure makes it unambiguous what counts as "the provided documents."

**How source attribution is surfaced in the response:**

Source attribution is appended **programmatically** from retrieved chunk metadata — it is not generated by the LLM. After the LLM returns its answer, `generate.py` builds the source list by iterating over the retrieved chunks and extracting `apartment`, `source`, and `url` fields that were stored in ChromaDB at ingestion time. This guarantees attribution is always present, always accurate, and never hallucinated — even if the LLM's answer doesn't mention source names. A deduplication step ensures each unique (apartment, source) pair appears only once in the source list.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do student reviews say about whether Nine20 Tempe is worth the price? | $1,025–$1,999/person/month; good value for 5-min walk to campus near Hayden Library | "I don't have enough information on that." — despite retrieving Nine20 chunks at scores 0.47–0.41 | Relevant (correct chunks retrieved) | Inaccurate |
| 2 | What unique amenities does Canvas Tempe offer compared to a typical student apartment? | Rooftop pool, esports lounge, podcast studio, sauna, private study pods, $999–$2,199/month | Correctly named rooftop pool, esports lounge, podcast studio, fitness center with yoga studio, computer lab. Missed sauna and private study pods. No pricing mentioned. | Relevant (top 3 chunks all Canvas Tempe) | Partially accurate |
| 3 | What do tenants say about maintenance and management quality at Gateway at Tempe? | Specific tenant experiences from ApartmentRatings reviews | "I don't have enough information on that." — no Gateway data in corpus. Retrieved unrelated apartments at very low scores (0.17–0.22). | Off-target | Inaccurate |
| 4 | How does oLiv Tempe compare to Apollo Tempe in terms of monthly pricing and available amenities? | oLiv: $1,150–$1,980/person/month; Apollo: two fitness centers, climbing wall, yoga studio, pools, coffee bar | Accurate detailed comparison: oLiv $1,150–$1,980 (Jan 2026), Apollo $1,199–$1,929 (Feb 2026). Listed specific amenities for both correctly, including rock wall, dog park, and dual pools for Apollo. | Relevant (oLiv + Apollo chunks) | Accurate |
| 5 | Which student apartments near ASU Tempe are within a 5-minute walk to campus? | Nine20 (~5-min), Union Tempe (~5-min), Canvas and University House (short walk) | "I don't have enough information on that." — retrieved generic listing pages (Amber Student, ASU portal) with high scores (0.59–0.62) instead of specific apartment reviews | Partially relevant (wrong level of specificity) | Inaccurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Q3 — "What do tenants say about maintenance and management quality at Gateway at Tempe?"

**What the system returned:**
> "I don't have enough information on that."

Retrieved chunks: Canvas Tempe (0.2157), Union Tempe (0.1889), Tempe Housing Market — State Press (0.1869), Various ASU Apartments — RamblerTempe (0.1762), Marshall Tempe (0.1758). None of the retrieved chunks mention Gateway at Tempe, and all similarity scores are very low (under 0.22), indicating the query has no close match in the vector store.

**Root cause (tied to a specific pipeline stage):**

This failure originates at the **Document Ingestion** stage. ApartmentRatings.com uses Cloudflare anti-bot protection, which blocked all six automated scraping attempts during `ingest.py`. As a result, no Gateway at Tempe documents were ever saved to `data/raw/`, no chunks were created for this property, and no vectors representing Gateway tenant reviews exist in ChromaDB. The retriever has nothing to find.

The LLM's "I don't have enough information" response is actually correct behavior — it refused to hallucinate an answer from unrelated chunks, which is exactly what the grounding system prompt is designed to enforce. The failure is not in generation or retrieval logic; it is in corpus coverage. A RAG system can only answer questions about data it has ingested.

**What you would change to fix it:**

The most direct fix is manual ingestion: open each ApartmentRatings URL in a browser, copy the review text, and save it to `data/raw/gateway_at_tempe.txt` with a matching `.json` metadata file, then re-run `chunk.py` and `embed.py`. A more robust long-term fix would be to use a headless browser tool (Playwright or Selenium) with randomized delays and session cookies to bypass Cloudflare, or to use a third-party scraping API (e.g., ScraperAPI, Bright Data) that handles bot detection automatically.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The `planning.md` chunking strategy section was used directly as the prompt to implement `chunk.py`. Because the spec specified not just the chunk size and overlap but also the exact separator priority (`["\n\n", "\n", ". ", " "]`) and the per-source chunking logic (ApartmentRatings = one review per chunk, RamblerTempe = split at section headers), the implementation could follow it precisely without having to make architectural decisions mid-code. The metadata header format — `"Apartment: <name> | Source: <site> | Date: <year>"` — was specified in the planning doc and carried through to every chunk, which directly enabled the programmatic source attribution in `generate.py`. Without that pre-planned format, attribution would have had to be left to the LLM.

**One way your implementation diverged from the spec, and why:**

The spec specified chunk size as **400 tokens**, but the implementation uses **1,600 characters**. This divergence happened because `RecursiveCharacterTextSplitter` measures chunk size in characters by default, not tokens. Using a token-aware splitter (such as `from_huggingface_tokenizer`) would have required loading a tokenizer model separately, adding complexity and startup time. The approximation of 4 characters per token is standard for English text and produced chunks averaging 1,445 characters (~361 tokens) in practice — close to the intended 400-token target and well within `nomic-embed-text`'s 8,192-token limit. The practical outcome was the same; only the unit of measurement differed.

---

## AI Usage

**Instance 1 — Chunking strategy implementation**

- *What I gave the AI:* The complete Chunking Strategy section from `planning.md`, including chunk size (400 tokens), overlap (50 tokens), the separator list, the metadata header format, and the per-source chunking logic table. Also provided the Architecture diagram stage showing the expected input (`data/raw/*.txt`) and output (`data/chunks.json`).
- *What it produced:* A complete `chunk.py` using `RecursiveCharacterTextSplitter` with the specified parameters, a `format_chunk()` function prepending the metadata header, and a `load_metadata()` function reading the `.json` sidecar files written by `ingest.py`. It also added a stats printout (min/max/avg chunk size) at the end.
- *What I changed or overrode:* The AI used `chunk_size=400` (tokens) directly in `RecursiveCharacterTextSplitter`, which interprets it as characters — producing 400-character chunks that were too small. I corrected it to `chunk_size=1600` to approximate 400 tokens at ~4 chars/token, and updated `chunk_overlap` from 50 to 200 for the same reason.

**Instance 2 — Grounded generation and Gradio interface**

- *What I gave the AI:* The Generation stage from the Architecture diagram, the exact system prompt text from `planning.md` (including the "I don't have enough information on that" fallback), the grounding requirement that source attribution must be programmatic (not LLM-generated), and the Gradio structure requirement specifying answer box + sources box as separate outputs at `http://localhost:7860`.
- *What it produced:* A complete `generate.py` with the system prompt, Groq API call, `build_context()` and `build_sources()` functions for programmatic attribution, and `app.py` with a Gradio `Blocks` layout including example query buttons, answer textbox, and sources textbox.
- *What I changed or overrode:* The AI set `temperature=0` by default. I changed it to `temperature=0.2` to allow slightly more natural phrasing in answers while still keeping responses factual. I also directed the AI to add deduplication in `build_sources()` — the initial version listed the same source multiple times when multiple chunks from the same document were retrieved, which cluttered the sources box.
