import uuid
from typing import Optional
from sqlalchemy import ForeignKey, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import Optional,TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    

class Post(Base):
    __tablename__ = "post"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # 標題
    title: Mapped[str | None]= mapped_column(String(255), nullable=True)
    
    # 內文
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # FK：指向 User 表
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), 
        nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="posts")

    # --- 自我關聯 (Self-Referencing) ---
    # 子項目id    
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("post.id", ondelete="SET NULL")
    )
    
    # 取得父項目 (指向上層的單一物件)
    parent: Mapped[Optional["Post"]] = relationship(
        "Post",
        foreign_keys=[parent_id], # 明確指定使用parent_id
        back_populates="replies",
        remote_side="Post.id" 
    )

    # 取得子項目清單 (指向下層的 List)
    replies: Mapped[list["Post"]] = relationship(
        "Post",
        foreign_keys=[parent_id], # 明確指定使用parent_id 
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    # 置頂留言
    top_comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("post.id", ondelete="SET NULL"), 
        nullable=True
    )

    # 與置頂留言建立關係
    top_comment: Mapped[Optional["Post"]] = relationship(
        "Post",
        foreign_keys=[top_comment_id],
        remote_side="Post.id",
        post_update=True #避免循環依賴
    )

    liked_by_users: Mapped[list["User"]] = relationship(
        "User",
        secondary="like",       
        back_populates="liked_posts",
        viewonly=True
    )