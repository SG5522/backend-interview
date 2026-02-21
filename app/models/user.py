import uuid
import sqlalchemy
from enum import IntEnum
from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .post import Post    
    from .like import Like
    from .blacklist import Blacklist

class UserRole(IntEnum):
    ADMIN = 0
    USER = 1
    GUEST = 2

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

    role : Mapped[UserRole] = mapped_column(sqlalchemy.Integer, server_default="1", nullable=False)

    # 對posts關聯一對多    
    posts: Mapped[list["Post"]] = relationship(
        "Post", 
        back_populates="user",
        cascade="all, delete-orphan" # 使用者刪除時，其貼文自動刪除
    )

    Blacklist_users: Mapped[list["User"]] = relationship(
        "User",
        secondary="blacklist",
        primaryjoin="User.id == Blacklist.user_id",
        secondaryjoin="User.id == Blacklist.blocked_user_id",        
        viewonly=True
    )

    liked_posts: Mapped[list["Post"]] = relationship(
        "Post",
        secondary="like",
        back_populates="liked_by_users",
        viewonly=True
    )