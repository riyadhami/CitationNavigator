# Citation Navigator

Explore a paper's citation network and ask natural-language questions about it. Given a paper ID (OpenAlex ID, arXiv ID, or DOI), Citation Navigator fetches the papers that cite it, builds a citation graph, and answers questions like "which papers extended this work?" or "why did BERT cite this?" — with an interactive graph visualization highlighting the relevant papers.

## How it works

1. **Graph construction**  — [`builder.py`] assembles a NetworkX `DiGraph`: every citing paper gets a `cites` edge to the root, and `add_similarity_edges()` adds `similar` edges between citing papers that share references (bibliographic coupling), capped at 5 per node.
2. **Question answering** — a `RouterAgent` classifies the question's intent (`citation_reasoning` vs `summarise`), then either a `CitationReasonerAgent` (explains why one paper cited another) or a `SummariserAgent` (analyses up to 40 citing papers) produces the answer. All three are agents on **Azure AI Foundry**, called through the shared `run_agent()` helper.
3. **Caching** — citation graphs and agent answers are cached in Supabase, keyed by paper ID and by `(paper_id, question)` respectively. Without `SUPABASE_URI` set, caching degrades to a no-op and everything is refetched per request.
4. **Graph rendering** — renders the NetworkX graph to a self-contained vis.js HTML page, with nodes colored by publication year, sized by citation count, and labeled `Surname, Year`. The relevant papers for the current answer are highlighted.
5. **Frontend**  — a React + Vite + Tailwind single-page app that posts to `/ask` and renders the answer alongside the graph.

