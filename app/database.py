import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator
from app.core.config import settings
from app.core.security import SecurityHelper
from .models import Base, User, UserRole, Post

DATABASE_URL = settings.DATABASE_URL

# 等同於Connection Pool
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG_MODE)

# 相似於efcore的 dbcontext 內部模擬做完sql在送到真實db做處理 或是ado 的Transaction Container
# 扮演 Unit of Work (工作單元) 角色，內部追蹤物件狀態，最後再統一 Flush/Commit 到真實 DB。
async_session_factory = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False # Commit 後不清除物件快取，確保非同步環境下資料可讀
)

# DI註入db
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

# 資料庫初始化（建立所有資料表）
class DatabaseInitializer:
    
    @staticmethod
    async def init_db():
        async with engine.begin() as conn:        
            await conn.run_sync(Base.metadata.create_all)
            
    @staticmethod            
    async def seed_all():
        """執行所有初始化邏輯"""
        async with async_session_factory() as session:
            try:
                await DatabaseInitializer.init_admin(session)
                await DatabaseInitializer.init_test_data(session)
            except Exception as e:
                logging.error(f"資料庫初始化失敗: {e}")
                await session.rollback()
            finally:
                await session.close()
        
    @staticmethod
    async def init_admin(session: AsyncSession):
        result = await session.execute(select(User).where(User.name == "admin"))
        if result.scalar_one_or_none():
            logging.info("管理員帳號已存在，跳過。")
            return
        
        new_admin = User(
            name="admin",
            email="admin@example.com",
            password=SecurityHelper.get_password_hash("1qaz@WSX"), # 暫時密碼
            role=UserRole.ADMIN
        )
        session.add(new_admin)
        await session.flush()
        logging.info("預設管理員建立成功！帳號: admin")

    @staticmethod
    async def init_test_data(session: AsyncSession):
        """
        初始化測試資料：3名使用者, 3篇主貼文, 9則留言
        """
        # 1. 檢查是否已有資料 (以 user1 為指標)
        result = await session.execute(select(User).where(User.name == "user1"))
        if result.scalar_one_or_none():
            logging.info("測試資料已存在，跳過。")
            return

        logging.info("正在建立測試資料...")
        try:
            # --- 建立 3 個 User ---
            test_users = []
            for i in range(1, 4):
                u = User(
                    name=f"user{i}",
                    email=f"user{i}@example.com",
                    password=SecurityHelper.get_password_hash("password123"),
                    role=UserRole.USER
                )
                session.add(u)
                test_users.append(u)            
            
            await session.flush()

            # --- 建立 3 篇主貼文 ---
            all_main_posts = []
            for i, u in enumerate(test_users):
                p = Post(
                    content=f"這是由 {u.name} 發佈的主貼文內容 #測試{i+1}",
                    owner_id=u.id
                )
                session.add(p)
                all_main_posts.append(p)
            
            await session.flush()

            # --- 建立 9 則留言 (Comment) ---
            for p in all_main_posts:
                for u in test_users:
                    comment = Post(
                        content=f"我是 {u.name}，這是對貼文 {p.id} 的回覆留言",
                        owner_id=u.id,
                        parent_id=p.id
                    )
                    session.add(comment)
            
            await session.commit()
            logging.info("測試資料 Seeding 成功！")
            
        except Exception as e:
            await session.rollback()
            logging.error(f"Seeding 過程發生錯誤: {e}")
            raise        