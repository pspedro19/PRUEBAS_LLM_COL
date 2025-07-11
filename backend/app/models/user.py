from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime
from typing import Optional, Dict, Any

# Temporarily commented out to avoid enum validation issues
# class UserRole(enum.Enum):
#     STUDENT = "student"
#     TEACHER = "teacher"
#     ADMIN = "admin"

class Clan(Base):
    __tablename__ = "clans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    members = relationship("User", back_populates="clan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # Game progression
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    rank = Column(String(50), default="Bronce I")
    clan_id = Column(Integer, ForeignKey("clans.id"), nullable=True)
    stats = Column(JSON, default=dict)  # e.g., {"MAT": 15, "LC": 12, "CN": 10}
    
    # Authentication & Authorization
    auth_provider = Column(String(20), default="email")  # "email", "google", "microsoft"
    google_id = Column(String(255), unique=True, nullable=True)
    microsoft_id = Column(String(255), unique=True, nullable=True)
    role = Column(String(20), default="student")  # Using String instead of Enum to avoid conflicts
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset and verification
    verification_token = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    clan = relationship("Clan", back_populates="members")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    responses = relationship("UserResponse", back_populates="user", cascade="all, delete-orphan") 