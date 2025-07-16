"""
Quiz Service for managing quizzes, sessions, and user responses
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_
from fastapi import HTTPException, status
import random
from datetime import datetime, timedelta

from app.models.question import Question
from app.models.user_response import UserResponse
from app.models.session_models import StudySession, SessionStatus
from app.models.user import User
from app.core.database import async_session_maker

class QuizService:
    """Service class for quiz operations"""
    
    @staticmethod
    async def start_quiz_session(
        user_id: int,
        area: str,  # Changed from ICFESArea to str
        difficulty: Optional[str] = None,  # Changed from DifficultyLevel to str
        question_count: int = 10
    ) -> Dict[str, Any]:
        """Start a new quiz session for a user"""
        
        async with async_session_maker() as db:
            # Create new quiz session
            session = StudySession(
                user_id=user_id,
                subject_area=area,
                planned_questions=question_count,
                difficulty_target=difficulty if difficulty else "adaptive",
                status="active",  # Using string instead of enum
                total_questions_answered=0,
                questions_correct=0
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            # Get first question
            first_question = await QuizService._get_next_question(
                db, session.id, area, difficulty
            )
            
            return {
                "session_id": str(session.id),
                "area": area,
                "difficulty": difficulty if difficulty else "MIXED",
                "total_questions": question_count,
                "current_question": first_question,
                "progress": {
                    "answered": 0,
                    "total": question_count,
                    "percentage": 0
                }
            }
    
    @staticmethod
    async def get_current_question(session_id: int) -> Dict[str, Any]:
        """Get the current question for a session"""
        
        async with async_session_maker() as db:
            # Get session
            result = await db.execute(
                select(StudySession).filter(StudySession.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Quiz session not found"
                )
            
            if session.status != "active":  # Using string instead of enum
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Quiz session is not active"
                )
            
            # Check if session is complete
            if session.total_questions_answered >= session.planned_questions:
                return await QuizService._complete_session(db, session)
            
            # Get next question
            question = await QuizService._get_next_question(
                db, session_id, session.subject_area, session.difficulty_target if session.difficulty_target != "adaptive" else None
            )
            
            return {
                "session_id": str(session_id),
                "question": question,
                "progress": {
                    "answered": session.total_questions_answered,
                    "total": session.planned_questions,
                    "percentage": round((session.total_questions_answered / session.planned_questions) * 100, 1)
                },
                "current_score": 0,  # TODO: implement scoring
                "current_xp": 0      # TODO: implement XP tracking
            }
    
    @staticmethod
    async def submit_answer(
        session_id: int,
        question_id: int,
        selected_answer: str
    ) -> Dict[str, Any]:
        """Submit an answer for a question"""
        
        async with async_session_maker() as db:
            # Get session and question
            session_result = await db.execute(
                select(StudySession).filter(StudySession.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            
            question_result = await db.execute(
                select(Question).filter(Question.id == question_id)
            )
            question = question_result.scalar_one_or_none()
            
            if not session or not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session or question not found"
                )
            
            if session.status != SessionStatus.ACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session is not active"
                )
            
            # Check if already answered this question
            existing_response = await db.execute(
                select(UserResponse).filter(
                    and_(
                        UserResponse.user_id == session.user_id,
                        UserResponse.question_id == question_id,
                        UserResponse.session_id == str(session_id)
                    )
                )
            )
            
            if existing_response.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Question already answered"
                )
            
            # Validate answer
            is_correct = selected_answer.upper() == question.correct_answer.upper()
            
            # Calculate points and XP
            base_points = question.points_value
            xp_earned = 0
            
            if is_correct:
                # Bonus points for difficulty
                difficulty_multiplier = {
                    "PRINCIPIANTE": 1.0,
                    "INTERMEDIO": 1.5,
                    "AVANZADO": 2.0
                }
                points_earned = int(base_points * difficulty_multiplier.get(question.difficulty, 1.0))
                xp_earned = points_earned * 2  # XP is double the points
            else:
                points_earned = 0
            
            # Save user response
            user_response = UserResponse(
                user_id=session.user_id,
                question_id=question_id,
                session_id=str(session_id),
                selected_answer=selected_answer.upper(),
                is_correct=is_correct,
                time_taken_seconds=0,  # TODO: implement time tracking
                points_earned=points_earned
            )
            
            db.add(user_response)
            
            # Update session statistics
            session.total_questions_answered += 1
            
            if is_correct:
                session.questions_correct += 1
            
            # Update question statistics
            question.times_answered += 1
            if is_correct:
                question.times_correct += 1
            question.success_rate = (question.times_correct / question.times_answered) * 100
            
            await db.commit()
            
            # Prepare response
            response_data = {
                "session_id": str(session_id),
                "question_id": str(question_id),
                "selected_answer": selected_answer.upper(),
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation,
                "points_earned": points_earned,
                "xp_earned": xp_earned,
                "total_score": session.questions_correct * base_points,
                "total_xp": session.questions_correct * base_points * 2,
                "progress": {
                    "answered": session.total_questions_answered,
                    "total": session.planned_questions,
                    "percentage": round((session.total_questions_answered / session.planned_questions) * 100, 1)
                }
            }
            
            # Check if session is complete
            if session.total_questions_answered >= session.planned_questions:
                completion_data = await QuizService._complete_session(db, session)
                response_data["session_complete"] = True
                response_data["final_results"] = completion_data
            else:
                response_data["session_complete"] = False
                # Get next question
                area = session.subject_area if session.subject_area else "MATEMATICAS"
                difficulty = session.difficulty_target if session.difficulty_target else None
                next_question = await QuizService._get_next_question(
                    db, session_id, area, difficulty
                )
                response_data["next_question"] = next_question
            
            return response_data
    
    @staticmethod
    async def get_session_progress(session_id: int) -> Dict[str, Any]:
        """Get progress information for a session"""
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(StudySession).filter(StudySession.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            
            if session.status != "active":  # Using string instead of enum
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session is not active"
                )
            
            return {
                "session_id": str(session_id),
                "area": session.subject_area or "MATEMATICAS",
                "difficulty": session.difficulty_target or "MIXED",
                "status": session.status,
                "progress": {
                    "answered": session.total_questions_answered,
                    "total": session.planned_questions,
                    "percentage": round((session.total_questions_answered / session.planned_questions) * 100, 1)
                },
                "score": session.questions_correct * 10,  # Approximate score calculation
                "xp_earned": session.questions_correct * 20,  # Approximate XP calculation
                "correct_answers": session.questions_correct,
                "accuracy": round((session.questions_correct / max(session.total_questions_answered, 1)) * 100, 1),
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "completed_at": session.ended_at.isoformat() if session.ended_at else None
            }
    
    @staticmethod
    async def get_user_feedback(session_id: int) -> Dict[str, Any]:
        """Generate personalized feedback based on user performance"""
        
        async with async_session_maker() as db:
            # Get session
            session_result = await db.execute(
                select(StudySession).filter(StudySession.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            
            # Get all responses for this session
            responses_result = await db.execute(
                select(UserResponse, Question).join(Question).filter(
                    UserResponse.session_id == str(session_id)
                )
            )
            responses = responses_result.all()
            
            # Analyze performance
            total_questions = len(responses)
            correct_count = sum(1 for response, _ in responses if response.is_correct)
            accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0
            
            # Identify weak topics
            weak_topics = {}
            strong_topics = {}
            
            for response, question in responses:
                topic = question.topic
                if topic not in weak_topics:
                    weak_topics[topic] = {"correct": 0, "total": 0}
                    strong_topics[topic] = {"correct": 0, "total": 0}
                
                weak_topics[topic]["total"] += 1
                strong_topics[topic]["total"] += 1
                
                if response.is_correct:
                    weak_topics[topic]["correct"] += 1
                    strong_topics[topic]["correct"] += 1
            
            # Calculate topic accuracies
            topic_accuracies = {}
            for topic, stats in weak_topics.items():
                topic_accuracies[topic] = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            # Identify strengths and weaknesses
            strong_topics_list = [topic for topic, acc in topic_accuracies.items() if acc >= 70]
            weak_topics_list = [topic for topic, acc in topic_accuracies.items() if acc < 50]
            
            # Generate feedback message
            if accuracy >= 80:
                performance_level = "Excelente"
                message = "¡Felicidades! Has demostrado un excelente dominio de los temas."
            elif accuracy >= 60:
                performance_level = "Bueno"
                message = "Buen trabajo. Sigues por el camino correcto."
            elif accuracy >= 40:
                performance_level = "Regular"
                message = "Hay espacio para mejorar. Sigue practicando."
            else:
                performance_level = "Necesita mejorar"
                message = "Te recomendamos revisar los conceptos básicos y practicar más."
            
            return {
                "session_id": str(session_id),
                "performance_level": performance_level,
                "accuracy": round(accuracy, 1),
                "total_questions": total_questions,
                "correct_answers": correct_count,
                "message": message,
                "strong_topics": strong_topics_list,
                "weak_topics": weak_topics_list,
                "topic_breakdown": topic_accuracies,
                "recommendations": [
                    "Practica más los temas débiles",
                    "Revisa las explicaciones de las preguntas incorrectas",
                    "Utiliza técnicas de resolución de problemas"
                ]
            }
    
    @staticmethod
    async def _get_next_question(
        db: Session,
        session_id: int,
        area: str,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the next question for a session"""
        
        # Get questions already answered in this session
        answered_questions = await db.execute(
            select(UserResponse.question_id).filter(
                UserResponse.session_id == str(session_id)
            )
        )
        answered_ids = [row[0] for row in answered_questions.fetchall()]
        
        # Build query for available questions
        query = select(Question).filter(
            and_(
                Question.area == area,
                Question.is_active == True,
                ~Question.id.in_(answered_ids) if answered_ids else True
            )
        )
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # Get available questions
        result = await db.execute(query)
        available_questions = result.scalars().all()
        
        if not available_questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No more questions available for this area and difficulty"
            )
        
        # Select random question
        question = random.choice(available_questions)
        
        return {
            "id": str(question.id),
            "title": question.title,
            "content": question.content,
            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d
            },
            "area": question.area,
            "topic": question.topic,
            "subtopic": question.subtopic,
            "difficulty": question.difficulty,
            "points_value": question.points_value
        }
    
    @staticmethod
    async def _complete_session(db: Session, session: StudySession) -> Dict[str, Any]:
        """Complete a quiz session and update user stats"""
        
        # Mark session as completed
        session.status = "completed"  # Using string instead of enum
        session.ended_at = datetime.utcnow()
        session.accuracy_percentage = (session.questions_correct / session.planned_questions) * 100
        
        # Calculate final metrics
        accuracy = (session.questions_correct / session.total_questions_answered * 100) if session.total_questions_answered > 0 else 0
        xp_earned = session.questions_correct * 20  # Approximate XP calculation
        
        # Update user stats
        user_result = await db.execute(
            select(User).filter(User.id == session.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            # Add XP to user
            user.xp += xp_earned
            
            # Level up logic (every 1000 XP = 1 level)
            new_level = (user.xp // 1000) + 1
            leveled_up = new_level > user.level
            user.level = new_level
            
            await db.commit()
        
        return {
            "session_id": str(session.id),
            "status": "completed",
            "final_stats": {
                "total_questions": session.planned_questions,
                "correct_answers": session.questions_correct,
                "accuracy": round(accuracy, 1),
                "final_score": session.questions_correct * 10,  # Approximate score calculation
                "xp_earned": xp_earned,
                "duration_minutes": (session.ended_at - session.started_at).total_seconds() / 60
            },
            "level_info": {
                "current_level": user.level if user else 1,
                "total_xp": user.xp if user else 0,
                "leveled_up": leveled_up if user else False
            } if user else None
        }

    @staticmethod
    async def get_available_areas() -> List[Dict[str, Any]]:
        """Get all available quiz areas with question counts"""
        
        async with async_session_maker() as db:
            # Get question counts by area and difficulty
            result = await db.execute(
                select(
                    Question.area,
                    Question.difficulty,
                    func.count(Question.id).label('count')
                ).filter(Question.is_active == True)
                .group_by(Question.area, Question.difficulty)
            )
            
            data = result.all()
            
            # Organize data by area
            areas = {}
            for row in data:
                area = row.area
                difficulty = row.difficulty
                count = row.count
                
                if area not in areas:
                    areas[area] = {
                        "area": area,
                        "total_questions": 0,
                        "difficulties": {}
                    }
                
                areas[area]["difficulties"][difficulty] = count
                areas[area]["total_questions"] += count
            
            return list(areas.values()) 