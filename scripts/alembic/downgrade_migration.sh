#!/bin/sh

if docker inspect telegram_bot >/dev/null 2>&1 && docker inspect -f '{{.State.Running}}' telegram_bot 2>/dev/null | grep -q true; then
    docker exec telegram_bot alembic downgrade -1
else
    alembic downgrade -1
fi

# sh scripts/alembic/downgrade_migration.sh
