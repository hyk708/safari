from fastapi import APIRouter, Depends, HTTPException, Body, Request
from bson import ObjectId
from app.core.database import programs_collection, categories_collection
from app.core.security import decode_access_token
from app.core.utils import convert_objectid
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    """JWT 토큰을 쿠키에서 가져오거나 Authorization 헤더에서 가져옴"""
    token = request.cookies.get("access_token") or token  # ✅ 쿠키에서 가져오기
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(token.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload

async def get_or_create_uncategorized(email: str):
    """사용자의 '미분류' 카테고리를 찾거나 없으면 생성"""
    category = await categories_collection.find_one({"name": "미분류", "created_by": email})

    if not category:
        new_category = {"name": "미분류", "created_by": email}
        result = await categories_collection.insert_one(new_category)
        category_id = str(result.inserted_id)
    else:
        category_id = str(category["_id"])

    return category_id

# ✅ Create a new program (프로그램 생성)
@router.post("/")
async def create_program(
    name: str = Body(..., embed=True), 
    category_id: str = None, 
    user: dict = Depends(get_current_user)
):
    """새로운 프로그램 생성 (본인만 생성 가능)"""
    if not category_id:
        category_id = await get_or_create_uncategorized(user["email"])  # ✅ 미분류 카테고리 자동 배정

    program = {"name": name, "category_id": category_id, "created_by": user["email"]}
    result = await programs_collection.insert_one(program)
    return {"id": str(result.inserted_id), "name": name, "category_id": category_id}

# ✅ Read all programs (프로그램 조회)
@router.get("/")
async def get_programs(category_id: str = None):
    """카테고리에 속한 프로그램 조회 (모든 사용자 가능)"""
    query = {"category_id": category_id} if category_id else {}
    programs = await programs_collection.find(query).to_list(100)
    return convert_objectid(programs)

# ✅ Update a program (프로그램 수정)
@router.put("/{program_id}")
async def update_program(
    program_id: str, 
    data: dict = Body(...),  # ✅ PUT 요청에서는 JSON으로 받는 것이 일반적
    user: dict = Depends(get_current_user)
):
    """프로그램 수정 (본인이 생성한 것만 가능)"""
    program = await programs_collection.find_one({"_id": ObjectId(program_id)})
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    if program["created_by"] != user["email"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    new_category_id = data.get("category_id")
    if new_category_id is None:
        raise HTTPException(status_code=400, detail="Missing 'category_id' field")

    await programs_collection.update_one({"_id": ObjectId(program_id)}, {"$set": {"category_id": new_category_id}})
    return {"message": "Program updated successfully"}

# ✅ Delete a program (프로그램 삭제)
@router.delete("/{program_id}")
async def delete_program(program_id: str, user: dict = Depends(get_current_user)):
    """프로그램 삭제 (본인이 생성한 것만 가능)"""
    program = await programs_collection.find_one({"_id": ObjectId(program_id)})
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    if program["created_by"] != user["email"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    await programs_collection.delete_one({"_id": ObjectId(program_id)})
    return {"message": "Program deleted successfully"}
