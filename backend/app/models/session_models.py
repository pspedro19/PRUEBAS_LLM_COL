from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
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
    security_flags = Column(JSON, nullable=True)  # ["unusual_location", "unusual_device"]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User")
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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    user_session_id = Column(String(36), ForeignKey("user_sessions.id"), nullable=True)
    
    # Session configuration
    session_type = Column(String(20), default=SessionType.PRACTICE.value, index=True)
    subject_area = Column(String(30), nullable=True, index=True)  # Focus area for this session
    target_competencies = Column(JSON, nullable=True)   # Specific competencies to work on
    
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
    starting_theta = Column(JSON, nullable=True)  # Theta values at session start
    ending_theta = Column(JSON, nullable=True)    # Theta values at session end
    theta_improvement = Column(JSON, nullable=True)  # Improvement per area
    
    # Session performance
    average_response_time_ms = Column(Integer, nullable=True)
    fastest_response_time_ms = Column(Integer, nullable=True)
    slowest_response_time_ms = Column(Integer, nullable=True)
    accuracy_percentage = Column(Float, nullable=True)
    
    # Learning analytics
    concepts_practiced = Column(JSON, nullable=True)
    concepts_mastered = Column(JSON, nullable=True)
    concepts_struggling = Column(JSON, nullable=True)
    
    # Behavioral patterns
    engagement_score = Column(Float, nullable=True)  # 0-1 scale
    focus_score = Column(Float, nullable=True)       # Based on response times and patterns
    persistence_score = Column(Float, nullable=True) # How user handles difficult questions
    
    # Session feedback
    user_satisfaction = Column(Integer, nullable=True)  # 1-5 scale
    perceived_difficulty = Column(Integer, nullable=True)  # 1-5 scale
    user_feedback = Column(Text, nullable=True)
    recommended_next_topics = Column(JSON, nullable=True)
    
    # Interruptions and breaks
    pause_count = Column(Integer, default=0)
    total_pause_time_ms = Column(Integer, default=0)
    interruption_reasons = Column(JSON, nullable=True)
    
    # AI insights
    ai_recommendations = Column(JSON, nullable=True)
    learning_path_adjustments = Column(JSON, nullable=True)
    performance_insights = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    user_session = relationship("UserSession", back_populates="study_sessions")
    responses = relationship("UserResponse", back_populates="study_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<StudySession(id={self.id}, type={self.session_type}, status={self.status})>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate session duration in minutes"""
        if self.ended_at:
            delta = self.ended_at - self.started_at
        else:
            delta = datetime.utcnow() - self.started_at
        return int(delta.total_seconds() / 60)
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate"""
        if self.total_questions_answered == 0:
            return 0.0
        return (self.questions_correct / self.total_questions_answered) * 100
    
    @property
    def questions_per_minute(self) -> float:
        """Calculate questions per minute rate"""
        duration = self.duration_minutes
        if duration == 0:
            return 0.0
        return self.total_questions_answered / duration
    
    def update_performance_metrics(self):
        """Update performance metrics based on responses"""
        if not self.responses:
            return
        
        # Calculate response time statistics
        response_times = [r.response_time_ms for r in self.responses if r.response_time_ms]
        if response_times:
            self.average_response_time_ms = sum(response_times) // len(response_times)
            self.fastest_response_time_ms = min(response_times)
            self.slowest_response_time_ms = max(response_times)
        
        # Update accuracy
        self.total_questions_answered = len(self.responses)
        self.questions_correct = sum(1 for r in self.responses if r.is_correct)
        self.accuracy_percentage = self.accuracy_rate
    
    def calculate_engagement_score(self) -> float:
        """Calculate engagement score based on various factors"""
        score = 0.0
        
        # Response time consistency (lower variance = higher engagement)
        if self.responses:
            response_times = [r.response_time_ms for r in self.responses if r.response_time_ms]
            if len(response_times) > 1:
                import statistics
                cv = statistics.stdev(response_times) / statistics.mean(response_times)
                time_consistency = max(0, 1 - cv)  # Lower coefficient of variation = higher score
                score += time_consistency * 0.3
        
        # Completion rate
        if self.planned_questions:
            completion_rate = min(1.0, self.total_questions_answered / self.planned_questions)
            score += completion_rate * 0.3
        
        # Break frequency (fewer breaks = higher engagement)
        if self.duration_minutes > 0:
            break_rate = self.pause_count / max(1, self.duration_minutes / 10)  # Breaks per 10 minutes
            break_score = max(0, 1 - break_rate / 3)  # More than 3 breaks per 10 min = low score
            score += break_score * 0.2
        
        # Help usage (moderate help = good engagement)
        help_requests = sum(1 for r in self.responses if r.help_used)
        if self.total_questions_answered > 0:
            help_rate = help_requests / self.total_questions_answered
            help_score = 1 - abs(help_rate - 0.2) / 0.8  # Optimal around 20% help usage
            score += max(0, help_score) * 0.2
        
        self.engagement_score = min(1.0, score)
        return self.engagement_score
    
    def end_session(self, user_feedback: Optional[str] = None, satisfaction: Optional[int] = None):
        """End the study session and calculate final metrics"""
        self.ended_at = datetime.utcnow()
        self.status = SessionStatus.COMPLETED.value
        
        if user_feedback:
            self.user_feedback = user_feedback
        if satisfaction:
            self.user_satisfaction = satisfaction
        
        # Update all performance metrics
        self.update_performance_metrics()
        
        # Calculate engagement and other scores
        self.calculate_engagement_score()
        
        # Generate AI recommendations for next session
        self.generate_ai_recommendations()
    
    def pause_session(self, reason: Optional[str] = None):
        """Pause the session"""
        self.status = SessionStatus.PAUSED.value
        self.pause_count += 1
        
        if reason and self.interruption_reasons:
            self.interruption_reasons[reason] = True
        elif reason:
            self.interruption_reasons = {reason: True}
    
    def resume_session(self):
        """Resume the session"""
        self.status = SessionStatus.ACTIVE.value
        self.last_activity_at = datetime.utcnow()
    
    def generate_ai_recommendations(self):
        """Generate AI-powered recommendations for future learning"""
        recommendations = {
            "next_topics": [],
            "difficulty_adjustment": "maintain",
            "focus_areas": [],
            "study_tips": []
        }
        
        # Analyze performance patterns
        if self.accuracy_percentage and self.accuracy_percentage < 60:
            recommendations["difficulty_adjustment"] = "decrease"
            recommendations["study_tips"].append("Consider reviewing fundamental concepts")
        elif self.accuracy_percentage and self.accuracy_percentage > 85:
            recommendations["difficulty_adjustment"] = "increase"
            recommendations["study_tips"].append("Ready for more challenging questions")
        
        # Identify struggling concepts
        if self.concepts_struggling:
            recommendations["focus_areas"] = list(self.concepts_struggling.keys())[:3]  # Top 3 struggling areas
        
        # Response time analysis
        if self.average_response_time_ms and self.average_response_time_ms > 180000:  # > 3 minutes
            recommendations["study_tips"].append("Practice time management strategies")
        
        self.ai_recommendations = recommendations 