from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.services.chain_of_thought_service import ChainOfThoughtService
from app.services.irt_service import IRTService
from app.models.user import User
from app.models.question import Question
from app.models.response import UserResponse, ChainOfThoughtStep
from app.models.session_models import StudySession
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class AnswerQuestionRequest(BaseModel):
    question_id: str
    selected_answer: str
    response_time_ms: int
    confidence_level: Optional[float] = None
    explanation_type: str = "detailed"  # "brief", "detailed", "comprehensive"

class ChainOfThoughtStepResponse(BaseModel):
    step_number: int
    title: str
    content: str
    step_type: str
    
class ExplanationResponse(BaseModel):
    success: bool
    summary: str
    steps: List[ChainOfThoughtStepResponse]
    common_errors: List[str]
    tips: List[str]
    key_concepts: List[str]
    connections: str
    quality_score: float
    is_correct: bool
    correct_answer: str
    user_answer: str
    
class QuestionWithExplanationResponse(BaseModel):
    question_id: str
    question_text: str
    options: List[str]
    subject_area: str
    competencia: str
    explanation: Optional[ExplanationResponse] = None

@router.post("/answer-and-explain", response_model=ExplanationResponse)
async def answer_question_with_explanation(
    request: AnswerQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint principal del MVP: responder una pregunta y obtener explicación con razonamiento en cadena
    """
    try:
        logger.info(f"Processing answer and explanation for user {current_user.id}, question {request.question_id}")
        
        # 1. Obtener la pregunta
        result = await db.execute(
            select(Question).filter(Question.id == request.question_id)
        )
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # 2. Validar la respuesta seleccionada
        if request.selected_answer not in ['A', 'B', 'C', 'D']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid answer format. Must be A, B, C, or D"
            )
        
        # 3. Determinar si la respuesta es correcta
        is_correct = request.selected_answer == question.correct_answer
        
        # 4. Crear registro de respuesta del usuario
        user_response = UserResponse(
            user_id=current_user.id,
            question_id=question.id,
            selected_answer=request.selected_answer,
            is_correct=is_correct,
            response_time_ms=request.response_time_ms,
            confidence_level=request.confidence_level,
            explanation_requested=True,
            explanation_type=request.explanation_type
        )
        
        db.add(user_response)
        await db.flush()  # Para obtener el ID antes del commit
        
        # 5. Actualizar estadísticas de la pregunta
        question.update_statistics(is_correct, request.response_time_ms)
        
        # 6. Generar explicación con razonamiento en cadena
        cot_service = ChainOfThoughtService()
        explanation_result = await cot_service.generate_explanation(
            question=question,
            user_response=user_response,
            user=current_user,
            explanation_type=request.explanation_type,
            db=db
        )
        
        # 7. Actualizar IRT si hay parámetros disponibles
        if question.irt_parameters and question.irt_parameters.is_calibrated:
            irt_service = IRTService()
            new_theta, std_error = await irt_service.update_user_theta(
                user_id=str(current_user.id),
                subject_area=question.subject_area,
                new_response=(
                    is_correct,
                    question.irt_parameters.discrimination_a,
                    question.irt_parameters.difficulty_b,
                    question.irt_parameters.guessing_c
                ),
                db=db
            )
            
            user_response.user_theta_after = new_theta
            logger.info(f"Updated theta for user {current_user.id}: {new_theta:.3f}")
        
        await db.commit()
        
        # 8. Construir respuesta
        if explanation_result["success"]:
            explanation_data = explanation_result["explanation"]
            
            steps = [
                ChainOfThoughtStepResponse(
                    step_number=step["step_number"],
                    title=step["title"],
                    content=step["content"],
                    step_type=step["step_type"]
                )
                for step in explanation_data["steps"]
            ]
            
            return ExplanationResponse(
                success=True,
                summary=explanation_data["summary"],
                steps=steps,
                common_errors=explanation_data["common_errors"],
                tips=explanation_data["tips"],
                key_concepts=explanation_data["key_concepts"],
                connections=explanation_data["connections"],
                quality_score=explanation_data["quality_score"],
                is_correct=is_correct,
                correct_answer=question.correct_answer,
                user_answer=request.selected_answer
            )
        else:
            # Fallback si falla la IA
            fallback = explanation_result["fallback_explanation"]
            
            steps = [
                ChainOfThoughtStepResponse(
                    step_number=step["step_number"],
                    title=step["title"],
                    content=step["content"],
                    step_type=step["step_type"]
                )
                for step in fallback["steps"]
            ]
            
            return ExplanationResponse(
                success=False,
                summary=fallback["summary"],
                steps=steps,
                common_errors=fallback["common_errors"],
                tips=fallback["tips"],
                key_concepts=fallback["key_concepts"],
                connections=fallback["connections"],
                quality_score=fallback["quality_score"],
                is_correct=is_correct,
                correct_answer=question.correct_answer,
                user_answer=request.selected_answer
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in answer_question_with_explanation: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing question response"
        )

@router.get("/next-question/{subject_area}")
async def get_next_adaptive_question(
    subject_area: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener la siguiente pregunta adaptativa para el usuario
    """
    try:
        # Validar área
        valid_areas = ["matematicas", "lectura_critica", "ciencias_naturales", "ciencias_sociales", "ingles"]
        if subject_area not in valid_areas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid subject area. Must be one of: {', '.join(valid_areas)}"
            )
        
        # Usar IRT para seleccionar siguiente pregunta
        irt_service = IRTService()
        question = await irt_service.select_next_question(
            user_id=str(current_user.id),
            subject_area=subject_area,
            db=db
        )
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No more questions available for {subject_area}"
            )
        
        return {
            "id": str(question.id),
            "question_text": question.question_text,
            "options": question.options,
            "subject_area": question.subject_area,
            "competencia": question.competencia,
            "sub_competencia": question.sub_competencia,
            "estimated_time_seconds": question.estimated_time_seconds,
            "difficulty_level": question.difficulty_level
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error selecting next question"
        )

