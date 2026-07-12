from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.logging import LoggingMiddleware
from src.interfaces.api.routes import alerts, files

settings = get_settings()

app = FastAPI(
    title="File Sharing API", version="1.0.0", description="API для загрузки и управления файлами"
)

# Добавляем middleware для логирования
app.add_middleware(LoggingMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(files.router)
app.include_router(alerts.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
