import os
from dotenv import load_dotenv

load_dotenv()

# Microsoft AI Foundry — account auth
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "")
FOUNDRY_API_KEY           = os.getenv("FOUNDRY_API_KEY", "")

# Pre-created agent IDs from AI Foundry portal
ROUTER_AGENT_ID            = os.getenv("ROUTER_AGENT_ID", "")
CITATION_REASONER_AGENT_ID = os.getenv("CITATION_REASONER_AGENT_ID", "")
SUMMARISER_AGENT_ID        = os.getenv("SUMMARISER_AGENT_ID", "")

# OpenAlex — free scholarly graph API (https://api.openalex.org)
# api_key is optional (premium pool); mailto opts into the faster "polite pool".
OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY", "")
OPENALEX_MAILTO  = os.getenv("OPENALEX_MAILTO", "")

# Supabase / Postgres connection string — used to cache graphs and agent answers.
# When unset, all DB operations degrade to no-ops and the app still works.
SUPABASE_URI = os.getenv("SUPABASE_URI", "")

# App settings
CITATION_FETCH_LIMIT = int(os.getenv("CITATION_FETCH_LIMIT", "50"))
# On Vercel the static/ directory is read-only; write graph.html to /tmp instead.
GRAPH_OUTPUT_PATH = (
    "/tmp/graph.html" if os.environ.get("VERCEL") else "static/graph.html"
)
