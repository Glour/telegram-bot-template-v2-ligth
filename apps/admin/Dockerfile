# Admin Panel service Dockerfile
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
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Copy application code
COPY . /app

# Set PYTHONPATH so Python can find the app modules
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 adminuser && chown -R adminuser:adminuser /app
USER adminuser

# Expose port
EXPOSE 8000

# Run admin panel
CMD ["python3", "apps/admin/main.py"]
