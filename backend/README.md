# Unravel — Backend

FastAPI + worker (Redis/RQ) implementing the tracing pipeline (scraping,
discovery, LLM-free similarity) and the semantic analysis engine (LLM
through OpenRouter).

## Running with Docker (recommended)

From the repository root:

```bash
cp .env.example .env   # and paste your OPENROUTER_API_KEY
docker compose up --build
```

## Running locally without Docker

1. Start only Postgres and Redis with Docker:

   ```bash
   docker compose up db redis
   ```

2. Create a virtual environment and install the dependencies:

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm   # optional, improves entity extraction
   playwright install chromium               # optional, fallback for JS-heavy pages
   ```

3. Copy `.env.example` to `backend/.env` (or export the variables) pointing
   at `localhost` instead of the Docker service names:

   ```bash
   DATABASE_URL=postgresql+psycopg://unravel:unravel@localhost:5432/unravel
   REDIS_URL=redis://localhost:6379/0
   ```

4. Apply the migrations:

   ```bash
   alembic upgrade head
   ```

5. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

6. In another terminal, start the worker (it processes analyses in the
   background):

   ```bash
   python -m app.worker
   ```

## Endpoints

- `POST /analyses` — `{"query_input": "https://..."}` → enqueues an
  analysis, answers `202` with `{"analysis_id", "status": "queued"}`.
- `GET /analyses/{id}` — analysis status; when `status == "done"` it also
  includes `graph` with `nodes`/`edges`/`summary_cards` ready for the
  frontend.
- `GET /health` — health check; reports whether an `OPENROUTER_API_KEY` is
  configured.

## Structure

```
app/
  scraping/     httpx + trafilatura + BeautifulSoup + Playwright fallback
  discovery/    GDELT, RSS, search (DuckDuckGo HTML, no key), dedup
  similarity/   TF-IDF, BM25, n-grams, entities (spaCy with fallback), time
  llm/          LLMProvider (abstract) + OpenRouterProvider (only impl.)
  pipeline/     full-flow orchestrator + relation heuristic
  graph/        builds the graph/timeline JSON consumed by the frontend
  api/routes/   FastAPI endpoints
  models/       SQLAlchemy
  schemas/      Pydantic
```

## Tests

```bash
pytest
```

The tests cover only the LLM-free engine (deterministic, no network):
query generation, similarity scoring and the relation classification
heuristic.
