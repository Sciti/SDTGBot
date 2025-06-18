from __future__ import annotations

from config import settings

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base

__all__ = ["engine", "async_session_factory", "AsyncSession", "Base"]

metadata = MetaData()

DB_DSN = settings.DB_DSN

engine: AsyncEngine = create_async_engine(
    DB_DSN,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
