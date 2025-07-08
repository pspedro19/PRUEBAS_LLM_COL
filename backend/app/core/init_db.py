from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.models.user import AuthProvider, UserRole, User
import logging

logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession) -> None:
    """Inicializa la base de datos con datos de prueba"""
    try:
        # Crear usuario administrador
        admin = await AuthService.create_user(
            email="admin@icfes.com",
            password="admin123",
            full_name="Administrador ICFES",
            auth_provider=AuthProvider.EMAIL,
            db=db
        )
        
        # Actualizar rol a administrador
        admin.role = UserRole.ADMIN.value
        await db.commit()
        
        # Crear usuario estudiante de prueba
        await AuthService.create_user(
            email="estudiante@ejemplo.com",
            password="user123",
            full_name="Estudiante Ejemplo",
            auth_provider=AuthProvider.EMAIL,
            db=db
        )
        
        logger.info("Base de datos inicializada con usuarios de prueba")
        
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {e}")
        await db.rollback()
        raise 