from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.services.irt_service import IRTService
from app.models.user import User, UserProfile

logger = logging.getLogger(__name__)
router = APIRouter()

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    grade: Optional[str]
    institution: Optional[str]
    target_career: Optional[str]
    questions_answered: int
    questions_correct: int
    accuracy_percentage: float
    study_time_hours: float
    current_streak: int
    level: int
    total_points: int

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener perfil completo del usuario"""
    try:
        # Obtener perfil
        profile = current_user.profile
        
        if not profile:
            # Crear perfil por defecto si no existe
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        
        # Calcular métricas de progreso
        progress = profile.calculate_overall_progress()
        
        return UserProfileResponse(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            grade=profile.grade,
            institution=profile.institution,
            target_career=profile.target_career,
            questions_answered=profile.questions_answered,
            questions_correct=profile.questions_correct,
            accuracy_percentage=progress["accuracy_percentage"],
            study_time_hours=progress["study_time_hours"],
            current_streak=profile.current_streak,
            level=profile.level,
            total_points=profile.total_points
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )

@router.get("/abilities")
async def get_user_abilities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener habilidades del usuario por área (IRT theta)"""
    try:
        irt_service = IRTService()
        abilities = await irt_service.get_user_ability_profile(
            user_id=str(current_user.id),
            db=db
        )
        
        return abilities
        
    except Exception as e:
        logger.error(f"Error getting user abilities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user abilities"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar perfil del usuario"""
    try:
        profile = current_user.profile
        
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Actualizar campos permitidos
        allowed_fields = [
            'grade', 'institution', 'target_career', 'target_universities',
            'preferred_study_time', 'learning_style', 'difficulty_preference',
            'daily_question_goal', 'weekly_study_goal_minutes', 'target_exam_date',
            'timezone', 'language', 'notifications_enabled', 'email_notifications'
        ]
        
        for field, value in profile_data.items():
            if field in allowed_fields and hasattr(profile, field):
                setattr(profile, field, value)
        
        await db.commit()
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user profile"
        ) 