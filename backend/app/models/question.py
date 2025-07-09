from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class SubjectArea(str, Enum):
    MATEMATICAS = "matematicas"
    LECTURA_CRITICA = "lectura_critica"
    CIENCIAS_NATURALES = "ciencias_naturales"
    CIENCIAS_SOCIALES = "ciencias_sociales"
    INGLES = "ingles"


class DifficultyLevel(str, Enum):
    VERY_EASY = "very_easy"      # theta < -1.5
    EASY = "easy"                # -1.5 <= theta < -0.5
    MEDIUM = "medium"            # -0.5 <= theta < 0.5
    HARD = "hard"                # 0.5 <= theta < 1.5
    VERY_HARD = "very_hard"      # theta >= 1.5


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    OPEN_ENDED = "open_ended"


class QuestionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Basic Question Information
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default=QuestionType.MULTIPLE_CHOICE.value)
    subject_area = Column(String(30), nullable=False, index=True)
    
    # Multiple choice options
    options = Column(JSON, nullable=True)  # ["A) Option 1", "B) Option 2", ...]
    correct_answer = Column(String(10), nullable=False)  # "A", "B", "C", "D" or "True"/"False"
    
    # ICFES Competency Framework
    competencia = Column(String(100), nullable=True, index=True)
    sub_competencia = Column(String(200), nullable=True)
    contenido_especifico = Column(String(300), nullable=True)
    contexto = Column(String(50), nullable=True)  # "personal", "laboral", "social", "cientifico"
    nivel_bloom = Column(String(50), nullable=True)  # "recordar", "comprender", "aplicar", etc.
    
    # Content and Difficulty
    difficulty_level = Column(String(20), nullable=True, index=True)
    estimated_time_seconds = Column(Integer, default=120)  # 2 minutes default
    
    # Rich Content
    image_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    additional_resources = Column(JSON, nullable=True)
    
    # Chain of Thought Explanation
    explanation_steps = Column(JSON, nullable=True)  # Step-by-step explanation
    common_mistakes = Column(JSON, nullable=True)   # Common wrong answers and why
    learning_objectives = Column(JSON, nullable=True)  # What this question teaches
    
    # Metadata
    source = Column(String(100), nullable=True)  # "ICFES_OFICIAL", "GENERATED", "TEACHER_CREATED"
    tags = Column(JSON, nullable=True)  # ["algebra", "ecuaciones", "grado_11"]
    keywords = Column(JSON, nullable=True)  # For search functionality
    
    # Status and Review
    status = Column(String(20), default=QuestionStatus.ACTIVE.value)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Statistics
    times_answered = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    irt_parameters = relationship("IRTParameters", back_populates="question", uselist=False, cascade="all, delete-orphan")
    legacy_responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")
    user_responses = relationship("UserResponse", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, area={self.subject_area}, difficulty={self.difficulty_level})>"
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate the accuracy rate for this question"""
        if self.times_answered == 0:
            return 0.0
        return (self.times_correct / self.times_answered) * 100
    
    def update_statistics(self, is_correct: bool, response_time_ms: int):
        """Update question statistics after a response"""
        self.times_answered += 1
        if is_correct:
            self.times_correct += 1
        
        # Update average response time
        if self.average_response_time is None:
            self.average_response_time = response_time_ms
        else:
            # Moving average
            total_time = self.average_response_time * (self.times_answered - 1) + response_time_ms
            self.average_response_time = total_time / self.times_answered


class IRTParameters(Base):
    __tablename__ = "irt_parameters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id"), unique=True, nullable=False)
    
    # IRT Model Parameters (3PL Model)
    discrimination_a = Column(Float, default=1.0)  # How well the item discriminates between abilities
    difficulty_b = Column(Float, default=0.0)      # Item difficulty (theta level where P(correct) = 0.5)
    guessing_c = Column(Float, default=0.0)        # Probability of guessing correctly (0-1)
    
    # Parameter estimation metadata
    estimation_method = Column(String(50), default="marginal_maximum_likelihood")
    sample_size = Column(Integer, default=0)  # Number of responses used for calibration
    standard_error_a = Column(Float, nullable=True)
    standard_error_b = Column(Float, nullable=True)
    standard_error_c = Column(Float, nullable=True)
    
    # Model fit statistics
    chi_square = Column(Float, nullable=True)
    degrees_of_freedom = Column(Integer, nullable=True)
    p_value = Column(Float, nullable=True)
    
    # Calibration status
    is_calibrated = Column(Boolean, default=False)
    needs_recalibration = Column(Boolean, default=False)
    last_calibrated = Column(DateTime(timezone=True), nullable=True)
    
    # Information function values at key theta points
    info_at_minus_2 = Column(Float, nullable=True)
    info_at_minus_1 = Column(Float, nullable=True)
    info_at_0 = Column(Float, nullable=True)
    info_at_plus_1 = Column(Float, nullable=True)
    info_at_plus_2 = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="irt_parameters")
    
    def __repr__(self):
        return f"<IRTParameters(question_id={self.question_id}, a={self.discrimination_a:.2f}, b={self.difficulty_b:.2f})>"
    
    def probability_correct(self, theta: float) -> float:
        """
        Calculate probability of correct response using 3PL IRT model
        P(θ) = c + (1 - c) / (1 + exp(-a(θ - b)))
        """
        import math
        
        if self.discrimination_a == 0:
            return 0.5  # No discrimination
        
        exponent = -self.discrimination_a * (theta - self.difficulty_b)
        try:
            probability = self.guessing_c + (1 - self.guessing_c) / (1 + math.exp(exponent))
            return max(0.0, min(1.0, probability))  # Clamp between 0 and 1
        except OverflowError:
            # Handle numerical overflow
            if exponent > 0:
                return self.guessing_c
            else:
                return 1.0
    
    def information_function(self, theta: float) -> float:
        """
        Calculate Fisher Information at given theta
        I(θ) = a² * [P(θ) - c]² * [1 - P(θ)] / [(1 - c)² * P(θ)]
        """
        p_theta = self.probability_correct(theta)
        
        if p_theta == 0 or p_theta == 1:
            return 0.0
        
        numerator = (self.discrimination_a ** 2) * ((p_theta - self.guessing_c) ** 2) * (1 - p_theta)
        denominator = ((1 - self.guessing_c) ** 2) * p_theta
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def optimal_theta_range(self) -> tuple[float, float]:
        """
        Calculate the theta range where this item provides maximum information
        Typically around b ± 2/a for 3PL models
        """
        range_width = 2 / max(self.discrimination_a, 0.1)  # Avoid division by zero
        return (
            self.difficulty_b - range_width,
            self.difficulty_b + range_width
        )


class QuestionArea(Base):
    __tablename__ = "question_areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False)  # "matematicas", "lectura_critica", etc.
    display_name = Column(String(100), nullable=False)  # "Matemáticas", "Lectura Crítica", etc.
    description = Column(Text, nullable=True)
    
    # Area configuration
    competencias = Column(JSON, nullable=True)  # List of competencies for this area
    sub_areas = Column(JSON, nullable=True)     # List of sub-areas
    
    # IRT Configuration for this area
    default_theta = Column(Float, default=0.0)
    theta_range_min = Column(Float, default=-3.0)
    theta_range_max = Column(Float, default=3.0)
    
    # Adaptive testing configuration
    min_questions = Column(Integer, default=10)
    max_questions = Column(Integer, default=50)
    target_sem = Column(Float, default=0.3)  # Standard error of measurement
    
    # Content weighting
    content_weights = Column(JSON, nullable=True)  # Weight different topics/competencies
    
    # Display and UI
    icon_url = Column(String(255), nullable=True)
    color_hex = Column(String(7), nullable=True)  # "#FF5733"
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<QuestionArea(name={self.name}, display_name={self.display_name})>"


class QuestionResponse(Base):
    """Historical responses to questions for analysis and improvement"""
    __tablename__ = "question_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Response data
    selected_answer = Column(String(10), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    
    # User state when answering
    user_theta_before = Column(Float, nullable=True)
    user_theta_after = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)  # 0-1 scale
    
    # Context
    session_id = Column(String(36), ForeignKey("study_sessions.id"), nullable=True)
    device_type = Column(String(20), nullable=True)  # "mobile", "tablet", "desktop"
    
    # Timestamps
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<QuestionResponse(question_id={self.question_id}, correct={self.is_correct})>" 