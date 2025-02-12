# routes/post.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.schemas import post
from app.services.post_service import (
    create_post, get_posts, get_post, save_image, update_post, delete_post, 
    update_post_reactions, update_scrap_count
)
from app.schemas.post import PostResponse, PostListResponse
from app.schemas.base import ResponseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 게시글 생성
@router.post("/", response_model=PostResponse)
async def create_post_route(
    title: str = Form(..., min_length=1, max_length=100),
    content: str = Form(..., min_length=1),
    preset_id: Optional[str] = Form(None),
    is_public: bool = Form(True),
    token: str = Depends(oauth2_scheme),
    file: Optional[UploadFile] = File(None)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    post_data = await create_post(
        title=title,
        content=content,
        preset_id=preset_id,
        is_public=is_public,
        created_by=payload["email"],
        file=file
    )
    return PostResponse(**post_data)

# 게시글 좋아요 / 싫어요
@router.post("/{post_id}/reaction", response_model=ResponseModel)
async def update_post_reactions_route(post_id: str, like: bool, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    await update_post_reactions(post_id, like)
    return ResponseModel(message="Reaction updated successfully")

# 게시글 목록 조회
@router.get("/", response_model=PostListResponse)
async def get_posts_route():
    return PostListResponse(posts=await get_posts())

# 특정 게시글 조회
@router.get("/{post_id}", response_model=PostResponse)
async def get_post_route(post_id: str):
    post = await get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse(**post)

# 게시글 수정 (Form 데이터로 처리)
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_route(
    post_id: str,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    preset_id: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(None),
    file: Optional[UploadFile] = File(None),
    token: str = Depends(oauth2_scheme)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    image_url = await save_image(file) if file else None

    updated_post = await update_post(
        post_id=post_id,
        title=title,
        content=content,
        preset_id=preset_id,
        is_public=is_public,
        image_url=image_url
    )
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse(**updated_post)

# 게시글 삭제
@router.delete("/{post_id}", response_model=ResponseModel)
async def delete_post_route(post_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    await delete_post(post_id)
    return ResponseModel(message="Post deleted successfully")

# 게시글 스크랩
@router.post("/{post_id}/scrap", response_model=ResponseModel)
async def update_scrap_count_route(post_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    await update_scrap_count(post_id, 1)
    return ResponseModel(message="Post scrapped successfully")
