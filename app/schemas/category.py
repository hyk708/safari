from pydantic import BaseModel, Field
from typing import Optional, List

# ✅ 카테고리 생성 요청
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)  # 빈 값 방지

# ✅ 카테고리 수정 요청
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)

# ✅ 카테고리 응답 모델
class CategoryResponse(BaseModel):
    id: str
    name: str

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
