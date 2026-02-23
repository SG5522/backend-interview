import logging
import os
from alembic.config import Config
from alembic import command
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.router import user_router, post_router, black_list_router
from app.models import User, UserRole
from app.database import async_session_factory, get_db
from app.core.config import settings
from app.core.security import SecurityHelper

# tokenUrl 登入 API 地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# lifespan 會在程式啟動時跑一次 yield 之前的code，關閉時跑一次 yield 之後的code
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 這段代碼相當於 EF Core 的 Database.Migrate()
    logging.info("正在檢查資料庫遷移...")
    try:
        # 取得ini檔的絕對路徑
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ini_path = os.path.join(root_dir, "alembic.ini")
        alembic_cfg = Config(ini_path)
        
        # 手動指定 script_location 的絕對路徑
        alembic_cfg.set_main_option("script_location", os.path.join(root_dir, "alembic"))

        # 設定Alembic連線字串
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        # 執行 upgrade head
        command.upgrade(alembic_cfg, "head")
        logging.info("資料庫遷移完成！")

        async with async_session_factory() as session:
        # 檢查是否已經有任何使用者 (或特定檢查 admin)
            result = await session.execute(select(User).where(User.name == "admin"))
            admin_user = result.scalar_one_or_none()

            if not admin_user:
                print("偵測到系統無管理員，正在建立預設 Admin...")
                new_admin = User(
                    name="admin",
                    email="admin@example.com",
                    password=SecurityHelper.get_password_hash("1qaz@WSX"), # 暫時密碼
                    role=UserRole.ADMIN
                )
                session.add(new_admin)
                await session.commit()
                await session.close()
                logging.info("預設管理員建立成功！帳號: admin")
            else:
                logging.info("管理員帳號已存在，跳過。")
    except Exception as e:
        logging.error(f"資料庫遷移失敗: {e}")    
    yield
    logging.info("正在關閉...")

# 實例化 FastAPI
app = FastAPI(
    title="面試題目", 
    description="貼文、按讚與黑名單功能的後端",
    version="0.1.0",
    lifespan=lifespan)

app.include_router(user_router, prefix="/users", tags=["User"])
app.include_router(post_router, prefix="/posts", tags=["Post"])
app.include_router(black_list_router, prefix="/blacklist", tags=["Blacklist"])

# 測試api是否有啟用
@app.get("/")
async def read_root():
    return {"status": "success", "message": "FastAPI 3.13 環境啟動成功！"}

# 測試db是否連線正常 (透過 DI 注入)
@app.get("/db-check")
async def check_db_connection(db: AsyncSession = Depends(get_db)):
    return {"status": "connected"}