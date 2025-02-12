from pydantic import BaseModel
from typing import Optional, Dict

# ✅ 공통 응답 모델
class ResponseModel(BaseModel):
    message: str
    data: Optional[Dict] = None  # 추가 데이터가 있을 경우 포함 가능
