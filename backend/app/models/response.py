from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class Response(Base):
    """Modelo para las respuestas de los usuarios a las preguntas"""
    __tablename__ = "responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    study_session_id = Column(String(36), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=True)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    study_session = relationship("StudySession", back_populates="responses")
    
    def __repr__(self):
        return f"<Response(id={self.id}, correct={self.is_correct})>"
    
    def get_feedback_message(self) -> str:
        """Get appropriate feedback message based on correctness"""
        if self.is_correct:
            return "¡Correcto! ¡Excelente trabajo!"
        else:
            return "Incorrecto. Revisa la explicación y sigue practicando." 