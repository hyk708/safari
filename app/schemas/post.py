# schemas/post.py
from pydantic import BaseModel, Field
from fastapi import Form
from typing import List, Optional
from datetime import datetime

def PostCreate(
    title: str = Form(..., min_length=1, max_length=100),
    content: str = Form(..., min_length=1),
    preset_id: Optional[str] = Form(None),
    is_public: bool = Form(True),
):
    return {"title": title, "content": content, "preset_id": preset_id, "is_public": is_public}

# 게시글 수정 요청 모델 (참고용)
class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    preset_id: Optional[str] = None
    is_public: Optional[bool] = None

# 게시글 응답 모델
class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    preset_id: Optional[str]
    image_url: Optional[str]
    is_public: bool
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    scrap_count: int = 0
    created_at: datetime
    updated_at: datetime

# 게시글 목록 응답 모델
class PostListResponse(BaseModel):
    posts: List[PostResponse]
