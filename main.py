import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from handlers import register_handlers

load_dotenv()

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f"✅ Bot logged in as {bot.user} (ID: {bot.user.id})")

register_handlers(bot)

def main():
    logging.info("🚀 Starting Discord bot...")
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    main()
