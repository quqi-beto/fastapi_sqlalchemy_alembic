import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_db_connection(session: AsyncSession):
    """Test that we can execute a raw query against the test DB."""
    result = await session.execute(text("SELECT 1"))
    value = result.scalar()
    assert value == 1


@pytest.mark.asyncio
async def test_tables_exist(session: AsyncSession):
    """Test that Alembic created the expected tables."""
    result = await session.execute(
        text(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name IN ('users', 'todos') "
            "ORDER BY name"
        )
    )
    tables = result.scalars().all()
    assert tables == ["todos", "users"]


@pytest.mark.asyncio
async def test_table_columns_users(session: AsyncSession):
    """Test that users table has expected columns."""
    result = await session.execute(
        text("PRAGMA table_info(users)")
    )
    columns = {row.name: row.type for row in result.fetchall()}
    assert "id" in columns
    assert "username" in columns
    assert "email" in columns
    assert "created_at" in columns


@pytest.mark.asyncio
async def test_table_columns_todos(session: AsyncSession):
    """Test that todos table has expected columns."""
    result = await session.execute(
        text("PRAGMA table_info(todos)")
    )
    columns = {row.name: row.type for row in result.fetchall()}
    assert "id" in columns
    assert "title" in columns
    assert "description" in columns
    assert "completed" in columns
    assert "date_completed" in columns
    assert "user_id" in columns
    assert "created_at" in columns
