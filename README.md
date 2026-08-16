# Unravel — News Traceability Graph

> *Unravel the story behind the news.*

Unravel es una herramienta de alfabetización mediática e informacional. El
usuario pega una URL, un titular o una descripción breve, y Unravel
reconstruye —con evidencia observable— cómo apareció esa historia, cómo se
propagó entre medios y cuentas, y cómo fue cambiando mientras se difundía.

El proyecto **no decide automáticamente si una noticia es verdadera o
falsa**. Su objetivo es reducir la fricción de investigar una noticia a
mano: mostrar las fuentes, el orden cronológico, las relaciones entre
publicaciones (confirmación, actualización, contradicción, corrección,
reacción) y un resumen sustentado en evidencia, para que cada persona
pueda formar su propio criterio.

Proyecto para el **Youth Hackathon 2026 — Alfabetización Mediática e
Informacional (UNESCO)**.

---

## Cómo está dividido el sistema

La arquitectura separa deliberadamente dos motores:

```
                        UNRAVEL
                            |
                +-----------+-----------+
                |                       |
                v                       v
     MOTOR DE RASTREO           MOTOR DE ANÁLISIS
     (sin LLM)                  (con LLM)
     --------------------       --------------------
     scraping (httpx,           extracción de claims
     trafilatura, bs4,          comparación de claims
     Playwright fallback)       (SUPPORTS/CONTRADICTS/
     discovery (GDELT,          RELATED/INSUFFICIENT)
     RSS, búsqueda,             detección de cambio
     hyperlinks/citas)          narrativo
     similitud (TF-IDF,         resumen final
     BM25, n-grams,             (OpenRouter, un solo
     spaCy, tiempo)             modelo gratuito)
                |                       |
                +-----------+-----------+
                            |
                            v
                  GRAFO + TIMELINE (JSON)
```

El motor de rastreo encuentra y organiza fuentes usando scraping y
algoritmos clásicos (nada de LLM). Solo cuando ya existe un conjunto de
fuentes relevantes entra el modelo de lenguaje, y únicamente para las
tareas que requieren comprensión semántica: extraer afirmaciones,
compararlas, explicar cómo cambió la narrativa y redactar el resumen final
citando la evidencia ya recolectada.

## Stack

| Componente | Tecnología |
|---|---|
| Frontend | Next.js 14 (App Router) + React + TypeScript + Tailwind CSS |
| Grafo | Cytoscape.js |
| Backend | Python + FastAPI |
| Cola / jobs asíncronos | Redis + RQ (workers en Python) |
| Descarga de páginas | httpx |
| Extracción de contenido | Trafilatura + BeautifulSoup, fallback Playwright |
| Descubrimiento de fuentes | GDELT DOC 2.0 API, RSS, búsqueda web (DuckDuckGo HTML, sin API key), hyperlinks/citas |
| Similitud sin LLM | TF-IDF y BM25 (scikit-learn / rank-bm25), n-gramas, entidades (spaCy), cercanía temporal |
| Base de datos | PostgreSQL (SQLAlchemy + Alembic), pgvector opcional |
| Modelo de lenguaje | **Un solo modelo gratuito vía OpenRouter** (`OPENROUTER_API_KEY`) |

Solo se necesita **una** API key para que el proyecto funcione al 100%: la
de OpenRouter. Todo lo demás (GDELT, RSS, búsqueda) usa endpoints públicos
sin autenticación.

## Estructura del repo

```
backend/    API FastAPI, worker, pipeline de scraping/discovery/similitud/LLM
frontend/   Next.js — pantalla de búsqueda y pantalla del grafo de trazabilidad
docker-compose.yml
.env.example
```

Ver `backend/README.md` y `frontend/README.md` para detalle de cada parte.

## Levantar el proyecto

1. Copia el archivo de entorno y completa tu API key de OpenRouter:

   ```bash
   cp .env.example .env
   # abre .env y pega tu OPENROUTER_API_KEY (https://openrouter.ai/keys)
   ```

2. Levanta todo con Docker Compose:

   ```bash
   docker compose up --build
   ```

   Esto levanta: PostgreSQL, Redis, el backend (FastAPI en
   `http://localhost:8000`), el worker que procesa los análisis, y el
   frontend (Next.js en `http://localhost:3000`).

3. Abre `http://localhost:3000`, pega una URL de una noticia y presiona
   **Trace it**.

### Desarrollo sin Docker

Ver las instrucciones detalladas en `backend/README.md` y
`frontend/README.md` para correr cada servicio localmente (requiere
Postgres y Redis corriendo, por ejemplo vía `docker compose up db redis`).

## Modelo de datos del grafo

El backend expone el grafo como JSON con la forma:

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

Esta misma estructura alimenta directamente el componente de grafo del
frontend (Cytoscape.js) y la línea de tiempo.

## Limitaciones conocidas del MVP

- La relación `POSSIBLY_DERIVED_FROM` (o `developing`/`republication`
  inferidas) se marca explícitamente como **inferida**, nunca como prueba
  de copia directa. Solo `CITES`/`LINKS_TO` (hyperlinks o citas
  explícitas) se tratan como relación observada.
- El discovery está acotado por `DISCOVERY_MAX_DEPTH` y
  `DISCOVERY_MAX_SOURCES` (ver `.env.example`) para mantener el análisis
  rápido y evitar coste innecesario del LLM.
- spaCy y Playwright son *fallbacks* opcionales: si no están instalados o
  el modelo de idioma no está descargado, el sistema sigue funcionando con
  las demás señales (TF-IDF, BM25, n-gramas, fechas, enlaces).
