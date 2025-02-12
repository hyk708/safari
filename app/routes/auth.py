from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import decode_access_token
from app.core.database import users_collection
from app.services.auth_service import (
    get_google_login_url,
    authenticate_google_user,
    logout_user,
    login_for_access_token,  # 일반 로그인 (아이디/비번)
)

router = APIRouter()

# ✅ 일반 로그인 (아이디 / 비번)
@router.post("/token")  # /auth/token
async def normal_login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)

# ✅ Google 로그인 URL 반환
@router.get("/google/login")  # /auth/google/login
async def google_login():
    google_auth = await get_google_login_url()
    return {"auth_url": google_auth.auth_url}

# ✅ Google OAuth Callback
@router.get("/google/callback")
async def google_callback(request: Request, code: str):
    return await authenticate_google_user(code)

# ✅ 로그아웃
@router.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/")  # ✅ 로그아웃 후 /로 이동
    response.delete_cookie("Authorization", path="/")  # ✅ 쿠키 삭제
    return response

# ✅ 로그인된 사용자 정보 조회 (username 포함)
@router.get("/me")
async def get_current_user(request: Request):
    token = request.cookies.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # ✅ Bearer 프리픽스를 자동으로 처리하도록 변경
    token = token.replace("Bearer ", "") if "Bearer " in token else token  
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload["email"]
    user = await users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "email": email,
        "username": user.get("username", "사용자"),
        "oauth_provider": user.get("oauth_provider", "local"),
    }

