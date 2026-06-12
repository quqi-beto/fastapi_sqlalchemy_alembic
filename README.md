# FastAPI To Do API — Async SQLAlchemy + Alembic

A production-ready To Do API built with **FastAPI**, **async SQLAlchemy**, and **Alembic** for database migrations. Users can create, update, and delete to-do items, with each user having many to-dos.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (async) |
| Database Driver | `asyncpg` (production), `aiosqlite` (tests) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Project Mgmt | [uv](https://docs.astral.sh/uv/) |
| Testing | pytest, pytest-asyncio, httpx |

## Features

- Full CRUD for **Users** and **Todos**
- One-to-many relationship: each user has many todos
- Cascade delete: deleting a user removes all their todos
- Auto-set `date_completed` when a todo is marked done
- Filter todos by user
- Async database operations end-to-end
- Alembic migrations for schema management (dev, test, and prod)
- Comprehensive test suite using SQLite + Alembic

## Project Structure

```
├── alembic/
│   ├── versions/
│   │   └── 2b7cd17bfd4e_add_user_and_todo_tables.py
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── todos.py
│   │   └── users.py
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── test_routes/
│   │   ├── __init__.py
│   │   ├── test_todos.py
│   │   └── test_users.py
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_models.py
│   └── test_schemas.py
├── .env
├── .env.test
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Prerequisites

- [Python 3.10+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) (package manager)
- [PostgreSQL](https://www.postgresql.org/) (running locally or remotely)

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd fastapi_sqlalchemy_alembic
uv sync
```

### 2. Configure environment variables

Edit `.env` with your PostgreSQL connection string:

```env
DATABASE_URL=postgresql+asyncpg://root:password@localhost:5432/todo_alembic_db
```

The test database is configured in `.env.test` and uses SQLite automatically:

```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

### 3. Run database migrations

```bash
uv run alembic upgrade head
```

This creates the `users` and `todos` tables in your PostgreSQL database.

### 4. Start the server

```bash
uv run uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create a user |
| `GET` | `/users/` | List all users |
| `GET` | `/users/{id}` | Get a user by ID |
| `PUT` | `/users/{id}` | Update a user |
| `DELETE` | `/users/{id}` | Delete a user (cascades to todos) |

### Todos

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/todos/` | Create a todo |
| `GET` | `/todos/` | List all todos |
| `GET` | `/todos/?user_id={id}` | Filter todos by user |
| `GET` | `/todos/{id}` | Get a todo by ID |
| `PUT` | `/todos/{id}` | Update a todo |
| `DELETE` | `/todos/{id}` | Delete a todo |

## Testing

The test suite uses **SQLite** with **Alembic migrations** for full isolation and fast feedback.

```bash
uv run pytest -v
```

All 41 tests should pass. The test strategy:

- **Session-scoped DB**: Alembic migrations run once per test session
- **Per-test rollback**: Each test is wrapped in a transaction that is rolled back — no data leaks between tests
- **Async client**: Uses `httpx.AsyncClient` with FastAPI's async test transport

## Migrations

Generate a new migration after changing models:

```bash
uv run alembic revision --autogenerate -m "description of changes"
```

Apply pending migrations:

```bash
uv run alembic upgrade head
```

Rollback the last migration:

```bash
uv run alembic downgrade -1
```

Check migration history:

```bash
uv run alembic history
```
