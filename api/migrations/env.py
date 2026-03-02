"""Alembic env.py – async-compatible, reads DATABASE_URL from environment."""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Alembic config ────────────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Pull DATABASE_URL from the environment (overrides alembic.ini) ────────────
# asyncpg is used at runtime, but Alembic's autogenerate needs the async URL too.
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Fall back to pydantic-settings so local .env is respected
    from app.core.config import get_settings

    database_url = get_settings().DATABASE_URL

# Railway (and most PaaS) provide a plain postgresql:// URL.
# Normalise to the asyncpg dialect so Alembic never falls back to psycopg2.
database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Alembic requires the async driver prefix for async engines
config.set_main_option("sqlalchemy.url", database_url)

# ── Import all models so autogenerate can detect them ────────────────────────
from app.core.database import Base  # noqa: E402
import app.models.lead  # noqa: E402, F401 – registers Lead model on Base.metadata

target_metadata = Base.metadata


# ── Offline mode (generates SQL without connecting) ──────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (async) ───────────────────────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Fail fast if DB is unreachable instead of hanging indefinitely
        connect_args={"timeout": 30},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
