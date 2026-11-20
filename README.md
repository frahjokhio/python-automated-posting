# Python Automated Multi-Platform Posting

FastAPI service that publishes a short CTA message to **Dev.to**, **Mastodon**, **Bluesky**, **Telegram**, and **Discord**.

Runs entirely with **Docker** — no local Python install required.

## Requirements

- Docker Desktop
- Docker Compose

## Quick start

```bash
# From the project root
copy .env.example .env
docker compose up --build
```

- API: http://localhost:4000
- Interactive docs: http://localhost:4000/docs

`DRY_RUN=true` is the default. In dry-run mode the API validates the message and returns realistic success results **without** calling third-party APIs.

## Sample request

```bash
curl -X POST http://localhost:4000/posting ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Check out our latest business platform and grow your online visibility. https://example.com\"}"
```

### Sample dry-run response

```json
{
  "success": true,
  "results": [
    {
      "platform": "Dev.to",
      "status": "success",
      "posted_url": "https://example.com/dry-run/devto",
      "public_access": true,
      "date": "2026-11-17",
      "time": "10:36:54",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://example.com/dry-run/mastodon",
      "public_access": true,
      "date": "2026-11-17",
      "time": "10:36:54",
      "error": null
    },
    {
      "platform": "Bluesky",
      "status": "success",
      "posted_url": "https://example.com/dry-run/bluesky",
      "public_access": true,
      "date": "2026-11-17",
      "time": "10:36:54",
      "error": null
    },
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://example.com/dry-run/telegram",
      "public_access": true,
      "date": "2026-11-17",
      "time": "10:36:54",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://example.com/dry-run/discord",
      "public_access": true,
      "date": "2026-11-17",
      "time": "10:36:54",
      "error": null
    }
  ]
}
```

## Demonstration log

Captured from a local dry-run (`DRY_RUN=true`) on 2026-11-17:

```text
POST http://localhost:4000/posting
Content-Type: application/json

Request:
{"message":"Check out our latest business platform and grow online. https://example.com"}

Result: HTTP 200
success=true
platforms=Dev.to, Mastodon, Bluesky, Telegram, Discord
all status=success (dry-run URLs under https://example.com/dry-run/...)

Tests: docker compose run --rm api pytest -q
Output: 7 passed
```

## Input validation

| Rule | Detail |
|---|---|
| Length | Message max **200** characters |
| CTA | Exactly **one** `http://` or `https://` URL |
| URL | Must be a valid URL |

Invalid input returns HTTP **422** with validation details.

## Environment variables

Copy `.env.example` to `.env` and fill values when you have real accounts:

| Variable | Platform |
|---|---|
| `DRY_RUN` | `true` / `false` |
| `DEVTO_API_KEY` | Dev.to |
| `MASTODON_BASE_URL` | Mastodon instance URL |
| `MASTODON_ACCESS_TOKEN` | Mastodon |
| `BLUESKY_HANDLE` | Bluesky handle |
| `BLUESKY_APP_PASSWORD` | Bluesky app password |
| `TELEGRAM_BOT_TOKEN` | Telegram bot |
| `TELEGRAM_CHAT_ID` | Telegram chat/channel |
| `DISCORD_WEBHOOK_URL` | Discord webhook |

Never commit real API keys. `.env` is gitignored.

### Switching to live posting

1. Create accounts and add credentials to `.env`
2. Set `DRY_RUN=false`
3. Restart: `docker compose up --build`

When dry-run is off and a platform key is missing, that platform returns `status: failed` with `"Missing credentials"` while others continue.

## Project structure

```text
python-automated-posting/
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   ├── platforms/
│   └── services/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## Run tests

```bash
docker compose run --rm api pytest -q
```

## Notes for reviewers

- Platform selection is internal; the client only sends `message`.
- Each platform is handled independently; one failure does not stop the rest.
- Dry-run demo log is included above. Live post screenshots can be added after real credentials are configured.
