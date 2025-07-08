from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create declarative base
Base = declarative_base()

async def init_models():
    """Initialize database models"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency for database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
        
        # Create initial data if needed
        async with async_session() as session:
            from app.models.user import User, UserRole, AuthProvider
            from app.services.auth_service import AuthService
            
            try:
                # Check if admin user exists
                admin_query = select(User).where(User.email == "admin@icfes.com")
                admin = (await session.execute(admin_query)).scalar_one_or_none()
                
                if not admin:
                    # Create admin user
                    admin = await AuthService.create_user(
                        email="admin@icfes.com",
                        password="admin123",
                        full_name="Administrador ICFES",
                        auth_provider=AuthProvider.EMAIL,
                        role=UserRole.ADMIN,
                        db=session
                    )
                    # Asegurarse de que el rol sea admin
                    admin.role = UserRole.ADMIN.value
                    await session.commit()
                    logger.info("Admin user created successfully")
                else:
                    # Asegurarse de que el rol sea admin
                    admin.role = UserRole.ADMIN.value
                    await session.commit()
                    logger.info("Admin user already exists")
                
                # Check if student user exists
                student_query = select(User).where(User.email == "estudiante@ejemplo.com")
                student = (await session.execute(student_query)).scalar_one_or_none()
                
                if not student:
                    # Create student user
                    await AuthService.create_user(
                        email="estudiante@ejemplo.com",
                        password="user123",
                        full_name="Estudiante Ejemplo",
                        auth_provider=AuthProvider.EMAIL,
                        role=UserRole.STUDENT,
                        db=session
                    )
                    logger.info("Student user created successfully")
                else:
                    logger.info("Student user already exists")
                
            except Exception as e:
                logger.error(f"Error creating users: {str(e)}")
                await session.rollback()
            else:
                await session.commit()
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed") 