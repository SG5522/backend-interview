from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from .models.base import Base
from .models.user import User
from .models.post import Post

# 使用 aiosqlite 驅動，sqlite+aiosqlite
# 如果以後換成 Postgres，只需改這行：postgresql+asyncpg://user:pass@localhost/dbname
# 上述參考ai得知的
DATABASE_URL = "sqlite+aiosqlite:///./test.db"


engine = create_async_engine(DATABASE_URL, echo=True)

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

# 初始化資料庫（建立所有資料表）
async def init_db():
    async with engine.begin() as conn:        
        await conn.run_sync(Base.metadata.create_all)