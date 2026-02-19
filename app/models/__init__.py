# app/models/__init__.py
from .base import Base
from .user import User
from .post import Post

# SQLModel tables
__all__ = ["Base", "User", "Post"]