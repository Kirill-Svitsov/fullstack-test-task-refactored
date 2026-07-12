from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile
from httpx import ASGITransport, AsyncClient

from src.application.services.alert_service import AlertService
from src.application.services.file_service import FileService
from src.domain.entities.models import Alert, StoredFile
from src.infrastructure.cache.redis_cache import RedisCache
from src.main import app

# ==================== API TESTS ====================


@pytest.mark.asyncio
async def test_api_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_files_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/files?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_api_files_create():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test_api.txt", b"test content", "text/plain")}
        data = {"title": "API Test"}
        response = await client.post("/files", data=data, files=files)
        assert response.status_code == 201
        file_data = response.json()
        assert file_data["title"] == "API Test"
        assert file_data["original_name"] == "test_api.txt"


@pytest.mark.asyncio
async def test_api_file_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/files/non-existent-id")
        assert response.status_code == 404


# ==================== SERVICE TESTS ====================


@pytest.mark.asyncio
async def test_service_upload():
    mock_repo = AsyncMock()
    mock_repo.save = AsyncMock()
    mock_repo.save.return_value = StoredFile(
        id="test-123",
        title="Test Upload",
        original_name="test.txt",
        stored_name="test.txt",
        mime_type="text/plain",
        size=100,
        processing_status="uploaded",
    )
    mock_storage = AsyncMock()
    mock_storage.save = AsyncMock()

    service = FileService(mock_repo, mock_storage)

    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=b"test content")
    mock_file.filename = "test.txt"
    mock_file.content_type = "text/plain"

    result = await service.upload_file("Test Upload", mock_file)
    assert result.title == "Test Upload"
    assert mock_storage.save.called


@pytest.mark.asyncio
async def test_service_get_file():
    mock_repo = AsyncMock()
    mock_repo.get = AsyncMock()
    mock_repo.get.return_value = StoredFile(
        id="test-456",
        title="Get Test",
        original_name="get.txt",
        stored_name="get.txt",
        mime_type="text/plain",
        size=100,
        processing_status="uploaded",
    )
    mock_storage = AsyncMock()

    service = FileService(mock_repo, mock_storage)
    result = await service.get_file("test-456")
    assert result.id == "test-456"
    assert result.title == "Get Test"


@pytest.mark.asyncio
async def test_service_list_files():
    mock_repo = AsyncMock()
    mock_repo.list = AsyncMock()
    mock_repo.list.return_value = ([], 0)
    mock_storage = AsyncMock()

    service = FileService(mock_repo, mock_storage)
    result = await service.list_files(skip=0, limit=10)
    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_alert_service_create():
    mock_repo = AsyncMock()
    mock_repo.save = AsyncMock()
    mock_repo.save.return_value = Alert(
        id=1, file_id="test-file", level="info", message="Test alert"
    )

    service = AlertService(mock_repo)
    result = await service.create_alert("test-file", "info", "Test alert")
    assert result.file_id == "test-file"
    assert result.level == "info"


@pytest.mark.asyncio
async def test_alert_service_bulk():
    mock_repo = AsyncMock()
    mock_repo.save_bulk = AsyncMock()
    mock_repo.save_bulk.return_value = [
        Alert(id=1, file_id="test-file", level="info", message="Alert 1"),
        Alert(id=2, file_id="test-file", level="warning", message="Alert 2"),
    ]

    service = AlertService(mock_repo)
    alerts_data = [
        {"file_id": "test-file", "level": "info", "message": "Alert 1"},
        {"file_id": "test-file", "level": "warning", "message": "Alert 2"},
    ]
    result = await service.create_alerts_bulk(alerts_data)
    assert len(result) == 2


# ==================== CACHE TESTS ====================


@pytest.mark.asyncio
async def test_cache_set_get():
    cache = RedisCache()
    cache.client = AsyncMock()
    cache.client.setex = AsyncMock()
    cache.client.get = AsyncMock(return_value='{"test": "value"}')

    await cache.set("test_key", {"test": "value"})
    cache.client.setex.assert_called_once()

    result = await cache.get("test_key")
    assert result == {"test": "value"}


@pytest.mark.asyncio
async def test_cache_delete():
    cache = RedisCache()
    cache.client = AsyncMock()
    cache.client.delete = AsyncMock()

    await cache.delete("test_key")
    cache.client.delete.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_cache_clear_pattern():
    cache = RedisCache()
    cache.client = AsyncMock()
    cache.client.keys = AsyncMock(return_value=["key1", "key2"])
    cache.client.delete = AsyncMock()

    await cache.clear_pattern("test:*")
    cache.client.keys.assert_called_once_with("test:*")
    cache.client.delete.assert_called_once()


# ==================== RUN ====================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
