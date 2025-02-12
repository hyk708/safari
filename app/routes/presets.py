from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.services.preset_service import (
    create_preset, get_presets, get_preset, update_preset, delete_preset
)
from app.schemas.preset import PresetCreate, PresetUpdate, PresetResponse, PresetListResponse
from app.schemas.base import ResponseModel
from datetime import datetime

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fucking API
# ✅ 프리셋 생성
@router.post("/", response_model=PresetResponse)
async def create_preset_route(preset: PresetCreate, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    preset_data = await create_preset(
        preset.name, preset.description, preset.category_ids, payload["email"], preset.is_public
    )
    
    return PresetResponse(
        id=preset_data["_id"],  # ✅ ObjectId 변환된 값 사용
        name=preset_data["name"],
        description=preset_data["description"],
        category_ids=preset_data["category_ids"],
        created_by=preset_data["created_by"],
        is_public=preset_data["is_public"],
        created_at=preset_data["created_at"],
    )

# ✅ 모든 프리셋 조회
@router.get("/", response_model=PresetListResponse)
async def get_presets_route():
    return PresetListResponse(presets=await get_presets())

# ✅ 특정 프리셋 조회
@router.get("/{preset_id}", response_model=PresetResponse)
async def get_preset_route(preset_id: str):
    preset = await get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    return preset

# ✅ 프리셋 수정
@router.put("/{preset_id}", response_model=PresetResponse)
async def update_preset_route(preset_id: str, preset: PresetUpdate, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    updated_preset = await update_preset(preset_id, preset.name, preset.description, preset.category_ids, preset.is_public)
    if not updated_preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    return updated_preset

# ✅ 프리셋 삭제
@router.delete("/{preset_id}", response_model=ResponseModel)
async def delete_preset_route(preset_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    await delete_preset(preset_id)
    return ResponseModel(message="Preset deleted successfully")