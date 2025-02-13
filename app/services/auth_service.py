import httpx
from fastapi import Depends, HTTPException, Request, Response
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm

from app.core.database import users_collection
from app.core.security import create_access_token, decode_access_token
from app.config import settings
from app.schemas.auth import OAuthLoginResponse, LogoutResponse

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
REDIRECT_URI = "http://localhost:8000/auth/google/callback"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# 1) 일반 로그인 로직
# -----------------------------
async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(email: str):
    return await users_collection.find_one({"email": email})

async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return None
    # 비번 검증
    if not await verify_password(password, user["password"]):
        return None
    return user

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    아이디/비번으로 로그인 후 JWT 발급
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"email": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# -----------------------------
# 2) Google OAuth 로직
# -----------------------------
async def get_google_login_url():
    return OAuthLoginResponse(auth_url=(
        f"{GOOGLE_AUTH_URL}"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=email%20profile"
        f"&access_type=offline"
    ))

async def authenticate_google_user(code: str):
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

        user_info_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_response.json()

        email = user_info.get("email")
        username = user_info.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="사용자 이메일을 가져올 수 없음")

        # DB에 저장된 유저 찾기
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            await users_collection.update_one(
                {"email": email},
                {"$set": {"username": username, "oauth_provider": "google"}}
            )
        else:
            await users_collection.insert_one(
                {"email": email, "username": username, "oauth_provider": "google"}
            )

        # JWT 토큰 생성
        jwt_token = create_access_token({"email": email})
        
        # ✅ Set-Cookie 수정
        response = RedirectResponse(url="/")
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {jwt_token}",
            httponly=True,  # ✅ JavaScript에서 접근 불가
            samesite="Lax",  # ✅ SameSite 설정 (쿠키 전송 가능)
            secure=False,  # 🚨 로컬에서는 `False`, 배포 시 `True` 변경
        )

        return response

# -----------------------------
# 3) 로그아웃 로직
# -----------------------------
async def logout_user(response: Response):
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response
