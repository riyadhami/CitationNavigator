"""
Graph construction and similarity scoring.
"""

import math
from collections import defaultdict

import networkx as nx

from app import db
from app.graph.openalex import (
    resolve_work, fetch_citations,
    short_id, extract_authors, reconstruct_abstract,
)


def build_graph(
    root_id: str,
    root_title: str,
    root_abstract: str,
    citing_works: list[dict],
    root_work: dict | None = None,
) -> nx.DiGraph:
    """Construct a directed citation graph: citing_paper → root_paper."""
    g = nx.DiGraph()
    root_work = root_work or {}
    g.add_node(
        root_id,
        title    = root_title,
        abstract = root_abstract,
        year     = root_work.get("publication_year"),
        authors  = extract_authors(root_work),
        cited_by = root_work.get("cited_by_count"),
        refs     = [short_id(r) for r in root_work.get("referenced_works", [])],
        type     = "root",
    )
    for w in citing_works:
        cid = short_id(w.get("id"))
        if not cid:
            continue
        g.add_node(
            cid,
            title    = w.get("display_name") or "",
            abstract = reconstruct_abstract(w.get("abstract_inverted_index")),
            year     = w.get("publication_year"),
            authors  = extract_authors(w),
            cited_by = w.get("cited_by_count"),
            refs     = [short_id(r) for r in w.get("referenced_works", [])],
            type     = "citing",
        )
        g.add_edge(cid, root_id, type="cites", intents=[], contexts=[], is_influential=False)
    return g


def add_similarity_edges(g: nx.DiGraph, top_k: int = 5, min_shared: int = 2) -> None:
    """
    Add bibliographic-coupling similarity edges between citing papers (in-place).

    BC(A,B) = |refs(A) ∩ refs(B)| / sqrt(|refs(A)| × |refs(B)|)

    Only pairs sharing ≥ min_shared references are considered.
    Each node keeps at most top_k similarity edges (strongest wins).
    Edges carry type="similar" and weight=BC score for the renderer.
    """
    citing = [
        (n, set(d.get("refs") or []))
        for n, d in g.nodes(data=True)
        if d.get("type") == "citing" and d.get("refs")
    ]

    pair_scores: list[tuple[float, str, str]] = []
    for i, (n1, refs1) in enumerate(citing):
        for n2, refs2 in citing[i + 1:]:
            shared = len(refs1 & refs2)
            if shared < min_shared:
                continue
            score = shared / math.sqrt(len(refs1) * len(refs2))
            pair_scores.append((score, n1, n2))

    if not pair_scores:
        return

    node_best: defaultdict[str, list] = defaultdict(list)
    for score, n1, n2 in pair_scores:
        node_best[n1].append((score, n2))
        node_best[n2].append((score, n1))

    kept: set[tuple[str, str]] = set()
    for node, neighbors in node_best.items():
        for score, other in sorted(neighbors, reverse=True)[:top_k]:
            key = (min(node, other), max(node, other))
            if key not in kept:
                kept.add(key)
                g.add_edge(
                    node, other,
                    type          = "similar",
                    weight        = round(score, 4),
                    intents       = [],
                    contexts      = [],
                    is_influential= False,
                )


def fetch_and_build_graph(paper_id: str) -> nx.DiGraph:
    """
    Load or build the citation + similarity graph for paper_id.

    Resolution order:
      1. Supabase cache — instant (skipped if refs/similarity data is absent)
      2. OpenAlex API  — fetches citing works, scores similarity, caches result
    """
    root          = resolve_work(paper_id)
    root_id       = short_id(root["id"])
    root_title    = root.get("display_name") or "Root paper"
    root_abstract = reconstruct_abstract(root.get("abstract_inverted_index"))

    cached = db.get_graph(root_id)
    if cached is not None:
        citing_nodes = [n for n, d in cached.nodes(data=True) if d.get("type") == "citing"]
        has_refs = any(cached.nodes[n].get("refs") for n in citing_nodes)
        has_sim  = any(d.get("type") == "similar" for _, _, d in cached.edges(data=True))

        if has_refs and has_sim:
            return cached

        if has_refs and not has_sim:
            add_similarity_edges(cached)
            db.save_graph(root_id, cached, root_id, root_title)
            return cached

    citing_works = fetch_citations(root_id)
    g = build_graph(root_id, root_title, root_abstract, citing_works, root)
    add_similarity_edges(g)
    db.save_graph(root_id, g, root_id, root_title)
    return g


def find_node_by_title(graph: nx.DiGraph, title_hint: str) -> str | None:
    """Fuzzy-match a title fragment against graph node titles."""
    hint       = title_hint.lower().split()
    best_id    = None
    best_score = 0.0
    for node_id, data in graph.nodes(data=True):
        node_title = (data.get("title") or "").lower()
        score = sum(1 for w in hint if w in node_title) / max(len(hint), 1)
        if score > best_score:
            best_score = score
            best_id    = node_id
    return best_id if best_score > 0 else None
