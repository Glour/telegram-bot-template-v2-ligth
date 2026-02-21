"""API routes for user management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.core.session import get_session
from infrastructure.database.uow import UnitOfWork
from shared.dto.user import UserResponseDTO, UserStatsDTO

router = APIRouter()


@router.get("/users/stats", response_model=UserStatsDTO)
async def get_user_stats(
    session: AsyncSession = Depends(get_session),
):
    """Get user statistics."""
    from datetime import datetime, timedelta

    from shared.enums import UserStatus

    uow = UnitOfWork(session)

    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    return UserStatsDTO(
        total_users=await uow.users.count(),
        active_users=await uow.users.count_by_status(UserStatus.ACTIVE),
        blocked_users=await uow.users.count_by_status(UserStatus.BLOCKED),
        banned_users=await uow.users.count_by_status(UserStatus.BANNED),
        new_users_today=await uow.users.count_new_users(today),
        new_users_this_week=await uow.users.count_new_users(week_ago),
        new_users_this_month=await uow.users.count_new_users(month_ago),
    )


@router.get("/users/{user_id}", response_model=UserResponseDTO)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get user by ID."""
    uow = UnitOfWork(session)
    user = await uow.users.get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponseDTO.model_validate(user)


@router.get("/users", response_model=list[UserResponseDTO])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    """Get list of users."""
    uow = UnitOfWork(session)
    users = await uow.users.get_all(limit=limit, offset=skip)

    return [UserResponseDTO.model_validate(user) for user in users]
