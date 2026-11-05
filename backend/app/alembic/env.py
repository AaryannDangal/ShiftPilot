"""Alembic environment configuration for ShiftPilot."""
import sys
import os
from logging.config import dictConfig

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.database import Base
from app.config import settings

config = context.config

# Logging configuration
dictConfig({
    "version": 1,
    "formatters": {"default": {"format": "%(levelname)s %(asctime)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"level": "INFO", "handlers": ["console"]},
})

target_metadata = Base.metadata


def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
