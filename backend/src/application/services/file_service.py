import mimetypes
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException, status
from src.domain.entities.models import StoredFile
from src.domain.repositories.file_repository import FileRepository
from src.infrastructure.storage.local_storage import LocalStorage
from src.core.config import get_settings

settings = get_settings()

class FileService:
    def __init__(self, file_repo: FileRepository, storage: LocalStorage):
        self.file_repo = file_repo
        self.storage = storage
    
    async def upload_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        # Читаем содержимое
        content = await upload_file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Проверка размера
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / (1024*1024)} MB"
            )
        
        # Генерируем ID
        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        
        # Сохраняем в storage
        await self.storage.save(stored_name, content)
        
        # Создаем запись в БД
        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=upload_file.content_type or 
                     mimetypes.guess_type(stored_name)[0] or 
                     "application/octet-stream",
            size=len(content),
            processing_status="uploaded",
        )
        
        return await self.file_repo.save(file_item)
    
    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self.file_repo.get(file_id)
        if not file_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        return file_item
    
    async def list_files(self) -> list[StoredFile]:
        return await self.file_repo.list()
    
    async def update_file(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get_file(file_id)
        file_item.title = title
        return await self.file_repo.update(file_item)
    
    async def delete_file(self, file_id: str) -> None:
        file_item = await self.get_file(file_id)
        await self.storage.delete(file_item.stored_name)
        await self.file_repo.delete(file_id)
    
    async def get_file_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        path = settings.STORAGE_DIR / file_item.stored_name
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stored file not found"
            )
        return file_item, path