@router.get("/explanation/{response_id}")
async def get_saved_explanation(
    response_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener una explicación previamente generada
    """
    try:
        # Verificar que la respuesta pertenece al usuario
        result = await db.execute(
            select(UserResponse)
            .filter(
                UserResponse.id == response_id,
                UserResponse.user_id == current_user.id
            )
        )
        user_response = result.scalar_one_or_none()
        
        if not user_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found"
            )
        
        # Obtener pasos del razonamiento
        result = await db.execute(
            select(ChainOfThoughtStep)
            .filter(ChainOfThoughtStep.user_response_id == response_id)
            .order_by(ChainOfThoughtStep.step_number)
        )
        cot_steps = result.scalars().all()
        
        # Obtener pregunta
        result = await db.execute(
            select(Question).filter(Question.id == user_response.question_id)
        )
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Construir respuesta
        steps = [
            ChainOfThoughtStepResponse(
                step_number=step.step_number,
                title=step.title,
                content=step.content,
                step_type=step.step_type
            )
            for step in cot_steps
        ]
        
        return ExplanationResponse(
            success=True,
            summary="Explicación guardada",
            steps=steps,
            common_errors=[],
            tips=[],
            key_concepts=[],
            connections="",
            quality_score=user_response.cot_quality_score or 0.8,
            is_correct=user_response.is_correct,
            correct_answer=question.correct_answer,
            user_answer=user_response.selected_answer
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting saved explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving explanation"
        )

@router.post("/rate-explanation/{response_id}")
async def rate_explanation(
    response_id: str,
    rating: int,
    feedback: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calificar la calidad de una explicación generada
    """
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Verificar que la respuesta pertenece al usuario
        result = await db.execute(
            select(UserResponse)
            .filter(
                UserResponse.id == response_id,
                UserResponse.user_id == current_user.id
            )
        )
        user_response = result.scalar_one_or_none()
        
        if not user_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found"
            )
        
        # Actualizar rating
        user_response.user_rating = rating
        if feedback:
            user_response.user_feedback = feedback
        
        # También actualizar los pasos individuales
        result = await db.execute(
            select(ChainOfThoughtStep)
            .filter(ChainOfThoughtStep.user_response_id == response_id)
        )
        cot_steps = result.scalars().all()
        
        for step in cot_steps:
            step.user_rating = rating
            if feedback:
                step.user_feedback = feedback
        
        await db.commit()
        
        return {"message": "Rating saved successfully", "rating": rating}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating explanation: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving rating"
        ) 