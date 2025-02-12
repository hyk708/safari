from pydantic import BaseModel, Field
from typing import Optional, List

# ✅ 댓글 생성 요청
class CommentCreate(BaseModel):
    post_id: str
    content: str = Field(..., min_length=1)

# ✅ 댓글 응답 모델
class CommentResponse(BaseModel):
    id: str
    post_id: str
    content: str
    like_count: int
    dislike_count: int

class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
