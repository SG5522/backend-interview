from fastapi import FastAPI, Depends
from app.router import user_router
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import init_db, get_db

# lifespan 會在程式啟動時跑一次 yield 之前的code，關閉時跑一次 yield 之後的code
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 伺服器重啟時會執行 init_db
    # SQLAlchemy 內部的 create_all 會檢查表是否存在，存在則跳過，確保資料不被覆蓋
    await init_db()
    yield

# 實例化 FastAPI
app = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix="/users", tags=["User"])

# 測試api是否有啟用
@app.get("/")
async def read_root():
    return {"status": "success", "message": "FastAPI 3.13 環境啟動成功！"}

# 測試db是否連線正常 (透過 DI 注入)
@app.get("/db-check")
async def check_db_connection(db: AsyncSession = Depends(get_db)):
    return {"status": "connected"}