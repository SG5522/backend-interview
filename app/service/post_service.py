import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, not_
from sqlalchemy.orm import selectinload
from app.models import Post, Like, Blacklist
from app.schemas.post import PostCreate, PostEdit, PostPublic

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
    async def get_by_id(db: AsyncSession, post_id: uuid.UUID, current_user_id: uuid.UUID):
        # 💡 重點：一次抓出貼文 + 按讚名單 + 發文者 + 回覆
        query = (
            select(Post)
            .options(
                selectinload(Post.liked_by_users),  # 抓出按讚名單
                selectinload(Post.user),           # 抓出發文者(owner)
                selectinload(Post.replies)         # 抓出子貼文(留言)
            )
            .where(Post.id == post_id)
        )
        
        result = await db.execute(query)
        p = result.scalar_one_or_none()
        
        if not p:
            return None

        # 轉成 Pydantic Schema 回傳
        return PostPublic(
            id=p.id,            
            content=p.content,
            owner_id=p.owner_id,
            createdDateTime=p.createdDateTime,
            updatedDateTime=p.updatedDateTime,
            parent_id=p.parent_id,
            likes_count=len(p.liked_by_users),
            is_liked=any(user.id == current_user_id for user in p.liked_by_users),
            owner=p.user,  
            top_comment=None, 
            replies=p.replies
        )

    @staticmethod
    async def get_multi(db: AsyncSession, current_user_id: uuid.UUID, skip: int = 0, limit: int = 20):
        '''
        依skip、limit搜尋貼文內容
        '''        
        # 找出黑名單
        blacklist_subquery = (
            select(Blacklist.blocked_user_id)
            .where(Blacklist.user_id == current_user_id)
        ).scalar_subquery()
        
        query = (
            select(Post)
            .options(
                selectinload(Post.liked_by_users),
                selectinload(Post.user)                
            ) 
            .where(
                Post.parent_id == None,
                not_(Post.owner_id.in_(blacklist_subquery))
            )
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)

        posts = result.scalars().all() # 這裡拿到的是 Post 物件列表
    
        return [
            PostPublic(
                id=p.id,                
                content=p.content,
                owner_id=p.owner_id,
                createdDateTime=p.createdDateTime,
                updatedDateTime=p.updatedDateTime,
                parent_id=p.parent_id,      
                likes_count=len(p.liked_by_users),
                is_liked=any(user.id == current_user_id for user in p.liked_by_users),          
                owner=p.user,                 
                top_comment=None,
                replies=[],     
            ) for p in posts
        ]

    @staticmethod
    async def toggle_like(db: AsyncSession, post_id: uuid.UUID, user_id: uuid.UUID) -> bool:
            """
            切換按讚狀態        
            """
            # 檢查是否已經按過讚
            like_query = select(Like).where(
                Like.post_id == post_id,
                Like.user_id == user_id
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
                new_like = Like(post_id=post_id, user_id=user_id)
                db.add(new_like)
                try:
                    await db.commit()
                except Exception:
                    # 以防貼文不存或按讚失敗rollback
                    await db.rollback()
                    raise Exception("貼文不存在或按讚失敗")
                return True
        
