from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate

class UserService:
    @staticmethod
    async def create_user(obj_in: UserCreate, db: AsyncSession):
        # 將ViewModel 轉為 Dict 並處理密碼
        user_data = obj_in.model_dump() # 將資料轉成 dict讓SQLAlchemy能看懂內容
        password = user_data.pop("password") # 抽掉password獨立處理
        
        # 密碼加密(假的)
        hashed_password = f"hashed_{password}" 
        
        # 3. 建立 SQLAlchemy Model 實例
        db_obj = User(
            **user_data,  # **為解包成User(name="test", email="a@b.com")
            password=hashed_password
        )
        
        # 4. 存入資料庫
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj