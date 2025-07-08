from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import logging
import bcrypt

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserProfile, AuthProvider, UserRole
from app.models.session_models import UserSession

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,
    deprecated="auto"
)

# JWT Bearer token
security = HTTPBearer()

class AuthService:
    """Servicio de autenticación con soporte para JWT y OAuth"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        try:
            # Primero intentar con passlib
            logger.debug(f"Intentando verificar contraseña con passlib")
            if pwd_context.verify(plain_password, hashed_password):
                return True
                
            # Si falla, intentar directamente con bcrypt
            logger.debug(f"Intentando verificar contraseña con bcrypt")
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error verificando contraseña: {str(e)}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera hash de una contraseña"""
        try:
            # Intentar primero con passlib
            logger.debug(f"Intentando generar hash con passlib")
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error al generar hash con passlib: {str(e)}")
            try:
                # Fallback a bcrypt directo
                logger.debug(f"Intentando generar hash con bcrypt")
                salt = bcrypt.gensalt(rounds=12)
                return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            except Exception as e2:
                logger.error(f"Error al generar hash con bcrypt: {str(e2)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al procesar la contraseña"
                )
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT de acceso"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Crea un token JWT de renovación"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # 7 días para el refresh token
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verifica y decodifica un token JWT"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
        """Autentica un usuario con email y contraseña"""
        try:
            result = await db.execute(
                select(User).filter(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if not user.hashed_password:
                # Usuario OAuth sin contraseña
                return None
            
            if not AuthService.verify_password(password, user.hashed_password):
                return None
            
            # Actualizar último login
            user.last_login = datetime.utcnow()
            await db.commit()
            
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    @staticmethod
    async def create_user(
        email: str,
        password: str,
        full_name: str,
        auth_provider: AuthProvider = AuthProvider.EMAIL,
        db: AsyncSession = None
    ) -> User:
        """Crea un nuevo usuario"""
        try:
            # Verificar si el usuario ya existe
            result = await db.execute(
                select(User).filter(User.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Crear usuario
            hashed_password = AuthService.get_password_hash(password) if password else None
            
            user = User(
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                auth_provider=auth_provider.value,
                role=UserRole.STUDENT.value,
                is_active=True,
                is_verified=auth_provider != AuthProvider.EMAIL  # OAuth users are pre-verified
            )
            
            db.add(user)
            await db.flush()  # Para obtener el ID
            
            # Crear perfil inicial
            profile = UserProfile(
                user_id=user.id,
                language="es",
                timezone="America/Bogota"
            )
            
            db.add(profile)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new user: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user account"
            )
    
    @staticmethod
    async def verify_google_token(token: str) -> Dict[str, Any]:
        """Verifica un token de Google OAuth"""
        try:
            # Verificar el token con Google
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            user_data = response.json()
            
            # Verificar que el token sea para nuestra aplicación
            if user_data.get("aud") != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token not for this application"
                )
            
            return user_data
            
        except httpx.RequestError as e:
            logger.error(f"Error verifying Google token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying Google token"
            )
    
    @staticmethod
    async def login_or_create_google_user(google_data: Dict[str, Any], db: AsyncSession) -> User:
        """Crea o busca un usuario a partir de datos de Google"""
        try:
            email = google_data.get("email")
            google_id = google_data.get("sub")
            full_name = google_data.get("name", "")
            
            if not email or not google_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Google user data"
                )
            
            # Buscar usuario existente por email o google_id
            result = await db.execute(
                select(User).filter(
                    (User.email == email) | (User.google_id == google_id)
                )
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Usuario existente - actualizar información si es necesario
                if not user.google_id:
                    user.google_id = google_id
                    user.auth_provider = AuthProvider.GOOGLE.value
                
                user.last_login = datetime.utcnow()
                user.is_verified = True
                
                await db.commit()
                return user
            
            else:
                # Crear nuevo usuario
                return await AuthService.create_user(
                    email=email,
                    password=None,  # No password for OAuth users
                    full_name=full_name,
                    auth_provider=AuthProvider.GOOGLE,
                    db=db
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error with Google OAuth user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing Google authentication"
            )
    
    @staticmethod
    async def create_user_session(
        user: User,
        ip_address: str,
        user_agent: str,
        db: AsyncSession
    ) -> UserSession:
        """Crea una nueva sesión de usuario"""
        try:
            # Generar tokens
            access_token = AuthService.create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role}
            )
            refresh_token = AuthService.create_refresh_token(
                data={"sub": str(user.id), "type": "refresh"}
            )
            
            # Crear sesión
            session = UserSession(
                user_id=user.id,
                session_token=access_token,
                refresh_token=refresh_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def get_current_user_from_token(token: str, db: AsyncSession) -> User:
        """Obtiene el usuario actual a partir del token"""
        try:
            # Verificar token
            payload = AuthService.verify_token(token)
            user_id = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            
            # Obtener usuario
            result = await db.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is disabled"
                )
            
            return user
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

# Dependency para obtener el usuario actual
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency para obtener el usuario autenticado actual"""
    return await AuthService.get_current_user_from_token(credentials.credentials, db)

# Dependency para obtener usuario activo
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency para obtener usuario activo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Dependency para verificar roles
def require_role(required_role: UserRole):
    """Dependency factory para requerir un rol específico"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Dependency para admin
get_admin_user = require_role(UserRole.ADMIN)

# Dependency para teacher
get_teacher_user = require_role(UserRole.TEACHER) 