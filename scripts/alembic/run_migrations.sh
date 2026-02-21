#!/bin/sh

if docker inspect telegram_bot >/dev/null 2>&1 && docker inspect -f '{{.State.Running}}' telegram_bot 2>/dev/null | grep -q true; then
    docker exec telegram_bot alembic upgrade head
else
    alembic upgrade head
fi

# sh scripts/alembic/run_migrations.sh
