import httpx
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from app.core.database import users_collection
from app.core.security import create_access_token
from app.config import settings

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
REDIRECT_URI = "http://localhost:8000/auth/google/callback"

# ✅ OAuth 로그인 URL 반환
@router.get("/google/login")
async def google_login():
    auth_url = (
        f"{GOOGLE_AUTH_URL}"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=email%20profile"
        f"&access_type=offline"
    )
    return JSONResponse(content={"auth_url": auth_url})

# ✅ OAuth 로그인 후 JWT 자동 저장
@router.get("/google/callback")
async def google_callback(code: str, response: Response):
    """OAuth 로그인 후 JWT 발급 및 자동 저장"""
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data=data)
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="OAuth 인증 실패")

        # ✅ Google 사용자 정보 가져오기
        response = await client.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        user_info = response.json()

        email = user_info.get("email")
        username = user_info.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="사용자 이메일을 가져올 수 없음")

        # ✅ 사용자 정보 저장 (이미 존재하면 저장하지 않음)
        existing_user = await users_collection.find_one({"email": email})
        if not existing_user:
            await users_collection.insert_one({"email": email, "username": username, "oauth_provider": "google"})

        # ✅ JWT 생성 & 자동 저장 (쿠키 활용)
        jwt_token = create_access_token({"email": email})
        response = JSONResponse(content={"access_token": jwt_token, "token_type": "bearer"})
        response.set_cookie(key="Authorization", value=f"Bearer {jwt_token}", httponly=True)

        return response
