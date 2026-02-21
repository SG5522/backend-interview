# app/schemas/__init__.py
from .user import UserCreate, UserUpdate, UserPublic
from .post import PostCreate, PostEdit, PostPublic

# ViewModel tables
__all__ = ["UserCreate", "UserUpdate", "UserPublic", "PostCreate", "PostEdit", "PostPublic"]