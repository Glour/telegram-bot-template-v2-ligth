# Bot service Dockerfile
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy only dependency files first (for caching)
COPY pyproject.toml poetry.lock ./

# Development build
FROM base as dev-build
RUN poetry config virtualenvs.create false \
    && poetry install --with dev --no-interaction --no-ansi

# Production build
FROM base as prod-build
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Final stage
FROM prod-build as final

# Copy application code
COPY . /app

# Set PYTHONPATH so Python can find the app modules
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Run bot
CMD ["python3", "apps/bot/main.py"]
