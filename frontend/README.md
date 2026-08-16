# Unravel — Frontend

Next.js (App Router) + TypeScript + Tailwind CSS + Cytoscape.js. Implementa
las dos pantallas del producto:

- `app/page.tsx` — pantalla de inicio: pegar URL/titular y "Trace it".
- `app/trace/[id]/page.tsx` — el **News Traceability Graph**: eje de
  tiempo, grafo interactivo (Cytoscape.js), leyenda, tarjetas de resumen
  (Origin / Story Drift / Latest State) y panel de detalle de fuente.

## Correr en local

```bash
npm install
cp ../.env.example .env.local   # o define NEXT_PUBLIC_API_BASE_URL manualmente
npm run dev
```

Por defecto apunta a `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` (el
backend de FastAPI). Asegúrate de que el backend y el worker estén
corriendo (ver `../backend/README.md` o `docker compose up`).

## Estructura

```
app/
  page.tsx              pantalla de inicio
  trace/[id]/page.tsx    pantalla del grafo (hace polling de GET /analyses/{id})
components/
  GraphCanvas.tsx        wrapper de Cytoscape.js con layout por línea de tiempo
  SourceDetailPanel.tsx   panel lateral de detalle de fuente
  Legend.tsx, SummaryCards.tsx, AnalysisProgress.tsx, ...
lib/
  api.ts                 cliente HTTP hacia el backend
  types.ts                tipos que reflejan los schemas de FastAPI
  layout.ts               algoritmo de posicionamiento (tiempo -> X, carriles -> Y)
  visualStyle.ts           mapeo de tipos de nodo/relación a color/ícono
```

## Notas de diseño

La paleta (`tailwind.config.ts`, prefijo `unravel-`) sigue el diseño de
Figma del proyecto: fondo crema (`#F7F3EE`), acento menta (`#E8F4F3`),
teal principal (`#1F6F6E`), texto oscuro (`#201B17`), ámbar para estados
"developing" y rojo para "corrected"/divergencias.
