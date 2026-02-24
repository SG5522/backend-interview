import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能黑名單自己")    
    
    # 確認是否有該user
    target_user = await UserService.get_user_by_id(target_user_id, db)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目標使用者不存在")
    
    # 是否已在黑名單
    if await BlacklistService.is_blocked(current_user.id, target_user_id, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已在黑名單中")        
    
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="黑名單中找不到該使用者")
    return {"message": "已解除黑名單"}