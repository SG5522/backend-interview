import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from app.core.config import settings

# 
class SecurityHelper:
    @staticmethod
    # 定義密碼hash
    def get_password_hash(password: str) -> str:        
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    # 驗證密碼
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:        
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    # 建立授權token
    @ staticmethod
    def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):        
        to_encode = data.copy() #以防改掉原來的資料要用.copy()處理
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        # 從環境變數讀取 SECRET_KEY
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt