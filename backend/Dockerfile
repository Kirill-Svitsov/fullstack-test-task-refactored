FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /backend

# Устанавливаем зависимости через pip
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi uvicorn sqlalchemy asyncpg alembic \
    pydantic python-multipart celery redis

COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
