import uuid

import pytest
from pydantic import ValidationError

from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.schemas.user import UserCreate, UserResponse


class TestUserSchemas:
    def test_user_create_valid(self):
        data = UserCreate(username="john", email="john@example.com")
        assert data.username == "john"
        assert data.email == "john@example.com"

    def test_user_create_missing_email(self):
        with pytest.raises(ValidationError):
            UserCreate(username="john")

    def test_user_create_missing_username(self):
        with pytest.raises(ValidationError):
            UserCreate(email="john@example.com")

    def test_user_response_from_orm(self):
        data = UserResponse(
            id=uuid.uuid4(),
            username="john",
            email="john@example.com",
            created_at="2024-01-01T00:00:00Z",
        )
        assert data.id is not None
        assert isinstance(data.id, uuid.UUID)


class TestTodoSchemas:
    def test_todo_create_valid(self):
        data = TodoCreate(
            title="Test Todo", user_id=uuid.uuid4()
        )
        assert data.title == "Test Todo"
        assert data.description is None
        assert data.completed is False

    def test_todo_create_with_description(self):
        data = TodoCreate(
            title="Test",
            description="A description",
            user_id=uuid.uuid4(),
        )
        assert data.description == "A description"

    def test_todo_create_missing_title(self):
        with pytest.raises(ValidationError):
            TodoCreate(user_id=uuid.uuid4())

    def test_todo_update_partial(self):
        data = TodoUpdate(completed=True)
        assert data.completed is True
        assert data.title is None
        assert data.description is None

    def test_todo_update_empty(self):
        data = TodoUpdate()
        assert data.title is None
        assert data.description is None
        assert data.completed is None

    def test_todo_response_from_orm(self):
        data = TodoResponse(
            id=uuid.uuid4(),
            title="Test",
            user_id=uuid.uuid4(),
            created_at="2024-01-01T00:00:00Z",
        )
        assert data.title == "Test"
        assert data.description is None
        assert data.completed is False
