from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import uuid

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.question import Question, Discipline

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


@router.get("/disciplines")
async def get_disciplines():
    """Obtener todas las disciplinas disponibles"""
    return [
        {"code": "MAT", "name": "Matemáticas", "icon": "🔢"},
        {"code": "LC", "name": "Lectura Crítica", "icon": "📖"},
        {"code": "SOC", "name": "Ciencias Sociales", "icon": "🏛️"},
        {"code": "CIE", "name": "Ciencias Naturales", "icon": "🧬"},
        {"code": "ING", "name": "Inglés", "icon": "🌍"}
    ]


@router.get("/next")
async def get_next_question(
    discipline: Optional[str] = Query(None, description="Filter by discipline"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener la siguiente pregunta para el usuario"""
    try:
        # Construir query base
        query = select(Question).filter(Question.discipline.isnot(None))
        
        # Filtrar por disciplina si se especifica
        if discipline:
            query = query.filter(Question.discipline == discipline)
        
        # Obtener pregunta aleatoria
        result = await db.execute(
            query.order_by(func.random()).limit(1)
        )
        question = result.scalar_one_or_none()
        
        if not question:
            # Pregunta de ejemplo si no hay preguntas en la BD
            return QuestionResponse(
                id=str(uuid.uuid4()),
                discipline="MAT",
                difficulty=2,
                topic="Ecuaciones",
                question="¿Cuál es el valor de x en 2x + 5 = 15?",
                options=[
                    QuestionOption(id="A", text="x = 5", isCorrect=True),
                    QuestionOption(id="B", text="x = 10", isCorrect=False),
                    QuestionOption(id="C", text="x = 7.5", isCorrect=False),
                    QuestionOption(id="D", text="x = 20", isCorrect=False)
                ],
                reward_xp=15,
                reward_item="Poción de Concentración"
            )
        
        # Convertir opciones del formato JSONB
        options = []
        for option_data in question.options:
            options.append(QuestionOption(
                id=option_data["id"],
                text=option_data["text"],
                isCorrect=(option_data["id"] == question.correct_option)
            ))
        
        return QuestionResponse(
            id=str(question.id),
            discipline=question.discipline,
            difficulty=question.difficulty,
            topic=question.topic,
            question=question.question_text,
            options=options,
            reward_xp=question.reward_xp,
            reward_item=question.reward_item
        )
        
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question"
        )


@router.get("/random/{discipline}")
async def get_random_question(
    discipline: str,
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Filter by difficulty"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener una pregunta aleatoria de una disciplina específica"""
    try:
        # Construir query
        query = select(Question).filter(Question.discipline == discipline)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        result = await db.execute(
            query.order_by(func.random()).limit(1)
        )
        
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No questions available for discipline {discipline}"
            )
        
        # Convertir opciones
        options = []
        for option_data in question.options:
            options.append(QuestionOption(
                id=option_data["id"],
                text=option_data["text"],
                isCorrect=(option_data["id"] == question.correct_option)
            ))
        
        return QuestionResponse(
            id=str(question.id),
            discipline=question.discipline,
            difficulty=question.difficulty,
            topic=question.topic,
            question=question.question_text,
            options=options,
            reward_xp=question.reward_xp,
            reward_item=question.reward_item
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
    discipline: Optional[str] = Query(None, description="Filter by discipline"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Filter by difficulty"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Buscar preguntas por texto"""
    try:
        # Construir query base
        query = select(Question)
        
        # Filtro de texto
        query = query.filter(
            Question.question_text.ilike(f"%{q}%") |
            Question.topic.ilike(f"%{q}%")
        )
        
        # Filtros opcionales
        if discipline:
            query = query.filter(Question.discipline == discipline)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # Limitar resultados
        query = query.limit(limit)
        
        result = await db.execute(query)
        questions = result.scalars().all()
        
        return [
            QuestionResponse(
                id=str(q.id),
                discipline=q.discipline,
                difficulty=q.difficulty,
                topic=q.topic,
                question=q.question_text,
                options=[
                    QuestionOption(
                        id=opt["id"],
                        text=opt["text"],
                        isCorrect=(opt["id"] == q.correct_option)
                    )
                    for opt in q.options
                ],
                reward_xp=q.reward_xp,
                reward_item=q.reward_item
            )
            for q in questions
        ]
        
    except Exception as e:
        logger.error(f"Error searching questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching questions"
        ) 