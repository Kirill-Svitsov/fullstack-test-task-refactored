from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.file_service import FileService
from src.core.database import get_db
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.repositories.postgres_repositories import PostgresFileRepository
from src.infrastructure.storage.local_storage import LocalStorage
from src.interfaces.schemas.file_schemas import FileItem, FileUpdate, PaginatedResponseSchema

router = APIRouter(prefix="/files", tags=["Files"])


def get_file_service(db: AsyncSession = Depends(get_db)) -> FileService:
    repo = PostgresFileRepository(db)
    storage = LocalStorage()
    cache = RedisCache()
    return FileService(repo, storage, cache)


@router.get("", response_model=PaginatedResponseSchema[FileItem])
async def list_files(
    skip: int = Query(default=0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(default=20, ge=1, le=100, description="Количество записей на страницу"),
    service: FileService = Depends(get_file_service),
):
    return await service.list_files(skip, limit)


@router.post("", response_model=FileItem, status_code=201)
async def create_file(
    title: str = Form(...),
    file: UploadFile = File(...),
    service: FileService = Depends(get_file_service),
):
    return await service.upload_file(title, file)


@router.get("/{file_id}", response_model=FileItem)
async def get_file(file_id: str, service: FileService = Depends(get_file_service)):
    return await service.get_file(file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file(
    file_id: str, payload: FileUpdate, service: FileService = Depends(get_file_service)
):
    return await service.update_file(file_id, payload.title)


@router.get("/{file_id}/download")
async def download_file(file_id: str, service: FileService = Depends(get_file_service)):
    file_item, stored_path = await service.get_file_path(file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file(file_id: str, service: FileService = Depends(get_file_service)):
    await service.delete_file(file_id)
