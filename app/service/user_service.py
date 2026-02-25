import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic
from app.core.security import SecurityHelper

class UserService:
    @staticmethod
    async def create_user(obj_in: UserCreate, db: AsyncSession):
        #驗證是否有相同信箱
        if await UserService.is_email_taken(obj_in.email, db): return None
    
        # 建立 SQLAlchemy Model 實例 (直接並加密密碼)
        user_data = User(
            name=obj_in.name,
            email=obj_in.email,
            # 密碼加密
            password=SecurityHelper.get_password_hash(obj_in.password),         
        ) # 將資料轉成 dict讓SQLAlchemy能看懂內容        
                            
        # 存入資料庫
        db.add(user_data)
        await db.commit()
        await db.refresh(user_data)
        return user_data
    
    @staticmethod
    async def authenticate_user(obj_in: UserCreate, db: AsyncSession):
        # 尋找使用者
        user = await UserService.get_user_by_email(obj_in.email, db)
        if not user:
            return None # 找不到人
        
        # 比對密碼
        # obj_in.password 明碼 user.password 加密後的密碼
        if not SecurityHelper.verify_password(obj_in.password, user.password): 
            return None # 密碼錯了            
        return user #驗證完成回傳user
    
    # 依照userId尋找user
    @staticmethod
    async def get_user_by_id(id:uuid.UUID, db:AsyncSession):        
        result = await db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()
        
    # 依照email尋找user
    @staticmethod
    async def get_user_by_email(email:str, db:AsyncSession):        
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    @staticmethod
    async def get_users(db:AsyncSession, name:str = None, skip: int = 0, limit: int = 20) -> list[UserPublic]:
        query = select(User)
        if name:
            query = query.where(User.name.icontains(name))
        result = await db.execute(query.order_by(User.createdDateTime.desc()).offset(skip).limit(limit))
        return [UserPublic.model_validate(u) for u in result.scalars().all()]

    
    # 確認是否有相同的信件
    @staticmethod
    async def is_email_taken(email: str, db: AsyncSession) -> bool:
        user = await UserService.get_user_by_email(email, db)
        return user is not None
        