import uuid
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.service.post_service import PostService
from app.schemas.post import PostPublic, PostCreate
from app.schemas.user import UserPublic 
from app.router.user_router import get_current_user


router = APIRouter()

@router.get("/{post_id}/", response_model=PostPublic)
async def get_by_id(
    post_id: uuid.UUID,    
    db: AsyncSession = Depends(get_db),
    current_user : UserPublic = Depends(get_current_user) 
):
    """
    從post_id獲取貼文內容
    """
    post = await PostService.get_by_id(
        db=db,
        post_id=post_id, 
        current_user_id=current_user.id, 
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到該貼文")    
    return post

@router.get("/", response_model=list[PostPublic])
async def get_post_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    # 這裡直接引用你剛才貼給我的那個函數
    current_user : UserPublic = Depends(get_current_user) 
):
    """
    獲取Post
    """
    posts = await PostService.get_multi(
        db=db,
        current_user_id=current_user.id, 
        skip=skip,
        limit=limit
    )
    return posts

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_new_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user : UserPublic = Depends(get_current_user)
):
    """
    建立新貼文：
    1. parent_id 為 null 代表主貼文
    2. parent_id 有值代表回覆某篇貼文
    """
    if post_in.parent_id:
        parent_post = await PostService.get_by_id(db, post_in.parent_id, current_user.id)
        if not parent_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="你要回覆的貼文不存在")
    
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
    current_user: UserPublic = Depends(get_current_user)
):
    post = await PostService.get_by_id(db, post_id, current_user.id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="貼文不存在，無法點讚")
    
    liked = await PostService.toggle_like(db, post_id, current_user.id)
    return {"status": status.HTTP_200_OK, "is_liked": liked}