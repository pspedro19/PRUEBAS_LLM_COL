from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
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
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # Epic Game Stats
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    rank = Column(String(50), default='Bronce I')
    clan_id = Column(UUID(as_uuid=True), ForeignKey("clans.id"), nullable=True)
    stats = Column(JSONB, default={})
    
    # Authentication
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
    clan = relationship("Clan", back_populates="members")
    responses = relationship("Response", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, level={self.level}, rank={self.rank})>"
    
    def get_stats_for_discipline(self, discipline: str) -> int:
        """Get stats for a specific discipline"""
        if not self.stats:
            return 0
        return self.stats.get(discipline, 0)
    
    def update_stats_for_discipline(self, discipline: str, value: int) -> None:
        """Update stats for a specific discipline"""
        if not self.stats:
            self.stats = {}
        self.stats[discipline] = value
    
    def add_xp(self, amount: int) -> None:
        """Add XP and check for level up"""
        self.xp += amount
        # Simple level up logic: every 100 XP = 1 level
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
            self.update_rank()
    
    def update_rank(self) -> None:
        """Update rank based on level"""
        if self.level >= 30:
            self.rank = "Diamante"
        elif self.level >= 25:
            self.rank = "Oro III"
        elif self.level >= 20:
            self.rank = "Oro II"
        elif self.level >= 15:
            self.rank = "Oro I"
        elif self.level >= 10:
            self.rank = "Plata I"
        elif self.level >= 5:
            self.rank = "Bronce II"
        else:
            self.rank = "Bronce I"


class Clan(Base):
    __tablename__ = "clans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    members = relationship("User", back_populates="clan")
    
    def __repr__(self):
        return f"<Clan(id={self.id}, name={self.name})>" 