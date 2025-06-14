import os
import logging
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands
from handlers import register_handlers

load_dotenv()

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True  # si tu veux lire les messages

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f"✅ Bot logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()
    logging.info("✅ Slash commands synced.")

# Enregistre tes handlers custom (slash commands, etc.)
register_handlers(bot)

def main():
    logging.info("🚀 Starting Discord bot...")
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    main()
