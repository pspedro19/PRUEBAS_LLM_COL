from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class ResponseStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class ChainOfThoughtStep(Base):
    """Individual steps in the chain of thought reasoning process"""
    __tablename__ = "chain_of_thought_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_response_id = Column(UUID(as_uuid=True), ForeignKey("user_responses.id"), nullable=False)
    
    # Step information
    step_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    step_type = Column(String(50), nullable=False)  # "analysis", "reasoning", "calculation", "conclusion"
    
    # Content
    title = Column(String(200), nullable=False)  # "Identificar la información clave"
    content = Column(Text, nullable=False)       # The actual reasoning step
    explanation = Column(Text, nullable=True)    # Additional explanation if needed
    
    # AI Generation metadata
    ai_model_used = Column(String(50), nullable=True)  # "gpt-4", "claude-3-opus"
    ai_prompt_used = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)  # 0-1 scale
    
    # Validation and Quality
    is_validated = Column(Boolean, default=False)
    validation_score = Column(Float, nullable=True)  # Quality score
    teacher_feedback = Column(Text, nullable=True)
    
    # User interaction
    user_found_helpful = Column(Boolean, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 scale
    user_feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_response = relationship("UserResponse", back_populates="cot_steps")
    
    def __repr__(self):
        return f"<ChainOfThoughtStep(id={self.id}, step={self.step_number}, type={self.step_type})>"


class UserResponse(Base):
    """User responses to questions with full context and analysis"""
    __tablename__ = "user_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Core response data
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id"), nullable=True, index=True)
    
    # Response details
    selected_answer = Column(String(10), nullable=False)  # "A", "B", "C", "D"
    is_correct = Column(Boolean, nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=False)
    status = Column(String(20), default=ResponseStatus.COMPLETED.value)
    
    # User state during response
    confidence_level = Column(Float, nullable=True)  # User's confidence 0-1
    difficulty_perceived = Column(Integer, nullable=True)  # User's perceived difficulty 1-5
    help_used = Column(Boolean, default=False)  # Did user ask for help/hint?
    
    # IRT Analysis
    user_theta_before = Column(Float, nullable=True)  # Ability estimate before this question
    user_theta_after = Column(Float, nullable=True)   # Ability estimate after this question
    theta_change = Column(Float, nullable=True)       # Change in ability estimate
    information_gained = Column(Float, nullable=True)  # Information function value
    
    # Question Analysis
    predicted_probability = Column(Float, nullable=True)  # IRT predicted P(correct)
    prediction_accuracy = Column(Float, nullable=True)   # How accurate was the prediction
    
    # Chain of Thought Analysis
    explanation_requested = Column(Boolean, default=False)
    explanation_generated = Column(Boolean, default=False)
    explanation_type = Column(String(50), nullable=True)  # "brief", "detailed", "comprehensive"
    cot_quality_score = Column(Float, nullable=True)     # Quality of generated explanation
    
    # Learning Analytics
    concept_mastery_before = Column(JSON, nullable=True)  # Mastery levels before this question
    concept_mastery_after = Column(JSON, nullable=True)   # Mastery levels after this question
    learning_objectives_met = Column(JSON, nullable=True)  # Which objectives were achieved
    
    # Behavioral Data
    mouse_movements = Column(JSON, nullable=True)      # Mouse tracking data (optional)
    keystroke_patterns = Column(JSON, nullable=True)   # Typing patterns (optional)
    screen_interactions = Column(JSON, nullable=True)  # Screen interaction data
    device_context = Column(JSON, nullable=True)       # Device and browser info
    
    # Feedback and Improvement
    user_feedback = Column(Text, nullable=True)         # User's feedback on the question
    user_rating = Column(Integer, nullable=True)        # User's rating 1-5
    reported_issues = Column(JSON, nullable=True)  # Any issues reported
    
    # Adaptive Learning
    next_question_suggestions = Column(JSON, nullable=True)  # Recommended next questions
    remediation_needed = Column(Boolean, default=False)      # Does user need remediation?
    advancement_ready = Column(Boolean, default=False)       # Ready for harder questions?
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    explanation_generated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_responses")
    question = relationship("Question", back_populates="user_responses")
    study_session = relationship("StudySession", back_populates="responses")
    cot_steps = relationship("ChainOfThoughtStep", back_populates="user_response", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserResponse(id={self.id}, correct={self.is_correct}, time={self.response_time_ms}ms)>"
    
    @property
    def response_speed_category(self) -> str:
        """Categorize response speed"""
        if self.response_time_ms < 30000:  # < 30 seconds
            return "fast"
        elif self.response_time_ms < 120000:  # < 2 minutes
            return "normal"
        elif self.response_time_ms < 300000:  # < 5 minutes
            return "slow"
        else:
            return "very_slow"
    
    @property
    def performance_analysis(self) -> Dict[str, Any]:
        """Analyze performance on this response"""
        analysis = {
            "is_correct": self.is_correct,
            "response_speed": self.response_speed_category,
            "confidence_accuracy": None,
            "theta_improvement": self.theta_change,
            "information_gained": self.information_gained
        }
        
        # Analyze confidence accuracy (confidence vs actual performance)
        if self.confidence_level is not None:
            if self.is_correct and self.confidence_level > 0.7:
                analysis["confidence_accuracy"] = "well_calibrated_confident"
            elif self.is_correct and self.confidence_level < 0.3:
                analysis["confidence_accuracy"] = "underconfident"
            elif not self.is_correct and self.confidence_level > 0.7:
                analysis["confidence_accuracy"] = "overconfident"
            elif not self.is_correct and self.confidence_level < 0.3:
                analysis["confidence_accuracy"] = "well_calibrated_uncertain"
            else:
                analysis["confidence_accuracy"] = "moderate_confidence"
        
        return analysis
    
    def update_learning_analytics(self, concept_mastery: Dict[str, float]):
        """Update learning analytics after response"""
        self.concept_mastery_after = concept_mastery
        
        # Determine if remediation or advancement is needed
        avg_mastery = sum(concept_mastery.values()) / len(concept_mastery) if concept_mastery else 0
        
        if avg_mastery < 0.4:  # Below 40% mastery
            self.remediation_needed = True
            self.advancement_ready = False
        elif avg_mastery > 0.8:  # Above 80% mastery
            self.remediation_needed = False
            self.advancement_ready = True
        else:
            self.remediation_needed = False
            self.advancement_ready = False
    
    def generate_next_question_suggestions(self, available_questions: List[Dict]) -> List[Dict]:
        """Generate suggestions for next questions based on this response"""
        suggestions = []
        
        if self.remediation_needed:
            # Suggest easier questions on same topic
            suggestions = [q for q in available_questions 
                         if q.get("difficulty", 0) < 0.3 and q.get("topic") == self.question.competencia]
        elif self.advancement_ready:
            # Suggest harder questions
            suggestions = [q for q in available_questions 
                         if q.get("difficulty", 0) > 0.7]
        else:
            # Suggest questions at current level
            suggestions = [q for q in available_questions 
                         if 0.3 <= q.get("difficulty", 0.5) <= 0.7]
        
        self.next_question_suggestions = suggestions[:5]  # Top 5 suggestions
        return suggestions


class Response(Base):
    """Modelo para las respuestas de los usuarios a las preguntas"""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="legacy_responses")
    question = relationship("Question", back_populates="legacy_responses")

    def __repr__(self):
        return f"<Response(id={self.id}, user_id={self.user_id}, question_id={self.question_id})>" 