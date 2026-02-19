import uuid
from pydantic import BaseModel, EmailStr, Field

# 繼承用的基底類別
class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    name: str | None = Field(default=None, max_length=255)

# 建立user時的 ViewModel
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

# 更新User資料的ViewModel
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    password: str | None = None

# 回傳給前端用的 ViewModel
class UserPublic(UserBase):
    id: uuid.UUID