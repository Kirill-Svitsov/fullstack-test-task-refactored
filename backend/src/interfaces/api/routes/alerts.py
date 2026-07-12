from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.alert_service import AlertService
from src.core.database import get_db
from src.infrastructure.repositories.postgres_repositories import PostgresAlertRepository
from src.interfaces.schemas.file_schemas import AlertItem, PaginatedResponseSchema

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    repo = PostgresAlertRepository(db)
    return AlertService(repo)


@router.get("", response_model=PaginatedResponseSchema[AlertItem])
async def list_alerts(
    skip: int = Query(default=0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(default=20, ge=1, le=100, description="Количество записей на страницу"),
    service: AlertService = Depends(get_alert_service),
):
    return await service.list_alerts(skip, limit)
