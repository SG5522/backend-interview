import uuid
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
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
    async def is_blocked(user_a: uuid.UUID, user_b: uuid.UUID, db: AsyncSession) -> bool:
        """
        檢查user_a與user_b是否在有封鎖關係
        """
        query = select(Blacklist).where(
                or_(
                    and_(Blacklist.user_id == user_a, Blacklist.blocked_user_id == user_b),
                    and_(Blacklist.user_id == user_b, Blacklist.blocked_user_id == user_a)
                )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
        
    @staticmethod
    async def get_blocked_ids(user_id: uuid.UUID, db: AsyncSession) -> set[uuid.UUID]:
        """
        取得雙向封鎖名單 ID。
        使用 set 是為了自動去除重複的 ID。
        """
        # 我封鎖的人  
        query1 = select(Blacklist.blocked_user_id).where(Blacklist.user_id == user_id)
        # 封鎖我的人
        query2 = select(Blacklist.user_id).where(Blacklist.blocked_user_id == user_id)
        res1 = await db.execute(query1)
        res2 = await db.execute(query2)
        return set(res1.scalars().all()) | set(res2.scalars().all())