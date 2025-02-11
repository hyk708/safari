from datetime import datetime, timedelta
from jose import jwt
from fastapi import Request
from app.config import settings

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    """JWT 생성 함수"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """JWT 디코딩 함수"""
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return decoded
    except Exception:
        return None

def get_current_user(request: Request):
    """쿠키에서 JWT 토큰 자동 추출"""
    token = request.cookies.get("Authorization")
    if not token:
        return None
    token = token.replace("Bearer ", "")
    return decode_access_token(token)
