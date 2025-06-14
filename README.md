
# A2A Discord Bot Template

This is a simple template for a **Discord bot** using [A2A](https://github.com/google/A2A) to connect with [kagent](https://github.com/kagent-dev/kagent).

> 🌀 Forked and reworked from the original [Slack bot template](https://github.com/kagent-dev/a2a-slack-template)  
> Now fully adapted for Discord via [discord.py](https://github.com/Rapptz/discord.py)

GitHub: [https://github.com/lekkerelou/kagent-a2a-discord](https://github.com/lekkerelou/kagent-a2a-discord)

---

## ⚙️ Setup

1. Clone the repo:

```bash
git clone https://github.com/lekkerelou/kagent-a2a-discord.git
cd kagent-a2a-discord
```

2. Create a virtual environment:

```bash
uv venv
```

3. Install dependencies:

```bash
uv sync
```

---

## 🧪 Configuration

Copy the env template and fill in your tokens:

```bash
cp .env.example .env
```

### Required ENV vars:

| Variable         | Description                                    |
|------------------|------------------------------------------------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token                       |
| `KAGENT_A2A_URL`     | URL of your A2A agent endpoint               |
| `DISCORD_MENTION_ONLY`       | (optional) Set to `true` to respond only when mentioned |
| `DISCORD_CHANNEL_ONLY`       | (optional) Comma-separated list of allowed channel IDs |

---

## 🚀 Run the bot

```bash
uv run main.py
```

Or with Python:

```bash
python main.py
```

---

## 🐳 Docker

Build & run:

```bash
docker build -t a2a-discord-bot .
docker run --env-file .env a2a-discord-bot
```

---

## 📡 Behavior

- Bot listens to messages in channels
- Responds to any text unless restricted via `DISCORD_MENTION_ONLY` or `DISCORD_CHANNEL_ONLY`
- Sends reply back with output from your A2A agent

---

## 🧠 Powered by

- [Discord.py](https://github.com/Rapptz/discord.py)
- [Kagent](https://github.com/kagent-dev/kagent)
- [A2A](https://github.com/google/A2A)
