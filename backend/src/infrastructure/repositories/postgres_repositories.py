from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories.file_repository import FileRepository, AlertRepository
from src.domain.entities.models import StoredFile, Alert

class PostgresFileRepository(FileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, file: StoredFile) -> StoredFile:
        self.session.add(file)
        await self.session.commit()
        await self.session.refresh(file)
        return file
    
    async def get(self, file_id: str) -> Optional[StoredFile]:
        return await self.session.get(StoredFile, file_id)
    
    async def list(self) -> list[StoredFile]:
        result = await self.session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, file: StoredFile) -> StoredFile:
        await self.session.commit()
        await self.session.refresh(file)
        return file
    
    async def delete(self, file_id: str) -> None:
        await self.session.execute(
            delete(StoredFile).where(StoredFile.id == file_id)
        )
        await self.session.commit()

class PostgresAlertRepository(AlertRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, alert: Alert) -> Alert:
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
    
    async def list(self) -> list[Alert]:
        result = await self.session.execute(
            select(Alert).order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())
