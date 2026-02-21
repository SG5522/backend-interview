import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.service.post_service import PostService
from app.schemas.post import PostPublic, PostCreate
from app.router.user_router import get_current_user


router = APIRouter()

@router.get("/", response_model=list[PostPublic])
async def get_post_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    # 這裡直接引用你剛才貼給我的那個函數
    current_user = Depends(get_current_user) 
):
    """
    獲取動態牆
    """
    posts = await PostService.get_multi(
        db=db,
        current_user_id=current_user.id, 
        skip=skip,
        limit=limit
    )
    return posts

@router.post("/create")
async def create_new_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    建立新貼文：
    1. parent_id 為 null 代表主貼文
    2. parent_id 有值代表回覆某篇貼文
    """
    # 這裡呼叫 Service 建立資料，並強制綁定當前登入者 ID
    new_post = await PostService.create_post(
        db=db, 
        obj_in=post_in, 
        user_id=current_user.id
    )
    return new_post

@router.post("/{post_id}/like")
async def toggle_post_like(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    liked = await PostService.toggle_like(db, post_id, current_user.id)
    return {"status": "success", "is_liked": liked}