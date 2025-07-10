from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
    ]
    
    # Application
    APP_NAME: str = "MathQuest"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Una plataforma gamificada para aprender matemáticas"
    
    # Security
    HASH_ALGORITHM: str = "bcrypt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 