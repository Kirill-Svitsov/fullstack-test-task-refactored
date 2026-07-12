import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Логируем входящий запрос
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        # Логируем ответ
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code} "
            f"time={process_time:.3f}s"
        )

        return response
