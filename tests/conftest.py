from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.database import get_db
from app.main import app

TEST_DB_PATH = Path(__file__).parent / "test.db"
ASYNC_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
SYNC_DB_URL = f"sqlite:///{TEST_DB_PATH}"


def run_alembic_upgrade():
    """Run Alembic migrations on the test database synchronously."""
    alembic_cfg = AlembicConfig(Path(__file__).parent.parent / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", SYNC_DB_URL)
    alembic_upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Session-scoped: create test DB, run Alembic migrations, clean up."""
    # Remove stale test database if exists
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # Run Alembic migrations
    run_alembic_upgrade()

    yield

    # Cleanup
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Session-scoped async engine for the test database."""
    engine = create_async_engine(
        ASYNC_DB_URL, echo=False, poolclass=NullPool
    )
    yield engine
    await engine.dispose()





@pytest_asyncio.fixture
async def session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Per-test fixture: wraps each test in a transaction that is rolled back.
    This gives full isolation without re-running migrations.
    """
    connection = await async_engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Per-test fixture: FastAPI test client with overridden DB dependency."""

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
