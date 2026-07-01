"""
API route handlers.
Mounted by main.py — keeps FastAPI wiring separate from business logic.
"""

import urllib.error

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app import db
from app.agents import RouterAgent, CitationReasonerAgent, SummariserAgent
from app.config import GRAPH_OUTPUT_PATH
from app.graph import fetch_and_build_graph, find_node_by_title
from app.graph.renderer import GraphRenderer

router = APIRouter()

# ── Singletons ────────────────────────────────────────────────────────────────

_router     = RouterAgent()
_reasoner   = CitationReasonerAgent()
_summariser = SummariserAgent()
_renderer   = GraphRenderer()

# Single-slot in-memory cache keyed by resolved OpenAlex ID
_cache: dict = {
    "paper_id":   None,
    "graph":      None,
    "root_id":    None,
    "root_data":  None,
    "root_title": None,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _ensure_graph(paper_id: str) -> None:
    """Load (or reuse) the citation graph for paper_id."""
    if _cache["paper_id"] == paper_id and _cache["graph"] is not None:
        return

    try:
        graph = fetch_and_build_graph(paper_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found on OpenAlex.")
        raise HTTPException(status_code=502, detail=f"OpenAlex API error: {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach OpenAlex: {exc.reason}")

    root_id = next((n for n, d in graph.nodes(data=True) if d.get("type") == "root"), None)
    if root_id is None:
        raise HTTPException(status_code=500, detail="Graph built with no root node.")

    _cache.update(
        paper_id   = root_id,
        graph      = graph,
        root_id    = root_id,
        root_data  = graph.nodes[root_id],
        root_title = graph.nodes[root_id].get("title", "the root paper"),
    )


def _node_to_source(node_id: str, data: dict) -> dict:
    return {
        "title": data.get("title", "Untitled"),
        "year":  data.get("year"),
        "url":   f"https://openalex.org/{node_id}",
    }


# ── Models ────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    paper_id: str
    question: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")


@router.post("/ask")
def ask(req: AskRequest) -> dict:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="question must not be empty.")

    _ensure_graph(req.paper_id)

    graph      = _cache["graph"]
    root_id    = _cache["root_id"]
    root_data  = _cache["root_data"]
    root_title = _cache["root_title"]

    # Return cached agent answer when the same question has been asked before
    cached = db.get_answer(req.paper_id, question)
    if cached:
        highlight_ids = cached.pop("_highlight_ids", [root_id])
        _renderer.generate(graph, highlight_ids, GRAPH_OUTPUT_PATH)
        return cached

    routing = _router.route(question)
    intent  = routing.get("intent", "summarise")
    hint    = routing.get("paper_b_hint")

    highlight_ids: list[str] = [root_id]
    response: dict = {"graph_url": "/static/graph.html"}

    if intent == "citation_reasoning" and hint:
        citing_id = find_node_by_title(graph, hint)
        if citing_id and citing_id != root_id:
            citing_data = graph.nodes[citing_id]
            answer = _reasoner.reason(
                cited_title     = root_title,
                cited_abstract  = root_data.get("abstract", ""),
                citing_title    = citing_data.get("title", hint),
                citing_abstract = citing_data.get("abstract", ""),
                question        = question,
            )
            highlight_ids.append(citing_id)
            response.update(
                agent   = "retriever",
                answer  = answer,
                sources = [
                    _node_to_source(citing_id, citing_data),
                    _node_to_source(root_id, root_data),
                ],
            )
        else:
            intent = "summarise"

    if intent == "summarise":
        papers = [
            {
                "id":             nid,
                "title":          ndata.get("title", ""),
                "year":           ndata.get("year"),
                "intents":        (graph.get_edge_data(nid, root_id) or {}).get("intents", []),
                "is_influential": (graph.get_edge_data(nid, root_id) or {}).get("is_influential", False),
            }
            for nid, ndata in graph.nodes(data=True)
            if ndata.get("type") == "citing"
        ]
        result = _summariser.summarise(root_title, papers, question)
        top_sources = sorted(
            papers,
            key=lambda p: (p["is_influential"], p.get("year") or 0),
            reverse=True,
        )[:8]
        response.update(
            agent           = "summarizer",
            answer          = result["answer"],
            group_counts    = result["group_counts"],
            papers_analysed = result["papers_analysed"],
            sources         = [_node_to_source(p["id"], graph.nodes[p["id"]]) for p in top_sources],
        )

    _renderer.generate(graph, highlight_ids, GRAPH_OUTPUT_PATH)
    db.save_answer(req.paper_id, question, {**response, "_highlight_ids": highlight_ids})
    return response


@router.get("/graph", include_in_schema=False)
@router.get("/static/graph.html", include_in_schema=False)
def graph_view():
    if not __import__("os").path.exists(GRAPH_OUTPUT_PATH):
        if _cache["graph"] is None:
            raise HTTPException(
                status_code=404,
                detail="No graph generated yet — POST /ask with a paper_id first.",
            )
        _renderer.generate(_cache["graph"], [_cache["root_id"]], GRAPH_OUTPUT_PATH)
    return FileResponse(GRAPH_OUTPUT_PATH, media_type="text/html")
