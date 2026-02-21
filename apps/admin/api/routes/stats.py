"""API routes for statistics and analytics."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.core.session import get_session
from infrastructure.database.uow import UnitOfWork
from shared.dto.analytics import MetricsDTO

router = APIRouter()


@router.get("/stats/overview", response_model=dict)
async def get_overview(
    session: AsyncSession = Depends(get_session),
):
    """Get general bot overview statistics."""
    uow = UnitOfWork(session)

    from datetime import datetime, timedelta

    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)

    return {
        "users": {
            "total": await uow.users.count(),
            "active_1h": await uow.users.count_active_users(1),
            "active_24h": await uow.users.count_active_users(24),
            "active_7d": await uow.users.count_active_users(168),
        },
        "events": {
            "total": await uow.analytics.count_total_events(),
            "last_24h": await uow.analytics.count_total_events(since=day_ago),
        },
    }


@router.get("/stats/metrics", response_model=MetricsDTO)
async def get_metrics(
    session: AsyncSession = Depends(get_session),
):
    """Get bot metrics."""
    from shared.enums import EventType

    uow = UnitOfWork(session)

    return MetricsDTO(
        total_messages=await uow.analytics.count_events_by_type(EventType.MESSAGE_SENT),
        total_commands=await uow.analytics.count_events_by_type(EventType.COMMAND_EXECUTED),
        total_errors=await uow.analytics.count_events_by_type(EventType.ERROR_OCCURRED),
        active_users_1h=await uow.users.count_active_users(1),
        active_users_24h=await uow.users.count_active_users(24),
        active_users_7d=await uow.users.count_active_users(168),
    )
