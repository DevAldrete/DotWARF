# Dotwarf

Website and backend for **Dotwarf**, a digital agency specializing in AI-powered solutions.

## Services

- AI chatbots and agents
- Workflow automations
- Model fine-tuning and training
- Website and API development
- Freelance / hourly projects

## Stack

| Layer | Tech |
|-------|------|
| Frontend | HTML, [Tailwind CSS v4](https://tailwindcss.com), [Alpine.js](https://alpinejs.dev), [HTMX](https://htmx.org) |
| Backend | [FastAPI](https://fastapi.tiangolo.com), async SQLAlchemy, [LiteLLM](https://docs.litellm.ai) |
| Database | PostgreSQL (via Docker) |
| Package manager | [uv](https://docs.astral.sh/uv/) (Python), npm (CSS build) |

## Structure

```
dotwarf/
├── api/                # FastAPI backend (see api/README.md)
├── static/             # Compiled CSS and JS assets
├── templates/          # HTML templates
├── index.html          # Entry point
├── tailwind.config.js
└── docker-compose.yml  # Postgres + API services
```

## Getting started

**Prerequisites:** Node.js, Python 3.13+, uv, Docker

```bash
# 1. Start Postgres
docker compose up db -d

# 2. Set up the API
cp api/.env.example api/.env   # fill in your values
cd api && uv sync && uv run uvicorn app.main:app --reload

# 3. Watch Tailwind CSS (separate terminal)
npm install && npm run dev
```

- Frontend: open `index.html` directly or serve with any static file server
- API + docs: `http://localhost:8000/docs`

See [`api/README.md`](api/README.md) for full backend documentation.
