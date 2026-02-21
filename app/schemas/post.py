import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .user import UserPublic

# 基底
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100, description="貼文標題")
    content: str = Field(max_length=4096, description="貼文內容")

# 建立貼文 (輸入)
class PostCreate(PostBase):
    parent_id: Optional[uuid.UUID] = Field(None, description="上層貼文 ID (若為回覆留言則必填)")    

# 編譯貼文
class PostEdit(BaseModel):
    title: str | None = Field(None, max_length=100, description="欲修改的標題，不修改則傳 null")
    content: str | None = Field(None, max_length=4096, description="欲修改的內容，不修改則傳 null")

# 回傳給前端用的 (輸出)
class PostPublic(PostBase):
    """
    貼文公開資訊回傳格式，包含作者資訊、上層貼文id、置頂貼文及按讚統計。
    """
    id: uuid.UUID = Field(description="貼文識別碼 (UUID)")
    owner_id: uuid.UUID = Field(description="發文者的user ID")
    createdDateTime: datetime = Field(description="建立時間")
    updatedDateTime: datetime = Field(description="最後更新時間")       
    owner: UserPublic | None = Field(None, description="發文者的詳細公開資訊")
    # 上層貼文id
    parent_id: Optional[uuid.UUID] = Field(None, description="上層貼文id")
    # 置頂貼文
    top_comment: Optional["PostPublic"] = Field(None, description="置頂貼文")
    # 回覆貼文ˋ
    replies: list["PostPublic"] = Field([], description="該貼文下方的所有回覆貼文列表")
    # 按讚統計
    likes_count: int = Field(0, description="按讚統計")
    # 是否按過讚
    is_liked: bool = Field(False, description="當前登入使用者是否按過讚")

    model_config = ConfigDict(from_attributes=True)

# 執行重建，讓PostPublic.replies的 list["PostPublic"] 產生效果
PostPublic.model_rebuild()