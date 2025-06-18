# SDTGBot
Telegram bot for SteamDeck telegram channel & chat https://t.me/steamdecksru

## Description

SDTGBot lets admins compose, schedule and post news about Steam games to several Telegram groups or channels. Posts can be created from templates with predefined buttons linking to Steam, SteamDB and ProtonDB.

## Running with Docker

Create a `.env` file in the project root and define environment variables used by `settings.py` such as `BOT_TOKEN` and optionally `DB_DSN`.

Build and run the services with docker compose:

```bash
docker compose up --build
```

This will start the bot, Redis broker, PostgreSQL database and a background worker.

All services are connected to a custom Docker network `sd_net`. Each container is
also reachable via an alias prefixed with `sd_` (for example `sd_db` for the
database and `sd_bot` for the bot container).
