from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.services.preset_service import (
    create_preset, get_presets, get_preset, update_preset, delete_preset, generate_preset_json
)
from app.services.post_service import create_post_from_preset
from app.schemas.preset import PresetCreate, PresetUpdate, PresetResponse, PresetListResponse
from app.schemas.base import ResponseModel
from datetime import datetime
from bson import ObjectId

from app.services.program_service import get_programs

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
async def get_presets_route(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    presets = await get_presets(payload["email"])
    return PresetListResponse(presets=presets)

# ✅ 특정 프리셋 조회 (프리셋 ID 기준)
@router.get("/{preset_id}", response_model=PresetResponse)
async def get_preset_route(preset_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    preset = await get_preset(preset_id, payload["email"])
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    return PresetResponse(**preset)

# ✅ 특정 프리셋 내 카테고리 목록 조회
@router.get("/{preset_id}/categories/", response_model=list)
async def get_preset_categories(preset_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    preset = await get_preset(preset_id, payload["email"])
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    return preset["category_ids"]

# ✅ 특정 카테고리 내 프로그램 목록 조회
@router.get("/{preset_id}/categories/{category_id}/programs/", response_model=list)
async def get_preset_category_programs(preset_id: str, category_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    preset = await get_preset(preset_id, payload["email"])
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    if category_id not in preset["category_ids"]:
        raise HTTPException(status_code=400, detail="Category not found in preset")

    programs = await get_programs(category_id)
    return programs

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

# ✅ 프리셋 공유 (preset.json 자동 생성 후 게시글 작성 연동)
@router.post("/{preset_id}/share", response_model=ResponseModel)
async def share_preset_route(preset_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    preset_json = await generate_preset_json(preset_id, payload["email"])
    if not preset_json:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    # 게시글 자동 생성 연동 (post_service 호출 가능)
    post_data = await create_post_from_preset(preset_json, payload["email"])
    if not post_data:
        raise HTTPException(status_code=500, detail="Failed to create post from preset")

    return ResponseModel(success=True, message="Preset shared successfully", data=post_data)