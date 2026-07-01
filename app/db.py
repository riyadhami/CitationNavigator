"""
db.py — Supabase (Postgres) persistence for Citation Navigator.

Two caches so we never repeat expensive work:
  paper_graphs   — one row per resolved paper, storing the built citation graph
                   (NetworkX node-link JSON). Avoids re-hitting OpenAlex.
  agent_answers  — one row per (paper_id, question), storing the /ask response.
                   Avoids re-running the LLM agents for a repeated question.

Every function degrades gracefully: if SUPABASE_URI is unset or the database
is unreachable, it logs and behaves as a no-op (returns None) so the app keeps
working without a cache.
"""

import hashlib
import json
import threading

import networkx as nx

from app.config import SUPABASE_URI

_init_lock = threading.Lock()
_init_done = False

_SCHEMA = """
create table if not exists paper_graphs (
    paper_id   text primary key,
    root_id    text,
    root_title text,
    graph      jsonb not null,
    created_at timestamptz not null default now()
);

create table if not exists agent_answers (
    paper_id      text        not null,
    question_hash text        not null,
    question      text        not null,
    response      jsonb       not null,
    created_at    timestamptz not null default now(),
    primary key (paper_id, question_hash)
);
"""


def _connect():
    import psycopg2
    return psycopg2.connect(SUPABASE_URI, connect_timeout=15, sslmode="require")


def _ensure_init() -> bool:
    """Create tables on first use. Returns True if the DB is usable."""
    global _init_done
    if not SUPABASE_URI:
        return False
    if _init_done:
        return True
    with _init_lock:
        if _init_done:
            return True
        try:
            with _connect() as conn, conn.cursor() as cur:
                cur.execute(_SCHEMA)
            _init_done = True
        except Exception as exc:                      # pragma: no cover - network
            print(f"[db] init failed, caching disabled: {exc}")
        return _init_done


def _hash(question: str) -> str:
    return hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()


def _as_dict(value):
    """psycopg2 usually returns jsonb as dict, but tolerate str too."""
    return json.loads(value) if isinstance(value, str) else value


# ── Graph cache ────────────────────────────────────────────────────────────────

def get_graph(paper_id: str) -> nx.DiGraph | None:
    if not _ensure_init():
        return None
    try:
        with _connect() as conn, conn.cursor() as cur:
            cur.execute("select graph from paper_graphs where paper_id = %s", (paper_id,))
            row = cur.fetchone()
        if row:
            return nx.node_link_graph(_as_dict(row[0]), edges="edges")
    except Exception as exc:                          # pragma: no cover - network
        print(f"[db] get_graph failed: {exc}")
    return None


def save_graph(paper_id: str, graph: nx.DiGraph,
               root_id: str | None = None, root_title: str | None = None) -> None:
    if not _ensure_init():
        return
    try:
        payload = json.dumps(nx.node_link_data(graph, edges="edges"))
        with _connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                insert into paper_graphs (paper_id, root_id, root_title, graph)
                values (%s, %s, %s, %s)
                on conflict (paper_id) do update
                    set graph = excluded.graph,
                        root_id = excluded.root_id,
                        root_title = excluded.root_title,
                        created_at = now()
                """,
                (paper_id, root_id, root_title, payload),
            )
    except Exception as exc:                          # pragma: no cover - network
        print(f"[db] save_graph failed: {exc}")


# ── Answer cache ─────────────────────────────────────────────────────────────

def get_answer(paper_id: str, question: str) -> dict | None:
    if not _ensure_init():
        return None
    try:
        with _connect() as conn, conn.cursor() as cur:
            cur.execute(
                "select response from agent_answers where paper_id = %s and question_hash = %s",
                (paper_id, _hash(question)),
            )
            row = cur.fetchone()
        if row:
            return _as_dict(row[0])
    except Exception as exc:                          # pragma: no cover - network
        print(f"[db] get_answer failed: {exc}")
    return None


def save_answer(paper_id: str, question: str, response: dict) -> None:
    if not _ensure_init():
        return
    try:
        with _connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                insert into agent_answers (paper_id, question_hash, question, response)
                values (%s, %s, %s, %s)
                on conflict (paper_id, question_hash) do update
                    set response = excluded.response,
                        created_at = now()
                """,
                (paper_id, _hash(question), question.strip(), json.dumps(response)),
            )
    except Exception as exc:                          # pragma: no cover - network
        print(f"[db] save_answer failed: {exc}")
