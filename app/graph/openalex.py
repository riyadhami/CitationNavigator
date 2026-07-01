"""
OpenAlex API client.
Handles HTTP, ID resolution (arXiv / DOI / title / OpenAlex ID), and data fetching.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from app.config import OPENALEX_API_KEY, OPENALEX_MAILTO, CITATION_FETCH_LIMIT

_OA_BASE = "https://api.openalex.org"
_ATOM    = "{http://www.w3.org/2005/Atom}"


# ── HTTP ──────────────────────────────────────────────────────────────────────

def _get(path: str, retries: int = 4, **params) -> dict:
    """GET {_OA_BASE}/{path} with api_key/mailto injection and 429 backoff."""
    if OPENALEX_API_KEY:
        params["api_key"] = OPENALEX_API_KEY
    if OPENALEX_MAILTO:
        params["mailto"] = OPENALEX_MAILTO

    url = f"{_OA_BASE}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                time.sleep(3 * (2 ** attempt))
                continue
            raise


def _try_single(**params) -> dict | None:
    data = _get("works", per_page=1, **params)
    results = data.get("results", [])
    return results[0] if results else None


# ── Data helpers ──────────────────────────────────────────────────────────────

def short_id(openalex_id: str | None) -> str | None:
    """'https://openalex.org/W123' → 'W123'."""
    return openalex_id.rsplit("/", 1)[-1] if openalex_id else None


def extract_authors(work: dict) -> list[str]:
    return [
        a["author"]["display_name"]
        for a in work.get("authorships", [])
        if a.get("author", {}).get("display_name")
    ]


def reconstruct_abstract(inverted_index: dict | None) -> str:
    """Rebuild plain text from OpenAlex's abstract_inverted_index format."""
    if not inverted_index:
        return ""
    positions: dict[int, str] = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


# ── Resolution helpers ────────────────────────────────────────────────────────

def _arxiv_title(arxiv_id: str) -> str | None:
    """Fetch paper title from the free arXiv Atom API."""
    url = f"http://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            root = ET.fromstring(resp.read())
    except Exception:
        return None
    node = root.find(f"{_ATOM}entry/{_ATOM}title")
    if node is None or not node.text:
        return None
    return re.sub(r"\s+", " ", node.text).strip()


def _norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _toks(s: str | None) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def _resolve_by_title(title: str) -> dict | None:
    """
    Find the best OpenAlex match for a known title.
    Ranks candidates by exact normalised-title match, then token-overlap,
    with citation count as a tiebreaker to prefer canonical papers over summaries.
    """
    if not title:
        return None
    sanitized = re.sub(r"[^\w\s]", " ", title)
    candidates = (
        _get("works", search=title, per_page=25).get("results", [])
        + _get("works", filter=f"title.search:{sanitized}", per_page=25).get("results", [])
    )
    seen: set[str] = set()
    uniq: list[dict] = []
    for w in candidates:
        wid = w.get("id")
        if wid and wid not in seen:
            seen.add(wid)
            uniq.append(w)
    if not uniq:
        return None

    exact = [w for w in uniq if _norm(w.get("display_name")) == _norm(title)]
    if exact:
        return max(exact, key=lambda w: w.get("cited_by_count") or 0)

    want = _toks(title)
    scored = sorted(
        (
            (len(want & _toks(w.get("display_name"))) / max(len(want), 1),
             w.get("cited_by_count") or 0, w)
            for w in uniq
        ),
        key=lambda s: (round(s[0], 2), s[1]),
        reverse=True,
    )
    strong = [s for s in scored if s[0] >= 0.6]
    best = (strong or scored)[0] if (strong or scored) else None
    if best is None:
        return None
    if best[0] < 0.7 and best[1] == 0:
        return None
    return best[2]


# ── Public API ────────────────────────────────────────────────────────────────

def resolve_work(paper_id: str) -> dict:
    """
    Resolve arbitrary input (OpenAlex ID, arXiv ID, DOI, free-text title)
    to a single OpenAlex work object.
    """
    pid = paper_id.strip()

    m = re.search(r"(W\d+)", pid, re.IGNORECASE)
    if m and (re.fullmatch(r"[Ww]\d+", pid) or "openalex.org" in pid):
        return _get(f"works/{m.group(1).upper()}")

    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", pid):
        bare = re.sub(r"v\d+$", "", pid)
        work = _resolve_by_title(_arxiv_title(bare)) or _try_single(filter=f"doi:10.48550/arxiv.{bare}")
        if work:
            return work

    if pid.lower().startswith("10.") or "doi.org" in pid:
        doi = pid.split("doi.org/")[-1]
        work = _try_single(filter=f"doi:{doi}")
        if work:
            return work

    work = _resolve_by_title(pid) or _try_single(search=pid)
    if work:
        return work

    raise FileNotFoundError(f"No OpenAlex work found for '{paper_id}'.")


def fetch_citations(work_id: str, limit: int = CITATION_FETCH_LIMIT) -> list[dict]:
    """Fetch citing works via cursor-paginated cites: filter."""
    results: list[dict] = []
    cursor = "*"
    while cursor and len(results) < limit:
        page = _get(
            "works",
            filter=f"cites:{work_id}",
            per_page=min(200, limit - len(results)),
            cursor=cursor,
        )
        results.extend(page.get("results", []))
        cursor = page.get("meta", {}).get("next_cursor")
    return results[:limit]
