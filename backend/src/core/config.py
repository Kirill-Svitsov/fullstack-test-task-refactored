import os
from pathlib import Path
from functools import lru_cache

class Settings:
    DB_USER: str = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT: str = os.getenv("PGPORT", "5432")
    DB_NAME: str = os.getenv("POSTGRES_DB", "test")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://backend-redis:6379/0")
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage" / "files"
    
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    
    def __init__(self):
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    return Settings()
