from app.config import CITATION_REASONER_AGENT_ID
from app.agents._client import run_agent


class CitationReasonerAgent:
    """Explains why paper A likely cited paper B."""

    _INSTRUCTIONS = """\
You are an expert academic citation analyst.
You will be given the title and abstract of a CITED paper (B) and a CITING paper (A).
Explain in 4-6 sentences why paper A likely cited paper B.
Focus on specific technical, methodological, or conceptual connections.
Use markdown formatting. Be precise and insightful."""

    def reason(
        self,
        cited_title: str,
        cited_abstract: str,
        citing_title: str,
        citing_abstract: str,
        question: str,
    ) -> str:
        prompt = f"""\
**CITED paper (B):** {cited_title}
Abstract: {cited_abstract or "Not available."}

**CITING paper (A):** {citing_title}
Abstract: {citing_abstract or "Not available."}

User question: {question}

Why did paper A cite paper B?"""

        return run_agent(CITATION_REASONER_AGENT_ID, prompt, instructions=self._INSTRUCTIONS)
