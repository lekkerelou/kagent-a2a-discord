import os
import uuid
import logging
import httpx
from discord import Message
from discord.ext import commands
from a2a.client import A2AClient
from a2a.types import SendMessageRequest, MessageSendParams, Message as A2AMessage, TextPart, Role

logger = logging.getLogger(__name__)

MAX_LENGTH = 2000

# Store contextId per Discord channel for session continuity
channel_contexts = {}

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


async def invoke_a2a_agent(agent_url: str, input: str, channel_id: str):
    """
    Send a prompt to the A2A agent and return the response as a string.
    Maintains conversation context per Discord channel using contextId.
    
    Args:
        agent_url: The A2A agent endpoint URL
        input: The user's message text
        channel_id: Discord channel ID for session management
    
    Returns:
        The agent's response text
    """
    # Create httpx client for the official A2AClient
    async with httpx.AsyncClient(timeout=600.0) as httpx_client:
        a2a_client = A2AClient(httpx_client=httpx_client, url=agent_url)
        
        # Get existing context for this channel, if any
        existing_context_id = channel_contexts.get(channel_id)
        logger.info(f"Channel {channel_id} existing context: {existing_context_id}")
        logger.info(f"All stored contexts: {channel_contexts}")
        
        # Create the message using official SDK types
        text_part = TextPart(text=input)
        message = A2AMessage(
            messageId=str(uuid.uuid4()),
            role=Role.user,
            parts=[text_part],
            contextId=existing_context_id  # Use existing context if available
        )
        
        # Create the request parameters
        params = MessageSendParams(message=message)
        
        # Create the request
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=params
        )
        
        logger.info(f"Invoking agent for channel {channel_id} with context: {existing_context_id}")
        
        # Send the message
        response = await a2a_client.send_message(request)
        
        logger.info(f"Received response from agent")
        
        # Extract text from response
        # response.root is the SendMessageSuccessResponse directly
        
        # Check if this is an error response
        if hasattr(response.root, 'error') and response.root.error:
            return f"Agent returned error: {response.root.error.message}"
        
        # Check if this is a success response with result
        if hasattr(response.root, 'result') and response.root.result:
            result = response.root.result
            
            # Extract and store contextId for session continuity
            logger.info(f"Result type: {type(result)}")
            logger.info(f"Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            
            # Try to access contextId directly (Task uses context_id in Python, contextId in JSON)
            try:
                context_id = getattr(result, 'context_id', None)  # Use snake_case for Python attribute
                logger.info(f"Result contextId via getattr (context_id): {context_id}")
            except Exception as e:
                logger.error(f"Error accessing context_id: {e}")
                context_id = None
            
            if context_id:
                logger.info(f"Storing contextId {context_id} for channel {channel_id}")
                channel_contexts[channel_id] = context_id
                logger.info(f"Updated contexts: {channel_contexts}")
            elif hasattr(result, 'id') and result.id:
                # Fallback: use task/message ID if no contextId
                logger.info(f"Using task/message ID {result.id} as context for channel {channel_id}")
                channel_contexts[channel_id] = result.id
                logger.info(f"Updated contexts: {channel_contexts}")
            else:
                logger.warning(f"No contextId or id found in result to store for session continuity")
            
            # Check if it's a task with artifacts
            if hasattr(result, 'artifacts') and result.artifacts:
                extracted_texts = []
                for artifact in result.artifacts:
                    if hasattr(artifact, 'parts') and artifact.parts:
                        for part in artifact.parts:
                            # Part is a RootModel, so we need to access .root first
                            actual_part = part.root
                            if hasattr(actual_part, 'text'):
                                extracted_texts.append(actual_part.text)
                
                final_text = "".join(extracted_texts)
                logger.info(f"Extracted {len(extracted_texts)} text parts from {len(result.artifacts)} artifacts")
                return final_text
            
            # Check if it's a direct message response
            elif hasattr(result, 'parts') and result.parts:
                return "".join(
                    part.root.text
                    for part in result.parts
                    if hasattr(part.root, 'text')
                )
            
            # Fallback to string representation
            else:
                logger.warning(f"Unexpected result format: {type(result)}")
                return str(result)
        else:
            logger.warning("No result found in response")
        
        return "No response received from agent"


def register_handlers(bot: commands.Bot):
    """
    Register the message listener and control behavior via env vars:
    - MENTION_ONLY=true: respond only when mentioned
    - CHANNEL_ONLY=ID1,ID2: only respond in specific channels
    
    Session Management:
    - Maintains conversation context per Discord channel
    - Use !reset, !clear, or !new to start a fresh conversation
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

        # Check for session reset command
        if content.lower() in ['!reset', '!clear', '!new']:
            if channel_id in channel_contexts:
                del channel_contexts[channel_id]
                await message.reply("🔄 Session context cleared. Starting fresh conversation.")
                logger.info(f"Cleared context for channel {channel_id}")
            else:
                await message.reply("ℹ️ No active session to clear.")
            return

        kagent_a2a_url = os.getenv("KAGENT_A2A_URL")
        if not kagent_a2a_url:
            await message.reply("⚠️ Missing `KAGENT_A2A_URL` in `.env`.")
            return

        try:
            await message.channel.typing()
            response = await invoke_a2a_agent(kagent_a2a_url, content, channel_id)

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
