# ── Stage 1: build Tailwind CSS ─────────────────────────────────────────────
FROM node:22-alpine AS css-builder

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

COPY tailwind.config.js ./
COPY static/css/input.css ./static/css/input.css
COPY index.html ./

RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify


# ── Stage 2: Python app ──────────────────────────────────────────────────────
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies inside /app/api so the venv lives next to the source
WORKDIR /app/api
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy API source
COPY api/ ./

# Copy frontend assets one level up (PROJECT_ROOT = /app)
COPY index.html /app/
COPY --from=css-builder /build/static /app/static/

EXPOSE 8000

# Run from /app/api so `from app.xxx` imports resolve correctly
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
