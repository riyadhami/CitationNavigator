# Citation Navigator

Explore a paper's citation network and ask natural-language questions about it. Given a paper ID (OpenAlex ID, arXiv ID, or DOI), Citation Navigator fetches the papers that cite it, builds a citation graph, and answers questions like "which papers extended this work?" or "why did BERT cite this?" — with an interactive graph visualization highlighting the relevant papers.

## How it works

1. **Graph construction** ([`app/graph/`](app/graph/)) — [`openalex.py`](app/graph/openalex.py) resolves the root paper and fetches citing works from the [OpenAlex API](https://api.openalex.org). [`builder.py`](app/graph/builder.py) assembles a NetworkX `DiGraph`: every citing paper gets a `cites` edge to the root, and `add_similarity_edges()` adds `similar` edges between citing papers that share references (bibliographic coupling), capped at 5 per node.
2. **Question answering** ([`app/agents/`](app/agents/)) — a `RouterAgent` classifies the question's intent (`citation_reasoning` vs `summarise`), then either a `CitationReasonerAgent` (explains why one paper cited another) or a `SummariserAgent` (analyses up to 40 citing papers) produces the answer. All three are pre-provisioned agents on **Azure AI Foundry's Agent Service**, called through the shared `run_agent()` helper in [`_client.py`](app/agents/_client.py).
3. **Caching** ([`app/db.py`](app/db.py)) — citation graphs and agent answers are cached in Supabase, keyed by paper ID and by `(paper_id, question)` respectively. Without `SUPABASE_URI` set, caching degrades to a no-op and everything is refetched per request.
4. **Graph rendering** ([`app/graph/renderer.py`](app/graph/renderer.py)) — renders the NetworkX graph to a self-contained vis.js HTML page ([`templates/graph.html`](templates/graph.html)), with nodes colored by publication year, sized by citation count, and labeled `Surname, Year`. The relevant papers for the current answer are highlighted.
5. **API** ([`app/routes.py`](app/routes.py), wired up in [`main.py`](main.py)) — a FastAPI app exposing `POST /ask` and serving the graph at `/static/graph.html`.
6. **Frontend** ([`frontend/`](frontend/)) — a React + Vite + Tailwind single-page app that posts to `/ask` and renders the answer alongside the graph.

## Project layout

```
app/
  routes.py          FastAPI route handlers
  config.py           Environment-driven settings
  db.py                Supabase-backed caching (graphs + agent answers)
  graph/
    openalex.py        OpenAlex API client
    builder.py          Citation graph construction + similarity scoring
    renderer.py          NetworkX -> vis.js HTML renderer
  agents/
    _client.py           Azure AI Foundry Agents client + run_agent() helper
    router.py             Classifies question intent
    reasoner.py             Explains why paper A cited paper B
    summariser.py            Summarises the citation landscape
templates/graph.html   Source template for the graph visualization
frontend/              React + Vite + Tailwind SPA
static/                Built frontend + generated graph.html (served by FastAPI)
main.py               FastAPI app entry point
```

## Setup

Requires Python 3.12+ and Node.js.

```bash
# Backend
uv sync                    # or: pip install -e .
cp .env.example .env       # if present — otherwise create .env (see below)

# Frontend
cd frontend
npm install
npm run build               # outputs into ../static
```

### Environment variables

| Variable | Purpose |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint |
| `FOUNDRY_API_KEY` | Azure AI Foundry API key |
| `ROUTER_AGENT_ID`, `CITATION_REASONER_AGENT_ID`, `SUMMARISER_AGENT_ID` | Pre-created agent IDs from the AI Foundry portal |
| `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` | Optional — service-principal auth; falls back to `DefaultAzureCredential` if unset |
| `OPENALEX_API_KEY` | Optional — OpenAlex premium pool |
| `OPENALEX_MAILTO` | Optional — opts into OpenAlex's faster "polite pool" |
| `SUPABASE_URI` | Optional — Postgres/Supabase connection string for caching; all DB operations no-op if unset |
| `CITATION_FETCH_LIMIT` | Max citing works to fetch per paper (default 50) |

## Running locally

```bash
uvicorn main:app --reload --port 8000
```

For frontend development with hot reload, run the Vite dev server alongside it (proxies `/ask` and `/static` to port 8000):

```bash
cd frontend
npm run dev
```

## Deployment

Configured for [Vercel](vercel.json) — the FastAPI app runs as a Python serverless function, with the built frontend served as static files. On Vercel, `GRAPH_OUTPUT_PATH` automatically points to `/tmp` since `static/` is read-only at runtime.
