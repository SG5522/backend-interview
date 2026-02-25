import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.database import get_db
from app.service.black_list_service import BlacklistService
from app.service.user_service import UserService
from app.schemas.user import UserPublic
from app.router.user_router import get_current_user

router = APIRouter()

@router.post("/{target_user_id}", status_code=status.HTTP_201_CREATED)
async def block_user(
    target_user_id: uuid.UUID,    
    db: AsyncSession = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user) 
):
    """
    將該使用者ID加入黑名單
    """            
    # 防止自己黑自己
    if target_user_id == current_user.id:        
        raise errors.BlacklistErrors.SelfBlock()
    
    # 確認是否有該user
    target_user = await UserService.get_user_by_id(target_user_id, db)
    if not target_user:        
        raise errors.BlacklistErrors.TargetNotFound()
    
    # 是否已在黑名單
    if await BlacklistService.is_blocked(current_user.id, target_user_id, db):
        raise errors.BlacklistErrors.AlreadyBlocked()            
    
    await BlacklistService.block_user(
        user_id=current_user.id, 
        blocked_user_id=target_user_id, 
        db=db
    )
    return {"message": "已成功加入黑名單"}  

@router.delete("/{target_user_id}")
async def unblock_user(
    target_user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user : UserPublic = Depends(get_current_user)
):
    """
    將該使用者ID移除黑名單
    """
    success = await BlacklistService.unblock_user(
        user_id=current_user.id, 
        blocked_user_id=target_user_id, 
        db=db
    )
    if not success:
        raise errors.BlacklistErrors.NotInBlacklist()
    return {"message": "已解除黑名單"}