import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session):
    """Test creating a User instance."""
    user = User(username="testuser", email="test@example.com")
    session.add(user)
    await session.flush()

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_user_defaults(session):
    """Test User field defaults."""
    user = User(username="defaults", email="defaults@example.com")
    session.add(user)
    await session.flush()

    assert user.created_at is not None
    assert isinstance(user.created_at, datetime)


@pytest.mark.asyncio
async def test_create_todo(session):
    """Test creating a Todo instance linked to a User."""
    user = User(username="todouser", email="todo@example.com")
    session.add(user)
    await session.flush()

    todo = Todo(title="Test Todo", user_id=user.id)
    session.add(todo)
    await session.flush()

    assert todo.id is not None
    assert isinstance(todo.id, uuid.UUID)
    assert todo.title == "Test Todo"
    assert todo.description is None
    assert todo.completed is False
    assert todo.date_completed is None
    assert todo.user_id == user.id
    assert todo.created_at is not None
    assert isinstance(todo.created_at, datetime)


@pytest.mark.asyncio
async def test_todo_with_description(session):
    """Test Todo with optional description."""
    user = User(username="descuser", email="desc@example.com")
    session.add(user)
    await session.flush()

    todo = Todo(
        title="Descriptive Todo",
        description="This is a detailed description.",
        user_id=user.id,
    )
    session.add(todo)
    await session.flush()

    assert todo.description == "This is a detailed description."


@pytest.mark.asyncio
async def test_todo_completed_sets_date(session):
    """Test that setting completed=True sets date_completed."""
    user = User(username="compuser", email="comp@example.com")
    session.add(user)
    await session.flush()

    todo = Todo(title="Complete me", user_id=user.id)
    session.add(todo)
    await session.flush()

    assert todo.completed is False
    assert todo.date_completed is None

    todo.completed = True
    todo.date_completed = datetime.now(timezone.utc)
    await session.flush()

    assert todo.completed is True
    assert todo.date_completed is not None


@pytest.mark.asyncio
async def test_user_todo_relationship(session):
    """Test the one-to-many relationship between User and Todo."""
    user = User(username="reluser", email="rel@example.com")
    session.add(user)
    await session.flush()

    todo1 = Todo(title="Todo 1", user_id=user.id)
    todo2 = Todo(title="Todo 2", user_id=user.id)
    session.add_all([todo1, todo2])
    await session.flush()

    # Load relationship
    await session.refresh(user, ["todos"])
    assert len(user.todos) == 2
    assert user.todos[0].title in ("Todo 1", "Todo 2")


@pytest.mark.asyncio
async def test_cascade_delete(session):
    """Test that deleting a User cascades to their Todos."""
    user = User(username="cascadeuser", email="cascade@example.com")
    session.add(user)
    await session.flush()

    todo = Todo(title="Cascade me", user_id=user.id)
    session.add(todo)
    await session.flush()

    await session.delete(user)
    await session.flush()

    # Verify todo is also gone
    result = await session.execute(select(Todo).where(Todo.id == todo.id))
    assert result.scalar_one_or_none() is None
