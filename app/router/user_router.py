from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate
from app.service.user_service import UserService


router = APIRouter()

@router.post("/create")
async def create_user_api(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
        new_user = await UserService.create_user(user_in, db)
        return new_user

    