import json

from app.config import ROUTER_AGENT_ID
from app.agents._client import run_agent


class RouterAgent:
    """Classifies a user question into an intent + optional paper hint."""

    _INSTRUCTIONS = """\
You are a citation-question router for an academic graph tool.
Given a user question about a paper, return JSON (and nothing else) with:
  "intent": "citation_reasoning" if the user asks why a specific paper cited the root paper,
            "summarise" for any other question about the citation landscape.
  "paper_b_hint": title fragment of the CITING paper if citation_reasoning, else null.
Examples:
  Q: "Why did BERT cite this?" → {"intent": "citation_reasoning", "paper_b_hint": "BERT"}
  Q: "Which papers extended this?" → {"intent": "summarise", "paper_b_hint": null}
Return only valid JSON, no other text."""

    def route(self, question: str) -> dict:
        text = run_agent(ROUTER_AGENT_ID, question, instructions=self._INSTRUCTIONS)
        try:
            return json.loads(text.strip())
        except (json.JSONDecodeError, ValueError):
            return {"intent": "summarise", "paper_b_hint": None}
