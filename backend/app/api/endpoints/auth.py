from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
from sqlalchemy import select

from app.core.database import get_db
from app.services.auth_service import AuthService, get_current_user
from app.models.user import User, AuthProvider

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: str
    
    class Config:
        from_attributes = True

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un nuevo usuario con email y contraseña
    """
    try:
        # Crear usuario
        user = await AuthService.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            auth_provider=AuthProvider.EMAIL,
            db=db
        )
        
        # Crear sesión
        session = await AuthService.create_user_session(
            user=user,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            db=db
        )
        
        return TokenResponse(
            access_token=session.session_token,
            refresh_token=session.refresh_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.display_name,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating account"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Iniciar sesión con email y contraseña
    """
    try:
        logger.info(f"Intento de login para el usuario: {user_data.email}")
        
        # Verificar si el usuario existe
        result = await db.execute(
            select(User).filter(User.email == user_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Usuario no encontrado: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        if not user.is_active:
            logger.warning(f"Intento de login con cuenta desactivada: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Autenticar usuario
        if not await AuthService.authenticate_user(user_data.email, user_data.password, db):
            logger.warning(f"Contraseña incorrecta para el usuario: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Crear sesión
        try:
            session = await AuthService.create_user_session(
                user=user,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                db=db
            )
        except Exception as e:
            logger.error(f"Error creando sesión para {user_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating session"
            )
        
        logger.info(f"Login exitoso para el usuario: {user_data.email}")
        
        return TokenResponse(
            access_token=session.session_token,
            refresh_token=session.refresh_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.display_name,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado durante el login para {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@router.post("/google", response_model=TokenResponse)
async def google_auth(
    auth_data: GoogleAuthRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Autenticación con Google OAuth
    """
    try:
        # Verificar token de Google
        google_data = await AuthService.verify_google_token(auth_data.id_token)
        
        # Crear o encontrar usuario
        user = await AuthService.login_or_create_google_user(google_data, db)
        
        # Crear sesión
        session = await AuthService.create_user_session(
            user=user,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            db=db
        )
        
        return TokenResponse(
            access_token=session.session_token,
            refresh_token=session.refresh_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.display_name,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during Google authentication"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener información del usuario actual
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.display_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat()
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cerrar sesión del usuario actual
    """
    # En una implementación completa, aquí se invalidaría el token
    # Por ahora retornamos un mensaje de éxito
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Renovar token de acceso usando refresh token
    """
    try:
        # Verificar refresh token
        payload = AuthService.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        
        # Obtener usuario
        user = await AuthService.get_current_user_from_token(refresh_token, db)
        
        # Crear nueva sesión
        session = await AuthService.create_user_session(
            user=user,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            db=db
        )
        
        return TokenResponse(
            access_token=session.session_token,
            refresh_token=session.refresh_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.display_name,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        ) 