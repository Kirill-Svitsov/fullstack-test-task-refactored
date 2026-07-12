from pathlib import Path

from src.core.config import get_settings

settings = get_settings()


class LocalStorage:
    def __init__(self):
        self.storage_dir = settings.STORAGE_DIR

    async def save(self, filename: str, content: bytes) -> None:
        """Сохранить файл"""
        path = self.storage_dir / filename
        path.write_bytes(content)

    async def delete(self, filename: str) -> None:
        """Удалить файл"""
        path = self.storage_dir / filename
        if path.exists():
            path.unlink()

    def get_path(self, filename: str) -> Path:
        """Получить путь к файлу"""
        return self.storage_dir / filename
