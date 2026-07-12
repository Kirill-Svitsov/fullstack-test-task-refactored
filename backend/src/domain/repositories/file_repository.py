from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.models import StoredFile, Alert

class FileRepository(ABC):
    @abstractmethod
    async def save(self, file: StoredFile) -> StoredFile:
        pass
    
    @abstractmethod
    async def get(self, file_id: str) -> Optional[StoredFile]:
        pass
    
    @abstractmethod
    async def list(self) -> list[StoredFile]:
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
    async def list(self) -> list[Alert]:
        pass
