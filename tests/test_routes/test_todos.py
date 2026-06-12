import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    # Create a user first
    user_resp = await client.post(
        "/users/",
        json={"username": "todo_user", "email": "todo_user@example.com"},
    )
    user_id = user_resp.json()["id"]

    response = await client.post(
        "/todos/",
        json={"title": "Buy milk", "user_id": user_id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["description"] is None
    assert data["completed"] is False
    assert data["date_completed"] is None
    assert data["user_id"] == user_id
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_todo_missing_user(client: AsyncClient):
    response = await client.post(
        "/todos/",
        json={"title": "Orphan todo", "user_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_todos(client: AsyncClient):
    user_resp = await client.post(
        "/users/",
        json={"username": "list_user", "email": "list_user@example.com"},
    )
    user_id = user_resp.json()["id"]

    await client.post(
        "/todos/", json={"title": "Todo 1", "user_id": user_id}
    )
    await client.post(
        "/todos/", json={"title": "Todo 2", "user_id": user_id}
    )

    response = await client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_get_todos_filter_by_user(client: AsyncClient):
    user_resp = await client.post(
        "/users/",
        json={"username": "filter_user", "email": "filter_user@example.com"},
    )
    user_id = user_resp.json()["id"]

    await client.post(
        "/todos/", json={"title": "Filtered todo", "user_id": user_id}
    )

    response = await client.get(f"/todos/?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["todos"][0]["user_id"] == user_id


@pytest.mark.asyncio
async def test_get_todo_by_id(client: AsyncClient):
    user_resp = await client.post(
        "/users/",
        json={"username": "get_user", "email": "get_user@example.com"},
    )
    user_id = user_resp.json()["id"]

    create_resp = await client.post(
        "/todos/",
        json={"title": "Specific todo", "user_id": user_id},
    )
    todo_id = create_resp.json()["id"]

    response = await client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific todo"


@pytest.mark.asyncio
async def test_get_todo_not_found(client: AsyncClient):
    response = await client.get(f"/todos/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient):
    user_resp = await client.post(
        "/users/",
        json={"username": "upd_user", "email": "upd_user@example.com"},
    )
    user_id = user_resp.json()["id"]

    create_resp = await client.post(
        "/todos/",
        json={"title": "Update me", "user_id": user_id},
    )
    todo_id = create_resp.json()["id"]

    response = await client.put(
        f"/todos/{todo_id}",
        json={"title": "Updated!", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated!"
    assert data["completed"] is True
    assert data["date_completed"] is not None


@pytest.mark.asyncio
async def test_update_todo_not_found(client: AsyncClient):
    response = await client.put(
        f"/todos/{uuid.uuid4()}",
        json={"title": "Ghost"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient):
    user_resp = await client.post(
        "/users/",
        json={"username": "del_user", "email": "del_user@example.com"},
    )
    user_id = user_resp.json()["id"]

    create_resp = await client.post(
        "/todos/",
        json={"title": "Delete me", "user_id": user_id},
    )
    todo_id = create_resp.json()["id"]

    response = await client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/todos/{todo_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo_not_found(client: AsyncClient):
    response = await client.delete(f"/todos/{uuid.uuid4()}")
    assert response.status_code == 404
