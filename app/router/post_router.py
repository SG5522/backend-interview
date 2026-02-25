import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.database import get_db
from app.service.post_service import PostService
from app.schemas.post import PostPublic, PostCreate, PostSimple
from app.schemas.user import UserPublic 
from app.service.black_list_service import BlacklistService
from app.router.user_router import get_current_user


router = APIRouter()

@router.get("/{post_id}/", response_model=PostPublic, summary="透過 post_id 取得貼文內容")
async def get_by_id(
    post_id: uuid.UUID,    
    db: AsyncSession = Depends(get_db),
    current_user : UserPublic = Depends(get_current_user) 
):
    """
    從post_id取得貼文內容
    內容包含：貼文者資訊、點讚數、點讚狀態、置頂留言以及所有回覆列表。
    """
    if not await PostService.check_post(db, post_id):
        raise errors.PostErrors.NotFound()
    
    owner_id = await PostService.get_owner_id(db, post_id)
    
    if await BlacklistService.is_blocked(owner_id, current_user.id , db):
        raise errors.PostErrors.Blocked()
    
    return await PostService.get_by_id(db, post_id, current_user.id)    

@router.get("/", response_model=list[PostSimple], summary="取得貼文列表")
async def get_post_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    # 這裡直接引用你剛才貼給我的那個函數
    current_user : UserPublic = Depends(get_current_user) 
):
    """
    分頁取得主貼文列表。
    1. 僅回傳 parent_id 為 null 的主貼文。
    2. 自動排除黑名單用戶的內容。
    """
    return await PostService.get_posts(db, current_user.id, skip, limit)    

@router.post("/create", status_code=status.HTTP_201_CREATED, summary="建立新貼文")
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
            raise errors.PostErrors.NotFound()
            
        is_blocked = await BlacklistService.is_blocked(parent_post.owner.id, current_user.id, db)
    
        if is_blocked:
            raise errors.PostErrors.Blocked()
    return await PostService.create_post(db, post_in, user_id=current_user.id)    

@router.post("/{post_id}/top-comment", summary="置頂留言")
async def set_post_top_Comment(
    post_id: uuid.UUID,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user)
):
    """
    將指定的回覆（comment_id）設為該貼文（post_id）的置頂留言。
    只有貼文作者本人可以執行此操作。
    """
    if not await PostService.check_post(db, post_id):    
        raise errors.PostErrors.NotFound()
    
    if not await PostService.is_comment_belong_to_post(db, post_id, comment_id):            
        raise errors.CommentErrors.NotBelongToPost()        
    
    success = await PostService.set_top_comment(db, post_id, current_user.id, comment_id)
    
    if not success:        
        raise errors.PostErrors.NotOwner()        
    
    return {"status": status.HTTP_200_OK}

@router.post("/{post_id}/like", summary="按讚貼文")
async def toggle_post_like(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user)
):
    """    
    切換按讚狀態。
    若未按讚則執行按讚；若已按讚則取消按讚。
    """
    if not await PostService.check_post(db, post_id):    
        raise errors.PostErrors.NotFound()
    
    liked = await PostService.toggle_like(db, post_id, current_user.id)
    return {"status": status.HTTP_200_OK, "is_liked": liked}