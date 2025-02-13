from pydantic import BaseModel, Field

# Google OAuth 로그인 URL 응답
class OAuthLoginResponse(BaseModel):
    auth_url: str = Field(..., example="https://accounts.google.com/o/oauth2/auth")

# Google OAuth callback 후 JWT
class OAuthCallbackResponse(BaseModel):
    message: str = Field(..., example="Login successful")
    access_token: str
    token_type: str = Field(default="Bearer", example="Bearer")

# 로그아웃 응답
class LogoutResponse(BaseModel):
    message: str = Field(..., example="Logout successful")
