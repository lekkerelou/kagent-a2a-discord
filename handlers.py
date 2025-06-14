import os
import uuid
import logging
from discord.ext import commands
from discord import app_commands, Interaction
from a2a.client import A2AClient

logger = logging.getLogger(__name__)

async def invoke_a2a_agent(agent_url: str, input: str):
    """
    Appelle l'agent A2A et renvoie la réponse.
    """
    a2a_client = A2AClient(url=agent_url, timeout=600.0)
    task_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    payload = {
        "id": task_id,
        "sessionId": session_id,
        "acceptedOutputModes": ["text"],
        "message": {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": input,
                }
            ]
        }
    }

    logger.info(f"Invoking the agent: {agent_url}")
    response = await a2a_client.send_task(payload)
    text = "".join(part.text for artifact in response.result.artifacts for part in artifact.parts)
    return text


def register_handlers(bot: commands.Bot):
    """
    Enregistre les commandes pour le bot Discord.
    """

    @bot.tree.command(name="mykagent", description="Parle à ton agent Kagent")
    async def mykagent(interaction: Interaction, prompt: str):
        await interaction.response.defer(thinking=True)

        kagent_a2a_url = os.getenv("KAGENT_A2A_URL")
        if not kagent_a2a_url:
            await interaction.followup.send(
                "⚠️ L'URL de l'agent Kagent (`KAGENT_A2A_URL`) est manquante dans le .env."
            )
            return

        try:
            result = await invoke_a2a_agent(kagent_a2a_url, prompt)
            await interaction.followup.send(result)
        except Exception as e:
            logger.error(f"Kagent error: {e}")
            await interaction.followup.send(f"❌ Erreur lors de l'appel à Kagent: {e}")
