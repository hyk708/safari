from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId, errors
from app.core.security import decode_access_token
from app.core.utils import convert_objectid
from app.services.program_service import (
    create_program, get_programs, get_program, update_program, delete_program
)
from app.services.category_service import get_or_create_uncategorized, get_category
from app.schemas.program import ProgramCreate, ProgramUpdate, ProgramResponse, ProgramListResponse
from app.schemas.base import ResponseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ✅ 프로그램 생성
@router.post("/", response_model=ProgramResponse)
async def create_program_route(program: ProgramCreate, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ "미분류" 카테고리 자동 배정
    category_id = program.category_id if program.category_id else await get_or_create_uncategorized(payload["email"])

    program_id = await create_program(program.name, category_id, payload["email"])
    return ProgramResponse(id=program_id, name=program.name, category_id=category_id if category_id else None)

# ✅ 모든 프로그램 조회
@router.get("/", response_model=ProgramListResponse)
async def get_programs_route(category_id: str = None):
    # ✅ category_id가 존재하면 ObjectId 변환 시도
    if category_id is not None:
        try:
            category_id = ObjectId(category_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid category ID format")

    return ProgramListResponse(programs=await get_programs(category_id))

# ✅ 특정 프로그램 조회
@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program_route(program_id: str):
    program = await get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    return program

@router.put("/{program_id}", response_model=ProgramResponse)
async def update_program_route(program_id: str, program: ProgramUpdate, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ category_id가 있으면 유효성 검증
    if program.category_id:
        try:
            obj_id = ObjectId(program.category_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid category ID format")

        # ✅ 해당 category_id가 존재하는지 확인
        category_exists = await get_category(program.category_id)
        if not category_exists:
            raise HTTPException(status_code=404, detail="Category not found")

    updated_program = await update_program(program_id, program.name, program.category_id)
    if not updated_program:
        raise HTTPException(status_code=404, detail="Program not found")

    return convert_objectid(updated_program)  # ✅ 변환 적용


# ✅ 프로그램 삭제
@router.delete("/{program_id}", response_model=ResponseModel)
async def delete_program_route(program_id: str, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    await delete_program(program_id)
    return ResponseModel(message="Program deleted successfully")
