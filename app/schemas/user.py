import uuid
from app.models.user import UserRole
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# 繼承用的基底類別
class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)    
    
# 登入用的 ViewModel
class UserLogin(UserBase):    
    password: str = Field(min_length=8, max_length=128)

# 建立user時的 ViewModel
class UserCreate(UserLogin):
    name: str | None = Field(default=None, max_length=255)    

# 更新User資料的ViewModel
class UserUpdate(BaseModel):    
    name: str | None = None
    password: str | None = None

# 回傳給前端用的 ViewModel
class UserPublic(UserBase):
    id: uuid.UUID
    name: str | None = None
    role: UserRole = UserRole.USER
    model_config = ConfigDict(from_attributes=True)