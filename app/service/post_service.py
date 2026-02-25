import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, not_
from sqlalchemy.orm import selectinload
from app.models import Post, Like
from app.schemas.post import PostCreate, PostPublic, PostSimple
from app.service.black_list_service import BlacklistService

class PostService:    
    @staticmethod
    async def create_post(db: AsyncSession, obj_in: PostCreate, user_id: uuid.UUID):
        """
        建立新貼文 or 回覆    
        """
        db_obj = Post(            
            content=obj_in.content,
            parent_id=obj_in.parent_id, # 如果是 None 就是發文，有值就是留言
            owner_id=user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj, attribute_names=["id", "createdDateTime"])
        return db_obj
    
    @staticmethod
    async def set_top_comment(
        db: AsyncSession, 
        post_id: uuid.UUID, 
        owner_id: uuid.UUID, 
        top_comment_id: uuid.UUID | None
    ) -> bool : 
        query = (
            update(Post)
            .where(Post.id == post_id, Post.owner_id == owner_id)
            .values(top_comment_id=top_comment_id)
        )
        
        result = await db.execute(query)
        await db.commit()
            
        return result.rowcount > 0
    
    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: uuid.UUID, current_user_id: uuid.UUID):             
        blocked_ids = await BlacklistService.get_blocked_ids(current_user_id, db)
                           
        query = (
            select(Post)
            .options(
                selectinload(Post.liked_by_users),  # 抓出按讚名單
                selectinload(Post.user),           # 抓出發文者(owner)
                selectinload(Post.comments).selectinload(Post.user),         # 抓出子貼文(留言)
                selectinload(Post.top_comment).selectinload(Post.user)       # 抓出置頂留言
            )
            .where(Post.id == post_id)
        )
        
        result = await db.execute(query)
        p = result.scalar_one_or_none()
        
        if not p:
            return None
                    
        final_top_comment = None
        if p.top_comment and p.top_comment.owner_id not in blocked_ids:
            final_top_comment = PostSimple.model_validate(p.top_comment)

        # 轉成 Pydantic Schema 回傳
        return PostPublic(
            id=p.id,            
            content=p.content,            
            createdDateTime=p.createdDateTime,
            updatedDateTime=p.updatedDateTime,
            parent_id=p.parent_id,
            likes_count=len(p.liked_by_users),
            is_liked=any(user.id == current_user_id for user in p.liked_by_users),
            owner=p.user,              
            top_comment=final_top_comment,            
            comment=[PostSimple.model_validate(r) for r in p.comments if r.id != p.top_comment_id and r.owner_id not in blocked_ids] #目前找不到更適合的方式用SQL過濾暫時由輸出時來過濾
        )     
        
    #確認是否有該筆post
    @staticmethod
    async def check_post(db: AsyncSession, post_id: uuid.UUID) -> bool:        
        result = await db.execute(
            select(Post.id).where(Post.id == post_id)
        )
        return result.first() is not None            

    @staticmethod
    async def get_owner_id(db: AsyncSession, post_id: uuid.UUID) -> uuid.UUID | None:
        """
        取得貼文作者 ID，用於權限或黑名單校驗
        """
        result = await db.execute(
            select(Post.owner_id).where(Post.id == post_id)
        )
        return result.scalar()
    
    @staticmethod
    async def is_comment_belong_to_post(db: AsyncSession, post_id: uuid.UUID, comment_id: uuid.UUID) -> bool:
        """
        檢查 comment_id 是否真的為 post_id 的回覆
        """
        query = select(Post).where(Post.id == comment_id, Post.parent_id == post_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_posts(db: AsyncSession, current_user_id: uuid.UUID, skip: int = 0, limit: int = 20):
        """
        依skip、limit搜尋貼文內容
        """        
        
        # 找出黑名單
        blocked_ids = await BlacklistService.get_blocked_ids(current_user_id, db)
        
        query = (
            select(Post)
            .options(
                selectinload(Post.liked_by_users),
                selectinload(Post.user)                
            ) 
            .where(
                Post.parent_id == None,
                not_(Post.owner_id.in_(blocked_ids))
            )
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)

        posts = result.scalars().all() # 這裡拿到的是 Post 物件列表
    
        return [
            PostSimple(
                id=p.id,                
                content=p.content,
                owner=p.user,
                createdDateTime=p.createdDateTime,                  
                likes_count=len(p.liked_by_users),
                is_liked=any(user.id == current_user_id for user in p.liked_by_users)  
            ) for p in posts
        ]

    @staticmethod
    async def toggle_like(db: AsyncSession, post_id: uuid.UUID, owner_id: uuid.UUID) -> bool:
            """
            切換按讚狀態        
            """
            # 檢查是否已經按過讚
            like_query = select(Like).where(
                Like.post_id == post_id,
                Like.user_id == owner_id
            )
            result = await db.execute(like_query)
            existing_like = result.scalar_one_or_none()

            if existing_like:
                # 如果存在，則刪除 (取消按讚)
                await db.delete(existing_like)
                await db.commit()
                return False
            else:
                # 如果不存在，則建立 (按讚)
                new_like = Like(post_id=post_id, user_id=owner_id)
                db.add(new_like)
                try:
                    await db.commit()
                except Exception:
                    # 以防貼文不存或按讚失敗rollback
                    await db.rollback()
                    raise Exception("貼文不存在或按讚失敗")
                return True
        
