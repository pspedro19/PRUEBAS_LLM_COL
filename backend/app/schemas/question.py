from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"
    EXPERTO = "experto"

class ICFESArea(str, Enum):
    MATEMATICAS = "matematicas"
    LECTURA_CRITICA = "lectura_critica"
    CIENCIAS_NATURALES = "ciencias_naturales"
    SOCIALES_CIUDADANAS = "sociales_ciudadanas"
    INGLES = "ingles"

class QuizMode(str, Enum):
    PRACTICE = "practice"
    EXAM = "exam"
    DUNGEON = "dungeon"
    QUICK = "quick"

# Base schemas
class QuestionBase(BaseModel):
    title: str = Field(..., max_length=500)
    content: str
    explanation: Optional[str] = None
    option_a: str = Field(..., max_length=500)
    option_b: str = Field(..., max_length=500)
    option_c: str = Field(..., max_length=500)
    option_d: str = Field(..., max_length=500)
    correct_answer: str = Field(..., pattern="^[ABCD]$")
    area: ICFESArea = ICFESArea.MATEMATICAS
    topic: str = Field(..., max_length=100)
    subtopic: Optional[str] = Field(None, max_length=100)
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIO
    points_value: int = Field(10, ge=1, le=100)
    is_active: bool = True

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    explanation: Optional[str] = None
    option_a: Optional[str] = Field(None, max_length=500)
    option_b: Optional[str] = Field(None, max_length=500)
    option_c: Optional[str] = Field(None, max_length=500)
    option_d: Optional[str] = Field(None, max_length=500)
    correct_answer: Optional[str] = Field(None, pattern="^[ABCD]$")
    area: Optional[ICFESArea] = None
    topic: Optional[str] = Field(None, max_length=100)
    subtopic: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[DifficultyLevel] = None
    points_value: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None

class Question(QuestionBase):
    id: int
    times_answered: int = 0
    times_correct: int = 0
    success_rate: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuestionForQuiz(BaseModel):
    """Pregunta sin mostrar la respuesta correcta ni explicación"""
    id: int
    title: str
    content: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    area: ICFESArea
    topic: str
    subtopic: Optional[str]
    difficulty: DifficultyLevel
    points_value: int
    
    class Config:
        from_attributes = True

# User Response schemas
class UserResponseBase(BaseModel):
    selected_answer: str = Field(..., pattern="^[ABCD]$")
    time_taken_seconds: Optional[int] = Field(None, ge=0)
    session_id: Optional[str] = Field(None, max_length=100)
    quiz_mode: Optional[QuizMode] = QuizMode.PRACTICE
    hints_used: int = Field(0, ge=0)
    confidence_level: Optional[int] = Field(None, ge=1, le=5)
    error_type: Optional[str] = Field(None, max_length=100)

class UserResponseCreate(UserResponseBase):
    question_id: int

class UserResponseSubmit(BaseModel):
    """Schema para enviar una respuesta desde el frontend"""
    question_id: int
    selected_answer: str = Field(..., pattern="^[ABCD]$")
    time_taken_seconds: Optional[int] = Field(None, ge=0)
    hints_used: int = Field(0, ge=0)
    confidence_level: Optional[int] = Field(None, ge=1, le=5)

class UserResponse(UserResponseBase):
    id: int
    user_id: int
    question_id: int
    is_correct: bool
    points_earned: int = 0
    difficulty_at_time: Optional[str] = None
    answered_at: datetime
    
    class Config:
        from_attributes = True

class UserResponseWithFeedback(UserResponse):
    """Respuesta con feedback y datos de la pregunta"""
    feedback_message: str
    correct_answer: str
    explanation: Optional[str] = None
    question_title: str

# Quiz session schemas
class QuizSessionStart(BaseModel):
    area: ICFESArea
    topic: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    quiz_mode: QuizMode = QuizMode.PRACTICE
    max_questions: int = Field(5, ge=1, le=50)

class QuizSessionInfo(BaseModel):
    session_id: str
    area: ICFESArea
    topic: Optional[str]
    difficulty: Optional[DifficultyLevel]
    quiz_mode: QuizMode
    total_questions: int
    current_question_index: int
    questions_answered: int
    questions_correct: int
    total_points: int
    started_at: datetime

class QuizProgress(BaseModel):
    session_id: str
    total_questions: int
    current_question: int
    questions_answered: int
    questions_correct: int
    accuracy_percentage: float
    total_points: int
    average_time_per_question: Optional[float] = None

# Question filters and search
class QuestionFilters(BaseModel):
    area: Optional[ICFESArea] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    is_active: bool = True
    min_success_rate: Optional[float] = Field(None, ge=0, le=100)
    max_success_rate: Optional[float] = Field(None, ge=0, le=100)

class QuestionSearch(BaseModel):
    query: Optional[str] = None
    filters: QuestionFilters = QuestionFilters()
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

# Statistics and analytics
class TopicStats(BaseModel):
    topic: str
    total_questions: int
    questions_answered: int
    questions_correct: int
    accuracy_percentage: float
    average_points: float
    total_time_spent: int  # en segundos

class UserQuizStats(BaseModel):
    user_id: int
    area: ICFESArea
    total_questions_answered: int
    total_questions_correct: int
    overall_accuracy: float
    total_points_earned: int
    topics_stats: List[TopicStats]
    average_time_per_question: float
    favorite_difficulty: DifficultyLevel
    weakest_topics: List[str]
    strongest_topics: List[str]

# Recommendations
class RecommendedQuestion(BaseModel):
    question: QuestionForQuiz
    reason: str  # Por qué se recomienda esta pregunta
    priority: int = Field(..., ge=1, le=10)  # 1 = máxima prioridad

class QuestionRecommendations(BaseModel):
    user_id: int
    area: ICFESArea
    recommended_questions: List[RecommendedQuestion]
    focus_topics: List[str]
    suggested_difficulty: DifficultyLevel
    reason_summary: str 