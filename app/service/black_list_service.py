import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.service.user_service import UserService
from app.models import Blacklist

class BlacklistService:
    @staticmethod
    async def block_user(user_id: uuid.UUID, blocked_user_id: uuid.UUID, db: AsyncSession):
        """
        新增黑名單
        """
        
        # 建立關聯
        new_block = Blacklist(
            user_id=user_id,
            blocked_user_id=blocked_user_id
        )
        
        db.add(new_block)
        await db.commit()
        await db.refresh(new_block)
        return new_block

    @staticmethod
    async def unblock_user(user_id: uuid.UUID, blocked_user_id: uuid.UUID, db: AsyncSession):
        """
        移除黑名單
        """
        query = select(Blacklist).where(
                Blacklist.user_id == user_id,
                Blacklist.blocked_user_id == blocked_user_id
        )
        result = await db.execute(query)
        target = result.scalar_one_or_none()

        if target:
            await db.delete(target)
            await db.commit()
            return True
        return False

    @staticmethod
    async def is_blocked(user_id: uuid.UUID, blocked_user_id: uuid.UUID, db: AsyncSession) -> bool:
        """
        檢查是否在黑名單中
        """
        query = select(Blacklist).where(
                Blacklist.user_id == user_id,
                Blacklist.blocked_user_id == blocked_user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None