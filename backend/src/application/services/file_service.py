import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from src.application.dtos.pagination import PaginatedResponse
from src.core.config import get_settings
from src.domain.entities.models import StoredFile
from src.domain.repositories.file_repository import FileRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.storage.local_storage import LocalStorage

settings = get_settings()


class FileService:
    def __init__(self, file_repo: FileRepository, storage: LocalStorage, cache: RedisCache = None):
        self.file_repo = file_repo
        self.storage = storage
        self.cache = cache
        self.cache_ttl = 300  # 5 минут

    async def upload_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        content = await upload_file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / (1024*1024)} MB",
            )

        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"

        await self.storage.save(stored_name, content)

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=upload_file.content_type
            or mimetypes.guess_type(stored_name)[0]
            or "application/octet-stream",
            size=len(content),
            processing_status="uploaded",
        )

        result = await self.file_repo.save(file_item)

        # Инвалидируем кеш списка файлов
        if self.cache:
            await self.cache.clear_pattern("files:list:*")

        return result

    async def get_file(self, file_id: str) -> StoredFile:
        # Проверяем кеш
        cache_key = f"file:{file_id}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                # Создаем объект StoredFile из dict
                return StoredFile(**cached)

        file_item = await self.file_repo.get(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        # Сохраняем в кеш
        if self.cache:
            await self.cache.set(cache_key, file_item, self.cache_ttl)

        return file_item

    async def list_files(self, skip: int = 0, limit: int = 20) -> PaginatedResponse[StoredFile]:
        # Проверяем кеш
        cache_key = f"files:list:{skip}:{limit}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                # Восстанавливаем объекты
                items = [StoredFile(**item) for item in cached.get("items", [])]
                return PaginatedResponse(
                    items=items,
                    total=cached["total"],
                    skip=cached["skip"],
                    limit=cached["limit"],
                    has_next=cached["has_next"],
                    has_previous=cached["has_previous"],
                )

        items, total = await self.file_repo.list(skip, limit)
        result = PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
            has_previous=skip > 0,
        )

        # Сохраняем в кеш
        if self.cache:
            # Преобразуем объекты в dict для кеша
            cache_data = {
                "items": [item.__dict__ for item in items],
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_next": result.has_next,
                "has_previous": result.has_previous,
            }
            await self.cache.set(cache_key, cache_data, self.cache_ttl)

        return result

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        # Получаем файл из БД (не из кеша!)
        file_item = await self.file_repo.get(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        # Обновляем
        file_item.title = title
        result = await self.file_repo.update(file_item)

        # Инвалидируем кеш
        if self.cache:
            await self.cache.delete(f"file:{file_id}")
            await self.cache.clear_pattern("files:list:*")

        return result

    async def delete_file(self, file_id: str) -> None:
        # Получаем файл из БД
        file_item = await self.file_repo.get(file_id)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        await self.storage.delete(file_item.stored_name)
        await self.file_repo.delete(file_id)

        # Инвалидируем кеш
        if self.cache:
            await self.cache.delete(f"file:{file_id}")
            await self.cache.clear_pattern("files:list:*")

    async def get_file_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        path = settings.STORAGE_DIR / file_item.stored_name
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
            )
        return file_item, path
