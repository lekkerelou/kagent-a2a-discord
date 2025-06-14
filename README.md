# A2A Slack Bot Template

This is a simple template for a Slack bot that uses [A2A](https://github.com/google/A2A) to connect to [kagent](https://github.com/kagent-dev/kagent).

Follow along with the [Integrating kagent with Slack](https://kagent.dev/docs/examples/slack-a2a) article for a complete walkthrough.

## Setup

1. Clone the repository

```bash
git clone https://github.com/kagent-dev/a2a-slack-template.git
```

2. Create a virtual environment

```bash
uv venv
```

3. Install the dependencies

```bash
uv sync
```

## Configuration

The bot is configured using environment variables. Make a copy of the `.env.example` file and fill in the values.

```bash
cp .env.example .env
```

## Running the bot

```bash
uv run main.py
```
