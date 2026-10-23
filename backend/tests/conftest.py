"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.project import ProjectRecord

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionFactory = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)
Base.metadata.create_all(test_engine)


@pytest.fixture
def db() -> Iterator[Session]:
    """Provide a fresh database session and remove rows after each test."""
    with TestSessionFactory() as session:
        yield session
    with TestSessionFactory.begin() as cleanup_session:
        cleanup_session.execute(delete(ProjectRecord))


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    """Provide a client that calls the ASGI app without a real server."""
    def override_get_db() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

