from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.core.database import categories_collection, programs_collection
from bson import ObjectId, errors
from app.core.utils import convert_objectid

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ✅ Create a new category (카테고리 생성)
@router.post("/")
async def create_category(name: str = Body(..., embed=True), token: str = Depends(oauth2_scheme)):
    """새로운 카테고리 생성 (본인만 생성 가능)"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    category = {"name": name, "created_by": payload["email"]}
    result = await categories_collection.insert_one(category)
    return {"id": str(result.inserted_id), "name": name}

# ✅ Read all categories (모든 카테고리 조회)
@router.get("/")
async def get_categories():
    """모든 카테고리 조회 (모든 사용자 가능)"""
    categories = await categories_collection.find().to_list(100)
    return convert_objectid(categories)

# ✅ Read a single category (특정 카테고리 조회)
@router.get("/{category_id}")
async def get_category(category_id: str):
    """특정 카테고리 정보 및 해당 카테고리에 속한 프로그램 조회"""
    
    try:
        obj_id = ObjectId(category_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    category = await categories_collection.find_one({"_id": obj_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    programs = await programs_collection.find({"category_id": category_id}).to_list(100)

    return {
        "category": convert_objectid(category),
        "programs": convert_objectid(programs)
    }

# ✅ Update a category (카테고리 수정)
@router.put("/{category_id}")
async def update_category(
    category_id: str, 
    data: dict = Body(...),  
    token: str = Depends(oauth2_scheme)
):
    """카테고리 수정 (본인이 생성한 것만 가능)"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        obj_id = ObjectId(category_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    category = await categories_collection.find_one({"_id": obj_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category["created_by"] != payload["email"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    new_name = data.get("name")
    if not new_name:
        raise HTTPException(status_code=400, detail="Missing 'name' field")

    await categories_collection.update_one({"_id": obj_id}, {"$set": {"name": new_name}})
    return {"message": "Category updated successfully"}

# ✅ Delete a category (카테고리 삭제)
@router.delete("/{category_id}")
async def delete_category(category_id: str, token: str = Depends(oauth2_scheme)):
    """카테고리 삭제 (본인이 생성한 것만 가능)"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        obj_id = ObjectId(category_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    category = await categories_collection.find_one({"_id": obj_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category["created_by"] != payload["email"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # ✅ 카테고리가 삭제되면 해당 카테고리에 속한 프로그램을 "미분류" 상태로 변경
    await programs_collection.update_many({"category_id": category_id}, {"$set": {"category_id": None}})
    
    await categories_collection.delete_one({"_id": obj_id})
    return {"message": "Category deleted successfully"}
