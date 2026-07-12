from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.infrastructure.repositories.postgres_repositories import PostgresAlertRepository
from src.application.services.alert_service import AlertService
from src.interfaces.schemas.file_schemas import AlertItem

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    repo = PostgresAlertRepository(db)
    return AlertService(repo)

@router.get("", response_model=list[AlertItem])  # Убрали / в конце
async def list_alerts(
    service: AlertService = Depends(get_alert_service)
):
    return await service.list_alerts()
