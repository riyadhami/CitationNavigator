from app.config import SUMMARISER_AGENT_ID
from app.agents._client import run_agent


class SummariserAgent:
    """Answers general questions about a paper's citation landscape."""

    _INSTRUCTIONS = """\
You are an academic research analyst specialising in citation networks.
You will receive a root paper title and a list of papers that cite it with year, title, and citation intents.
Answer the user's question concisely using markdown. Cite specific paper titles where relevant.
Highlight patterns and research trends."""

    _INTENT_MAP = {
        "methodology": "extends",
        "extends":     "extends",
        "background":  "supports",
        "result":      "supports",
        "supports":    "supports",
        "contrast":    "contradicts",
        "contradicts": "contradicts",
    }

    def summarise(self, root_title: str, papers: list[dict], question: str) -> dict:
        lines = []
        for p in papers[:40]:
            intents_str = ", ".join(p.get("intents", [])) or "unspecified"
            star = "★" if p.get("is_influential") else " "
            lines.append(
                f"{star} [{p.get('year', '?')}] {p.get('title', 'Untitled')} "
                f"| intents: {intents_str}"
            )

        prompt = f"""\
Root paper: "{root_title}"

Citing papers:
{chr(10).join(lines)}

Question: {question}"""

        answer = run_agent(SUMMARISER_AGENT_ID, prompt, instructions=self._INSTRUCTIONS)

        counts = {"extends": 0, "supports": 0, "contradicts": 0, "mentions": 0}
        for p in papers:
            for raw in p.get("intents", []):
                bucket = self._INTENT_MAP.get(raw.lower(), "mentions")
                counts[bucket] += 1

        return {
            "answer":          answer,
            "group_counts":    counts,
            "papers_analysed": len(papers),
        }
