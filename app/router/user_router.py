import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.database import get_db
from app.models.user import UserRole
from app.schemas.user import UserCreate, UserLogin, UserPublic
from app.service.user_service import UserService
from app.core.security import SecurityHelper
from app.core.config import settings


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserPublic: 
        credentials_exception = errors.AuthErrors.InvalidToken()
        try:
                # 解碼 Token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                email: str = payload.get("sub")
                if email is None:
                        raise credentials_exception
        except jwt.InvalidTokenError:
                raise credentials_exception        
        user = await UserService.get_user_by_email(email, db)
        if user is None:
                raise credentials_exception        
        return UserPublic.model_validate(user)

# 登入處理
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):    
        user_in = UserLogin(
                email=form_data.username, 
                password=form_data.password
        )
        user = await UserService.authenticate_user(user_in, db)
        if not user:
                raise errors.UserErrors.InvalidCredentials()

        # 驗證成功，發放 Token
        access_token = SecurityHelper.create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}


# 確認是否登入
@router.get("/me", response_model=UserPublic)
async def get_my_info(current_user = Depends(get_current_user)):    
        return current_user

@router.get("/", response_model=list[UserPublic])
async def get_users(name: str = None, skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db), current_user: UserPublic = Depends(get_current_user)):
        if current_user.role != UserRole.ADMIN:        
                raise errors.AuthErrors.AccessDenied()
        return await UserService.get_users(db, name, skip, limit)

# 建立User
@router.post("/create")
async def create_user_api(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
        new_user = await UserService.create_user(user_in, db)
        if new_user is None:
                raise errors.UserErrors.AlreadyExists()
        return new_user

    