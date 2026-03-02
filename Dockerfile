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

# Install Python dependencies inside /app/api so the venv lives next to the source.
# UV_PYTHON_PREFERENCE=only-system forces uv to use the image's own Python
# instead of downloading/symlinking a uv-managed Python. Without this, the
# venv symlinks point to a host path that doesn't exist in the container,
# causing uv to silently nuke and rebuild the venv on every `uv run` call
# (including the Railway pre-deploy migration command).
WORKDIR /app/api
COPY api/pyproject.toml api/uv.lock ./
RUN UV_PYTHON_PREFERENCE=only-system uv sync --frozen --no-dev

# Copy API source (includes alembic.ini and migrations/)
COPY api/ ./

# Copy frontend assets one level up (PROJECT_ROOT = /app)
COPY index.html /app/
COPY --from=css-builder /build/static /app/static/

EXPOSE 8000

# UV_PYTHON_PREFERENCE=only-system keeps uv from re-resolving the venv at runtime.
CMD ["sh", "-c", "UV_PYTHON_PREFERENCE=only-system uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
