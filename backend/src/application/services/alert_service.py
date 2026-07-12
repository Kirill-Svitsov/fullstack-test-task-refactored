from src.domain.entities.models import Alert
from src.domain.repositories.file_repository import AlertRepository

class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo
    
    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        alert = Alert(file_id=file_id, level=level, message=message)
        return await self.alert_repo.save(alert)
    
    async def list_alerts(self) -> list[Alert]:
        return await self.alert_repo.list()
