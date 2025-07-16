from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Clan
from app.schemas.user import UserStats, UserWithClan, Clan as ClanSchema

logger = logging.getLogger(__name__)
router = APIRouter()


class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    level: int
    xp: int
    rank: str
    stats: Dict[str, int]
    clan: Optional[ClanSchema] = None
    questions_answered: int = 0
    questions_correct: int = 0
    accuracy_percentage: float = 0.0


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener perfil completo del usuario con stats épicos"""
    try:
        # Obtener clan si existe
        clan = None
        if current_user.clan_id:
            clan_result = await db.execute(
                select(Clan).where(Clan.id == current_user.clan_id)
            )
            clan = clan_result.scalar_one_or_none()
        
        # Calcular estadísticas de respuestas
        from app.models.user_response import UserResponse
        responses_result = await db.execute(
            select(UserResponse).where(UserResponse.user_id == current_user.id)
        )
        responses = responses_result.scalars().all()
        
        questions_answered = len(responses)
        questions_correct = len([r for r in responses if r.is_correct])
        accuracy_percentage = (questions_correct / questions_answered * 100) if questions_answered > 0 else 0
        
        return UserProfileResponse(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            display_name=current_user.display_name,
            avatar_url=current_user.avatar_url,
            level=current_user.level,
            xp=current_user.xp,
            rank=current_user.rank,
            stats=current_user.stats or {},
            clan=ClanSchema.from_orm(clan) if clan else None,
            questions_answered=questions_answered,
            questions_correct=questions_correct,
            accuracy_percentage=round(accuracy_percentage, 1)
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener estadísticas épicas del usuario"""
    try:
        # Obtener clan si existe
        clan = None
        if current_user.clan_id:
            clan_result = await db.execute(
                select(Clan).where(Clan.id == current_user.clan_id)
            )
            clan = clan_result.scalar_one_or_none()
        
        return UserStats(
            level=current_user.level,
            xp=current_user.xp,
            rank=current_user.rank,
            stats=current_user.stats or {},
            clan=ClanSchema.from_orm(clan) if clan else None
        )
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user stats"
        )


@router.get("/clans", response_model=List[ClanSchema])
async def get_clans(
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de clanes disponibles"""
    try:
        clans_result = await db.execute(select(Clan))
        clans = clans_result.scalars().all()
        
        return [ClanSchema.from_orm(clan) for clan in clans]
        
    except Exception as e:
        logger.error(f"Error getting clans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving clans"
        )


@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar perfil del usuario"""
    try:
        # Actualizar campos permitidos
        allowed_fields = [
            'display_name', 'avatar_url', 'level', 'xp', 'rank', 'clan_id', 'stats'
        ]
        
        for field, value in profile_data.items():
            if field in allowed_fields and hasattr(current_user, field):
                setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user profile"
        ) 