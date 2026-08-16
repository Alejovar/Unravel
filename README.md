# Unravel — News Traceability Graph

> *Unravel the story behind the news.*

Unravel is a media and information literacy tool. The user pastes a URL, a
headline or a short description, and Unravel reconstructs — with
observable evidence — how that story first appeared, how it spread across
outlets and accounts, and how it changed while it travelled.

The project **does not automatically decide whether a story is true or
false**. Its goal is to remove the friction of investigating a story by
hand: showing the sources, the chronological order, the relations between
publications (confirmation, update, contradiction, correction, reaction)
and an evidence-backed summary, so that each person can form their own
judgement.

Built for the **Youth Hackathon 2026 — Media and Information Literacy
(UNESCO)**.

---

## How the system is split

The architecture deliberately separates two engines:

```
                        UNRAVEL
                            |
                +-----------+-----------+
                |                       |
                v                       v
      TRACING ENGINE             ANALYSIS ENGINE
      (no LLM)                   (with LLM)
      --------------------       --------------------
      scraping (httpx,           claim extraction
      trafilatura, bs4,          claim comparison
      Playwright fallback)       (SUPPORTS/CONTRADICTS/
      discovery (GDELT,          RELATED/INSUFFICIENT)
      RSS, search,               narrative change
      hyperlinks/citations)      detection
      similarity (TF-IDF,        final summary
      BM25, n-grams,             (NVIDIA NIM, a single
      spaCy, time)               free model)
                |                       |
                +-----------+-----------+
                            |
                            v
                   GRAPH + TIMELINE (JSON)
```

The tracing engine finds and organises sources using scraping and classic
algorithms (no LLM at all). Only once a set of relevant sources exists does
the language model step in, and only for the tasks that require semantic
understanding: extracting claims, comparing them, explaining how the
narrative changed, and writing the final summary citing the evidence
already collected.

## Stack

| Component | Technology |
|---|---|
| Frontend | Next.js 14 (App Router) + React + TypeScript + Tailwind CSS |
| Graph | Cytoscape.js |
| Backend | Python + FastAPI |
| Queue / async jobs | Redis + RQ (Python workers) |
| Page download | httpx |
| Content extraction | Trafilatura + BeautifulSoup, Playwright fallback |
| Source discovery | GDELT DOC 2.0 API, RSS, web search (DuckDuckGo HTML, no API key), hyperlinks/citations |
| LLM-free similarity | TF-IDF and BM25 (scikit-learn / rank-bm25), n-grams, entities (spaCy), temporal proximity |
| Database | PostgreSQL (SQLAlchemy + Alembic), optional pgvector |
| Language model | **A single free model through NVIDIA NIM** (`meta/llama-3.1-8b-instruct`, via `OPENROUTER_API_KEY`) |

Only **one** API key is needed for the project to work end to end: the
NVIDIA NIM one (get it for free at https://build.nvidia.com). Everything
else (GDELT, RSS, search) uses public endpoints with no authentication.
The LLM client speaks the OpenAI/OpenRouter-compatible chat completions
format, so it also works unchanged with OpenRouter or any other
compatible provider if you prefer — just point `OPENROUTER_BASE_URL` and
`OPENROUTER_MODEL` at it.

## Repository layout

```
backend/    FastAPI API, worker, scraping/discovery/similarity/LLM pipeline
frontend/   Next.js — search screen and traceability graph screen
docker-compose.yml
.env.example
```

See `backend/README.md` and `frontend/README.md` for the details of each
part.

## Getting the project up

1. Copy the environment file and fill in your NVIDIA NIM API key:

   ```bash
   cp .env.example .env
   # open .env and paste your OPENROUTER_API_KEY (get a free one at https://build.nvidia.com)
   ```

2. Bring everything up with Docker Compose:

   ```bash
   docker compose up --build
   ```

   This starts: PostgreSQL, Redis, the backend (FastAPI on
   `http://localhost:8000`), the worker that processes analyses, and the
   frontend (Next.js on `http://localhost:3000`).

3. Open `http://localhost:3000`, paste a news URL and press **Trace it**.

### Development without Docker

See the detailed instructions in `backend/README.md` and
`frontend/README.md` to run each service locally (it requires Postgres and
Redis running, for example through `docker compose up db redis`).

## Graph data model

The backend exposes the graph as JSON with this shape:

```json
{
  "nodes": [
    {
      "id": "art_1",
      "type": "origin | confirmed | developing | corrected",
      "label": "Metro Tribune",
      "source": "@downtown_witness",
      "url": "...",
      "published_at": "2024-08-14T14:02:00Z",
      "headline": "...",
      "summary": "...",
      "status": "unverified | confirmed | developing | corrected",
      "reads": 142000,
      "shares": 8400
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "art_1",
      "target": "art_2",
      "relation": "confirmation | developing | correction | reaction | update | republication",
      "confidence": 0.86,
      "kind": "observed | inferred"
    }
  ]
}
```

That same structure feeds the frontend graph component (Cytoscape.js) and
the timeline directly.

## Known MVP limitations

- The `POSSIBLY_DERIVED_FROM` relation (or the inferred
  `developing`/`republication` ones) is explicitly flagged as **inferred**,
  never as proof of direct copying. Only `CITES`/`LINKS_TO` (hyperlinks or
  explicit citations) are treated as an observed relation.
- Discovery is bounded by `DISCOVERY_MAX_DEPTH` and
  `DISCOVERY_MAX_SOURCES` (see `.env.example`) to keep the analysis fast
  and avoid unnecessary LLM cost.
- spaCy and Playwright are optional *fallbacks*: if they are not installed,
  or the language model is not downloaded, the system keeps working with
  the remaining signals (TF-IDF, BM25, n-grams, dates, links).
- The interface and the generated summaries are in English, but the sources
  being traced can be in any language: discovery, similarity and entity
  extraction are configured to handle multilingual coverage.
