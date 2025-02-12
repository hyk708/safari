from fastapi import HTTPException
from app.core.database import presets_collection, categories_collection
from bson import ObjectId, errors
from datetime import datetime
from app.core.utils import convert_objectid
from typing import Optional, List
import json

async def create_preset(name: str, description: Optional[str], category_ids: List[str], programs: List[str], created_by: str, is_public: bool):
    """프리셋 생성"""

    # 동일한 이름의 프리셋이 존재하는지 확인
    existing_preset = await presets_collection.find_one({"name": name, "created_by": created_by})
    if existing_preset:
        raise HTTPException(status_code=400, detail="You already have a preset with this name.")

    valid_category_ids = []
    for category_id in category_ids:
        try:
            obj_id = ObjectId(category_id)
            category = await categories_collection.find_one({"_id": obj_id})
            if category:
                valid_category_ids.append(category_id)
        except errors.InvalidId:
            continue

    preset = {
        "name": name,
        "description": description,
        "category_ids": valid_category_ids,
        "programs": programs,
        "created_by": created_by,
        "is_public": is_public,
        "created_at": datetime.utcnow(),
    }

    result = await presets_collection.insert_one(preset)
    preset["_id"] = str(result.inserted_id)  # ✅ ObjectId를 문자열로 변환
    return preset

async def generate_preset_json(preset_id: str, user_email: str):
    """프리셋 JSON 생성"""
    preset = await presets_collection.find_one({"_id": ObjectId(preset_id), "created_by": user_email})
    if not preset:
        return None
    
    preset_json = {
        "name": preset["name"],
        "description": preset["description"],
        "categories": preset["category_ids"],
        "programs": preset["programs"],
        "created_by": preset["created_by"],
    }

    return json.dumps(preset_json, indent=4)

async def get_presets():
    """모든 프리셋 조회"""
    presets = await presets_collection.find().to_list(100)

    return [
        {
            "id": str(preset["_id"]),
            "name": preset.get("name", ""),
            "description": preset.get("description", ""),
            "category_ids": preset.get("category_ids", []),
            "created_by": preset.get("created_by", ""),
            "is_public": preset.get("is_public", False),
            "created_at": preset.get("created_at", datetime.utcnow()),
        }
        for preset in presets
    ]

async def get_preset(preset_id: str):
    """특정 프리셋 조회"""
    try:
        obj_id = ObjectId(preset_id)
    except errors.InvalidId:
        return None

    preset = await presets_collection.find_one({"_id": obj_id})
    if not preset:
        return None

    return {
        "id": str(preset["_id"]),
        "name": preset.get("name", ""),
        "description": preset.get("description", ""),
        "category_ids": preset.get("category_ids", []),
        "created_by": preset.get("created_by", ""),
        "is_public": preset.get("is_public", False),
        "created_at": preset.get("created_at", datetime.utcnow()),
    }

async def update_preset(preset_id: str, name: Optional[str], description: Optional[str], category_ids: Optional[List[str]], is_public: Optional[bool]):
    """프리셋 수정"""
    obj_id = ObjectId(preset_id)
    update_fields = {}

    if name:
        update_fields["name"] = name
    if description:
        update_fields["description"] = description
    if is_public is not None:
        update_fields["is_public"] = is_public
    if category_ids is not None:
        valid_category_ids = []
        for category_id in category_ids:
            try:
                obj_id = ObjectId(category_id)
                category = await categories_collection.find_one({"_id": obj_id})
                if category:
                    valid_category_ids.append(category_id)
            except errors.InvalidId:
                continue
        update_fields["category_ids"] = valid_category_ids

    if update_fields:
        await presets_collection.update_one({"_id": obj_id}, {"$set": update_fields})

    updated_preset = await presets_collection.find_one({"_id": obj_id})
    if not updated_preset:
        return None

    return {
        "id": str(updated_preset["_id"]),
        "name": updated_preset.get("name", ""),
        "description": updated_preset.get("description", ""),
        "category_ids": updated_preset.get("category_ids", []),
        "created_by": updated_preset.get("created_by", ""),
        "is_public": updated_preset.get("is_public", False),
        "created_at": updated_preset.get("created_at", datetime.utcnow()),
    }

async def delete_preset(preset_id: str):
    """프리셋 삭제"""
    obj_id = ObjectId(preset_id)
    await presets_collection.delete_one({"_id": obj_id})