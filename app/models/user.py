import uuid
from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .post import Post    

class User(Base):
    __tablename__ = "user"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # 對posts關聯一對多    
    posts: Mapped[list["Post"]] = relationship(
        "Post", 
        back_populates="user",
        cascade="all, delete-orphan" # 使用者刪除時，其貼文自動刪除
    )