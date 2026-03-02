# Dotwarf API

Backend for the [Dotwarf](https://dotwarf.com) agency website. Built with **FastAPI**, async SQLAlchemy, LiteLLM, and aiosmtplib.

## Features

- **AI chat widget** — powered by LiteLLM (drop-in support for OpenAI, Anthropic, Groq, etc.)
- **Contact form** — stores leads in PostgreSQL and sends a Gmail notification email
- **Lead management** — admin endpoint to list and inspect submitted leads
- **Rate limiting** — per-IP limits on chat and contact routes via slowapi
- **Async throughout** — async SQLAlchemy + asyncpg, async SMTP, async LiteLLM

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Docker & Docker Compose (for Postgres)

## Quick start

```bash
# 1. Start the database
docker compose up db -d

# 2. Set up your environment
cp api/.env.example api/.env
# Edit api/.env with your values (see Environment Variables below)

# 3. Install dependencies
cd api
uv sync

# 4. Run the dev server
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## Project structure

```
api/
├── app/
│   ├── main.py                  # App factory, lifespan, middleware
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   └── database.py          # Async engine, session factory, get_db
│   ├── models/
│   │   └── lead.py              # Lead SQLAlchemy model
│   ├── schemas/
│   │   ├── chat.py              # ChatRequest / ChatResponse
│   │   └── lead.py              # ContactFormCreate / LeadRead
│   ├── repositories/
│   │   └── lead_repository.py   # DB access layer
│   ├── services/
│   │   └── lead_service.py      # Business logic + email notification
│   └── api/v1/
│       ├── router.py
│       └── endpoints/
│           ├── chat.py          # POST /api/v1/chat/
│           ├── contact.py       # POST /api/v1/contact/
│           └── leads.py         # GET  /api/v1/leads/  (admin)
├── main.py                      # Uvicorn entrypoint
└── pyproject.toml
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | — | Health check |
| `POST` | `/api/v1/chat/` | — | AI chat widget (rate-limited) |
| `POST` | `/api/v1/contact/` | — | Submit contact form (rate-limited) |
| `GET` | `/api/v1/leads/` | `X-Admin-Key` | List all leads |
| `GET` | `/api/v1/leads/{id}` | `X-Admin-Key` | Get a single lead |

### `POST /api/v1/chat/`

```json
{
  "messages": [
    { "role": "user", "content": "What services do you offer?" }
  ]
}
```

Response:

```json
{ "reply": "We specialize in AI chatbots, agents, workflow automations…" }
```

### `POST /api/v1/contact/`

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "company": "Acme Inc.",
  "service_interest": "chatbot",
  "budget_range": "5k_15k",
  "timeline": "1_month",
  "message": "We need a customer support chatbot for our e-commerce store."
}
```

**`service_interest` options:** `chatbot`, `agent`, `workflow_automation`, `model_finetuning`, `website`, `api_development`, `freelance_hourly`, `other`

**`budget_range` options:** `under_1k`, `1k_5k`, `5k_15k`, `15k_plus`, `not_sure`

**`timeline` options:** `asap`, `1_month`, `3_months`, `flexible`

### `GET /api/v1/leads/`

Requires the `X-Admin-Key` header matching `ADMIN_API_KEY` in your `.env`.

```bash
curl http://localhost:8000/api/v1/leads/ \
  -H "X-Admin-Key: your-admin-key"
```

Supports `?skip=0&limit=50` query parameters.

## Environment variables

Copy `api/.env.example` to `api/.env` and fill in your values.

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable SQLAlchemy query logging |
| `ADMIN_API_KEY` | `change-me-in-production` | Key for the admin leads endpoint |
| `DATABASE_URL` | `postgresql+asyncpg://dotwarf:dotwarf@localhost:5432/dotwarf` | Async Postgres connection string |
| `LITELLM_MODEL` | `openai/gpt-4o-mini` | Any model string supported by LiteLLM |
| `OPENAI_API_KEY` | — | API key for your LLM provider |
| `AI_SYSTEM_PROMPT` | *(built-in)* | System prompt for the chat widget |
| `CHAT_RATE_LIMIT` | `20/hour` | Per-IP limit for the chat endpoint |
| `CONTACT_RATE_LIMIT` | `5/hour` | Per-IP limit for the contact endpoint |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port (STARTTLS) |
| `SMTP_USERNAME` | — | Gmail address |
| `SMTP_PASSWORD` | — | [Gmail App Password](https://myaccount.google.com/apppasswords) |
| `SMTP_FROM_EMAIL` | — | Sender address in notification emails |
| `CONTACT_RECIPIENT_EMAIL` | — | Your inbox for lead notifications |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | JSON list of allowed origins |

> **Gmail App Password:** go to Google Account → Security → 2-Step Verification → App passwords. Use that 16-character password as `SMTP_PASSWORD`. Do not use your regular Gmail password.

## Running with Docker Compose

```bash
# Build and start everything (Postgres + API)
docker compose up --build

# Postgres only (useful when running the API locally)
docker compose up db -d
```

The `docker-compose.yml` at the project root defines both services. The `DATABASE_URL` is automatically set to point to the Compose Postgres service; all other env vars are loaded from `api/.env`.

## Switching LLM providers

LiteLLM supports 100+ providers with no code changes — just update `.env`:

```env
# Anthropic
LITELLM_MODEL=anthropic/claude-3-haiku-20240307

# Groq
LITELLM_MODEL=groq/llama3-8b-8192

# Local Ollama
LITELLM_MODEL=ollama/llama3
```

Set the appropriate API key env var for your chosen provider (`ANTHROPIC_API_KEY`, `GROQ_API_KEY`, etc.).

## Database migrations

Tables are created automatically on startup (via SQLAlchemy metadata) for convenience during development. For production, use Alembic (already installed):

```bash
cd api

# Initialize (first time only)
uv run alembic init alembic

# Generate a migration after model changes
uv run alembic revision --autogenerate -m "describe change"

# Apply migrations
uv run alembic upgrade head
```
