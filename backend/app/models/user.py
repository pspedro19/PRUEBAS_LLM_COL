from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # None for OAuth users
    auth_provider = Column(String(20), default=AuthProvider.EMAIL.value)
    google_id = Column(String(255), unique=True, nullable=True)
    microsoft_id = Column(String(255), unique=True, nullable=True)
    
    # Profile
    role = Column(String(20), default=UserRole.STUDENT.value)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Verification
    verification_token = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_responses = relationship("UserResponse", back_populates="user", cascade="all, delete-orphan")
    legacy_responses = relationship("Response", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Academic Information
    grade = Column(String(20), nullable=True)  # "10", "11", "universitario"
    institution = Column(String(255), nullable=True)
    target_career = Column(String(255), nullable=True)
    target_universities = Column(JSON, nullable=True)  # ["Universidad Nacional", "Universidad de los Andes"]
    
    # Learning Preferences
    preferred_study_time = Column(String(50), nullable=True)  # "morning", "afternoon", "evening"
    learning_style = Column(String(50), nullable=True)  # "visual", "auditory", "kinesthetic"
    difficulty_preference = Column(String(20), default="adaptive")  # "easy", "medium", "hard", "adaptive"
    
    # IRT Parameters per subject area
    theta_matematicas = Column(Float, default=0.0)
    theta_lectura_critica = Column(Float, default=0.0)
    theta_ciencias_naturales = Column(Float, default=0.0)
    theta_ciencias_sociales = Column(Float, default=0.0)
    theta_ingles = Column(Float, default=0.0)
    
    # Confidence intervals for theta estimates
    theta_std_errors = Column(JSON, nullable=True)
    
    # Study Metrics
    total_study_time_minutes = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Personalization
    avatar_url = Column(String(255), nullable=True)
    timezone = Column(String(50), default="America/Bogota")
    language = Column(String(10), default="es")
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    
    # Analytics and Insights
    strengths = Column(JSON, nullable=True)  # Areas where user excels
    weaknesses = Column(JSON, nullable=True)  # Areas needing improvement
    learning_patterns = Column(JSON, nullable=True)  # Time of day, frequency, etc.
    
    # Goals and Progress
    daily_question_goal = Column(Integer, default=10)
    weekly_study_goal_minutes = Column(Integer, default=300)  # 5 hours
    target_exam_date = Column(DateTime(timezone=True), nullable=True)
    
    # Gamification
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    badges = Column(JSON, nullable=True)  # List of earned badges
    achievements = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, grade={self.grade})>"
    
    def get_theta_for_area(self, area: str) -> float:
        """Get theta (ability estimate) for a specific subject area"""
        area_mapping = {
            "matematicas": self.theta_matematicas,
            "lectura_critica": self.theta_lectura_critica,
            "ciencias_naturales": self.theta_ciencias_naturales,
            "ciencias_sociales": self.theta_ciencias_sociales,
            "ingles": self.theta_ingles
        }
        return area_mapping.get(area.lower(), 0.0)
    
    def update_theta_for_area(self, area: str, new_theta: float) -> None:
        """Update theta estimate for a specific subject area"""
        area_mapping = {
            "matematicas": "theta_matematicas",
            "lectura_critica": "theta_lectura_critica", 
            "ciencias_naturales": "theta_ciencias_naturales",
            "ciencias_sociales": "theta_ciencias_sociales",
            "ingles": "theta_ingles"
        }
        
        attr_name = area_mapping.get(area.lower())
        if attr_name:
            setattr(self, attr_name, new_theta)
    
    def calculate_overall_progress(self) -> Dict[str, Any]:
        """Calculate overall progress metrics"""
        accuracy = (self.questions_correct / self.questions_answered * 100) if self.questions_answered > 0 else 0
        
        # Calculate average theta across all areas
        thetas = [
            self.theta_matematicas,
            self.theta_lectura_critica,
            self.theta_ciencias_naturales,
            self.theta_ciencias_sociales,
            self.theta_ingles
        ]
        avg_theta = sum(thetas) / len(thetas)
        
        # Convert theta to a 0-100 score (theta typically ranges from -3 to +3)
        # Using a sigmoid transformation: score = 100 / (1 + exp(-theta))
        import math
        score = 100 / (1 + math.exp(-avg_theta))
        
        return {
            "overall_score": round(score, 1),
            "accuracy_percentage": round(accuracy, 1),
            "questions_answered": self.questions_answered,
            "study_time_hours": round(self.total_study_time_minutes / 60, 1),
            "current_streak": self.current_streak,
            "level": self.level,
            "total_points": self.total_points
        } 