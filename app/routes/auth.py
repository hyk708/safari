from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import JSONResponse
from app.services.auth_service import get_google_login_url, authenticate_google_user, logout_user, get_authenticated_user
from app.schemas.auth import OAuthLoginResponse, OAuthCallbackResponse, LogoutResponse, UserResponse

router = APIRouter()

# ✅ Google OAuth 로그인 URL 반환
@router.get("/google/login", response_model=OAuthLoginResponse)
async def google_login():
    return await get_google_login_url()

# ✅ Google OAuth 인증 후 JWT 발급 및 쿠키 저장
@router.get("/google/callback", response_model=OAuthCallbackResponse)
async def google_callback(code: str):
    return await authenticate_google_user(code)

# ✅ 로그아웃 (쿠키 삭제)
@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response):
    return logout_user(response)

# ✅ 현재 로그인한 사용자 정보 조회
@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request):
    """현재 로그인한 사용자 정보 가져오기"""
    token = request.cookies.get("Authorization")
    return {"email": get_authenticated_user(token)}
