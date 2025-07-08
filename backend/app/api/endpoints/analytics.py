from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/dashboard")
async def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener datos del dashboard del usuario"""
    return {
        "message": "Analytics dashboard - Coming soon!",
        "user_id": str(current_user.id)
    } 