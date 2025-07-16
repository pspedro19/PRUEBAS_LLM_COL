from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.question import Question
from app.models.user_response import UserResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuestionService:
    """Servicio para manejar preguntas y respuestas"""

    @staticmethod
    async def get_question(question_id: int, db: AsyncSession) -> Optional[Question]:
        """Obtiene una pregunta por su ID"""
        try:
            result = await db.execute(
                select(Question).filter(Question.id == question_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting question {question_id}: {e}")
            return None

    @staticmethod
    async def get_questions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Question]:
        """Obtiene una lista de preguntas"""
        try:
            result = await db.execute(
                select(Question)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            return []

    @staticmethod
    async def create_question(
        db: AsyncSession,
        text: str,
        subject: str,
        difficulty: str,
        correct_answer: str,
        explanation: str = None
    ) -> Optional[Question]:
        """Crea una nueva pregunta"""
        try:
            question = Question(
                text=text,
                subject=subject,
                difficulty=difficulty,
                correct_answer=correct_answer,
                explanation=explanation,
                created_at=datetime.utcnow()
            )
            db.add(question)
            await db.commit()
            await db.refresh(question)
            return question
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            await db.rollback()
            return None

    @staticmethod
    async def update_question(
        db: AsyncSession,
        question_id: int,
        text: str = None,
        subject: str = None,
        difficulty: str = None,
        correct_answer: str = None,
        explanation: str = None
    ) -> Optional[Question]:
        """Actualiza una pregunta existente"""
        try:
            result = await db.execute(
                select(Question).filter(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                return None
            
            if text is not None:
                question.text = text
            if subject is not None:
                question.subject = subject
            if difficulty is not None:
                question.difficulty = difficulty
            if correct_answer is not None:
                question.correct_answer = correct_answer
            if explanation is not None:
                question.explanation = explanation
            
            question.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(question)
            return question
        except Exception as e:
            logger.error(f"Error updating question {question_id}: {e}")
            await db.rollback()
            return None

    @staticmethod
    async def delete_question(db: AsyncSession, question_id: int) -> bool:
        """Elimina una pregunta"""
        try:
            result = await db.execute(
                select(Question).filter(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                return False
            
            await db.delete(question)
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting question {question_id}: {e}")
            await db.rollback()
            return False

    @staticmethod
    async def get_question_responses(
        db: AsyncSession,
        question_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserResponse]:
        """Obtiene las respuestas para una pregunta específica"""
        try:
            result = await db.execute(
                select(UserResponse)
                .filter(UserResponse.question_id == question_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting responses for question {question_id}: {e}")
            return [] 