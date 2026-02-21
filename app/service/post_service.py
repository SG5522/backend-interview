import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, exists, case
from app.models import Post, Like, Blacklist
from app.schemas.post import PostCreate, PostEdit, PostPublic

# 過濾黑名單的user與被黑名單的User貼文    
def get_blocked_filter(user_id: uuid.UUID):
        return ~exists().where(
            Blacklist.user_id == user_id, 
            Blacklist.blocked_user_id == Post.owner_id
        )

# 確認是否點讚    
def get_is_liked_expr(user_id: uuid.UUID):
    return (
        select(Like.post_id)
        .where(Like.post_id == Post.id, Like.user_id == user_id)
        .scalar_subquery()
    )

class PostService:    
    @staticmethod
    async def create_post(db: AsyncSession, obj_in: PostCreate, user_id: uuid.UUID):
        """
        建立新貼文 or 回覆    
        """
        db_obj = Post(
            title=obj_in.title,
            content=obj_in.content,
            parent_id=obj_in.parent_id, # 如果是 None 就是發文，有值就是留言
            user_id=user_id
        )
        db.add(db_obj)
        await db.commit()        
        return db_obj

    @staticmethod
    async def get_multi(db: AsyncSession, current_user_id: uuid.UUID, skip: int = 0, limit: int = 20):
        '''
        搜尋貼文預計到20篇
        '''    

        query = (
            select(Post)
            .where(Post.parent_id == None)
            .order_by(Post.createdDateTime.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)

        posts = result.scalars().all() # 這裡拿到的是 Post 物件列表
    
        return [
            PostPublic(
                id=p.id,
                title=p.title,
                content=p.content,
                owner_id=p.owner_id,
                createdDateTime=p.createdDateTime,
                updatedDateTime=p.updatedDateTime,
                parent_id=p.parent_id,
                # 💡 關鍵：強制把會觸發 Lazy Load 的地方設為 None 或空列表
                owner=None, 
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
        
