from pydantic import BaseModel, Field
from typing import Optional

# ✅ OAuth 로그인 요청 모델 (프론트엔드가 필요 시 사용할 수 있음)
class OAuthLoginRequest(BaseModel):
    provider: str = Field(..., example="google")

# ✅ OAuth 로그인 응답 모델
class OAuthLoginResponse(BaseModel):
    auth_url: str = Field(..., example="https://accounts.google.com/o/oauth2/auth")

# ✅ OAuth 로그인 후 JWT 반환
class OAuthCallbackResponse(BaseModel):
    message: str = Field(..., example="Login successful")
    access_token: str
    token_type: str = Field(default="Bearer", example="Bearer")

# ✅ 로그아웃 응답 모델
class LogoutResponse(BaseModel):
    message: str = Field(..., example="Logout successful")

# ✅ 현재 로그인한 사용자 정보 응답 모델
class UserResponse(BaseModel):
    email: str = Field(..., example="test@example.com")
