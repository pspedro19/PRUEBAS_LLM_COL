"""
MINIMAL BACKEND - SOLO LOGIN FUNCIONAL + QUIZ
Evitando todos los problemas de enum
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, select, and_, func
from sqlalchemy.sql import func
import asyncio
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import random

# Configuración simple
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database URL
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@mathquest-db:5432/mathquest_db"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Base para modelos simples
class Base(DeclarativeBase):
    pass

# Modelo User simplificado
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)

# Modelo Question simplificado
class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    explanation = Column(Text)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_answer = Column(String(1), nullable=False)
    area = Column(String(50), nullable=False, default='matematicas')
    topic = Column(String(100), nullable=False)
    subtopic = Column(String(100))
    difficulty = Column(String(20), nullable=False, default='intermedio')
    times_answered = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    points_value = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Modelo StudySession simplificado
class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_area = Column(String(30), nullable=True, index=True)
    planned_questions = Column(Integer, nullable=True)
    difficulty_target = Column(String(20), nullable=True)
    status = Column(String(20), default='active', index=True)
    current_question_index = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    accuracy_percentage = Column(Float, nullable=True)

# Modelo UserResponse simplificado
class UserResponse(Base):
    __tablename__ = "user_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    selected_answer = Column(String(1), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)
    session_id = Column(String(100))
    quiz_mode = Column(String(50))
    points_earned = Column(Integer, default=0)
    answered_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class StartQuizRequest(BaseModel):
    area: str
    difficulty: Optional[str] = None
    question_count: int = 5

class SubmitAnswerRequest(BaseModel):
    question_id: str
    selected_answer: str

# Engine y sesión
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session_maker() as session:
        yield session

# Funciones de autenticación
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

# FastAPI app
app = FastAPI(title="MathQuest Auth + Quiz API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint - OAuth2 compatible"""
    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "access": access_token,
            "refresh": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_verified": True
            }
        }
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/v1/auth/register")
async def register(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register endpoint for frontend compatibility"""
    try:
        # Check if user exists
        result = await db.execute(select(User).filter(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username if user_data.username else user_data.email.split("@")[0],
            email=user_data.email,
            password_hash=hashed_password,
            display_name=f"{user_data.first_name} {user_data.last_name}".strip(),
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(new_user.id)}, expires_delta=access_token_expires
        )
        
        return {
            "tokens": {
                "access": access_token,
                "refresh": access_token
            },
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "is_verified": True
            }
        }
    except Exception as e:
        print(f"Register error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.get("/api/auth/stats/")
async def get_user_stats(
    current_user: User = Depends(get_current_user)
):
    """Get user stats for frontend compatibility"""
    return {
        "user_info": {
            "id": current_user.id,
            "email": current_user.email,
            "hero_class": "warrior",
            "level": 1,
            "experience_points": 0
        },
        "assessments": {
            "initial_completed": True,
            "vocational_completed": True,
            "assigned_role": "warrior"
        }
    }

@app.post("/api/auth/complete-assessment/")
async def complete_assessment(
    assessment_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Complete assessment for frontend compatibility"""
    return {
        "success": True,
        "message": "Assessment completed",
        "assigned_role": assessment_data.get("assigned_role", "warrior")
    }

@app.post("/api/quiz/start-session")
async def start_quiz_session(
    request: StartQuizRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new quiz session"""
    try:
        # Validate area
        valid_areas = ["matematicas", "lectura_critica", "ciencias_naturales", "sociales_ciudadanas", "ingles"]
        if request.area.lower() not in valid_areas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid area: {request.area}"
            )
        
        # Create new quiz session
        session = StudySession(
            user_id=current_user.id,
            subject_area=request.area.lower(),
            planned_questions=request.question_count,
            difficulty_target=request.difficulty if request.difficulty else "adaptive",
            status="active",
            total_questions_answered=0,
            questions_correct=0
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Get first question
        query = select(Question).filter(
            Question.area == request.area.lower(),
            Question.is_active == True
        )
        
        if request.difficulty and request.difficulty != "adaptive":
            query = query.filter(Question.difficulty == request.difficulty.lower())
        
        result = await db.execute(query.order_by(func.random()).limit(1))
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No questions available for this area"
            )
        
        question_data = {
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
            "difficulty": question.difficulty,
            "points_value": question.points_value
        }
        
        return {
            "success": True,
            "message": "Quiz session started successfully",
            "data": {
                "session_id": str(session.id),
                "area": request.area,
                "difficulty": request.difficulty if request.difficulty else "MIXED",
                "total_questions": request.question_count,
                "current_question": question_data,
                "progress": {
                    "answered": 0,
                    "total": request.question_count,
                    "percentage": 0
                }
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Start quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start quiz session: {str(e)}"
        )

@app.get("/api/quiz/session/{session_id}/current-question")
async def get_current_question(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current question for a session"""
    try:
        session_int = int(session_id)
        
        # Get session
        result = await db.execute(
            select(StudySession).filter(StudySession.id == session_int)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz session not found"
            )
        
        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quiz session is not active"
            )
        
        # Check if session is complete
        if session.total_questions_answered >= session.planned_questions:
            # Mark session as completed
            session.status = "completed"
            session.ended_at = datetime.utcnow()
            session.accuracy_percentage = (session.questions_correct / session.planned_questions) * 100
            await db.commit()
            
            return {
                "success": True,
                "data": {
                    "session_complete": True,
                    "final_score": session.questions_correct,
                    "total_questions": session.planned_questions,
                    "accuracy": session.accuracy_percentage
                }
            }
        
        # Get next question
        query = select(Question).filter(
            Question.area == session.subject_area,
            Question.is_active == True
        )
        
        # Exclude already answered questions
        answered_questions = await db.execute(
            select(UserResponse.question_id).filter(
                UserResponse.user_id == session.user_id,
                UserResponse.session_id == str(session_id)
            )
        )
        answered_ids = [row[0] for row in answered_questions.fetchall()]
        
        if answered_ids:
            query = query.filter(~Question.id.in_(answered_ids))
        
        result = await db.execute(query.order_by(func.random()).limit(1))
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No more questions available"
            )
        
        question_data = {
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
            "difficulty": question.difficulty,
            "points_value": question.points_value
        }
        
        return {
            "success": True,
            "data": {
                "session_id": str(session_id),
                "question": question_data,
                "progress": {
                    "answered": session.total_questions_answered,
                    "total": session.planned_questions,
                    "percentage": round((session.total_questions_answered / session.planned_questions) * 100, 1)
                }
            }
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Get question error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current question: {str(e)}"
        )

