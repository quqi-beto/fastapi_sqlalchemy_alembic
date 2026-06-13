import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoUpdate


async def create_todo(db: AsyncSession, todo_data: TodoCreate) -> Todo:
    """Create a new todo, verifying the referenced user exists."""
    result = await db.execute(select(User).where(User.id == todo_data.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        user_id=todo_data.user_id,
    )
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


async def get_todos(
    db: AsyncSession, user_id: uuid.UUID | None = None
) -> tuple[list[Todo], int]:
    """Return all todos (optionally filtered by user_id), ordered by creation date descending."""
    query = select(Todo).order_by(Todo.created_at.desc())
    if user_id:
        query = query.where(Todo.user_id == user_id)
    result = await db.execute(query)
    todos = result.scalars().all()
    return todos, len(todos)


async def get_todo_by_id(db: AsyncSession, todo_id: uuid.UUID) -> Todo:
    """Return a single todo by ID, or raise 404."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo


async def update_todo(
    db: AsyncSession, todo_id: uuid.UUID, todo_data: TodoUpdate
) -> Todo:
    """Partially update a todo (title, description, completed)."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.description is not None:
        todo.description = todo_data.description
    if todo_data.completed is not None:
        todo.completed = todo_data.completed
        todo.date_completed = (
            datetime.now(timezone.utc) if todo_data.completed else None
        )

    await db.commit()
    await db.refresh(todo)
    return todo


async def delete_todo(db: AsyncSession, todo_id: uuid.UUID) -> None:
    """Delete a todo by ID, or raise 404."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    await db.delete(todo)
    await db.commit()
