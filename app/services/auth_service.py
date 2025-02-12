import httpx
from fastapi import HTTPException
from app.core.database import users_collection
from app.core.security import create_access_token, decode_access_token
from app.config import settings
from fastapi.responses import JSONResponse
from app.schemas.auth import OAuthLoginResponse, OAuthCallbackResponse, LogoutResponse

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
REDIRECT_URI = "http://localhost:8000/auth/google/callback"

async def get_google_login_url():
    """Google OAuth 로그인 URL 생성"""
    return OAuthLoginResponse(auth_url=(
        f"{GOOGLE_AUTH_URL}"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=email%20profile"
        f"&access_type=offline"
    ))

async def authenticate_google_user(code: str):
    """Google OAuth 인증 후 사용자 정보 가져오기 및 JWT 발급"""
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        # 🔹 Google OAuth2 토큰 요청
        token_response = await client.post(GOOGLE_TOKEN_URL, data=data)
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="OAuth 인증 실패")

        # 🔹 Google 사용자 정보 가져오기
        user_info_response = await client.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        user_info = user_info_response.json()

        email = user_info.get("email")
        username = user_info.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="사용자 이메일을 가져올 수 없음")

        # ✅ 사용자 정보 저장 (업데이트 가능하도록 변경)
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            await users_collection.update_one(
                {"email": email},
                {"$set": {"username": username, "oauth_provider": "google"}}
            )
        else:
            await users_collection.insert_one({"email": email, "username": username, "oauth_provider": "google"})

        # 🔹 JWT 생성 및 쿠키 저장
        jwt_token = create_access_token({"email": email})
        response = JSONResponse(content={"message": "Login successful", "access_token": jwt_token})

        # ✅ 보안 강화를 위한 쿠키 설정
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {jwt_token}",
            httponly=True,
            samesite="Strict",  # ✅ 보안 강화
        )

        return OAuthCallbackResponse(message="Login successful", access_token=jwt_token)

def logout_user(response: JSONResponse):
    """로그아웃 (쿠키 삭제)"""
    response.delete_cookie("Authorization")
    return LogoutResponse(message="Logout successful")

def get_authenticated_user(token: str):
    """JWT에서 현재 로그인한 사용자 정보 가져오기"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(token.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload["email"]
