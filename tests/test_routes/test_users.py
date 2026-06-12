import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"username": "alice", "email": "alice@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_user_duplicate(client: AsyncClient):
    # Create once
    await client.post(
        "/users/",
        json={"username": "bob", "email": "bob@example.com"},
    )
    # Duplicate username
    response = await client.post(
        "/users/",
        json={"username": "bob", "email": "bob2@example.com"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_users_empty(client: AsyncClient):
    response = await client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["users"] == []


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient):
    # Create a user
    await client.post(
        "/users/",
        json={"username": "charlie", "email": "charlie@example.com"},
    )
    response = await client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient):
    create_resp = await client.post(
        "/users/",
        json={"username": "dave", "email": "dave@example.com"},
    )
    user_id = create_resp.json()["id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "dave"


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get(f"/users/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient):
    create_resp = await client.post(
        "/users/",
        json={"username": "eve", "email": "eve@example.com"},
    )
    user_id = create_resp.json()["id"]

    response = await client.put(
        f"/users/{user_id}",
        json={"username": "eve_updated", "email": "eve_new@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "eve_updated"
    assert response.json()["email"] == "eve_new@example.com"


@pytest.mark.asyncio
async def test_update_user_not_found(client: AsyncClient):
    response = await client.put(
        f"/users/{uuid.uuid4()}",
        json={"username": "ghost", "email": "ghost@example.com"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    create_resp = await client.post(
        "/users/",
        json={"username": "frank", "email": "frank@example.com"},
    )
    user_id = create_resp.json()["id"]

    response = await client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found(client: AsyncClient):
    response = await client.delete(f"/users/{uuid.uuid4()}")
    assert response.status_code == 404
