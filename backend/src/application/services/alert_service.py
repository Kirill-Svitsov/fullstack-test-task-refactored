from src.application.dtos.pagination import PaginatedResponse
from src.domain.entities.models import Alert
from src.domain.repositories.file_repository import AlertRepository


class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        alert = Alert(file_id=file_id, level=level, message=message)
        return await self.alert_repo.save(alert)

    async def create_alerts_bulk(self, alerts_data: list[dict]) -> list[Alert]:
        """Bulk создание алертов"""
        alerts = [Alert(**data) for data in alerts_data]
        return await self.alert_repo.save_bulk(alerts)

    async def list_alerts(self, skip: int = 0, limit: int = 20) -> PaginatedResponse[Alert]:
        items, total = await self.alert_repo.list(skip, limit)
        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
            has_previous=skip > 0,
        )
