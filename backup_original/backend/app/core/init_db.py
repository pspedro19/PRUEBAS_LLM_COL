from app.core.database import async_session_maker, init_models
from app.models.user import User, UserRole
from app.models.question import Question
from app.core.security import get_password_hash
from app.core.sample_questions import SAMPLE_QUESTIONS
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def create_test_users():
    """Create predefined test users if they don't exist"""
    test_users = [
        {
            "email": "admin@test.com",
            "password": "admin123",
            "username": "admin",
            "display_name": "Admin User",
            "role": UserRole.ADMIN
        },
        {
            "email": "teacher@test.com",
            "password": "teacher123",
            "username": "teacher",
            "display_name": "Teacher User",
            "role": UserRole.TEACHER
        },
        {
            "email": "student@test.com",
            "password": "student123",
            "username": "student",
            "display_name": "Student User",
            "role": UserRole.STUDENT
        }
    ]

    async with async_session_maker() as db:
        for user_data in test_users:
            try:
                # Check if user exists by email or username
                result = await db.execute(
                    select(User).filter(
                        (User.email == user_data["email"]) | 
                        (User.username == user_data["username"])
                    )
                )
                existing_user = result.scalar_one_or_none()
                
                if not existing_user:
                    user = User(
                        email=user_data["email"],
                        username=user_data["username"],
                        display_name=user_data["display_name"],
                        password_hash=get_password_hash(user_data["password"]),
                        role=user_data["role"],
                        is_active=True,
                        is_verified=True
                    )
                    db.add(user)
                    await db.commit()
                    logger.info(f"Created test user: {user.email}")
                else:
                    logger.info(f"User {user_data['email']} already exists, skipping")
                    
            except Exception as e:
                await db.rollback()
                logger.warning(f"Failed to create user {user_data['email']}: {e}")

async def create_sample_questions():
    """Create sample questions for each ICFES area"""
    async with async_session_maker() as db:
        # Check if questions already exist
        result = await db.execute(select(Question))
        existing_questions = result.scalars().all()
        
        if len(existing_questions) > 0:
            logger.info(f"Database already has {len(existing_questions)} questions, skipping sample creation")
            return
            
        # Create sample questions
        questions_created = 0
        for question_data in SAMPLE_QUESTIONS:
            question = Question(
                title=question_data["title"],
                content=question_data["content"],
                option_a=question_data["option_a"],
                option_b=question_data["option_b"],
                option_c=question_data["option_c"],
                option_d=question_data["option_d"],
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"],
                area=question_data["area"],
                topic=question_data["topic"],
                subtopic=question_data["subtopic"],
                difficulty=question_data["difficulty"],
                points_value=question_data["points_value"],
                is_active=True,
                times_answered=0,
                times_correct=0,
                success_rate=0.0
            )
            db.add(question)
            questions_created += 1
            
        await db.commit()
        logger.info(f"Created {questions_created} sample questions successfully")

async def init_db():
    """Initialize database with required data"""
    try:
        # Skip table creation since they are created by SQL initialization
        # await init_models()
        logger.info("Database tables creation skipped (handled by SQL)")

        # Skip test users creation since they are created by SQL initialization
        # await create_test_users()
        logger.info("Test users initialization skipped (handled by SQL)")
        
        # Skip sample questions creation since they are created by SQL initialization
        # await create_sample_questions()
        logger.info("Sample questions initialization skipped (handled by SQL)")
        
        logger.info("Database initialization completed - all handled by SQL")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise 