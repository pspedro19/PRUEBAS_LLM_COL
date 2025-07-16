"""
Quiz endpoints for the ICFES preparation system - FIXED VERSION WITHOUT ENUMS
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.user import User
from app.services.quiz_service import QuizService

router = APIRouter()

# Pydantic models for requests/responses
class StartQuizRequest(BaseModel):
    area: str  # Using string instead of enum
    difficulty: Optional[str] = None  # Using string instead of enum
    question_count: int = 10

class SubmitAnswerRequest(BaseModel):
    question_id: str
    selected_answer: str

class QuizAreaResponse(BaseModel):
    area: str
    total_questions: int
    difficulties: dict

@router.get("/areas", response_model=List[QuizAreaResponse])
async def get_available_areas():
    """Get all available quiz areas with question counts"""
    return await QuizService.get_available_areas()

@router.post("/start-session")
async def start_quiz_session(
    request: StartQuizRequest,
    current_user: User = Depends(get_current_user)
):
    """Start a new quiz session"""
    try:
        # Validate area (simple string validation)
        valid_areas = ["matematicas", "lectura_critica", "ciencias_naturales", "sociales_ciudadanas", "ingles"]
        if request.area not in valid_areas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid area: {request.area}"
            )
        
        # Validate difficulty if provided
        if request.difficulty:
            valid_difficulties = ["principiante", "intermedio", "avanzado", "experto"]
            if request.difficulty not in valid_difficulties:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid difficulty: {request.difficulty}"
                )
        
        session_data = await QuizService.start_quiz_session(
            user_id=current_user.id,
            area=request.area,
            difficulty=request.difficulty,
            question_count=request.question_count
        )
        return {
            "success": True,
            "message": "Quiz session started successfully",
            "data": session_data
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start quiz session: {str(e)}"
        )

@router.get("/session/{session_id}/current-question")
async def get_current_question(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the current question for a session"""
    try:
        session_int = int(session_id)
        question_data = await QuizService.get_current_question(session_int)
        return {
            "success": True,
            "data": question_data
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current question: {str(e)}"
        )

@router.post("/session/{session_id}/submit-answer")
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit an answer for a question"""
    try:
        session_int = int(session_id)
        question_int = int(request.question_id)
        
        result = await QuizService.submit_answer(
            session_id=session_int,
            question_id=question_int,
            selected_answer=request.selected_answer
        )
        
        return {
            "success": True,
            "message": "Answer submitted successfully",
            "data": result
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )

@router.get("/session/{session_id}/progress")
async def get_session_progress(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get progress information for a session"""
    try:
        session_int = int(session_id)
        progress_data = await QuizService.get_session_progress(session_int)
        return {
            "success": True,
            "data": progress_data
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session progress: {str(e)}"
        )

@router.get("/session/{session_id}/feedback")
async def get_session_feedback(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get personalized feedback for a completed session"""
    try:
        session_int = int(session_id)
        feedback_data = await QuizService.get_user_feedback(session_int)
        return {
            "success": True,
            "data": feedback_data
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session feedback: {str(e)}"
        )

# Endpoints for frontend integration
@router.get("/areas/{area_name}/questions/count")
async def get_area_question_count(area_name: str):
    """Get question count for a specific area"""
    try:
        # Simple string validation instead of enum
        valid_areas = ["matematicas", "lectura_critica", "ciencias_naturales", "sociales_ciudadanas", "ingles"]
        area = area_name.lower()
        
        if area not in valid_areas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid area name"
            )
        
        areas = await QuizService.get_available_areas()
        
        for area_data in areas:
            if area_data["area"] == area:
                return {
                    "success": True,
                    "data": area_data
                }
        
        return {
            "success": True,
            "data": {
                "area": area,
                "total_questions": 0,
                "difficulties": {}
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get area question count: {str(e)}"
        )

@router.get("/user/stats")
async def get_user_quiz_stats(
    current_user: User = Depends(get_current_user)
):
    """Get user quiz statistics"""
    try:
        # TODO: Implement user stats functionality
        return {
            "success": True,
            "data": {
                "total_quizzes": 0,
                "total_questions": 0,
                "average_score": 0,
                "favorite_area": "matematicas"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        ) 