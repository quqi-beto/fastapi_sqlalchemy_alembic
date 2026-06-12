from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    def __init__(self):
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://root:password@localhost:5432/todo_alembic_db",
        )


settings = Settings()
