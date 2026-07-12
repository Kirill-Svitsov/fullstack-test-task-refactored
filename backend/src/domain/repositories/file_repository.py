from abc import ABC, abstractmethod
from typing import Optional, Tuple

from src.domain.entities.models import Alert, StoredFile


class FileRepository(ABC):
    @abstractmethod
    async def save(self, file: StoredFile) -> StoredFile:
        pass

    @abstractmethod
    async def get(self, file_id: str) -> Optional[StoredFile]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 20) -> Tuple[list[StoredFile], int]:
        pass

    @abstractmethod
    async def update(self, file: StoredFile) -> StoredFile:
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> None:
        pass


class AlertRepository(ABC):
    @abstractmethod
    async def save(self, alert: Alert) -> Alert:
        pass

    @abstractmethod
    async def save_bulk(self, alerts: list[Alert]) -> list[Alert]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 20) -> Tuple[list[Alert], int]:
        pass
