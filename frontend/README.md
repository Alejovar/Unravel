# Unravel — Frontend

Next.js (App Router) + TypeScript + Tailwind CSS + Cytoscape.js. It
implements the two screens of the product:

- `app/page.tsx` — landing screen: paste a URL/headline and hit "Trace it".
- `app/trace/[id]/page.tsx` — the **News Traceability Graph**: timeline,
  interactive graph (Cytoscape.js), legend, summary cards (Origin / Story
  Drift / Latest State) and the source detail panel.

## Running locally

```bash
npm install
cp ../.env.example .env.local   # or set NEXT_PUBLIC_API_BASE_URL manually
npm run dev
```

By default it points at `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
(the FastAPI backend). Make sure the backend and the worker are running
(see `../backend/README.md` or `docker compose up`).

## Structure

```
app/
  page.tsx               landing screen
  trace/[id]/page.tsx    graph screen (polls GET /analyses/{id})
components/
  GraphCanvas.tsx        Cytoscape.js wrapper with the timeline layout
  SourceDetailPanel.tsx  side panel with the source detail
  Legend.tsx, SummaryCards.tsx, AnalysisProgress.tsx, ...
lib/
  api.ts                 HTTP client for the backend
  types.ts               types mirroring the FastAPI schemas
  time.ts                helpers for publication timestamps
  visualStyle.ts         maps node/relation types to colour and icon
```

## Design notes

The palette (`tailwind.config.ts`, prefix `unravel-`) follows the project's
Figma design: cream background (`#F7F3EE`), mint accent (`#E8F4F3`), primary
teal (`#1F6F6E`), dark text (`#201B17`), amber for "developing" states and
red for "corrected" states and divergences.
