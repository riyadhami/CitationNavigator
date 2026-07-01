"""
Azure AI Foundry client singleton and low-level agent runner.
All agent classes import `run_agent` from here.
"""

import os

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from azure.identity import ClientSecretCredential, DefaultAzureCredential

from app.config import FOUNDRY_PROJECT_ENDPOINT

_tenant_id     = os.getenv("AZURE_TENANT_ID")
_client_id     = os.getenv("AZURE_CLIENT_ID")
_client_secret = os.getenv("AZURE_CLIENT_SECRET")

_credential = (
    ClientSecretCredential(_tenant_id, _client_id, _client_secret)
    if all([_tenant_id, _client_id, _client_secret])
    else DefaultAzureCredential()
)

client = AgentsClient(endpoint=FOUNDRY_PROJECT_ENDPOINT, credential=_credential)


def run_agent(agent_id: str, user_message: str, instructions: str | None = None) -> str:
    """Post a message to a pre-existing Foundry agent and return its text reply."""
    thread = client.threads.create()
    try:
        client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_message,
        )
        run = client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent_id,
            instructions=instructions,
        )
        if run.status != "completed":
            return ""
        reply = client.messages.get_last_message_text_by_role(
            thread_id=thread.id,
            role=MessageRole.AGENT,
        )
        return reply.text.value if reply else ""
    finally:
        client.threads.delete(thread.id)
