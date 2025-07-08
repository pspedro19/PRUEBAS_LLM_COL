from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, questions, users, chain_of_thought, analytics
from app.core.config import settings
from app.core.init_db import init_db
from app.core.database import init_models, get_db
import logging

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    questions.router,
    prefix="/questions",
    tags=["questions"]
)

api_router.include_router(
    chain_of_thought.router,
    prefix="/chain-of-thought",
    tags=["chain-of-thought"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

# Include API router in main app
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize database and create test users on startup"""
    try:
        # Initialize database models
        await init_models()
        logger.info("Database models initialized")
        
        # Initialize test data
        async for db in get_db():
            await init_db(db)
            break
        logger.info("Test data initialized")
    except Exception as e:
        logger.error(f"Error during startup: {e}") 