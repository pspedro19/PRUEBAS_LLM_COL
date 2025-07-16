from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.question import Question
from app.models.user_response import UserResponse
from app.services.question_service import QuestionService

logger = logging.getLogger(__name__)
router = APIRouter()


class ResponseCreate(BaseModel):
    question_id: str
    answer_text: str
    confidence_score: Optional[float] = None


class ResponseResult(BaseModel):
    is_correct: bool
    feedback: str
    reward_xp: int
    reward_item: Optional[str]
    user_level: int
    user_xp: int
    user_rank: str
    stats_updated: dict


@router.post("/submit", response_model=ResponseResult)
async def submit_response(
    response_data: ResponseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enviar respuesta a una pregunta y obtener recompensas épicas"""
    try:
        # Obtener la pregunta
        question_result = await db.execute(
            select(Question).where(Question.id == response_data.question_id)
        )
        question = question_result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Verificar si la respuesta es correcta
        is_correct = response_data.answer_text == question.correct_option
        
        # Crear la respuesta
        response = UserResponse(
            user_id=current_user.id,
            question_id=question.id,
            answer_text=response_data.answer_text,
            is_correct=is_correct,
            confidence_score=response_data.confidence_score,
            feedback="¡Correcto! ¡Excelente trabajo!" if is_correct else "Incorrecto. Revisa la explicación y sigue practicando."
        )
        
        db.add(response)
        
        # Actualizar stats del usuario si la respuesta es correcta
        stats_updated = {}
        if is_correct:
            # Agregar XP
            current_user.add_xp(question.reward_xp)
            
            # Actualizar stats por disciplina
            discipline = question.discipline
            current_stats = current_user.get_stats_for_discipline(discipline)
            new_stats = current_stats + 1
            current_user.update_stats_for_discipline(discipline, new_stats)
            stats_updated[discipline] = new_stats
        
        await db.commit()
        await db.refresh(current_user)
        
        return ResponseResult(
            is_correct=is_correct,
            feedback=response.feedback,
            reward_xp=question.reward_xp if is_correct else 0,
            reward_item=question.reward_item if is_correct else None,
            user_level=current_user.level,
            user_xp=current_user.xp,
            user_rank=current_user.rank,
            stats_updated=stats_updated
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting response: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting response"
        )


@router.get("/history")
async def get_response_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener historial de respuestas del usuario"""
    try:
        responses_result = await db.execute(
                    select(UserResponse)
        .where(UserResponse.user_id == current_user.id)
        .order_by(UserResponse.created_at.desc())
        )
        responses = responses_result.scalars().all()
        
        return [
            {
                "id": str(r.id),
                "question_id": str(r.question_id),
                "answer_text": r.answer_text,
                "is_correct": r.is_correct,
                "confidence_score": r.confidence_score,
                "feedback": r.feedback,
                "created_at": r.created_at
            }
            for r in responses
        ]
        
    except Exception as e:
        logger.error(f"Error getting response history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving response history"
        ) 