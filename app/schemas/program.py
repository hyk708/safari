from pydantic import BaseModel, Field
from typing import Optional, List

# ✅ 프로그램 생성 요청
class ProgramCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[str] = None  # 선택적으로 미분류 가능

# ✅ 프로그램 수정 요청
class ProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    category_id: Optional[str] = None

# ✅ 프로그램 응답 모델
class ProgramResponse(BaseModel):
    id: str
    name: str
    category_id: Optional[str]

class ProgramListResponse(BaseModel):
    programs: List[ProgramResponse]
