from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ✅ 프리셋 생성 요청 모델
class PresetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    category_ids: List[str] = []  # ✅ 카테고리 ID 목록
    is_public: bool = Field(default=False)  # ✅ 공개 여부

# ✅ 프리셋 수정 요청 모델
class PresetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    category_ids: Optional[List[str]] = None
    is_public: Optional[bool] = None  # ✅ 공개 여부 수정 가능

# ✅ 프리셋 응답 모델
class PresetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category_ids: List[str]
    created_by: str
    is_public: bool
    created_at: datetime

# ✅ 프리셋 목록 응답 모델
class PresetListResponse(BaseModel):
    presets: List[PresetResponse]
