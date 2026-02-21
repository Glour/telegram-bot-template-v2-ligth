#!/bin/sh
# shellcheck disable=SC2162
read -p "Enter name of migration: " message

if docker inspect telegram_bot >/dev/null 2>&1 && docker inspect -f '{{.State.Running}}' telegram_bot 2>/dev/null | grep -q true; then
    docker exec telegram_bot alembic revision --autogenerate -m "$message"
else
    alembic revision --autogenerate -m "$message"
fi

# sh scripts/alembic/create_migrations.sh
