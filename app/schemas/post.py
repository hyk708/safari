from pydantic import BaseModel, Field
from typing import Optional, List

# ✅ 게시글 생성 요청
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    category_id: Optional[str] = None
    image_url: Optional[str] = None

# ✅ 게시글 응답 모델
class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    category_id: Optional[str]
    image_url: Optional[str]
    like_count: int
    dislike_count: int
    comment_count: int
    scrap_count: int

class PostListResponse(BaseModel):
    posts: List[PostResponse]
