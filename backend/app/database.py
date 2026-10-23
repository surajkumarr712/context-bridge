"""Database engine, session factory, and FastAPI session dependency."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://contextbridge:contextbridge_dev@localhost:5432/contextbridge"
)


class Base(DeclarativeBase):
    """Base class from which every SQLAlchemy table model inherits."""


def database_url() -> str:
    """Read the connection string at call time so tools can override it."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


engine = create_engine(database_url(), pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Provide one database session for the lifetime of one HTTP request."""
    with SessionFactory() as session:
        yield session

