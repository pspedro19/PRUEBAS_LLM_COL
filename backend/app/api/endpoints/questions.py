from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.question import Question, QuestionArea

logger = logging.getLogger(__name__)
router = APIRouter()

class QuestionResponse(BaseModel):
    id: str
    question_text: str
    options: List[str]
    subject_area: str
    competencia: str
    sub_competencia: Optional[str]
    difficulty_level: Optional[str]
    estimated_time_seconds: int

@router.get("/areas")
async def get_subject_areas(db: AsyncSession = Depends(get_db)):
    """Obtener todas las áreas de estudio disponibles"""
    try:
        result = await db.execute(
            select(QuestionArea)
            .filter(QuestionArea.is_active == True)
            .order_by(QuestionArea.order_index)
        )
        areas = result.scalars().all()
        
        return [
            {
                "name": area.name,
                "display_name": area.display_name,
                "description": area.description,
                "icon_url": area.icon_url,
                "color_hex": area.color_hex
            }
            for area in areas
        ]
        
    except Exception as e:
        logger.error(f"Error getting subject areas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving subject areas"
        )

@router.get("/random/{subject_area}")
async def get_random_question(
    subject_area: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener una pregunta aleatoria de un área específica"""
    try:
        # Obtener preguntas no respondidas por el usuario
        subquery = (
            select(UserResponse.question_id)
            .filter(UserResponse.user_id == current_user.id)
        )
        
        result = await db.execute(
            select(Question)
            .filter(
                and_(
                    Question.subject_area == subject_area,
                    Question.status == "active",
                    ~Question.id.in_(subquery)
                )
            )
            .order_by(func.random())
            .limit(1)
        )
        
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No questions available for {subject_area}"
            )
        
        return QuestionResponse(
            id=str(question.id),
            question_text=question.question_text,
            options=question.options,
            subject_area=question.subject_area,
            competencia=question.competencia,
            sub_competencia=question.sub_competencia,
            difficulty_level=question.difficulty_level,
            estimated_time_seconds=question.estimated_time_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting random question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question"
        )

@router.get("/search")
async def search_questions(
    q: str = Query(..., min_length=3, description="Search query"),
    subject_area: Optional[str] = Query(None, description="Filter by subject area"),
    competencia: Optional[str] = Query(None, description="Filter by competencia"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Buscar preguntas por texto"""
    try:
        # Construir query base
        query = select(Question).filter(Question.status == "active")
        
        # Filtro de texto (buscar en pregunta y competencias)
        query = query.filter(
            Question.question_text.ilike(f"%{q}%") |
            Question.competencia.ilike(f"%{q}%") |
            Question.sub_competencia.ilike(f"%{q}%")
        )
        
        # Filtros opcionales
        if subject_area:
            query = query.filter(Question.subject_area == subject_area)
        
        if competencia:
            query = query.filter(Question.competencia.ilike(f"%{competencia}%"))
        
        # Limitar resultados
        query = query.limit(limit)
        
        result = await db.execute(query)
        questions = result.scalars().all()
        
        return [
            QuestionResponse(
                id=str(q.id),
                question_text=q.question_text,
                options=q.options,
                subject_area=q.subject_area,
                competencia=q.competencia,
                sub_competencia=q.sub_competencia,
                difficulty_level=q.difficulty_level,
                estimated_time_seconds=q.estimated_time_seconds
            )
            for q in questions
        ]
        
    except Exception as e:
        logger.error(f"Error searching questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching questions"
        ) 