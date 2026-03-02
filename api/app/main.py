import logging
import subprocess
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ── Logging (must run before any logger.xxx calls) ────────────────────────────
configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

# ── Rate limiter (shared instance) ────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/day", "60/hour"])


# ── Lifespan ──────────────────────────────────────────────────────────────────
def _run_migrations() -> None:
    """Run Alembic migrations before the app accepts traffic.

    Executed as a subprocess so the migration environment is fully isolated
    from the running application (separate engine, separate connection).
    """
    logger.info("Running database migrations …")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).resolve().parents[1],  # /app/api
        capture_output=True,
        text=True,
    )
    if result.stdout:
        logger.info("alembic stdout: %s", result.stdout.strip())
    if result.returncode != 0:
        logger.error("alembic stderr: %s", result.stderr.strip())
        raise RuntimeError(
            f"Alembic migration failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    logger.info("Migrations complete.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    _run_migrations()
    logger.info("Ready.")
    yield
    logger.info("Shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Backend API for the Dotwarf agency website.",
    # Disable interactive docs in production to reduce attack surface
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)

# Trusted host (production only — Railway terminates TLS at the edge,
# so HTTPSRedirectMiddleware is not used; it would block internal
# healthcheck probes which arrive over plain HTTP).
if not settings.DEBUG:
    # Always include healthcheck.railway.app so Railway's health probe (which
    # originates from that hostname) is not rejected with a 400.
    allowed_hosts = list(settings.ALLOWED_HOSTS)
    if "healthcheck.railway.app" not in allowed_hosts and "*" not in allowed_hosts:
        allowed_hosts.append("healthcheck.railway.app")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static assets (/static/css/output.css, /static/js/…)
app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "static"), name="static")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


# ── Frontend catch-all (must be last) ─────────────────────────────────────────
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str) -> FileResponse:
    return FileResponse(PROJECT_ROOT / "index.html")
