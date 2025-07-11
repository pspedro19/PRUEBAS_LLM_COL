from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.question import Question
# Removed enum imports since they are commented out

logger = logging.getLogger(__name__)
router = APIRouter()


class QuestionOption(BaseModel):
    id: str
    text: str
    isCorrect: bool


class QuestionResponse(BaseModel):
    id: str
    discipline: str
    difficulty: int
    topic: Optional[str]
    question: str
    options: List[QuestionOption]
    reward_xp: int
    reward_item: Optional[str]


@router.get("/areas")
async def get_areas():
    """Obtener todas las áreas ICFES disponibles"""
    return [
        {"code": "matematicas", "name": "Matemáticas", "icon": "🧮"},
        {"code": "lectura_critica", "name": "Lectura Crítica", "icon": "📚"},
        {"code": "ciencias_naturales", "name": "Ciencias Naturales", "icon": "🔬"},
        {"code": "sociales_ciudadanas", "name": "Sociales y Ciudadanas", "icon": "🏛️"},
        {"code": "ingles", "name": "Inglés", "icon": "🌍"}
    ]


@router.get("/next")
async def get_next_question(
    area: Optional[str] = Query(None, description="Filter by ICFES area"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener la siguiente pregunta para el usuario"""
    try:
        # Construir query base
        query = select(Question).filter(Question.is_active == True)
        
        # Filtrar por área si se especifica
        if area:
            valid_areas = ["matematicas", "lectura_critica", "ciencias_naturales", "sociales_ciudadanas", "ingles"]
            if area not in valid_areas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid area: {area}"
                )
            query = query.filter(Question.area == area)
        
        # Filtrar por tema si se especifica
        if topic:
            query = query.filter(Question.topic == topic)
        
        # Obtener pregunta aleatoria
        result = await db.execute(
            query.order_by(func.random()).limit(1)
        )
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No questions available with the specified criteria"
            )
        
        # Crear opciones en el formato legacy
        options = [
            QuestionOption(id="A", text=question.option_a, isCorrect=(question.correct_answer == "A")),
            QuestionOption(id="B", text=question.option_b, isCorrect=(question.correct_answer == "B")),
            QuestionOption(id="C", text=question.option_c, isCorrect=(question.correct_answer == "C")),
            QuestionOption(id="D", text=question.option_d, isCorrect=(question.correct_answer == "D"))
        ]
        
        return QuestionResponse(
            id=str(question.id),
            discipline=question.area, # Changed from question.area.value to question.area
            difficulty=["principiante", "intermedio", "avanzado", "experto"].index(question.difficulty) + 1, # Changed from question.difficulty.value to question.difficulty
            topic=question.topic,
            question=question.content,
            options=options,
            reward_xp=question.points_value,
            reward_item=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question"
        )


@router.get("/random/{area}")
async def get_random_question(
    area: str,
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener una pregunta aleatoria de un área específica"""
    try:
        # Validar que el área sea válida (opcional, usando lista hardcoded)
        valid_areas = ["matematicas", "lectura_critica", "ciencias_naturales", "sociales_ciudadanas", "ingles"]
        if area not in valid_areas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid area: {area}"
            )
        
        # Construir query
        query = select(Question).filter(
            Question.area == area,
            Question.is_active == True
        )
        
        if difficulty:
            valid_difficulties = ["principiante", "intermedio", "avanzado", "experto"]
            if difficulty not in valid_difficulties:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid difficulty: {difficulty}"
                )
            query = query.filter(Question.difficulty == difficulty)
        
        if topic:
            query = query.filter(Question.topic == topic)
        
        result = await db.execute(
            query.order_by(func.random()).limit(1)
        )
        
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No questions available for area {area}"
            )
        
        # Crear opciones en el formato legacy
        options = [
            QuestionOption(id="A", text=question.option_a, isCorrect=(question.correct_answer == "A")),
            QuestionOption(id="B", text=question.option_b, isCorrect=(question.correct_answer == "B")),
            QuestionOption(id="C", text=question.option_c, isCorrect=(question.correct_answer == "C")),
            QuestionOption(id="D", text=question.option_d, isCorrect=(question.correct_answer == "D"))
        ]
        
        return QuestionResponse(
            id=str(question.id),
            discipline=question.area, # Changed from question.area.value to question.area
            difficulty=["principiante", "intermedio", "avanzado", "experto"].index(question.difficulty) + 1, # Changed from question.difficulty.value to question.difficulty
            topic=question.topic,
            question=question.content,
            options=options,
            reward_xp=question.points_value,
            reward_item=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting random question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question"
        )


@router.get("/redirect-to-quiz")
async def redirect_to_quiz(
    area: str = Query(..., description="ICFES area"),
    current_user: User = Depends(get_current_user)
):
    """Endpoint para redireccionar a la nueva API de quiz"""
    return {
        "message": "This endpoint has been replaced by the quiz API",
        "new_endpoints": {
            "start_session": "/api/v1/quiz/start-session",
            "get_questions": "/api/v1/quiz/questions",
            "get_topics": f"/api/v1/quiz/topics/{area}",
            "get_stats": f"/api/v1/quiz/stats/{area}"
        },
        "documentation": "/docs"
    } 