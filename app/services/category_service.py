from app.core.database import categories_collection, programs_collection
from bson import ObjectId, errors
from app.core.utils import convert_objectid

async def create_category(name: str, created_by: str):
    """카테고리 생성"""
    category = {"name": name, "created_by": created_by}
    result = await categories_collection.insert_one(category)
    return str(result.inserted_id)

async def get_categories():
    """모든 카테고리 조회"""
    categories = await categories_collection.find().to_list(100)
    
    # ✅ ObjectId -> str 변환 + 필드명 `_id` → `id` 변경
    return [{"id": str(cat["_id"]), "name": cat["name"]} for cat in categories]


async def get_category(category_id: str):
    """특정 카테고리 조회"""
    try:
        obj_id = ObjectId(category_id)
    except errors.InvalidId:
        return None

    category = await categories_collection.find_one({"_id": obj_id})
    if category:
        return {"id": str(category["_id"]), "name": category["name"]}
    
    return None


async def update_category(category_id: str, new_name: str):
    """카테고리 이름 수정"""
    obj_id = ObjectId(category_id)
    await categories_collection.update_one({"_id": obj_id}, {"$set": {"name": new_name}})
    
    category = await categories_collection.find_one({"_id": obj_id})
    if category:
        return {"id": str(category["_id"]), "name": category["name"]}
    
    return None


async def delete_category(category_id: str):
    """카테고리 삭제"""
    obj_id = ObjectId(category_id)
    await categories_collection.delete_one({"_id": obj_id})

async def get_or_create_uncategorized(email: str):
    """사용자의 '미분류' 카테고리를 찾거나 없으면 생성"""
    category = await categories_collection.find_one({"name": "미분류", "created_by": "system"})

    if not category:
        new_category = {"name": "미분류", "created_by": "system"}
        result = await categories_collection.insert_one(new_category)
        category_id = str(result.inserted_id)
    else:
        category_id = str(category["_id"])

    return category_id
