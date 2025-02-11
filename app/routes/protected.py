from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    """JWT 토큰을 쿠키에서 가져오거나 Authorization 헤더에서 가져옴"""
    token = request.cookies.get("access_token") or token  # ✅ 쿠키에서 가져오기
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(token.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload


@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    """JWT가 필요한 보호된 API"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"message": f"Hello, {payload['email']}! This is a protected route."}
