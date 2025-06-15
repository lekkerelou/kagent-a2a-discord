import os
import uuid
import logging
from discord import Message
from discord.ext import commands
from a2a.client import A2AClient

logger = logging.getLogger(__name__)

MAX_LENGTH = 2000

def split_by_lines(text, max_len=MAX_LENGTH):
    lines = text.splitlines(keepends=True)
    chunks = []
    current = ""

    for line in lines:
        if len(current) + len(line) > max_len:
            chunks.append(current)
            current = line
        else:
            current += line

    if current:
        chunks.append(current)

    return chunks


async def invoke_a2a_agent(agent_url: str, input: str):
    """
    Send a prompt to the A2A agent and return the response as a string.
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
            "parts": [{"type": "text", "text": input}]
        }
    }

    logger.info(f"Invoking the agent: {agent_url}")
    response = await a2a_client.send_task(payload)

    return "".join(part.text for artifact in response.result.artifacts for part in artifact.parts)


def register_handlers(bot: commands.Bot):
    """
    Register the message listener and control behavior via env vars:
    - MENTION_ONLY=true: respond only when mentioned
    - CHANNEL_ONLY=ID1,ID2: only respond in specific channels
    """
    mention_only = os.getenv("DISCORD_MENTION_ONLY", "false").lower() == "true"
    allowed_channels_raw = os.getenv("DISCORD_CHANNEL_ONLY", "")
    allowed_channels = [c.strip() for c in allowed_channels_raw.split(",") if c.strip().isdigit()]

    @bot.event
    async def on_message(message: Message):
        if message.author.bot:
            return  # Ignore bots (including self)

        content = message.content.strip()
        user_id = message.author.id
        channel_id = str(message.channel.id)

        # If MENTION_ONLY is enabled, ignore messages that don't mention the bot
        if mention_only and message.guild and message.guild.me not in message.mentions:
            return

        # If CHANNEL_ONLY is set, ignore messages in channels not listed
        if allowed_channels and channel_id not in allowed_channels:
            return

        logger.info(f"Received a message from user {user_id} in channel {channel_id}: {content}")

        kagent_a2a_url = os.getenv("KAGENT_A2A_URL")
        if not kagent_a2a_url:
            await message.reply("⚠️ Missing `KAGENT_A2A_URL` in `.env`.")
            return

        try:
            await message.channel.typing()
            response = await invoke_a2a_agent(kagent_a2a_url, content)

            if len(response) <= MAX_LENGTH:
                await message.reply(response)
            else:
                chunks = split_by_lines(response)
                await message.reply(chunks[0])  # only the first chunk as reply
                for chunk in chunks[1:]:
                    await message.channel.send(chunk)  # rest as follow-ups


        except Exception as e:
            logger.error(f"Error: {e}")
            await message.reply(f"❌ Error while talking to Kagent: {e}")
