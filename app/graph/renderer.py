"""
Graph renderer — converts a NetworkX citation graph to a self-contained vis.js HTML file.
Reads the template from templates/graph.html and substitutes data placeholders.
"""

import json
import math
import os
from pathlib import Path

import networkx as nx

from app.config import GRAPH_OUTPUT_PATH

_TEMPLATE_PATH = Path(__file__).parents[2] / "templates" / "graph.html"


class GraphRenderer:
    """
    Renders a NetworkX citation graph to an interactive HTML file.

    Node encoding:
      colour  — monochrome year gradient: pale slate (old) → deep teal (recent)
      size    — log-scaled citation count, normalised within the graph
      label   — "Surname, Year" on every node; full title/authors in tooltip & side panel

    Edge encoding:
      type="cites"   — thin grey line to the root, no arrowhead (kept subtle)
      type="similar" — same grey hue, width/opacity ∝ BC score (closer cluster = stronger line)
    Both edge types share one visual language so the graph reads as a single
    web of relationships rather than two competing colour systems.
    """

    # Pale slate (old) → deep teal (recent)
    _YEAR_LIGHT   = (176, 196, 191)
    _YEAR_DARK    = (10, 61, 61)
    _UNKNOWN_YEAR = "#94a3b8"
    _ROOT_BORDER  = "#a21caf"
    _HL_BORDER    = "#f87171"

    # ── colour helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _lerp(c0, c1, t):
        return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))

    @classmethod
    def _year_colour(cls, year, min_year, max_year):
        if not year:
            return cls._UNKNOWN_YEAR
        if max_year == min_year:
            t = 1.0
        else:
            t = (int(year) - min_year) / (max_year - min_year)
        t = max(0.0, min(1.0, t))
        r, g, b = cls._lerp(cls._YEAR_LIGHT, cls._YEAR_DARK, t)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _author_surname(authors: list[str]) -> str:
        if not authors:
            return ""
        return authors[0].split()[-1]

    @staticmethod
    def _node_size(cited_by: int, log_min: float, log_range: float) -> float:
        """Map cited_by onto [7, 20] normalised within the graph's citation range."""
        if not cited_by:
            return 7
        log_val = math.log2(cited_by + 1)
        t = (log_val - log_min) / log_range if log_range > 0 else 0
        return round(7 + t * 13, 1)

    # ── main entry point ──────────────────────────────────────────────────────

    def generate(
        self,
        graph: nx.DiGraph,
        highlight_ids: list[str],
        output_path: str = GRAPH_OUTPUT_PATH,
    ) -> str:
        cb_vals = [
            math.log2((d.get("cited_by") or 0) + 1)
            for _, d in graph.nodes(data=True)
            if d.get("cited_by")
        ]
        log_min   = min(cb_vals) if cb_vals else 0.0
        log_range = max((max(cb_vals) if cb_vals else 1.0) - log_min, 1.0)

        years     = [d.get("year") for _, d in graph.nodes(data=True) if d.get("year")]
        min_year  = min(years) if years else 2000
        max_year  = max(years) if years else 2000

        nodes_js  = []
        edges_js  = []
        node_data = {}

        for node_id, data in graph.nodes(data=True):
            year      = data.get("year")
            cited_by  = data.get("cited_by") or 0
            is_root   = data.get("type") == "root"
            is_hl     = node_id in highlight_ids and not is_root
            title     = data.get("title") or node_id
            authors   = data.get("authors") or []
            abstract  = data.get("abstract") or ""
            size      = self._node_size(cited_by, log_min, log_range)
            surname   = self._author_surname(authors)
            label     = f"{surname}, {year}" if surname and year else (str(year) if year else surname)

            bg = self._year_colour(year, min_year, max_year)

            if is_root:
                border = self._ROOT_BORDER
                size   = max(16, size)
                font   = {"size": 13, "color": self._ROOT_BORDER}
                bw     = 3
            elif is_hl:
                border = self._HL_BORDER
                size   = max(14, size)
                font   = {"size": 10, "color": "#dc2626"}
                bw     = 3
            else:
                border = bg
                font   = {"size": 9, "color": "#64748b"}
                bw     = 0

            authors_str      = ", ".join(authors[:2]) if authors else "Unknown authors"
            abstract_snippet = (abstract[:140] + "…") if len(abstract) > 140 else abstract
            tooltip = (
                "<div class='tt'>"
                f"<b class='tt-title'>{title}</b>"
                f"<span class='tt-meta'>{year or '?'} · {authors_str}</span><br>"
                f"<span class='tt-meta2'>{cited_by:,} citations</span>"
                + (f"<p class='tt-abstract'>{abstract_snippet}</p>" if abstract_snippet else "")
                + "</div>"
            )

            nodes_js.append({
                "id":    node_id,
                "label": label,
                "title": tooltip,
                "color": {
                    "background": bg,
                    "border":     border,
                    "highlight":  {"background": bg, "border": "#a21caf"},
                    "hover":      {"background": bg, "border": "#a21caf"},
                },
                "size":               size,
                "shape":              "dot",
                "font":               font,
                "borderWidth":        bw,
                "borderWidthSelected": 3,
            })

            node_data[node_id] = {
                "title":    title,
                "authors":  authors[:5],
                "year":     year,
                "cited_by": cited_by,
                "abstract": abstract[:400],
                "url":      f"https://openalex.org/{node_id}",
                "is_root":  is_root,
            }

        # Single grey hue for every edge — strength is conveyed by width/opacity only,
        # so the graph reads as one relationship web instead of two competing colours.
        for u, v, edata in graph.edges(data=True):
            if edata.get("type") == "similar":
                w      = edata.get("weight", 0.05)
                alpha  = round(min(0.55, 0.12 + w * 1.1), 2)
                width  = round(0.6 + w * 3.5, 1)
                length = int(max(70, 200 - w * 500))
                edges_js.append({
                    "from":   u, "to": v,
                    "_sim":   True,
                    "length": length,
                    "color":  {"color": f"rgba(100,116,139,{alpha})",
                               "highlight": "rgba(71,85,105,0.85)",
                               "hover":     "rgba(71,85,105,0.6)"},
                    "width":  width,
                    "smooth": False,
                    "arrows": {"to": {"enabled": False}},
                    "title":  f"Similarity (shared refs): {w:.3f}",
                })
            else:
                edges_js.append({
                    "from":   u, "to": v,
                    "_sim":   False,
                    "length": 220,
                    "color":  {"color": "rgba(100,116,139,0.14)",
                               "highlight": "rgba(71,85,105,0.85)",
                               "hover":     "rgba(71,85,105,0.6)"},
                    "width":  0.6,
                    "smooth": False,
                    "arrows": {"to": {"enabled": False}},
                })

        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(self._render_template(nodes_js, edges_js, node_data, min_year, max_year))
        return output_path

    def _render_template(self, nodes, edges, node_data, min_year, max_year) -> str:
        template = _TEMPLATE_PATH.read_text(encoding="utf-8")
        return (
            template
            .replace("__NODES_JSON__",     json.dumps(nodes,     ensure_ascii=False))
            .replace("__EDGES_JSON__",     json.dumps(edges,     ensure_ascii=False))
            .replace("__NODE_DATA_JSON__", json.dumps(node_data, ensure_ascii=False))
            .replace("__YEAR0__",          str(min_year))
            .replace("__YEAR1__",          str(max_year))
        )
