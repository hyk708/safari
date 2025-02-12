from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.services.category_service import (
    create_category, get_categories, get_category, update_category, delete_category
)
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from app.schemas.base import ResponseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ✅ 카테고리 생성
@router.post("/", response_model=CategoryResponse)
async def create_category_route(category: CategoryCreate, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    category_id = await create_category(category.name, payload["email"])
    return CategoryResponse(id=category_id, name=category.name)

# ✅ 모든 카테고리 조회
@router.get("/", response_model=CategoryListResponse)
async def get_categories_route():
    return CategoryListResponse(categories=await get_categories())

# ✅ 특정 카테고리 조회
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_route(category_id: str):
    category = await get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category

# ✅ 카테고리 수정
@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category_route(category_id: str, category: CategoryUpdate, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    updated_category = await update_category(category_id, category.name)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")

    return updated_category

# ✅ 카테고리 삭제
@router.delete("/{category_id}", response_model=ResponseModel)
async def delete_category_route(category_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    await delete_category(category_id)
    return ResponseModel(message="Category deleted successfully")
