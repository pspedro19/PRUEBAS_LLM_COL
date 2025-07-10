from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class Discipline(str, Enum):
    MAT = "MAT"
    LC = "LC"
    SOC = "SOC"
    CIE = "CIE"
    ING = "ING"


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Epic Game Fields
    discipline = Column(String(50), nullable=False, index=True)
    difficulty = Column(Integer, nullable=False, index=True)
    topic = Column(String(100), nullable=True)
    question_text = Column(Text, nullable=False, unique=True)
    options = Column(JSONB, nullable=False)
    correct_option = Column(String(10), nullable=False)
    reward_xp = Column(Integer, default=10)
    reward_item = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, discipline={self.discipline}, difficulty={self.difficulty})>"
    
    def get_difficulty_stars(self) -> int:
        """Get difficulty as number of stars (1-5)"""
        return min(5, max(1, self.difficulty))
    
    def get_reward_description(self) -> str:
        """Get human-readable reward description"""
        if self.reward_item:
            return f"{self.reward_xp} XP + {self.reward_item}"
        return f"{self.reward_xp} XP" 