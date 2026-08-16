# Unravel — Backend

FastAPI + worker (Redis/RQ) que implementa el pipeline de rastreo (scraping,
discovery, similitud sin LLM) y el motor de análisis semántico (LLM vía
OpenRouter).

## Correr con Docker (recomendado)

Desde la raíz del repo:

```bash
cp .env.example .env   # y pega tu OPENROUTER_API_KEY
docker compose up --build
```

## Correr en local sin Docker

1. Levanta solo Postgres y Redis con Docker:

   ```bash
   docker compose up db redis
   ```

2. Crea un entorno virtual e instala dependencias:

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python -m spacy download es_core_news_sm   # opcional, mejora extracción de entidades
   playwright install chromium                # opcional, fallback para páginas con JS
   ```

3. Copia `.env.example` a `backend/.env` (o exporta las variables) apuntando
   a `localhost` en vez de los nombres de servicio de Docker:

   ```bash
   DATABASE_URL=postgresql+psycopg://unravel:unravel@localhost:5432/unravel
   REDIS_URL=redis://localhost:6379/0
   ```

4. Aplica las migraciones:

   ```bash
   alembic upgrade head
   ```

5. Levanta la API:

   ```bash
   uvicorn app.main:app --reload
   ```

6. En otra terminal, levanta el worker (procesa los análisis en segundo plano):

   ```bash
   python -m app.worker
   ```

## Endpoints

- `POST /analyses` — `{"query_input": "https://..."}` → encola un análisis,
  responde `202` con `{"analysis_id", "status": "queued"}`.
- `GET /analyses/{id}` — estado del análisis; cuando `status == "done"`
  incluye `graph` con `nodes`/`edges`/`summary_cards` listos para el
  frontend.
- `GET /health` — chequeo de salud; incluye si hay `OPENROUTER_API_KEY`
  configurada.

## Estructura

```
app/
  scraping/     httpx + trafilatura + BeautifulSoup + fallback Playwright
  discovery/    GDELT, RSS, búsqueda (DuckDuckGo HTML, sin key), dedup
  similarity/   TF-IDF, BM25, n-gramas, entidades (spaCy con fallback), tiempo
  llm/          LLMProvider (abstracto) + OpenRouterProvider (único impl.)
  pipeline/     orquestador del flujo completo + heurística de relaciones
  graph/        arma el JSON de grafo/timeline que consume el frontend
  api/routes/   endpoints FastAPI
  models/       SQLAlchemy
  schemas/      Pydantic
```

## Tests

```bash
pytest
```

Los tests cubren únicamente el motor sin LLM (determinista, sin red):
generación de queries, scoring de similitud y la heurística de
clasificación de relaciones.
