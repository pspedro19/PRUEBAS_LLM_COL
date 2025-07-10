from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class SessionType(str, Enum):
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    REVIEW = "review"
    ADAPTIVE = "adaptive"
    CHALLENGE = "challenge"


class UserSession(Base):
    """User login sessions for authentication and tracking"""
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session identification
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True)
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(20), nullable=True)  # "mobile", "tablet", "desktop"
    browser = Column(String(50), nullable=True)
    operating_system = Column(String(50), nullable=True)
    
    # Geographic information
    country = Column(String(2), nullable=True)  # ISO country code
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Security
    is_suspicious = Column(Boolean, default=False)
    security_flags = Column(JSONB, nullable=True)  # ["unusual_location", "unusual_device"]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_sessions")
    study_sessions = relationship("StudySession", back_populates="user_session")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def time_remaining(self) -> timedelta:
        """Get remaining time before expiration"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - datetime.utcnow()
    
    def extend_session(self, hours: int = 24):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()
    
    def mark_suspicious(self, reason: str):
        """Mark session as suspicious"""
        self.is_suspicious = True
        if self.security_flags is None:
            self.security_flags = {}
        self.security_flags[reason] = True


class StudySession(Base):
    """Individual study sessions with questions and progress tracking"""
    __tablename__ = "study_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user_session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)
    
    # Session configuration
    session_type = Column(String(20), default=SessionType.PRACTICE.value, index=True)
    subject_area = Column(String(30), nullable=True, index=True)  # Focus area for this session
    target_competencies = Column(JSONB, nullable=True)   # Specific competencies to work on
    
    # Session planning
    planned_duration_minutes = Column(Integer, nullable=True)
    planned_questions = Column(Integer, nullable=True)
    difficulty_target = Column(String(20), nullable=True)  # "easy", "medium", "hard", "adaptive"
    
    # Session status and progress
    status = Column(String(20), default=SessionStatus.ACTIVE.value, index=True)
    current_question_index = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    total_active_time_ms = Column(Integer, default=0)  # Actual active time
    
    # IRT and Adaptive Learning
    starting_theta = Column(JSONB, nullable=True)  # Theta values at session start
    ending_theta = Column(JSONB, nullable=True)    # Theta values at session end
    theta_improvement = Column(JSONB, nullable=True)  # Improvement per area
    
    # Session performance
    average_response_time_ms = Column(Integer, nullable=True)
    fastest_response_time_ms = Column(Integer, nullable=True)
    slowest_response_time_ms = Column(Integer, nullable=True)
    accuracy_percentage = Column(Float, nullable=True)
    
    # Learning analytics
    concepts_practiced = Column(JSONB, nullable=True)
    concepts_mastered = Column(JSONB, nullable=True)
    concepts_struggling = Column(JSONB, nullable=True)
    
    # Behavioral patterns
    engagement_score = Column(Float, nullable=True)  # 0-1 scale
    focus_score = Column(Float, nullable=True)       # Based on response times and patterns
    persistence_score = Column(Float, nullable=True) # How user handles difficult questions
    
    # Session feedback
    user_satisfaction = Column(Integer, nullable=True)  # 1-5 scale
    perceived_difficulty = Column(Integer, nullable=True)  # 1-5 scale
    user_feedback = Column(Text, nullable=True)
    recommended_next_topics = Column(JSONB, nullable=True)
    
    # Interruptions and breaks
    pause_count = Column(Integer, default=0)
    total_pause_time_ms = Column(Integer, default=0)
    interruption_reasons = Column(JSONB, nullable=True)
    
    # AI insights
    ai_recommendations = Column(JSONB, nullable=True)
    learning_path_adjustments = Column(JSONB, nullable=True)
    performance_insights = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    user_session = relationship("UserSession", back_populates="study_sessions")
    responses = relationship("Response", back_populates="study_session", cascade="all, delete-orphan") 