@app.post("/api/quiz/session/{session_id}/submit-answer")
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit an answer for a question"""
    try:
        session_int = int(session_id)
        question_int = int(request.question_id)
        
        # Get session and question
        session_result = await db.execute(
            select(StudySession).filter(StudySession.id == session_int)
        )
        session = session_result.scalar_one_or_none()
        
        question_result = await db.execute(
            select(Question).filter(Question.id == question_int)
        )
        question = question_result.scalar_one_or_none()
        
        if not session or not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session or question not found"
            )
        
        # Check if already answered this question
        existing_response = await db.execute(
            select(UserResponse).filter(
                and_(
                    UserResponse.user_id == session.user_id,
                    UserResponse.question_id == question_int,
                    UserResponse.session_id == str(session_int)
                )
            )
        )
        
        if existing_response.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question already answered"
            )
        
        # Validate answer
        is_correct = request.selected_answer.upper() == question.correct_answer.upper()
        
        # Calculate points
        points_earned = question.points_value if is_correct else 0
        
        # Save user response
        user_response = UserResponse(
            user_id=session.user_id,
            question_id=question_int,
            session_id=str(session_int),
            selected_answer=request.selected_answer.upper(),
            is_correct=is_correct,
            time_taken_seconds=0,
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
        
        return {
            "success": True,
            "message": "Answer submitted successfully",
            "data": {
                "session_id": str(session_int),
                "question_id": str(question_int),
                "selected_answer": request.selected_answer.upper(),
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation,
                "points_earned": points_earned,
                "session_complete": session.total_questions_answered >= session.planned_questions
            }
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Submit answer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )

@app.get("/api/quiz/session/{session_id}/feedback")
async def get_session_feedback(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get feedback for completed session"""
    try:
        session_int = int(session_id)
        
        # Get session
        result = await db.execute(
            select(StudySession).filter(StudySession.id == session_int)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "success": True,
            "data": {
                "session_id": str(session_int),
                "final_score": session.questions_correct,
                "total_questions": session.planned_questions,
                "accuracy": round(session.accuracy_percentage or 0, 1),
                "feedback": {
                    "message": "¡Buen trabajo!" if (session.accuracy_percentage or 0) >= 70 else "Sigue practicando",
                    "strengths": ["Matemáticas básicas"],
                    "improvements": ["Álgebra avanzada"] if (session.accuracy_percentage or 0) < 70 else []
                }
            }
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except Exception as e:
        print(f"Feedback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback: {str(e)}"
        )

@app.get("/api/quiz/session/{session_id}/progress")
async def get_session_progress(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get session progress"""
    try:
        session_int = int(session_id)
        
        result = await db.execute(
            select(StudySession).filter(StudySession.id == session_int)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "success": True,
            "data": {
                "session_id": str(session_int),
                "answered": session.total_questions_answered,
                "total": session.planned_questions,
                "percentage": round((session.total_questions_answered / session.planned_questions) * 100, 1),
                "correct": session.questions_correct,
                "accuracy": round((session.questions_correct / max(session.total_questions_answered, 1)) * 100, 1)
            }
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    except Exception as e:
        print(f"Progress error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "MathQuest Auth + Quiz API - Running"}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 