# Standalone Dockerfile — one container with external DB
# Usage: docker build -t bot . && docker run --env-file .env bot
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.5

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Production build
FROM base AS prod-build
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Final stage
FROM prod-build AS final

COPY . /app

ENV PYTHONPATH=/app

RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Auto-run migrations on startup, then start bot
CMD ["sh", "-c", "alembic upgrade head && python3 apps/bot/main.py"]
