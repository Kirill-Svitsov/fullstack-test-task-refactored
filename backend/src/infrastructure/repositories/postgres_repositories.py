from typing import Optional, Tuple

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.models import Alert, StoredFile
from src.domain.repositories.file_repository import AlertRepository, FileRepository


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

    async def list(self, skip: int = 0, limit: int = 20) -> Tuple[list[StoredFile], int]:
        # Получаем общее количество
        total_query = select(func.count()).select_from(StoredFile)
        total = await self.session.scalar(total_query) or 0

        # Получаем список с пагинацией
        query = select(StoredFile).order_by(StoredFile.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, file: StoredFile) -> StoredFile:
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def delete(self, file_id: str) -> None:
        await self.session.execute(delete(StoredFile).where(StoredFile.id == file_id))
        await self.session.commit()


class PostgresAlertRepository(AlertRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, alert: Alert) -> Alert:
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def save_bulk(self, alerts: list[Alert]) -> list[Alert]:
        """Bulk сохранение алертов"""
        self.session.add_all(alerts)
        await self.session.commit()
        for alert in alerts:
            await self.session.refresh(alert)
        return alerts

    async def list(self, skip: int = 0, limit: int = 20) -> Tuple[list[Alert], int]:
        total_query = select(func.count()).select_from(Alert)
        total = await self.session.scalar(total_query) or 0

        query = select(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total
