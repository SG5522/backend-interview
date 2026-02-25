from fastapi import HTTPException, status

class ServiceException(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: dict = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

# --- 驗證相關 ---        
class AuthErrors:
    class InvalidToken(ServiceException):
        def __init__(self):
            # 這裡直接把 Headers 包進去，外部就不用每次都寫
            super().__init__(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="憑證無效或已過期",
                headers = {"WWW-Authenticate": "Bearer"}
            )
    class AccessDenied(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_403_FORBIDDEN, "你沒有權限操作")            
        
# --- 使用者相關 (User) ---
class UserErrors:
    class InvalidCredentials(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_401_UNAUTHORIZED, "帳號或密碼錯誤")

    class AlreadyExists(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_400_BAD_REQUEST, "該 Email 已經被註冊過了")

# --- 貼文相關 (Post) ---
class PostErrors:
    class NotFound(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_404_NOT_FOUND, "找不到該貼文")

    class AccessDenied(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_403_FORBIDDEN, "你沒有權限操作此貼文")

    class Blocked(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_403_FORBIDDEN, "由於封鎖關係，無法查看或回覆內容")
            
    class NotOwner(ServiceException):        
        def __init__(self):
            super().__init__(status.HTTP_403_FORBIDDEN, "無權進行此操作，只有作者可以執行")

# --- 留言相關 (Comment) ---
class CommentErrors:
    class NotFound(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_404_NOT_FOUND, "找不到該則留言")

    class NotBelongToPost(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_400_BAD_REQUEST, "該留言不屬於此貼文，或留言不存在")
            
# --- 黑名單相關 (Blacklist) ---
class BlacklistErrors:
    class SelfBlock(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_400_BAD_REQUEST, "不能黑名單自己")

    class TargetNotFound(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_404_NOT_FOUND, "目標使用者不存在")

    class AlreadyBlocked(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_400_BAD_REQUEST, "已在黑名單中")

    class NotInBlacklist(ServiceException):
        def __init__(self):
            super().__init__(status.HTTP_404_NOT_FOUND, "黑名單中找不到該使用者")            
    