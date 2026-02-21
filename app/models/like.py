import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Like(Base):
    __tablename__ = "like"

    # 按讚使用者ID
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    # 按讚的貼文ID
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), primary_key=True
    )